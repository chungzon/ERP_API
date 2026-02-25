import logging
from typing import Optional

from app.database.connection import db_manager
from app.models.vendor import VendorDTO

logger = logging.getLogger(__name__)


def _get_vendor_by_code(vendor_code: str) -> Optional[dict]:
    """Fetch vendor by ObjectID (vendorCode)."""
    with db_manager.cursor() as cursor:
        cursor.execute(
            """SELECT m.id, m.ObjectID, m.ObjectName, m.ObjectNickName,
                m.PersonInCharge, m.ContactPerson, m.Email,
                m.InvoiceTitle, m.TaxIDNumber, m.OrderTax,
                m.PayableDiscount, m.Remark, m.DefaultPaymentMethod,
                p.Telephone1, p.Telephone2, p.Cellphone, p.Fax,
                a.CompanyAddress, a.DeliveryAddress, a.InvoiceAddress,
                pi.PayableDay, pi.CheckTitle, pi.CheckDueDay,
                pi.DiscountRemittanceFee, pi.RemittanceFee,
                pi.DiscountPostage, pi.Postage,
                pi.BankBranch, pi.AccountName, pi.BankAccount,
                pi.IsCheckoutByMonth
            FROM dbo.Manufacturer m
            LEFT JOIN dbo.Manufacturer_Phone p ON m.id = p.Manufacturer_id
            LEFT JOIN dbo.Manufacturer_Address a ON m.id = a.Manufacturer_id
            LEFT JOIN dbo.Manufacturer_PayInfo pi ON m.id = pi.Manufacturer_id
            WHERE m.ObjectID = %s""",
            (vendor_code,),
        )
        return cursor.fetchone()


def _get_vendor_by_id(vendor_id: int) -> Optional[dict]:
    """Fetch vendor by Manufacturer.id (vendorId)."""
    with db_manager.cursor() as cursor:
        cursor.execute(
            """SELECT m.id, m.ObjectID, m.ObjectName, m.ObjectNickName,
                m.PersonInCharge, m.ContactPerson, m.Email,
                m.InvoiceTitle, m.TaxIDNumber, m.OrderTax,
                m.PayableDiscount, m.Remark, m.DefaultPaymentMethod,
                p.Telephone1, p.Telephone2, p.Cellphone, p.Fax,
                a.CompanyAddress, a.DeliveryAddress, a.InvoiceAddress,
                pi.PayableDay, pi.CheckTitle, pi.CheckDueDay,
                pi.DiscountRemittanceFee, pi.RemittanceFee,
                pi.DiscountPostage, pi.Postage,
                pi.BankBranch, pi.AccountName, pi.BankAccount,
                pi.IsCheckoutByMonth
            FROM dbo.Manufacturer m
            LEFT JOIN dbo.Manufacturer_Phone p ON m.id = p.Manufacturer_id
            LEFT JOIN dbo.Manufacturer_Address a ON m.id = a.Manufacturer_id
            LEFT JOIN dbo.Manufacturer_PayInfo pi ON m.id = pi.Manufacturer_id
            WHERE m.id = %s""",
            (vendor_id,),
        )
        return cursor.fetchone()


def _row_to_dto(row: dict) -> VendorDTO:
    """Convert a database row to VendorDTO."""
    return VendorDTO(
        vendor_id=row["id"],
        vendor_code=row["ObjectID"],
        vendor_name=row["ObjectName"],
        nick_name=row["ObjectNickName"] or None,
        person_in_charge=row["PersonInCharge"] or None,
        contact_person=row["ContactPerson"] or None,
        email=row["Email"] or None,
        invoice_title=row["InvoiceTitle"] or None,
        tax_id_number=row["TaxIDNumber"] or None,
        order_tax=row["OrderTax"],
        payable_discount=float(row["PayableDiscount"]) if row["PayableDiscount"] is not None else None,
        default_payment_method=row["DefaultPaymentMethod"],
        remark=row["Remark"] or None,
        telephone1=row["Telephone1"] or None,
        telephone2=row["Telephone2"] or None,
        cellphone=row["Cellphone"] or None,
        fax=row["Fax"] or None,
        company_address=row["CompanyAddress"] or None,
        delivery_address=row["DeliveryAddress"] or None,
        invoice_address=row["InvoiceAddress"] or None,
        payable_day=row["PayableDay"],
        check_title=row["CheckTitle"] or None,
        check_due_day=row["CheckDueDay"],
        discount_remittance_fee=row["DiscountRemittanceFee"],
        remittance_fee=row["RemittanceFee"],
        discount_postage=row["DiscountPostage"],
        postage=row["Postage"],
        bank_branch=row["BankBranch"] or None,
        account_name=row["AccountName"] or None,
        bank_account=row["BankAccount"] or None,
        is_checkout_by_month=bool(row["IsCheckoutByMonth"]) if row["IsCheckoutByMonth"] is not None else None,
    )


