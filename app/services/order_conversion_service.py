"""Order conversion service - handles order lifecycle conversions."""

import logging
from datetime import datetime
from typing import Optional

from app.database.connection import db_manager
from app.models.order_conversion import (
    ConversionResultDTO,
    AutoPurchaseOrderInfo,
)
from app.models.stock import StockCheckResultDTO
from app.services.order_service import (
    get_order_by_id,
    get_order_items,
    update_order_waiting_fields,
    update_order_already_fields,
    create_order_reference,
    ORDER_SOURCE_QUOTATION,
    ORDER_SOURCE_PURCHASE,
    ORDER_SOURCE_WAITING_SHIPMENT,
    ORDER_SOURCE_SHIPMENT,
    ORDER_SOURCE_WAITING_RECEIPT,
    ORDER_SOURCE_RECEIPT,
)
from app.services.stock_service import (
    check_stock_for_items,
    update_waiting_shipment_quantity,
    update_waiting_into_in_stock,
    update_in_stock,
)
from app.services.purchase_order_service import generate_purchase_quotation

logger = logging.getLogger(__name__)

# EstablishSource (bit: 0=系統建立, 1=人工建立)
ESTABLISH_SOURCE_SYSTEM = 0


def _generate_order_number(order_source: int, order_date: str) -> int:
    """Generate order number based on source type and date. Returns bigint."""
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
            (order_source, f"{prefix}%"),
        )
        row = cursor.fetchone()

    if row and row.get("MaxNum"):
        max_num = str(row["MaxNum"])
        seq = int(max_num[len(prefix):]) + 1
    else:
        seq = 1

    return int(f"{prefix}{seq:04d}")


def _create_new_order(
    source_order_id: int,
    target_order_source: int,
    items: Optional[list[dict]] = None,
) -> tuple[int, str, str]:
    """Create a new order based on source order.

    Args:
        source_order_id: Source order ID
        target_order_source: Target order source type
        items: Optional list of items with quantity overrides

    Returns:
        Tuple of (new_order_id, order_number, order_date)
    """
    source_order = get_order_by_id(source_order_id)
    if not source_order:
        raise ValueError(f"來源訂單 #{source_order_id} 不存在")

    source_items = get_order_items(source_order_id)
    if not source_items:
        raise ValueError(f"來源訂單 #{source_order_id} 沒有商品項目")

    order_date = datetime.now().strftime("%Y/%m/%d")
    order_number = _generate_order_number(target_order_source, order_date)

    # Build items map for quantity overrides
    items_map = {}
    if items:
        for item in items:
            key = item.get("isbn") or item.get("item_number")
            if key:
                items_map[key] = item.get("quantity")

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
                target_order_source,
                source_order.object_id,
                0,  # isCheckout
                len(source_items),
                ESTABLISH_SOURCE_SYSTEM,
                0,  # isBorrowed
                0,  # isOffset
                f"由訂單 #{source_order_id} 轉換產生",
                "",
                0,  # status
            ),
        )

        # Get inserted order ID
        cursor.execute("SELECT SCOPE_IDENTITY() AS id")
        new_order_id = int(cursor.fetchone()["id"])

        # Insert into Orders_Price table (copy from source)
        cursor.execute(
            """SELECT * FROM dbo.Orders_Price WHERE Order_id = %s""",
            (source_order_id,),
        )
        price_row = cursor.fetchone()

        if price_row:
            cursor.execute(
                """INSERT INTO dbo.Orders_Price (
                    Order_id, OrderNumber, TotalPriceNoneTax, Tax, Discount, TotalPriceIncludeTax
                ) VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    new_order_id,
                    order_number,
                    price_row.get("TotalPriceNoneTax", 0),
                    price_row.get("Tax", 0),
                    price_row.get("Discount", 0),
                    price_row.get("TotalPriceIncludeTax", 0),
                ),
            )
        else:
            cursor.execute(
                """INSERT INTO dbo.Orders_Price (
                    Order_id, OrderNumber, TotalPriceNoneTax, Tax, Discount, TotalPriceIncludeTax
                ) VALUES (%s, %s, %s, %s, %s, %s)""",
                (new_order_id, order_number, 0, 0, 0, 0),
            )

        # Insert order items
        for item in source_items:
            # Check for quantity override
            quantity = item.quantity
            if item.isbn and item.isbn in items_map:
                quantity = items_map[item.isbn]
            elif item.item_number and item.item_number in items_map:
                quantity = items_map[item.item_number]

            cursor.execute(
                """INSERT INTO dbo.Orders_Items (
                    Order_id, OrderNumber, ItemNumber, ISBN, ProductName,
                    Quantity, Unit, BatchPrice, SinglePrice, Pricing, PriceAmount, Remark
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    new_order_id,
                    order_number,
                    item.item_number,
                    item.isbn,
                    item.product_name,
                    quantity,
                    item.unit or "",
                    item.batch_price or 0.0,
                    item.single_price or 0.0,
                    item.pricing or 0.0,
                    item.price_amount or 0,
                    item.remark or "",
                ),
            )

        # Create reference to source order
        create_order_reference(new_order_id, source_order_id, None)

    logger.info(
        "Created order %d (source: %d) from order %d",
        new_order_id,
        target_order_source,
        source_order_id,
    )

    return new_order_id, str(order_number), order_date


