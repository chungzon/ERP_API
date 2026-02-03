from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CreateWaitingProductRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Required fields
    product_code: str = Field(alias="productCode")
    product_name: str = Field(alias="productName")
    vendor_code: int = Field(alias="vendorCode")
    vendor: str = Field(alias="vendor")

    # Optional - prices
    pricing: Optional[float] = Field(default=None, alias="pricing")
    single_price: Optional[float] = Field(default=None, alias="singlePrice")
    batch_price: Optional[float] = Field(default=None, alias="batchPrice")
    vip_price1: Optional[float] = Field(default=None, alias="vipPrice1")
    vip_price2: Optional[float] = Field(default=None, alias="vipPrice2")
    vip_price3: Optional[float] = Field(default=None, alias="vipPrice3")

    # Optional - basic info
    unit: Optional[str] = Field(default=None, alias="unit")
    brand: Optional[str] = Field(default=None, alias="brand")
    describe: Optional[str] = Field(default=None, alias="describe")
    remark: Optional[str] = Field(default=None, alias="remark")
    supply_status: Optional[str] = Field(default=None, alias="supplyStatus")

    # Optional - categories
    new_first_category: Optional[str] = Field(default=None, alias="newFirstCategory")
    first_category_id: Optional[int] = Field(default=None, alias="firstCategoryId")
    second_category_id: Optional[int] = Field(default=None, alias="secondCategoryId")
    third_category_id: Optional[int] = Field(default=None, alias="thirdCategoryId")

    # Optional - pictures (Base64)
    picture1: Optional[str] = Field(default=None, alias="picture1")
    picture2: Optional[str] = Field(default=None, alias="picture2")
    picture3: Optional[str] = Field(default=None, alias="picture3")


class WaitingProductDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_code: Optional[str] = Field(default=None, alias="productCode")
    product_name: Optional[str] = Field(default=None, alias="productName")
    vendor_code: Optional[int] = Field(default=None, alias="vendorCode")
    vendor: Optional[str] = Field(default=None, alias="vendor")

    pricing: Optional[float] = Field(default=None, alias="pricing")
    single_price: Optional[float] = Field(default=None, alias="singlePrice")
    batch_price: Optional[float] = Field(default=None, alias="batchPrice")
    vip_price1: Optional[float] = Field(default=None, alias="vipPrice1")
    vip_price2: Optional[float] = Field(default=None, alias="vipPrice2")
    vip_price3: Optional[float] = Field(default=None, alias="vipPrice3")

    unit: Optional[str] = Field(default=None, alias="unit")
    brand: Optional[str] = Field(default=None, alias="brand")
    describe: Optional[str] = Field(default=None, alias="describe")
    remark: Optional[str] = Field(default=None, alias="remark")
    supply_status: Optional[str] = Field(default=None, alias="supplyStatus")
    new_first_category: Optional[str] = Field(default=None, alias="newFirstCategory")

    first_category_id: Optional[int] = Field(default=None, alias="firstCategoryId")
    second_category_id: Optional[int] = Field(default=None, alias="secondCategoryId")
    third_category_id: Optional[int] = Field(default=None, alias="thirdCategoryId")

    keyin_date: Optional[str] = Field(default=None, alias="keyinDate")
    update_date: Optional[str] = Field(default=None, alias="updateDate")
    status: Optional[str] = Field(default=None, alias="status")

    picture1: Optional[str] = Field(default=None, alias="picture1")
    picture2: Optional[str] = Field(default=None, alias="picture2")
    picture3: Optional[str] = Field(default=None, alias="picture3")


class ErrorInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = ""
    details: str = ""


class WaitingProductData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_code: Optional[str] = Field(default=None, alias="productCode")
    product_name: Optional[str] = Field(default=None, alias="productName")


class CreateWaitingProductResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[WaitingProductData] = None
    error: Optional[ErrorInfo] = None


class WaitingProductListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[list[WaitingProductDTO]] = None
    total: int = 0
    error: Optional[ErrorInfo] = None
