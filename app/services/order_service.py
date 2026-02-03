"""Order CRUD and query service."""

import logging
from typing import Optional

from app.database.connection import db_manager
from app.models.order import (
    OrderDTO,
    OrderItemDTO,
    OrderReferenceDTO,
    OrderDetailDTO,
    OrderTraceabilityDTO,
)

logger = logging.getLogger(__name__)

# OrderSource ordinal values
ORDER_SOURCE_QUOTATION = 0  # 報價單 (customer quotation)
ORDER_SOURCE_SUB_BILL = 1  # 出貨子貨單
ORDER_SOURCE_PURCHASE = 2  # 採購單 (purchase order to supplier)
ORDER_SOURCE_WAITING_SHIPMENT = 3  # 待出貨單
ORDER_SOURCE_SHIPMENT = 4  # 出貨單
ORDER_SOURCE_WAITING_RECEIPT = 5  # 待入倉單
ORDER_SOURCE_RECEIPT = 6  # 進貨單


def _row_to_order_dto(row: dict) -> OrderDTO:
    """Convert a database row to OrderDTO."""
    return OrderDTO(
        id=row.get("id"),
        order_number=str(row.get("OrderNumber")) if row.get("OrderNumber") else None,
        order_date=str(row.get("OrderDate")) if row.get("OrderDate") else None,
        order_source=row.get("OrderSource"),
        object_id=row.get("ObjectID"),
        is_checkout=bool(row.get("isCheckout")),
        number_of_items=row.get("NumberOfItems"),
        establish_source=row.get("EstablishSource"),
        is_borrowed=bool(row.get("isBorrowed")),
        is_offset=bool(row.get("isOffset")),
        remark=row.get("Remark"),
        cashier_remark=row.get("CashierRemark"),
        status=row.get("status"),
        waiting_order_date=str(row.get("WaitingOrderDate")) if row.get("WaitingOrderDate") else None,
        waiting_order_number=str(row.get("WaitingOrderNumber")) if row.get("WaitingOrderNumber") else None,
        already_order_date=str(row.get("AlreadyOrderDate")) if row.get("AlreadyOrderDate") else None,
        already_order_number=str(row.get("AlreadyOrderNumber")) if row.get("AlreadyOrderNumber") else None,
    )


def _row_to_item_dto(row: dict) -> OrderItemDTO:
    """Convert a database row to OrderItemDTO."""
    return OrderItemDTO(
        item_number=row.get("ItemNumber"),
        isbn=row.get("ISBN"),
        product_name=row.get("ProductName"),
        quantity=row.get("Quantity"),
        unit=row.get("Unit"),
        batch_price=row.get("BatchPrice"),
        single_price=row.get("SinglePrice"),
        pricing=row.get("Pricing"),
        price_amount=row.get("PriceAmount"),
        remark=row.get("Remark"),
    )


def get_order_by_id(order_id: int) -> Optional[OrderDTO]:
    """Get order by ID.

    Args:
        order_id: Order ID

    Returns:
        OrderDTO or None if not found
    """
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM dbo.Orders WHERE id = %s",
            (order_id,),
        )
        row = cursor.fetchone()

    if not row:
        return None

    return _row_to_order_dto(row)


def get_order_items(order_id: int) -> list[OrderItemDTO]:
    """Get items for an order.

    Args:
        order_id: Order ID

    Returns:
        List of OrderItemDTO
    """
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM dbo.Orders_Items WHERE Order_id = %s ORDER BY ItemNumber",
            (order_id,),
        )
        rows = cursor.fetchall()

    return [_row_to_item_dto(row) for row in rows]


def get_order_references(order_id: int) -> list[OrderReferenceDTO]:
    """Get references for an order.

    Args:
        order_id: Order ID

    Returns:
        List of OrderReferenceDTO
    """
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM dbo.Orders_Reference WHERE Order_Id = %s",
            (order_id,),
        )
        rows = cursor.fetchall()

    return [
        OrderReferenceDTO(
            id=row.get("id"),
            order_id=row.get("Order_Id"),
            order_reference_id=row.get("Order_Reference_Id"),
            sub_bill_reference_id=row.get("SubBill_Reference_Id"),
        )
        for row in rows
    ]


def get_order_detail(order_id: int) -> Optional[OrderDetailDTO]:
    """Get full order details including items and references.

    Args:
        order_id: Order ID

    Returns:
        OrderDetailDTO or None if not found
    """
    order = get_order_by_id(order_id)
    if not order:
        return None

    items = get_order_items(order_id)
    references = get_order_references(order_id)

    return OrderDetailDTO(
        order=order,
        items=items,
        references=references,
    )