def create_vendor(request) -> VendorDTO:
    """Create a new vendor (Manufacturer + satellite tables)."""

    vendor_code = request.vendor_code.strip()
    vendor_name = request.vendor_name.strip()

    if not vendor_code:
        raise ValueError("廠商代碼不能為空")
    if not vendor_name:
        raise ValueError("廠商名稱不能為空")

    # Check duplicate
    existing = _get_vendor_by_code(vendor_code)
    if existing:
        raise ValueError(f"廠商代碼已存在：{vendor_code}")

    # Apply defaults (following ERP desktop logic)
    nick_name = request.nick_name or ""
    person_in_charge = request.person_in_charge or ""
    contact_person = request.contact_person or ""
    email = request.email or ""
    invoice_title = request.invoice_title or ""
    tax_id_number = request.tax_id_number or ""
    order_tax = request.order_tax if request.order_tax is not None else 0
    payable_discount = request.payable_discount if request.payable_discount is not None else 1.0
    default_payment_method = request.default_payment_method if request.default_payment_method is not None else 0
    remark = request.remark or ""

    telephone1 = request.telephone1 or ""
    telephone2 = request.telephone2 or ""
    cellphone = request.cellphone or ""
    fax = request.fax or ""

    company_address = request.company_address or ""
    delivery_address = request.delivery_address or ""
    invoice_address = request.invoice_address or ""

    payable_day = request.payable_day if request.payable_day is not None else 25
    check_title = request.check_title or ""
    check_due_day = request.check_due_day if request.check_due_day is not None else 0
    discount_remittance_fee = request.discount_remittance_fee if request.discount_remittance_fee is not None else 0
    remittance_fee = request.remittance_fee if request.remittance_fee is not None else 0
    discount_postage = request.discount_postage if request.discount_postage is not None else 0
    postage = request.postage if request.postage is not None else 0
    bank_branch = request.bank_branch or ""
    account_name = request.account_name or ""
    bank_account = request.bank_account or ""
    is_checkout_by_month = 1 if request.is_checkout_by_month else 0

    with db_manager.cursor() as cursor:
        # Insert Manufacturer
        cursor.execute(
            """INSERT INTO dbo.Manufacturer (
                ObjectID, ObjectName, ObjectNickName, PersonInCharge, ContactPerson,
                Email, InvoiceTitle, TaxIDNumber, OrderTax, PayableDiscount,
                Remark, DefaultPaymentMethod
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                vendor_code, vendor_name, nick_name, person_in_charge, contact_person,
                email, invoice_title, tax_id_number, order_tax, payable_discount,
                remark, default_payment_method,
            ),
        )

        cursor.execute("SELECT SCOPE_IDENTITY() AS id")
        manufacturer_id = int(cursor.fetchone()["id"])

        # Insert Manufacturer_Phone
        cursor.execute(
            """INSERT INTO dbo.Manufacturer_Phone (
                Manufacturer_id, ObjectID, Telephone1, Telephone2, Cellphone, Fax
            ) VALUES (%s, %s, %s, %s, %s, %s)""",
            (manufacturer_id, vendor_code, telephone1, telephone2, cellphone, fax),
        )

        # Insert Manufacturer_Address
        cursor.execute(
            """INSERT INTO dbo.Manufacturer_Address (
                Manufacturer_id, ObjectID, CompanyAddress, DeliveryAddress, InvoiceAddress
            ) VALUES (%s, %s, %s, %s, %s)""",
            (manufacturer_id, vendor_code, company_address, delivery_address, invoice_address),
        )

        # Insert Manufacturer_PayInfo
        cursor.execute(
            """INSERT INTO dbo.Manufacturer_PayInfo (
                Manufacturer_id, ObjectID, PayableDay, CheckTitle, CheckDueDay,
                DiscountRemittanceFee, RemittanceFee, DiscountPostage, Postage,
                BankBranch, AccountName, BankAccount, IsCheckoutByMonth
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                manufacturer_id, vendor_code, payable_day, check_title, check_due_day,
                discount_remittance_fee, remittance_fee, discount_postage, postage,
                bank_branch, account_name, bank_account, is_checkout_by_month,
            ),
        )

    logger.info(
        "Vendor created - ID: %s, Code: %s, Name: %s",
        manufacturer_id, vendor_code, vendor_name,
    )

    row = _get_vendor_by_code(vendor_code)
    return _row_to_dto(row)


