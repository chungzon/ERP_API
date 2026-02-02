import logging
from datetime import datetime

from app.database.connection import db_manager
from app.models.quotation import CreateQuotationRequest

logger = logging.getLogger(__name__)

# WaitConfirmStatus ordinal values matching Java enum
WAIT_CONFIRM_STATUS = {"新增": 0, "更新": 1, "封存": 2, "忽略": 3}

# OrderSource ordinal values matching Java enum
ORDER_SOURCE_QUOTATION = "0"  # 報價單
ORDER_SOURCE_SUB_BILL = "1"  # 出貨子貨單

# EstablishSource
ESTABLISH_SOURCE_SYSTEM = "系統建立"
ESTABLISH_SOURCE_MANUAL = "人工建立"

# OffsetOrderStatus
OFFSET_STATUS_NOT_OFFSET = "未沖帳"

# ReviewStatus
REVIEW_STATUS_NONE = "無"


def _customer_exists(object_id: str) -> bool:
    """Check if customer ID exists."""
    with db_manager.cursor() as cursor:
        cursor.execute("SELECT 1 AS cnt FROM dbo.Customer WHERE ObjectID = %s", (object_id,))
        return cursor.fetchone() is not None


def _create_customer(object_id: str, info) -> None:
    """Insert a new customer record."""
    order_tax = "未稅"
    if info.order_tax and info.order_tax in ("應稅", "含稅"):
        order_tax = "應稅"

    print_pricing = "Y"
    if info.print_pricing and info.print_pricing.upper() == "N":
        print_pricing = "N"

    sale_model = info.sale_model or "單價"
    valid_sale_models = ("VipPrice1", "VipPrice2", "VipPrice3", "成本價", "單價", "定價")
    if sale_model not in valid_sale_models:
        sale_model = "單價"

    with db_manager.cursor() as cursor:
        cursor.execute(
            "INSERT INTO dbo.Customer ("
            "ObjectID, ObjectName, ObjectNickName, PersonInCharge, ContactPerson, "
            "Telephone1, Telephone2, CellPhone, Fax, Email, MemberID, "
            "CompanyAddress, DeliveryAddress, InvoiceTitle, TaxIDNumber, InvoiceAddress, "
            "OrderTax, PayableReceivableDiscount, PrintPricing, SaleModel, SaleDiscount, "
            "Remark, ReceivableDay, CheckoutByMonth, StoreCode"
            ") VALUES ("
            "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
            ")",
            (
                object_id,
                info.object_name or "",
                info.object_nick_name or "",
                info.person_in_charge or "",
                info.contact_person or "",
                info.telephone1 or "",
                info.telephone2 or "",
                info.cellphone or "",
                info.fax or "",
                info.email or "",
                info.member_id or "",
                info.company_address or "",
                info.delivery_address or "",
                info.invoice_title or "",
                info.tax_id_number or "",
                info.invoice_address or "",
                order_tax,
                info.receivable_discount if info.receivable_discount is not None else 1.0,
                print_pricing,
                sale_model,
                info.sale_discount if info.sale_discount is not None else 1.0,
                info.remark or "",
                info.receivable_day if info.receivable_day is not None else 25,
                1 if (info.checkout_by_month is True) else 0,
                info.store_code or "",
            ),
        )
    logger.info("Created new customer - CustomerID: %s, CustomerName: %s", object_id, info.object_name)


def _generate_order_number(order_date: str) -> str:
    """Generate order number based on date (matching Java generateNewestOrderNumberOfEstablishOrder)."""
    # Parse order date to get date prefix
    date_str = order_date.replace("-", "/")
    try:
        dt = datetime.strptime(date_str, "%Y/%m/%d")
    except ValueError:
        dt = datetime.now()

    prefix = dt.strftime("%Y%m%d")

    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT MAX(NowOrderNumber) as MaxNum FROM Orders "
            "WHERE OrderSource = %s AND NowOrderNumber LIKE %s",
            (ORDER_SOURCE_QUOTATION, f"{prefix}%"),
        )
        row = cursor.fetchone()

    if row and row.get("MaxNum"):
        max_num = row["MaxNum"]
        # Extract trailing number and increment
        seq = int(max_num[len(prefix):]) + 1
    else:
        seq = 1

    return f"{prefix}{seq:04d}"


