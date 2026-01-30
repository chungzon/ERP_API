from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    isbn: str = Field(default="", alias="isbn")
    international_code: str = Field(default="", alias="internationalCode")
    firm_code: str = Field(default="", alias="firmCode")
    product_code: str = Field(default="", alias="productCode")
    product_name: str = Field(default="", alias="productName")
    unit: str = Field(default="", alias="unit")
    vendor_code: str = Field(default="", alias="vendorCode")
    vendor_name: str = Field(default="", alias="vendorName")
    first_category: str = Field(default="", alias="firstCategory")
    second_category: str = Field(default="", alias="secondCategory")
    third_category: str = Field(default="", alias="thirdCategory")
    batch_price: str = Field(default="0", alias="batchPrice")
    single_price: str = Field(default="0", alias="singlePrice")
    pricing: str = Field(default="0", alias="pricing")
    vip_price1: str = Field(default="0", alias="vipPrice1")
    vip_price2: str = Field(default="0", alias="vipPrice2")
    vip_price3: str = Field(default="0", alias="vipPrice3")
    in_stock: str = Field(default="0", alias="inStock")
    safety_stock: str = Field(default="0", alias="safetyStock")
    discount: float = Field(default=0.0, alias="discount")


class ErrorInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = ""
    details: str = ""


class ProductListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[list[ProductDTO]] = None
    total: int = 0
    error: Optional[ErrorInfo] = None
