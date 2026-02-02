from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PriceInfoDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_price_none_tax: Optional[str] = Field(default=None, alias="totalPriceNoneTax")
    tax: Optional[str] = Field(default=None, alias="tax")
    discount: Optional[str] = Field(default=None, alias="discount")
    total_price_include_tax: Optional[str] = Field(default=None, alias="totalPriceIncludeTax")


class ProjectInfoDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project_code: Optional[str] = Field(default=None, alias="projectCode")
    project_name: Optional[str] = Field(default=None, alias="projectName")
    project_quantity: Optional[str] = Field(default=None, alias="projectQuantity")
    project_unit: Optional[str] = Field(default=None, alias="projectUnit")
    project_price_amount: Optional[str] = Field(default=None, alias="projectPriceAmount")
    project_total_price_none_tax: Optional[str] = Field(default=None, alias="projectTotalPriceNoneTax")
    project_tax: Optional[str] = Field(default=None, alias="projectTax")
    project_total_price_include_tax: Optional[str] = Field(default=None, alias="projectTotalPriceIncludeTax")
    project_different_price: Optional[str] = Field(default=None, alias="projectDifferentPrice")


class ShoppingInfoDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    purchaser_name: Optional[str] = Field(default=None, alias="purchaserName")
    purchaser_telephone: Optional[str] = Field(default=None, alias="purchaserTelephone")
    purchaser_cellphone: Optional[str] = Field(default=None, alias="purchaserCellphone")
    purchaser_address: Optional[str] = Field(default=None, alias="purchaserAddress")
    recipient_name: Optional[str] = Field(default=None, alias="recipientName")
    recipient_telephone: Optional[str] = Field(default=None, alias="recipientTelephone")
    recipient_cellphone: Optional[str] = Field(default=None, alias="recipientCellphone")
    recipient_address: Optional[str] = Field(default=None, alias="recipientAddress")


class ProductItemDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    item_number: Optional[int] = Field(default=None, alias="itemNumber")
    isbn: Optional[str] = Field(default=None, alias="isbn")
    product_name: Optional[str] = Field(default=None, alias="productName")
    quantity: Optional[int] = Field(default=None, alias="quantity")
    unit: Optional[str] = Field(default=None, alias="unit")
    batch_price: Optional[float] = Field(default=None, alias="batchPrice")
    single_price: Optional[float] = Field(default=None, alias="singlePrice")
    pricing: Optional[float] = Field(default=None, alias="pricing")
    price_amount: Optional[int] = Field(default=None, alias="priceAmount")
    remark: Optional[str] = Field(default=None, alias="remark")


class OrderReferenceDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    quotation_ids: Optional[list[int]] = Field(default=None, alias="quotationIds")
    sub_bill_ids: Optional[list[int]] = Field(default=None, alias="subBillIds")


class PictureDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    item_number: Optional[int] = Field(default=None, alias="itemNumber")
    base64_image: Optional[str] = Field(default=None, alias="base64Image")


class CustomerInfoDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    object_name: Optional[str] = Field(default=None, alias="objectName")
    object_nick_name: Optional[str] = Field(default=None, alias="objectNickName")
    person_in_charge: Optional[str] = Field(default=None, alias="personInCharge")
    contact_person: Optional[str] = Field(default=None, alias="contactPerson")
    telephone1: Optional[str] = Field(default=None, alias="telephone1")
    telephone2: Optional[str] = Field(default=None, alias="telephone2")
    cellphone: Optional[str] = Field(default=None, alias="cellphone")
    fax: Optional[str] = Field(default=None, alias="fax")
    email: Optional[str] = Field(default=None, alias="email")
    member_id: Optional[str] = Field(default=None, alias="memberID")
    company_address: Optional[str] = Field(default=None, alias="companyAddress")
    delivery_address: Optional[str] = Field(default=None, alias="deliveryAddress")
    invoice_title: Optional[str] = Field(default=None, alias="invoiceTitle")
    tax_id_number: Optional[str] = Field(default=None, alias="taxIDNumber")
    invoice_address: Optional[str] = Field(default=None, alias="invoiceAddress")
    order_tax: Optional[str] = Field(default=None, alias="orderTax")
    receivable_discount: Optional[float] = Field(default=None, alias="receivableDiscount")
    print_pricing: Optional[str] = Field(default=None, alias="printPricing")
    sale_model: Optional[str] = Field(default=None, alias="saleModel")
    sale_discount: Optional[float] = Field(default=None, alias="saleDiscount")
    remark: Optional[str] = Field(default=None, alias="remark")
    receivable_day: Optional[int] = Field(default=None, alias="receivableDay")
    checkout_by_month: Optional[bool] = Field(default=None, alias="checkoutByMonth")
    store_code: Optional[str] = Field(default=None, alias="storeCode")


class CreateQuotationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    order_date: str = Field(alias="orderDate")
    object_id: str = Field(alias="objectID")
    order_number: Optional[str] = Field(default=None, alias="orderNumber")
    establish_source: Optional[str] = Field(default=None, alias="establishSource")
    customer_info: Optional[CustomerInfoDTO] = Field(default=None, alias="customerInfo")
    price_info: Optional[PriceInfoDTO] = Field(default=None, alias="priceInfo")
    project_info: Optional[ProjectInfoDTO] = Field(default=None, alias="projectInfo")
    shopping_info: Optional[ShoppingInfoDTO] = Field(default=None, alias="shoppingInfo")
    products: list[ProductItemDTO] = Field(alias="products")
    remark: Optional[str] = Field(default=None, alias="remark")
    cashier_remark: Optional[str] = Field(default=None, alias="cashierRemark")
    is_borrowed: Optional[bool] = Field(default=None, alias="isBorrowed")
    is_checkout: Optional[bool] = Field(default=None, alias="isCheckout")
    order_references: Optional[OrderReferenceDTO] = Field(default=None, alias="orderReferences")
    pictures: Optional[list[PictureDTO]] = Field(default=None, alias="pictures")


class ErrorInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = ""
    details: str = ""


class QuotationData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    order_id: Optional[int] = Field(default=None, alias="orderId")
    order_number: Optional[str] = Field(default=None, alias="orderNumber")
    order_date: Optional[str] = Field(default=None, alias="orderDate")


class CreateQuotationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[QuotationData] = None
    error: Optional[ErrorInfo] = None
