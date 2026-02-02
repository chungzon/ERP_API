import logging
from datetime import datetime

from app.database.connection import db_manager
from app.models.quotation import CreateQuotationRequest

logger = logging.getLogger(__name__)

# OrderSource ordinal values (bit: 0=報價單/廠商, 1=出貨子貨單/客戶)
ORDER_SOURCE_QUOTATION = 0
ORDER_SOURCE_SUB_BILL = 1

# EstablishSource (bit: 0=系統建立, 1=人工建立)
ESTABLISH_SOURCE_SYSTEM = 0
ESTABLISH_SOURCE_MANUAL = 1

# SaleModel mapping (int)
SALE_MODEL_MAP = {
    "單價": 0,
    "成本價": 1,
    "定價": 2,
    "VipPrice1": 3,
    "VipPrice2": 4,
    "VipPrice3": 5,
}


def _customer_exists(object_id: str) -> bool:
    """Check if customer ID exists."""
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT 1 AS cnt FROM dbo.Customer WHERE ObjectID = %s",
            (object_id,),
        )
        return cursor.fetchone() is not None


def _create_customer(object_id: str, info) -> None:
    """Insert a new customer record into Customer and related tables."""
    # OrderTax: bit (0=未稅, 1=應稅)
    order_tax = 0
    if info.order_tax and info.order_tax in ("應稅", "含稅"):
        order_tax = 1

    # PrintPricing: bit (0=N, 1=Y)
    print_pricing = 1
    if info.print_pricing and info.print_pricing.upper() == "N":
        print_pricing = 0

    # SaleModel: int
    sale_model = SALE_MODEL_MAP.get(info.sale_model, 0)

    with db_manager.cursor() as cursor:
        # Insert into Customer table
        cursor.execute(
            """INSERT INTO dbo.Customer (
                ObjectID, ObjectName, ObjectNickName, PersonInCharge, ContactPerson,
                Email, MemberID, InvoiceTitle, TaxIDNumber,
                OrderTax, ReceivableDiscount, PrintPricing, SaleModel, SaleDiscount,
                Remark, StoreCode
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s
            )""",
            (
                object_id,
                info.object_name or "",
                info.object_nick_name or "",
                info.person_in_charge or "",
                info.contact_person or "",
                info.email or "",
                info.member_id or "",
                info.invoice_title or "",
                info.tax_id_number or "",
                order_tax,
                info.receivable_discount if info.receivable_discount is not None else 1.0,
                print_pricing,
                sale_model,
                info.sale_discount if info.sale_discount is not None else 1.0,
                info.remark or "",
                info.store_code or "",
            ),
        )

        # Get inserted customer ID
        cursor.execute("SELECT SCOPE_IDENTITY() AS id")
        customer_id = int(cursor.fetchone()["id"])

        # Insert into Customer_Phone table
        cursor.execute(
            """INSERT INTO dbo.Customer_Phone (
                Customer_id, ObjectID, Telephone1, Telephone2, Cellphone, Fax
            ) VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                customer_id,
                object_id,
                info.telephone1 or "",
                info.telephone2 or "",
                info.cellphone or "",
                info.fax or "",
            ),
        )

        # Insert into Customer_Address table
        cursor.execute(
            """INSERT INTO dbo.Customer_Address (
                Customer_id, ObjectID, CompanyAddress, DeliveryAddress, InvoiceAddress
            ) VALUES (%s, %s, %s, %s, %s)""",
            (
                customer_id,
                object_id,
                info.company_address or "",
                info.delivery_address or "",
                info.invoice_address or "",
            ),
        )

        # Insert into Customer_ReceiveInfo table
        cursor.execute(
            """INSERT INTO dbo.Customer_ReceiveInfo (
                Customer_id, ObjectID, ReceivableDay, IsCheckoutByMonth
            ) VALUES (%s, %s, %s, %s)""",
            (
                customer_id,
                object_id,
                info.receivable_day if info.receivable_day is not None else 25,
                1 if info.checkout_by_month else 0,
            ),
        )

    logger.info(
        "Created new customer - CustomerID: %s, ObjectID: %s, CustomerName: %s",
        customer_id,
        object_id,
        info.object_name,
    )


def _generate_order_number(order_date: str) -> int:
    """Generate order number based on date. Returns bigint."""
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
            (ORDER_SOURCE_QUOTATION, f"{prefix}%"),
        )
        row = cursor.fetchone()

    if row and row.get("MaxNum"):
        max_num = str(row["MaxNum"])
        seq = int(max_num[len(prefix):]) + 1
    else:
        seq = 1

    return int(f"{prefix}{seq:04d}")


def create_quotation(request: CreateQuotationRequest) -> dict:
    """Create a quotation order. Returns dict with orderId, orderNumber, orderDate."""

    object_id = request.object_id.strip()

    # Check customer existence
    if not _customer_exists(object_id):
        if request.customer_info is None:
            raise ValueError("客戶ID不存在，且未提供客戶資料資訊")
        if (
            not request.customer_info.object_name
            or not request.customer_info.object_name.strip()
        ):
            raise ValueError("客戶名稱不能為空")
        _create_customer(object_id, request.customer_info)

    # Generate order number (bigint)
    if request.order_number and request.order_number.strip():
        order_number = int(request.order_number.strip())
    else:
        order_number = _generate_order_number(request.order_date)

    # EstablishSource (bit: 0=系統建立, 1=人工建立)
    establish_source = ESTABLISH_SOURCE_SYSTEM
    if request.establish_source == "人工建立":
        establish_source = ESTABLISH_SOURCE_MANUAL

    # Price info defaults (int)
    pi = request.price_info
    total_price_none_tax = int(pi.total_price_none_tax) if pi and pi.total_price_none_tax else 0
    tax = int(pi.tax) if pi and pi.tax else 0
    discount = int(pi.discount) if pi and pi.discount else 0
    total_price_include_tax = int(pi.total_price_include_tax) if pi and pi.total_price_include_tax else 0

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
    number_of_items = len(request.products)

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
                request.order_date,
                ORDER_SOURCE_QUOTATION,
                object_id,
                is_checkout,
                number_of_items,
                establish_source,
                is_borrowed,
                0,  # isOffset: 0=未沖帳
                order_remark,
                cashier_remark,
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
            (
                order_id,
                order_number,
                total_price_none_tax,
                tax,
                discount,
                total_price_include_tax,
            ),
        )

        # Insert into Orders_ProjectInfo table
        cursor.execute(
            """INSERT INTO dbo.Orders_ProjectInfo (
                Order_id, OrderNumber, ProjectName, ProjectQuantity, ProjectUnit,
                ProjectPriceAmount, ProjectTotalPriceNoneTax, ProjectTax,
                ProjectTotalPriceIncludeTax, ProjectDifferentPrice, ProjectCode
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                order_id,
                order_number,
                project_name,
                project_quantity,
                project_unit,
                project_price_amount,
                project_total_none_tax,
                project_tax,
                project_total_include_tax,
                project_different_price,
                project_code,
            ),
        )

        # Insert into Orders_ShoppingInfo table
        cursor.execute(
            """INSERT INTO dbo.Orders_ShoppingInfo (
                Order_id, OrderNumber,
                PurchaserName, PurchaserTelephone, PurchaserCellphone, PurchaserAddress,
                RecipientName, RecipientTelephone, RecipientCellphone, RecipientAddress
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                order_id,
                order_number,
                purchaser_name,
                purchaser_telephone,
                purchaser_cellphone,
                purchaser_address,
                recipient_name,
                recipient_telephone,
                recipient_cellphone,
                recipient_address,
            ),
        )

        # Insert order items into Orders_Items table
        for i, product in enumerate(request.products):
            item_number = product.item_number if product.item_number is not None else (i + 1)
            cursor.execute(
                """INSERT INTO dbo.Orders_Items (
                    Order_id, OrderNumber, ItemNumber, ISBN, ProductName,
                    Quantity, Unit, BatchPrice, SinglePrice, Pricing, PriceAmount, Remark
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    order_id,
                    order_number,
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
                ),
            )

        # Insert order references into Orders_Reference table
        if request.order_references:
            if request.order_references.quotation_ids:
                for ref_id in request.order_references.quotation_ids:
                    cursor.execute(
                        """INSERT INTO dbo.Orders_Reference (
                            Order_Id, Order_Reference_Id, SubBill_Reference_Id
                        ) VALUES (%s, %s, %s)""",
                        (order_id, ref_id, None),
                    )
            if request.order_references.sub_bill_ids:
                for ref_id in request.order_references.sub_bill_ids:
                    cursor.execute(
                        """INSERT INTO dbo.Orders_Reference (
                            Order_Id, Order_Reference_Id, SubBill_Reference_Id
                        ) VALUES (%s, %s, %s)""",
                        (order_id, None, ref_id),
                    )

        # Insert pictures into Orders_Picture table
        if request.pictures:
            for pic in request.pictures:
                if pic.base64_image:
                    base64_data = pic.base64_image
                    if "," in base64_data:
                        base64_data = base64_data.split(",", 1)[1]
                    cursor.execute(
                        """INSERT INTO dbo.Orders_Picture (
                            Order_id, ItemNumber, Picture, Source
                        ) VALUES (%s, %s, %s, %s)""",
                        (order_id, pic.item_number or 0, base64_data, "API"),
                    )

    logger.info("Quotation created - OrderID: %s, OrderNumber: %s", order_id, order_number)
    return {
        "orderId": order_id,
        "orderNumber": str(order_number),
        "orderDate": request.order_date,
    }