def convert_quotation_to_waiting_shipment(
    quotation_id: int,
    items: Optional[list[dict]] = None,
    auto_generate_purchase: bool = True,
) -> ConversionResultDTO:
    """Convert quotation to waiting shipment order.

    報價單 → 待出貨單

    Args:
        quotation_id: Quotation order ID
        items: Optional items with quantity overrides
        auto_generate_purchase: Whether to auto-generate purchase orders for shortages

    Returns:
        ConversionResultDTO with result info
    """
    # Validate source order
    source_order = get_order_by_id(quotation_id)
    if not source_order:
        raise ValueError(f"報價單 #{quotation_id} 不存在")

    if source_order.order_source != ORDER_SOURCE_QUOTATION:
        raise ValueError(f"訂單 #{quotation_id} 不是報價單類型")

    # Get source items
    source_items = get_order_items(quotation_id)
    if not source_items:
        raise ValueError(f"報價單 #{quotation_id} 沒有商品項目")

    # Check stock for all items
    stock_check_items = [
        {"isbn": item.isbn, "quantity": item.quantity or 0}
        for item in source_items
        if item.isbn
    ]
    stock_results = check_stock_for_items(stock_check_items)

    # Identify shortage items
    shortage_items = [
        {
            "isbn": r.isbn,
            "quantity": r.requested_quantity,
            "shortage_quantity": r.shortage_quantity,
        }
        for r in stock_results
        if not r.is_sufficient and r.shortage_quantity and r.shortage_quantity > 0
    ]

    # Auto-generate purchase orders if needed
    auto_purchase_orders: list[AutoPurchaseOrderInfo] = []
    if auto_generate_purchase and shortage_items:
        auto_purchase_orders = generate_purchase_quotation(quotation_id, shortage_items)

    # Create waiting shipment order
    new_order_id, order_number, order_date = _create_new_order(
        quotation_id,
        ORDER_SOURCE_WAITING_SHIPMENT,
        items,
    )

    # Update source quotation tracking fields
    update_order_waiting_fields(quotation_id, order_date, order_number)

    # Update WaitingShipmentQuantity for each product
    for item in source_items:
        if item.isbn and item.quantity:
            update_waiting_shipment_quantity(item.isbn, item.quantity)

    return ConversionResultDTO(
        source_order_id=quotation_id,
        target_order_id=new_order_id,
        target_order_number=order_number,
        target_order_date=order_date,
        stock_check_results=stock_results,
        auto_purchase_orders=auto_purchase_orders if auto_purchase_orders else None,
    )


