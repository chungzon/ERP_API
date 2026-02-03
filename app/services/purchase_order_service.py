"""Auto purchase order generation service."""

import logging
from datetime import datetime
from typing import Optional

from app.database.connection import db_manager
from app.models.order_conversion import AutoPurchaseOrderInfo
from app.services.order_service import (
    ORDER_SOURCE_PURCHASE,
    create_order_reference,
)
from app.services.stock_service import update_waiting_into_in_stock

logger = logging.getLogger(__name__)

# EstablishSource (bit: 0=系統建立, 1=人工建立)
ESTABLISH_SOURCE_SYSTEM = 0


def _get_supplier_for_product(isbn: str) -> Optional[dict]:
    """Get supplier information for a product.

    Args:
        isbn: Product ISBN

    Returns:
        Dict with supplier info or None
    """
    with db_manager.cursor() as cursor:
        # Try to get supplier from Product table
        cursor.execute(
            """SELECT p.ISBN, p.ProductName, p.SupplierID,
                      s.ObjectID, s.ObjectName
               FROM dbo.Product p
               LEFT JOIN dbo.Supplier s ON p.SupplierID = s.ObjectID
               WHERE p.ISBN = %s""",
            (isbn,),
        )
        row = cursor.fetchone()

    if not row:
        return None

    return {
        "isbn": row.get("ISBN"),
        "product_name": row.get("ProductName"),
        "supplier_id": row.get("SupplierID") or row.get("ObjectID"),
        "supplier_name": row.get("ObjectName"),
    }


def _generate_purchase_order_number(order_date: str) -> int:
    """Generate purchase order number based on date. Returns bigint."""
    date_str = order_date.replace("-", "/")
    try:
        dt = datetime.strptime(date_str, "%Y/%m/%d")
    except ValueError:
        dt = datetime.now()

    prefix = dt.strftime("%Y%m%d")

    with db_manager.cursor() as cursor:
        cursor.execute(
            """SELECT MAX(OrderNumber) AS MaxNum FROM dbo.Orders
               WHERE OrderSource = %s AND OrderNumber LIKE %s""",
            (ORDER_SOURCE_PURCHASE, f"{prefix}%"),
        )
        row = cursor.fetchone()

    if row and row.get("MaxNum"):
        max_num = str(row["MaxNum"])
        seq = int(max_num[len(prefix):]) + 1
    else:
        seq = 1

    return int(f"{prefix}{seq:04d}")


def generate_purchase_quotation(
    source_quotation_id: int,
    shortage_items: list[dict],
) -> list[AutoPurchaseOrderInfo]:
    """Generate purchase orders for shortage items.

    Args:
        source_quotation_id: ID of the source quotation
        shortage_items: List of dicts with isbn, quantity, shortage_quantity

    Returns:
        List of AutoPurchaseOrderInfo for created orders
    """
    if not shortage_items:
        return []

    # Group items by supplier
    supplier_items: dict[str, list[dict]] = {}

    for item in shortage_items:
        isbn = item.get("isbn", "")
        shortage = item.get("shortage_quantity", 0)

        if shortage <= 0:
            continue

        supplier_info = _get_supplier_for_product(isbn)

        if supplier_info:
            supplier_id = supplier_info.get("supplier_id") or "UNKNOWN"
            supplier_name = supplier_info.get("supplier_name") or "未知供應商"
        else:
            supplier_id = "UNKNOWN"
            supplier_name = "未知供應商"

        if supplier_id not in supplier_items:
            supplier_items[supplier_id] = {
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "items": [],
            }

        supplier_items[supplier_id]["items"].append({
            "isbn": isbn,
            "product_name": supplier_info.get("product_name") if supplier_info else "",
            "quantity": shortage,
        })

    # Create purchase order for each supplier
    created_orders = []
    order_date = datetime.now().strftime("%Y/%m/%d")

    for supplier_id, supplier_data in supplier_items.items():
        items = supplier_data["items"]
        supplier_name = supplier_data["supplier_name"]

        if not items:
            continue

        order_number = _generate_purchase_order_number(order_date)

        try:
            with db_manager.cursor() as cursor:
                # Insert into Orders table
                cursor.execute(
                    """INSERT INTO dbo.Orders (
                        OrderNumber, OrderDate, OrderSource, ObjectID,
                        isCheckout, NumberOfItems, EstablishSource, isBorrowed, isOffset,
                        Remark, CashierRemark, status
                    ) VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s
                    )""",
                    (
                        order_number,
                        order_date,
                        ORDER_SOURCE_PURCHASE,
                        supplier_id,
                        0,  # isCheckout
                        len(items),
                        ESTABLISH_SOURCE_SYSTEM,
                        0,  # isBorrowed
                        0,  # isOffset
                        f"由報價單 #{source_quotation_id} 自動產生",
                        "",
                        0,  # status
                    ),
                )

                # Get inserted order ID
                cursor.execute("SELECT SCOPE_IDENTITY() AS id")
                order_id = int(cursor.fetchone()["id"])

                # Insert into Orders_Price table
                cursor.execute(
                    """INSERT INTO dbo.Orders_Price (
                        Order_id, OrderNumber, TotalPriceNoneTax, Tax, Discount, TotalPriceIncludeTax
                    ) VALUES (%s, %s, %s, %s, %s, %s)""",
                    (order_id, order_number, 0, 0, 0, 0),
                )

                # Insert order items
                for i, prod in enumerate(items):
                    cursor.execute(
                        """INSERT INTO dbo.Orders_Items (
                            Order_id, OrderNumber, ItemNumber, ISBN, ProductName,
                            Quantity, Unit, BatchPrice, SinglePrice, Pricing, PriceAmount, Remark
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            order_id,
                            order_number,
                            i + 1,
                            prod["isbn"],
                            prod["product_name"],
                            prod["quantity"],
                            "",  # unit
                            0.0,  # batch_price
                            0.0,  # single_price
                            0.0,  # pricing
                            0,  # price_amount
                            "",  # remark
                        ),
                    )

                    # Update WaitingIntoInStock for product
                    update_waiting_into_in_stock(prod["isbn"], prod["quantity"])

                # Create reference to source quotation
                create_order_reference(order_id, source_quotation_id, None)

            logger.info(
                "Created purchase order %d for supplier %s with %d items",
                order_id,
                supplier_id,
                len(items),
            )

            created_orders.append(AutoPurchaseOrderInfo(
                order_id=order_id,
                order_number=str(order_number),
                supplier_id=supplier_id,
                supplier_name=supplier_name,
                items_count=len(items),
            ))

        except Exception as e:
            logger.error("Failed to create purchase order for supplier %s: %s", supplier_id, e)
            raise

    return created_orders
