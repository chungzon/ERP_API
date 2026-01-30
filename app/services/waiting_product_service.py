import logging
from datetime import datetime
from typing import Optional

from app.database.connection import db_manager
from app.models.waiting_product import WaitingProductDTO

logger = logging.getLogger(__name__)

# WaitConfirmStatus ordinal values matching Java Product_Enum.WaitConfirmStatus
WAIT_CONFIRM_STATUS = {"新增": 0, "更新": 1, "封存": 2, "忽略": 3}
WAIT_CONFIRM_STATUS_REVERSE = {v: k for k, v in WAIT_CONFIRM_STATUS.items()}


def _product_code_exists(product_code: str) -> bool:
    """Check if product code already exists in CheckStore."""
    with db_manager.cursor() as cursor:
        cursor.execute("SELECT 1 FROM CheckStore WHERE ProductCode = %s", (product_code,))
        return cursor.fetchone() is not None


def create_waiting_product(request) -> dict:
    """Create a waiting product record. Returns dict with productCode and productName."""

    if _product_code_exists(request.product_code):
        raise ValueError(f"商品碼已存在：{request.product_code}")

    current_date = datetime.now().strftime("%Y/%m/%d")
    status_ordinal = WAIT_CONFIRM_STATUS["新增"]

    with db_manager.cursor() as cursor:
        cursor.execute(
            "INSERT INTO CheckStore ("
            "ProductCode, ProductName, VendorCode, Vendor, "
            "Pricing, SinglePrice, BatchPrice, VipPrice1, VipPrice2, VipPrice3, "
            "Unit, Brand, [Describe], Remark, SupplyStatus, "
            "FirstCategory_Id, SecondCategory_Id, ThirdCategory_Id, "
            "Picture1, Picture2, Picture3, "
            "KeyinDate, UpdateDate, Status"
            ") VALUES ("
            "%s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, "
            "%s, %s, %s, "
            "%s, %s, %s"
            ")",
            (
                request.product_code,
                request.product_name,
                request.vendor_code,
                request.vendor,
                request.pricing if request.pricing is not None else 0,
                request.single_price if request.single_price is not None else 0,
                request.batch_price if request.batch_price is not None else 0,
                request.vip_price1 if request.vip_price1 is not None else 0,
                request.vip_price2 if request.vip_price2 is not None else 0,
                request.vip_price3 if request.vip_price3 is not None else 0,
                request.unit or "",
                request.brand or "",
                request.describe or "",
                request.remark or "",
                request.supply_status or "",
                request.first_category_id,
                request.second_category_id,
                request.third_category_id,
                request.picture1,
                request.picture2,
                request.picture3,
                current_date,
                current_date,
                status_ordinal,
            ),
        )

    logger.info("Waiting product created - ProductCode: %s", request.product_code)
    return {
        "productCode": request.product_code,
        "productName": request.product_name,
    }


def get_waiting_product_list(
    vendor_code: Optional[int] = None,
    product_name: Optional[str] = None,
    status: Optional[str] = None,
) -> list[WaitingProductDTO]:
    """Query waiting product list from CheckStore table."""

    query = (
        "SELECT ProductCode, ProductName, VendorCode, Vendor, "
        "Pricing, SinglePrice, BatchPrice, VipPrice1, VipPrice2, VipPrice3, "
        "Unit, Brand, [Describe], Remark, SupplyStatus, NewFirstCategory, "
        "FirstCategory_Id, SecondCategory_Id, ThirdCategory_Id, "
        "KeyinDate, CONVERT(nvarchar, UpdateDate) as UpdateDate, Status, "
        "Picture1, Picture2, Picture3 "
        "FROM CheckStore WHERE 1=1"
    )
    params = []

    if vendor_code is not None:
        query += " AND VendorCode = %s"
        params.append(vendor_code)

    if product_name and product_name.strip():
        query += " AND ProductName LIKE %s"
        params.append(f"%{product_name.strip()}%")

    if status and status.strip():
        if status not in WAIT_CONFIRM_STATUS:
            raise ValueError(
                f"無效的狀態值：{status}，有效值為：新增、更新、封存、忽略"
            )
        query += " AND Status = %s"
        params.append(WAIT_CONFIRM_STATUS[status])

    query += " ORDER BY ProductCode"

    results = []
    with db_manager.cursor() as cursor:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        for row in rows:
            # Convert status ordinal back to name
            status_ordinal = row.get("Status")
            status_name = WAIT_CONFIRM_STATUS_REVERSE.get(status_ordinal, "")

            dto = WaitingProductDTO(
                productCode=row.get("ProductCode"),
                productName=row.get("ProductName"),
                vendorCode=row.get("VendorCode"),
                vendor=row.get("Vendor"),
                pricing=row.get("Pricing"),
                singlePrice=row.get("SinglePrice"),
                batchPrice=row.get("BatchPrice"),
                vipPrice1=row.get("VipPrice1"),
                vipPrice2=row.get("VipPrice2"),
                vipPrice3=row.get("VipPrice3"),
                unit=row.get("Unit"),
                brand=row.get("Brand"),
                describe=row.get("Describe"),
                remark=row.get("Remark"),
                supplyStatus=row.get("SupplyStatus"),
                newFirstCategory=row.get("NewFirstCategory"),
                firstCategoryId=row.get("FirstCategory_Id"),
                secondCategoryId=row.get("SecondCategory_Id"),
                thirdCategoryId=row.get("ThirdCategory_Id"),
                keyinDate=row.get("KeyinDate"),
                updateDate=row.get("UpdateDate"),
                status=status_name,
                picture1=row.get("Picture1"),
                picture2=row.get("Picture2"),
                picture3=row.get("Picture3"),
            )
            results.append(dto)

    return results