def create_quotation(request: CreateQuotationRequest) -> dict:
    """Create a quotation order. Returns dict with orderId, orderNumber, orderDate."""

    object_id = request.object_id.strip()

    # Check customer existence
    if not _customer_exists(object_id):
        if request.customer_info is None:
            raise ValueError("客戶ID不存在，且未提供客戶資料資訊")
        if not request.customer_info.object_name or not request.customer_info.object_name.strip():
            raise ValueError("客戶名稱不能為空")
        _create_customer(object_id, request.customer_info)

    # Generate order number
    order_number = request.order_number
    if not order_number or not order_number.strip():
        order_number = _generate_order_number(request.order_date)

    # Establish source
    establish_source = ESTABLISH_SOURCE_SYSTEM
    if request.establish_source == "人工建立":
        establish_source = ESTABLISH_SOURCE_MANUAL

    # Price info defaults
    pi = request.price_info
    total_price_none_tax = pi.total_price_none_tax if pi and pi.total_price_none_tax else "0"
    tax = pi.tax if pi and pi.tax else "0"
    discount = pi.discount if pi and pi.discount else "0"
    total_price_include_tax = pi.total_price_include_tax if pi and pi.total_price_include_tax else "0"
    number_of_items = str(len(request.products))

    # Project info defaults
    pj = request.project_info
    project_code = pj.project_code if pj and pj.project_code else ""
    project_name = pj.project_name if pj and pj.project_name else ""
    project_quantity = pj.project_quantity if pj and pj.project_quantity else ""
    project_unit = pj.project_unit if pj and pj.project_unit else ""
    project_price_amount = pj.project_price_amount if pj and pj.project_price_amount else ""
    project_total_none_tax = pj.project_total_price_none_tax if pj and pj.project_total_price_none_tax else ""
    project_tax = pj.project_tax if pj and pj.project_tax else ""
    project_total_include_tax = pj.project_total_price_include_tax if pj and pj.project_total_price_include_tax else ""
    project_different_price = pj.project_different_price if pj and pj.project_different_price else ""

    # Shopping info defaults
    si = request.shopping_info
    purchaser_name = si.purchaser_name if si and si.purchaser_name else ""
    purchaser_telephone = si.purchaser_telephone if si and si.purchaser_telephone else ""
    purchaser_cellphone = si.purchaser_cellphone if si and si.purchaser_cellphone else ""
    purchaser_address = si.purchaser_address if si and si.purchaser_address else ""
    recipient_name = si.recipient_name if si and si.recipient_name else ""
    recipient_telephone = si.recipient_telephone if si and si.recipient_telephone else ""
    recipient_cellphone = si.recipient_cellphone if si and si.recipient_cellphone else ""
    recipient_address = si.recipient_address if si and si.recipient_address else ""

    # Other defaults
    order_remark = request.remark or ""
    cashier_remark = request.cashier_remark or ""
    is_borrowed = 1 if request.is_borrowed else 0
    is_checkout = 1 if request.is_checkout else 0

    # Insert order
    with db_manager.cursor() as cursor:
        cursor.execute(
            "INSERT INTO Orders ("
            "OrderSource, OrderDate, ObjectID, NowOrderNumber, EstablishSource, "
            "TotalPriceNoneTax, Tax, Discount, TotalPriceIncludeTax, NumberOfItems, "
            "ProjectCode, ProjectName, ProjectQuantity, ProjectUnit, ProjectPriceAmount, "
            "ProjectTotalPriceNoneTax, ProjectTax, ProjectTotalPriceIncludeTax, ProjectDifferentPrice, "
            "PurchaserName, PurchaserTelephone, PurchaserCellphone, PurchaserAddress, "
            "RecipientName, RecipientTelephone, RecipientCellphone, RecipientAddress, "
            "OrderRemark, CashierRemark, IsBorrowed, IsCheckout, "
            "IsOffset, ReviewStatus_Product, ReviewStatus_ProductGroup, status"
            ") VALUES ("
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, "
            "%s, %s, %s, %s, "
            "%s, %s, %s, %s, "
            "%s, %s, %s, %s, "
            "%s, %s, %s, %s"
            ")",
            (
                ORDER_SOURCE_QUOTATION, request.order_date, object_id, order_number, establish_source,
                total_price_none_tax, tax, discount, total_price_include_tax, number_of_items,
                project_code, project_name, project_quantity, project_unit, project_price_amount,
                project_total_none_tax, project_tax, project_total_include_tax, project_different_price,
                purchaser_name, purchaser_telephone, purchaser_cellphone, purchaser_address,
                recipient_name, recipient_telephone, recipient_cellphone, recipient_address,
                order_remark, cashier_remark, is_borrowed, is_checkout,
                OFFSET_STATUS_NOT_OFFSET, REVIEW_STATUS_NONE, REVIEW_STATUS_NONE, "0",
            ),
        )

        # Get inserted order ID
        cursor.execute("SELECT SCOPE_IDENTITY() AS id")
        order_id = int(cursor.fetchone()["id"])

        # Insert order items
        for i, product in enumerate(request.products):
            item_number = product.item_number if product.item_number is not None else (i + 1)
            cursor.execute(
                "INSERT INTO Orders_Items ("
                "Order_id, ItemNumber, ISBN, ProductName, Quantity, Unit, "
                "BatchPrice, SinglePrice, Pricing, PriceAmount, Remark, Store_id"
                ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    order_id,
                    item_number,
                    product.isbn or "",
                    product.product_name or "",
                    product.quantity or 0,
                    product.unit or "",
                    product.batch_price or 0.0,
                    product.single_price or 0.0,
                    product.pricing or 0.0,
                    product.price_amount or 0,
                    product.remark or "",
                    product.store_id,
                ),
            )

        # Insert order references
        if request.order_references:
            if request.order_references.quotation_ids:
                for ref_id in request.order_references.quotation_ids:
                    cursor.execute(
                        "INSERT INTO OrderReference (Order_id, ReferenceOrderSource, ReferenceOrder_id) "
                        "VALUES (%s, %s, %s)",
                        (order_id, ORDER_SOURCE_QUOTATION, ref_id),
                    )
            if request.order_references.sub_bill_ids:
                for ref_id in request.order_references.sub_bill_ids:
                    cursor.execute(
                        "INSERT INTO OrderReference (Order_id, ReferenceOrderSource, ReferenceOrder_id) "
                        "VALUES (%s, %s, %s)",
                        (order_id, ORDER_SOURCE_SUB_BILL, ref_id),
                    )

        # Insert pictures
        if request.pictures:
            for pic in request.pictures:
                if pic.base64_image:
                    base64_data = pic.base64_image
                    if "," in base64_data:
                        base64_data = base64_data.split(",", 1)[1]
                    cursor.execute(
                        "INSERT INTO OrderPicture (Order_id, ItemNumber, Picture) "
                        "VALUES (%s, %s, %s)",
                        (order_id, pic.item_number, base64_data),
                    )

    logger.info("Quotation created - OrderID: %s, OrderNumber: %s", order_id, order_number)
    return {
        "orderId": order_id,
        "orderNumber": order_number,
        "orderDate": request.order_date,
    }