def update_vendor(request) -> VendorDTO:
    """Update an existing vendor. Locate by vendorId or vendorCode."""

    vendor_id = request.vendor_id
    vendor_code = request.vendor_code

    if vendor_id is None and (vendor_code is None or not vendor_code.strip()):
        raise ValueError("必須提供 vendorId 或 vendorCode")

    # Locate vendor
    if vendor_id is not None:
        existing = _get_vendor_by_id(vendor_id)
        if not existing:
            raise ValueError(f"廠商不存在：vendorId={vendor_id}")
    else:
        vendor_code = vendor_code.strip()
        existing = _get_vendor_by_code(vendor_code)
        if not existing:
            raise ValueError(f"廠商不存在：vendorCode={vendor_code}")

    manufacturer_id = existing["id"]
    object_id = existing["ObjectID"]

    # Build dynamic UPDATE for Manufacturer main table
    main_updates = []
    main_params = []
    field_map = {
        "vendor_name": ("ObjectName", request.vendor_name),
        "nick_name": ("ObjectNickName", request.nick_name),
        "person_in_charge": ("PersonInCharge", request.person_in_charge),
        "contact_person": ("ContactPerson", request.contact_person),
        "email": ("Email", request.email),
        "invoice_title": ("InvoiceTitle", request.invoice_title),
        "tax_id_number": ("TaxIDNumber", request.tax_id_number),
        "order_tax": ("OrderTax", request.order_tax),
        "payable_discount": ("PayableDiscount", request.payable_discount),
        "default_payment_method": ("DefaultPaymentMethod", request.default_payment_method),
        "remark": ("Remark", request.remark),
    }
    for _, (col, val) in field_map.items():
        if val is not None:
            main_updates.append(f"{col} = %s")
            main_params.append(val)

    # Build dynamic UPDATE for Phone
    phone_updates = []
    phone_params = []
    for attr, col in [
        ("telephone1", "Telephone1"), ("telephone2", "Telephone2"),
        ("cellphone", "Cellphone"), ("fax", "Fax"),
    ]:
        val = getattr(request, attr)
        if val is not None:
            phone_updates.append(f"{col} = %s")
            phone_params.append(val)

    # Build dynamic UPDATE for Address
    addr_updates = []
    addr_params = []
    for attr, col in [
        ("company_address", "CompanyAddress"),
        ("delivery_address", "DeliveryAddress"),
        ("invoice_address", "InvoiceAddress"),
    ]:
        val = getattr(request, attr)
        if val is not None:
            addr_updates.append(f"{col} = %s")
            addr_params.append(val)

    # Build dynamic UPDATE for PayInfo
    pay_updates = []
    pay_params = []
    for attr, col in [
        ("payable_day", "PayableDay"), ("check_title", "CheckTitle"),
        ("check_due_day", "CheckDueDay"),
        ("discount_remittance_fee", "DiscountRemittanceFee"),
        ("remittance_fee", "RemittanceFee"),
        ("discount_postage", "DiscountPostage"), ("postage", "Postage"),
        ("bank_branch", "BankBranch"), ("account_name", "AccountName"),
        ("bank_account", "BankAccount"),
    ]:
        val = getattr(request, attr)
        if val is not None:
            pay_updates.append(f"{col} = %s")
            pay_params.append(val)

    if request.is_checkout_by_month is not None:
        pay_updates.append("IsCheckoutByMonth = %s")
        pay_params.append(1 if request.is_checkout_by_month else 0)

    has_updates = main_updates or phone_updates or addr_updates or pay_updates
    if not has_updates:
        # Nothing to update, return existing
        return _row_to_dto(existing)

    with db_manager.cursor() as cursor:
        if main_updates:
            cursor.execute(
                f"UPDATE dbo.Manufacturer SET {', '.join(main_updates)} WHERE id = %s",
                tuple(main_params) + (manufacturer_id,),
            )
        if phone_updates:
            cursor.execute(
                f"UPDATE dbo.Manufacturer_Phone SET {', '.join(phone_updates)} WHERE Manufacturer_id = %s",
                tuple(phone_params) + (manufacturer_id,),
            )
        if addr_updates:
            cursor.execute(
                f"UPDATE dbo.Manufacturer_Address SET {', '.join(addr_updates)} WHERE Manufacturer_id = %s",
                tuple(addr_params) + (manufacturer_id,),
            )
        if pay_updates:
            cursor.execute(
                f"UPDATE dbo.Manufacturer_PayInfo SET {', '.join(pay_updates)} WHERE Manufacturer_id = %s",
                tuple(pay_params) + (manufacturer_id,),
            )

    logger.info("Vendor updated - ID: %s, Code: %s", manufacturer_id, object_id)

    row = _get_vendor_by_code(object_id)
    return _row_to_dto(row)


