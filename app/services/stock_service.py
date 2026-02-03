"""Stock checking service."""

import logging
from typing import Optional

from app.database.connection import db_manager
from app.models.stock import ProductStockDTO, StockCheckResultDTO

logger = logging.getLogger(__name__)


def get_product_stock(isbn: str) -> Optional[ProductStockDTO]:
    """Get stock information for a product by ISBN.

    Args:
        isbn: Product ISBN

    Returns:
        ProductStockDTO with stock info, or None if product not found
    """
    with db_manager.cursor() as cursor:
        cursor.execute(
            """SELECT ISBN, ProductName, InStock, SafetyStock,
                      WaitingIntoInStock, WaitingShipmentQuantity
               FROM dbo.Product WHERE ISBN = %s""",
            (isbn,),
        )
        row = cursor.fetchone()

    if not row:
        return None

    in_stock = row.get("InStock") or 0
    safety_stock = row.get("SafetyStock") or 0
    waiting_into = row.get("WaitingIntoInStock") or 0
    waiting_shipment = row.get("WaitingShipmentQuantity") or 0

    # Available = InStock - SafetyStock + WaitingIntoInStock - WaitingShipmentQuantity
    available = in_stock - safety_stock + waiting_into - waiting_shipment

    return ProductStockDTO(
        isbn=row.get("ISBN"),
        product_name=row.get("ProductName"),
        in_stock=in_stock,
        safety_stock=safety_stock,
        waiting_into_in_stock=waiting_into,
        waiting_shipment_quantity=waiting_shipment,
        available_quantity=max(0, available),
    )


def is_shipment_in_stock_enough(isbn: str, quantity: int) -> tuple[bool, int]:
    """Check if there's enough stock for shipment.

    Args:
        isbn: Product ISBN
        quantity: Required quantity

    Returns:
        Tuple of (is_enough, available_quantity)
    """
    stock = get_product_stock(isbn)
    if not stock:
        return False, 0

    available = stock.available_quantity or 0
    return available >= quantity, available


def check_stock_for_items(items: list[dict]) -> list[StockCheckResultDTO]:
    """Check stock availability for multiple items.

    Args:
        items: List of dicts with 'isbn' and 'quantity' keys

    Returns:
        List of StockCheckResultDTO for each item
    """
    results = []

    for item in items:
        isbn = item.get("isbn", "")
        requested = item.get("quantity", 0)

        stock = get_product_stock(isbn)

        if stock:
            available = stock.available_quantity or 0
            is_sufficient = available >= requested
            shortage = max(0, requested - available) if not is_sufficient else 0

            results.append(StockCheckResultDTO(
                isbn=isbn,
                product_name=stock.product_name,
                requested_quantity=requested,
                available_quantity=available,
                is_sufficient=is_sufficient,
                shortage_quantity=shortage,
            ))
        else:
            # Product not found - treat as zero stock
            results.append(StockCheckResultDTO(
                isbn=isbn,
                product_name=None,
                requested_quantity=requested,
                available_quantity=0,
                is_sufficient=False,
                shortage_quantity=requested,
            ))

    return results


def update_waiting_shipment_quantity(isbn: str, delta: int) -> bool:
    """Update the WaitingShipmentQuantity for a product.

    Args:
        isbn: Product ISBN
        delta: Amount to add (positive) or subtract (negative)

    Returns:
        True if update succeeded
    """
    try:
        with db_manager.cursor() as cursor:
            cursor.execute(
                """UPDATE dbo.Product
                   SET WaitingShipmentQuantity = ISNULL(WaitingShipmentQuantity, 0) + %s
                   WHERE ISBN = %s""",
                (delta, isbn),
            )
        logger.info("Updated WaitingShipmentQuantity for %s by %d", isbn, delta)
        return True
    except Exception as e:
        logger.error("Failed to update WaitingShipmentQuantity for %s: %s", isbn, e)
        return False


def update_waiting_into_in_stock(isbn: str, delta: int) -> bool:
    """Update the WaitingIntoInStock for a product.

    Args:
        isbn: Product ISBN
        delta: Amount to add (positive) or subtract (negative)

    Returns:
        True if update succeeded
    """
    try:
        with db_manager.cursor() as cursor:
            cursor.execute(
                """UPDATE dbo.Product
                   SET WaitingIntoInStock = ISNULL(WaitingIntoInStock, 0) + %s
                   WHERE ISBN = %s""",
                (delta, isbn),
            )
        logger.info("Updated WaitingIntoInStock for %s by %d", isbn, delta)
        return True
    except Exception as e:
        logger.error("Failed to update WaitingIntoInStock for %s: %s", isbn, e)
        return False


def update_in_stock(isbn: str, delta: int) -> bool:
    """Update the InStock for a product.

    Args:
        isbn: Product ISBN
        delta: Amount to add (positive) or subtract (negative)

    Returns:
        True if update succeeded
    """
    try:
        with db_manager.cursor() as cursor:
            cursor.execute(
                """UPDATE dbo.Product
                   SET InStock = ISNULL(InStock, 0) + %s
                   WHERE ISBN = %s""",
                (delta, isbn),
            )
        logger.info("Updated InStock for %s by %d", isbn, delta)
        return True
    except Exception as e:
        logger.error("Failed to update InStock for %s: %s", isbn, e)
        return False
