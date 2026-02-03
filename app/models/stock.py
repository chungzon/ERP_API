"""Stock checking DTOs."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductStockDTO(BaseModel):
    """Product stock information."""

    model_config = ConfigDict(populate_by_name=True)

    isbn: Optional[str] = Field(default=None, alias="isbn")
    product_name: Optional[str] = Field(default=None, alias="productName")
    in_stock: Optional[int] = Field(default=0, alias="inStock")
    safety_stock: Optional[int] = Field(default=0, alias="safetyStock")
    waiting_into_in_stock: Optional[int] = Field(default=0, alias="waitingIntoInStock")
    waiting_shipment_quantity: Optional[int] = Field(default=0, alias="waitingShipmentQuantity")
    available_quantity: Optional[int] = Field(default=0, alias="availableQuantity")


class StockCheckItemDTO(BaseModel):
    """Item to check stock for."""

    model_config = ConfigDict(populate_by_name=True)

    isbn: str = Field(alias="isbn")
    quantity: int = Field(alias="quantity")


class StockCheckResultDTO(BaseModel):
    """Stock check result for a single item."""

    model_config = ConfigDict(populate_by_name=True)

    isbn: Optional[str] = Field(default=None, alias="isbn")
    product_name: Optional[str] = Field(default=None, alias="productName")
    requested_quantity: Optional[int] = Field(default=0, alias="requestedQuantity")
    available_quantity: Optional[int] = Field(default=0, alias="availableQuantity")
    is_sufficient: Optional[bool] = Field(default=False, alias="isSufficient")
    shortage_quantity: Optional[int] = Field(default=0, alias="shortageQuantity")


class StockCheckRequest(BaseModel):
    """Request for checking stock of multiple items."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[StockCheckItemDTO] = Field(alias="items")


class StockCheckResponse(BaseModel):
    """Response for stock check."""

    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    all_sufficient: Optional[bool] = Field(default=False, alias="allSufficient")
    results: Optional[list[StockCheckResultDTO]] = Field(default=None, alias="results")
    error: Optional[dict] = None