def delete_vendor(vendor_code: str) -> None:
    """Delete a vendor after checking for related orders and products."""

    vendor_code = vendor_code.strip()
    if not vendor_code:
        raise ValueError("廠商代碼不能為空")

    existing = _get_vendor_by_code(vendor_code)
    if not existing:
        raise ValueError(f"廠商不存在：vendorCode={vendor_code}")

    manufacturer_id = existing["id"]

    # Check for related orders
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM dbo.Orders WHERE ObjectID = %s",
            (vendor_code,),
        )
        row = cursor.fetchone()
        if row and row["cnt"] > 0:
            raise ValueError(f"此廠商尚有 {row['cnt']} 筆關聯訂單，無法刪除")

    # Check for related products
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM dbo.store WHERE VendorCode = %s",
            (vendor_code,),
        )
        row = cursor.fetchone()
        if row and row["cnt"] > 0:
            raise ValueError(f"此廠商尚有 {row['cnt']} 筆關聯商品，無法刪除")

    # Delete satellite tables first, then main table
    with db_manager.cursor() as cursor:
        cursor.execute(
            "DELETE FROM dbo.Manufacturer_PayInfo WHERE Manufacturer_id = %s",
            (manufacturer_id,),
        )
        cursor.execute(
            "DELETE FROM dbo.Manufacturer_Address WHERE Manufacturer_id = %s",
            (manufacturer_id,),
        )
        cursor.execute(
            "DELETE FROM dbo.Manufacturer_Phone WHERE Manufacturer_id = %s",
            (manufacturer_id,),
        )
        cursor.execute(
            "DELETE FROM dbo.Manufacturer WHERE id = %s",
            (manufacturer_id,),
        )

    logger.info(
        "Vendor deleted - ID: %s, Code: %s, Name: %s",
        manufacturer_id, vendor_code, existing["ObjectName"],
    )


def list_vendors(
    vendor_name: Optional[str] = None,
    vendor_code: Optional[str] = None,
) -> list[VendorDTO]:
    """Query vendor list with optional filters."""

    conditions = []
    params = []

    if vendor_code and vendor_code.strip():
        conditions.append("m.ObjectID = %s")
        params.append(vendor_code.strip())

    if vendor_name and vendor_name.strip():
        conditions.append("m.ObjectName LIKE %s")
        params.append(f"%{vendor_name.strip()}%")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    with db_manager.cursor() as cursor:
        cursor.execute(
            f"""SELECT m.id, m.ObjectID, m.ObjectName, m.ObjectNickName,
                m.PersonInCharge, m.ContactPerson, m.Email,
                m.InvoiceTitle, m.TaxIDNumber, m.OrderTax,
                m.PayableDiscount, m.Remark, m.DefaultPaymentMethod,
                p.Telephone1, p.Telephone2, p.Cellphone, p.Fax,
                a.CompanyAddress, a.DeliveryAddress, a.InvoiceAddress,
                pi.PayableDay, pi.CheckTitle, pi.CheckDueDay,
                pi.DiscountRemittanceFee, pi.RemittanceFee,
                pi.DiscountPostage, pi.Postage,
                pi.BankBranch, pi.AccountName, pi.BankAccount,
                pi.IsCheckoutByMonth
            FROM dbo.Manufacturer m
            LEFT JOIN dbo.Manufacturer_Phone p ON m.id = p.Manufacturer_id
            LEFT JOIN dbo.Manufacturer_Address a ON m.id = a.Manufacturer_id
            LEFT JOIN dbo.Manufacturer_PayInfo pi ON m.id = pi.Manufacturer_id
            WHERE {where_clause}
            ORDER BY m.ObjectID""",
            tuple(params),
        )
        rows = cursor.fetchall()

    return [_row_to_dto(row) for row in rows]