def convert_purchase_to_waiting_receipt(
    purchase_order_id: int,
    items: Optional[list[dict]] = None,
) -> ConversionResultDTO:
    """Convert purchase order to waiting receipt order.

    採購單 → 待入倉單

    Args:
        purchase_order_id: Purchase order ID
        items: Optional items with quantity overrides

    Returns:
        ConversionResultDTO with result info
    """
    # Validate source order
    source_order = get_order_by_id(purchase_order_id)
    if not source_order:
        raise ValueError(f"採購單 #{purchase_order_id} 不存在")

    if source_order.order_source != ORDER_SOURCE_PURCHASE:
        raise ValueError(f"訂單 #{purchase_order_id} 不是採購單類型")

    # Create waiting receipt order
    new_order_id, order_number, order_date = _create_new_order(
        purchase_order_id,
        ORDER_SOURCE_WAITING_RECEIPT,
        items,
    )

    # Update source purchase order tracking fields
    update_order_waiting_fields(purchase_order_id, order_date, order_number)

    return ConversionResultDTO(
        source_order_id=purchase_order_id,
        target_order_id=new_order_id,
        target_order_number=order_number,
        target_order_date=order_date,
    )


def convert_waiting_shipment_to_shipment(
    waiting_order_id: int,
    items: Optional[list[dict]] = None,
    is_partial: bool = False,
) -> ConversionResultDTO:
    """Convert waiting shipment to shipment order.

    待出貨單 → 出貨單

    Args:
        waiting_order_id: Waiting shipment order ID
        items: Optional items with quantity overrides (for partial shipment)
        is_partial: Whether this is a partial shipment

    Returns:
        ConversionResultDTO with result info
    """
    # Validate source order
    source_order = get_order_by_id(waiting_order_id)
    if not source_order:
        raise ValueError(f"待出貨單 #{waiting_order_id} 不存在")

    if source_order.order_source != ORDER_SOURCE_WAITING_SHIPMENT:
        raise ValueError(f"訂單 #{waiting_order_id} 不是待出貨單類型")

    # Get source items
    source_items = get_order_items(waiting_order_id)

    # Create shipment order
    new_order_id, order_number, order_date = _create_new_order(
        waiting_order_id,
        ORDER_SOURCE_SHIPMENT,
        items,
    )

    # Update source waiting order tracking fields
    update_order_already_fields(waiting_order_id, order_date, order_number)

    # Update stock quantities
    for item in source_items:
        if item.isbn and item.quantity:
            # Decrease WaitingShipmentQuantity
            update_waiting_shipment_quantity(item.isbn, -item.quantity)
            # Decrease InStock
            update_in_stock(item.isbn, -item.quantity)

    return ConversionResultDTO(
        source_order_id=waiting_order_id,
        target_order_id=new_order_id,
        target_order_number=order_number,
        target_order_date=order_date,
    )


def convert_waiting_receipt_to_receipt(
    waiting_order_id: int,
    items: Optional[list[dict]] = None,
    is_partial: bool = False,
) -> ConversionResultDTO:
    """Convert waiting receipt to receipt order.

    待入倉單 → 進貨單

    Args:
        waiting_order_id: Waiting receipt order ID
        items: Optional items with quantity overrides (for partial receipt)
        is_partial: Whether this is a partial receipt

    Returns:
        ConversionResultDTO with result info
    """
    # Validate source order
    source_order = get_order_by_id(waiting_order_id)
    if not source_order:
        raise ValueError(f"待入倉單 #{waiting_order_id} 不存在")

    if source_order.order_source != ORDER_SOURCE_WAITING_RECEIPT:
        raise ValueError(f"訂單 #{waiting_order_id} 不是待入倉單類型")

    # Get source items
    source_items = get_order_items(waiting_order_id)

    # Create receipt order
    new_order_id, order_number, order_date = _create_new_order(
        waiting_order_id,
        ORDER_SOURCE_RECEIPT,
        items,
    )

    # Update source waiting order tracking fields
    update_order_already_fields(waiting_order_id, order_date, order_number)

    # Update stock quantities
    for item in source_items:
        if item.isbn and item.quantity:
            # Decrease WaitingIntoInStock
            update_waiting_into_in_stock(item.isbn, -item.quantity)
            # Increase InStock
            update_in_stock(item.isbn, item.quantity)

    return ConversionResultDTO(
        source_order_id=waiting_order_id,
        target_order_id=new_order_id,
        target_order_number=order_number,
        target_order_date=order_date,
    )
