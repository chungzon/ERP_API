import logging
from typing import Optional

from app.database.connection import db_manager
from app.models.product import ProductDTO

logger = logging.getLogger(__name__)


def _round_price(value) -> str:
    """Round a numeric value to string, matching Java ToolKit.RoundingString."""
    if value is None:
        return "0"
    try:
        num = float(value)
        if num == int(num):
            return str(int(num))
        return str(round(num, 2))
    except (ValueError, TypeError):
        return "0"


def _build_search_query(isbn: Optional[str], firm_code: Optional[str], product_name: Optional[str]) -> tuple[str, list]:
    """Build the product search SQL query matching Java Product_Model.generateSearchProductQuery.

    Returns (query_string, params).
    Uses parameterized queries for safety.
    """
    base = (
        "SELECT A.*, B.*, C.*, "
        "D.InventoryDate, D.KeyinDate, D.UpdateDate, D.ShipmentDate, "
        "E.*, F.* "
        "FROM Store A "
        "INNER JOIN store_price B ON A.id = B.store_id "
        "INNER JOIN store_category C ON A.id = C.store_id "
        "INNER JOIN store_date D ON A.id = D.store_id "
        "INNER JOIN ProductPicture E ON A.id = E.store_id "
        "INNER JOIN ProductBookCase F ON A.id = F.store_id "
        "WHERE ("
    )

    params = []

    if isbn:
        base += "A.ISBN LIKE %s"
        params.append(f"{isbn}%")
    elif firm_code:
        base += "A.FirmCode LIKE %s"
        params.append(f"%{firm_code}%")
    elif product_name:
        # Support space-separated keywords (OR matching)
        keywords = product_name.strip().split()
        conditions = []
        for kw in keywords:
            conditions.append("A.ProductName LIKE %s")
            params.append(f"%{kw}%")
        base += " OR ".join(conditions)
    else:
        # No filter — match all via FirmCode LIKE '%%'
        base += "A.FirmCode LIKE %s"
        params.append("%%")

    base += ")"
    return base, params


def get_product_list(isbn: Optional[str] = None,
                     firm_code: Optional[str] = None,
                     product_name: Optional[str] = None) -> list[ProductDTO]:
    """Query product list from database.

    Priority: isbn > firmCode > productName.
    No params returns all products.
    """
    query, params = _build_search_query(isbn, firm_code, product_name)
    logger.info("Product search query: %s | params: %s", query, params)

    products = []
    with db_manager.cursor() as cursor:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        for row in rows:
            dto = ProductDTO(
                isbn=row.get("ISBN") or "",
                internationalCode=row.get("InternationalCode") or "",
                firmCode=row.get("FirmCode") or "",
                productCode=row.get("ProductCode") or "",
                productName=row.get("ProductName") or "",
                unit=row.get("Unit") or "",
                vendorCode=str(row.get("VendorCode") or ""),
                vendorName=row.get("Vendor") or "",
                firstCategory=row.get("NewFirstCategory") or "",
                secondCategory=row.get("NewSecondCategory") or "",
                thirdCategory=row.get("NewThirdCategory") or "",
                batchPrice=_round_price(row.get("BatchPrice")),
                singlePrice=_round_price(row.get("SinglePrice")),
                pricing=_round_price(row.get("Pricing")),
                vipPrice1=_round_price(row.get("VipPrice1")),
                vipPrice2=_round_price(row.get("VipPrice2")),
                vipPrice3=_round_price(row.get("VipPrice3")),
                inStock=str(row.get("InStock") or 0),
                safetyStock=str(row.get("SafetyStock") or 0),
                discount=float(row.get("Discount") or 0.0),
            )
            products.append(dto)

    return products