def list_orders(
    order_source: Optional[int] = None,
    object_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[OrderDTO], int]:
    """List orders with filtering and pagination.

    Args:
        order_source: Filter by order source
        object_id: Filter by customer/supplier ID
        start_date: Filter by start date (inclusive)
        end_date: Filter by end date (inclusive)
        status: Filter by status
        page: Page number (1-based)
        page_size: Page size

    Returns:
        Tuple of (list of OrderDTO, total count)
    """
    conditions = []
    params = []

    if order_source is not None:
        conditions.append("OrderSource = %s")
        params.append(order_source)

    if object_id:
        conditions.append("ObjectID = %s")
        params.append(object_id)

    if start_date:
        conditions.append("OrderDate >= %s")
        params.append(start_date)

    if end_date:
        conditions.append("OrderDate <= %s")
        params.append(end_date)

    if status is not None:
        conditions.append("status = %s")
        params.append(status)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Get total count
    with db_manager.cursor() as cursor:
        cursor.execute(
            f"SELECT COUNT(*) AS cnt FROM dbo.Orders WHERE {where_clause}",
            tuple(params),
        )
        total = cursor.fetchone()["cnt"]

    # Get page of results
    offset = (page - 1) * page_size
    with db_manager.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM dbo.Orders
                WHERE {where_clause}
                ORDER BY OrderDate DESC, id DESC
                OFFSET %s ROWS FETCH NEXT %s ROWS ONLY""",
            tuple(params) + (offset, page_size),
        )
        rows = cursor.fetchall()

    orders = [_row_to_order_dto(row) for row in rows]
    return orders, total


def get_order_traceability(order_id: int) -> Optional[OrderTraceabilityDTO]:
    """Get order traceability chain.

    Args:
        order_id: Order ID

    Returns:
        OrderTraceabilityDTO with source and derived orders
    """
    current = get_order_by_id(order_id)
    if not current:
        return None

    # Get orders this one was derived from (source orders)
    with db_manager.cursor() as cursor:
        cursor.execute(
            """SELECT o.* FROM dbo.Orders o
               INNER JOIN dbo.Orders_Reference r ON o.id = r.Order_Reference_Id
               WHERE r.Order_Id = %s AND r.Order_Reference_Id IS NOT NULL""",
            (order_id,),
        )
        source_rows = cursor.fetchall()

    # Get orders derived from this one
    with db_manager.cursor() as cursor:
        cursor.execute(
            """SELECT o.* FROM dbo.Orders o
               INNER JOIN dbo.Orders_Reference r ON o.id = r.Order_Id
               WHERE r.Order_Reference_Id = %s""",
            (order_id,),
        )
        derived_rows = cursor.fetchall()

    source_orders = [_row_to_order_dto(row) for row in source_rows]
    derived_orders = [_row_to_order_dto(row) for row in derived_rows]

    return OrderTraceabilityDTO(
        current_order=current,
        source_orders=source_orders,
        derived_orders=derived_orders,
    )


def update_order_waiting_fields(
    order_id: int,
    waiting_order_date: str,
    waiting_order_number: str,
) -> bool:
    """Update waiting order tracking fields.

    Args:
        order_id: Order ID
        waiting_order_date: Date of waiting order
        waiting_order_number: Number of waiting order

    Returns:
        True if update succeeded
    """
    try:
        with db_manager.cursor() as cursor:
            cursor.execute(
                """UPDATE dbo.Orders
                   SET WaitingOrderDate = %s, WaitingOrderNumber = %s
                   WHERE id = %s""",
                (waiting_order_date, waiting_order_number, order_id),
            )
        logger.info("Updated waiting fields for order %d", order_id)
        return True
    except Exception as e:
        logger.error("Failed to update waiting fields for order %d: %s", order_id, e)
        return False


def update_order_already_fields(
    order_id: int,
    already_order_date: str,
    already_order_number: str,
) -> bool:
    """Update already order tracking fields.

    Args:
        order_id: Order ID
        already_order_date: Date of already order
        already_order_number: Number of already order

    Returns:
        True if update succeeded
    """
    try:
        with db_manager.cursor() as cursor:
            cursor.execute(
                """UPDATE dbo.Orders
                   SET AlreadyOrderDate = %s, AlreadyOrderNumber = %s
                   WHERE id = %s""",
                (already_order_date, already_order_number, order_id),
            )
        logger.info("Updated already fields for order %d", order_id)
        return True
    except Exception as e:
        logger.error("Failed to update already fields for order %d: %s", order_id, e)
        return False


def create_order_reference(
    order_id: int,
    order_reference_id: Optional[int] = None,
    sub_bill_reference_id: Optional[int] = None,
) -> bool:
    """Create an order reference record.

    Args:
        order_id: The order that references another
        order_reference_id: The referenced order ID
        sub_bill_reference_id: The referenced sub-bill ID

    Returns:
        True if insert succeeded
    """
    try:
        with db_manager.cursor() as cursor:
            cursor.execute(
                """INSERT INTO dbo.Orders_Reference
                   (Order_Id, Order_Reference_Id, SubBill_Reference_Id)
                   VALUES (%s, %s, %s)""",
                (order_id, order_reference_id, sub_bill_reference_id),
            )
        logger.info(
            "Created order reference: %d -> %s (sub: %s)",
            order_id,
            order_reference_id,
            sub_bill_reference_id,
        )
        return True
    except Exception as e:
        logger.error("Failed to create order reference: %s", e)
        return False
