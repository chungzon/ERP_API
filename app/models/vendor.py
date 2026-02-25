from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateVendorRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # 必填
    vendor_name: str = Field(alias="vendorName")
    vendor_code: str = Field(alias="vendorCode")

    # 主表選填
    nick_name: Optional[str] = Field(default=None, alias="nickName")
    person_in_charge: Optional[str] = Field(default=None, alias="personInCharge")
    contact_person: Optional[str] = Field(default=None, alias="contactPerson")
    email: Optional[str] = Field(default=None, alias="email")
    invoice_title: Optional[str] = Field(default=None, alias="invoiceTitle")
    tax_id_number: Optional[str] = Field(default=None, alias="taxIDNumber")
    order_tax: Optional[int] = Field(default=None, alias="orderTax")
    payable_discount: Optional[float] = Field(default=None, alias="payableDiscount")
    default_payment_method: Optional[int] = Field(default=None, alias="defaultPaymentMethod")
    remark: Optional[str] = Field(default=None, alias="remark")

    # 電話
    telephone1: Optional[str] = Field(default=None, alias="telephone1")
    telephone2: Optional[str] = Field(default=None, alias="telephone2")
    cellphone: Optional[str] = Field(default=None, alias="cellphone")
    fax: Optional[str] = Field(default=None, alias="fax")

    # 地址
    company_address: Optional[str] = Field(default=None, alias="companyAddress")
    delivery_address: Optional[str] = Field(default=None, alias="deliveryAddress")
    invoice_address: Optional[str] = Field(default=None, alias="invoiceAddress")

    # 付款資訊
    payable_day: Optional[int] = Field(default=None, alias="payableDay")
    check_title: Optional[str] = Field(default=None, alias="checkTitle")
    check_due_day: Optional[int] = Field(default=None, alias="checkDueDay")
    discount_remittance_fee: Optional[int] = Field(default=None, alias="discountRemittanceFee")
    remittance_fee: Optional[int] = Field(default=None, alias="remittanceFee")
    discount_postage: Optional[int] = Field(default=None, alias="discountPostage")
    postage: Optional[int] = Field(default=None, alias="postage")
    bank_branch: Optional[str] = Field(default=None, alias="bankBranch")
    account_name: Optional[str] = Field(default=None, alias="accountName")
    bank_account: Optional[str] = Field(default=None, alias="bankAccount")
    is_checkout_by_month: Optional[bool] = Field(default=None, alias="isCheckoutByMonth")


class UpdateVendorRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # 定位（二擇一）
    vendor_id: Optional[int] = Field(default=None, alias="vendorId")
    vendor_code: Optional[str] = Field(default=None, alias="vendorCode")

    # 主表
    vendor_name: Optional[str] = Field(default=None, alias="vendorName")
    nick_name: Optional[str] = Field(default=None, alias="nickName")
    person_in_charge: Optional[str] = Field(default=None, alias="personInCharge")
    contact_person: Optional[str] = Field(default=None, alias="contactPerson")
    email: Optional[str] = Field(default=None, alias="email")
    invoice_title: Optional[str] = Field(default=None, alias="invoiceTitle")
    tax_id_number: Optional[str] = Field(default=None, alias="taxIDNumber")
    order_tax: Optional[int] = Field(default=None, alias="orderTax")
    payable_discount: Optional[float] = Field(default=None, alias="payableDiscount")
    default_payment_method: Optional[int] = Field(default=None, alias="defaultPaymentMethod")
    remark: Optional[str] = Field(default=None, alias="remark")

    # 電話
    telephone1: Optional[str] = Field(default=None, alias="telephone1")
    telephone2: Optional[str] = Field(default=None, alias="telephone2")
    cellphone: Optional[str] = Field(default=None, alias="cellphone")
    fax: Optional[str] = Field(default=None, alias="fax")

    # 地址
    company_address: Optional[str] = Field(default=None, alias="companyAddress")
    delivery_address: Optional[str] = Field(default=None, alias="deliveryAddress")
    invoice_address: Optional[str] = Field(default=None, alias="invoiceAddress")

    # 付款資訊
    payable_day: Optional[int] = Field(default=None, alias="payableDay")
    check_title: Optional[str] = Field(default=None, alias="checkTitle")
    check_due_day: Optional[int] = Field(default=None, alias="checkDueDay")
    discount_remittance_fee: Optional[int] = Field(default=None, alias="discountRemittanceFee")
    remittance_fee: Optional[int] = Field(default=None, alias="remittanceFee")
    discount_postage: Optional[int] = Field(default=None, alias="discountPostage")
    postage: Optional[int] = Field(default=None, alias="postage")
    bank_branch: Optional[str] = Field(default=None, alias="bankBranch")
    account_name: Optional[str] = Field(default=None, alias="accountName")
    bank_account: Optional[str] = Field(default=None, alias="bankAccount")
    is_checkout_by_month: Optional[bool] = Field(default=None, alias="isCheckoutByMonth")


class VendorDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendor_id: Optional[int] = Field(default=None, alias="vendorId")
    vendor_code: Optional[str] = Field(default=None, alias="vendorCode")
    vendor_name: Optional[str] = Field(default=None, alias="vendorName")
    nick_name: Optional[str] = Field(default=None, alias="nickName")
    person_in_charge: Optional[str] = Field(default=None, alias="personInCharge")
    contact_person: Optional[str] = Field(default=None, alias="contactPerson")
    email: Optional[str] = Field(default=None, alias="email")
    invoice_title: Optional[str] = Field(default=None, alias="invoiceTitle")
    tax_id_number: Optional[str] = Field(default=None, alias="taxIDNumber")
    order_tax: Optional[int] = Field(default=None, alias="orderTax")
    payable_discount: Optional[float] = Field(default=None, alias="payableDiscount")
    default_payment_method: Optional[int] = Field(default=None, alias="defaultPaymentMethod")
    remark: Optional[str] = Field(default=None, alias="remark")

    # 電話
    telephone1: Optional[str] = Field(default=None, alias="telephone1")
    telephone2: Optional[str] = Field(default=None, alias="telephone2")
    cellphone: Optional[str] = Field(default=None, alias="cellphone")
    fax: Optional[str] = Field(default=None, alias="fax")

    # 地址
    company_address: Optional[str] = Field(default=None, alias="companyAddress")
    delivery_address: Optional[str] = Field(default=None, alias="deliveryAddress")
    invoice_address: Optional[str] = Field(default=None, alias="invoiceAddress")

    # 付款資訊
    payable_day: Optional[int] = Field(default=None, alias="payableDay")
    check_title: Optional[str] = Field(default=None, alias="checkTitle")
    check_due_day: Optional[int] = Field(default=None, alias="checkDueDay")
    discount_remittance_fee: Optional[int] = Field(default=None, alias="discountRemittanceFee")
    remittance_fee: Optional[int] = Field(default=None, alias="remittanceFee")
    discount_postage: Optional[int] = Field(default=None, alias="discountPostage")
    postage: Optional[int] = Field(default=None, alias="postage")
    bank_branch: Optional[str] = Field(default=None, alias="bankBranch")
    account_name: Optional[str] = Field(default=None, alias="accountName")
    bank_account: Optional[str] = Field(default=None, alias="bankAccount")
    is_checkout_by_month: Optional[bool] = Field(default=None, alias="isCheckoutByMonth")


class ErrorInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = ""
    details: str = ""


class CreateVendorResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[VendorDTO] = None
    error: Optional[ErrorInfo] = None


class UpdateVendorResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[VendorDTO] = None
    error: Optional[ErrorInfo] = None


class DeleteVendorResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    error: Optional[ErrorInfo] = None


class VendorListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[list[VendorDTO]] = None
    total: int = 0
    error: Optional[ErrorInfo] = None
