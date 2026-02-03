"""Order conversion request/response DTOs."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.stock import StockCheckResultDTO


class ConversionItemDTO(BaseModel):
    """Item for order conversion with optional quantity override."""

    model_config = ConfigDict(populate_by_name=True)

    item_number: Optional[int] = Field(default=None, alias="itemNumber")
    isbn: Optional[str] = Field(default=None, alias="isbn")
    quantity: Optional[int] = Field(default=None, alias="quantity")


class QuotationToWaitingShipmentRequest(BaseModel):
    """Request to convert quotation to waiting shipment order."""

    model_config = ConfigDict(populate_by_name=True)

    quotation_id: int = Field(alias="quotationId")
    items: Optional[list[ConversionItemDTO]] = Field(default=None, alias="items")
    auto_generate_purchase: Optional[bool] = Field(default=True, alias="autoGeneratePurchase")


class PurchaseToWaitingReceiptRequest(BaseModel):
    """Request to convert purchase order to waiting receipt order."""

    model_config = ConfigDict(populate_by_name=True)

    purchase_order_id: int = Field(alias="purchaseOrderId")
    items: Optional[list[ConversionItemDTO]] = Field(default=None, alias="items")


class WaitingShipmentToShipmentRequest(BaseModel):
    """Request to convert waiting shipment to shipment order."""

    model_config = ConfigDict(populate_by_name=True)

    waiting_order_id: int = Field(alias="waitingOrderId")
    items: Optional[list[ConversionItemDTO]] = Field(default=None, alias="items")
    is_partial: Optional[bool] = Field(default=False, alias="isPartial")


class WaitingReceiptToReceiptRequest(BaseModel):
    """Request to convert waiting receipt to receipt order."""

    model_config = ConfigDict(populate_by_name=True)

    waiting_order_id: int = Field(alias="waitingOrderId")
    items: Optional[list[ConversionItemDTO]] = Field(default=None, alias="items")
    is_partial: Optional[bool] = Field(default=False, alias="isPartial")


class AutoPurchaseOrderInfo(BaseModel):
    """Info about auto-generated purchase order."""

    model_config = ConfigDict(populate_by_name=True)

    order_id: Optional[int] = Field(default=None, alias="orderId")
    order_number: Optional[str] = Field(default=None, alias="orderNumber")
    supplier_id: Optional[str] = Field(default=None, alias="supplierId")
    supplier_name: Optional[str] = Field(default=None, alias="supplierName")
    items_count: Optional[int] = Field(default=None, alias="itemsCount")


class ConversionResultDTO(BaseModel):
    """Result of order conversion."""

    model_config = ConfigDict(populate_by_name=True)

    source_order_id: Optional[int] = Field(default=None, alias="sourceOrderId")
    target_order_id: Optional[int] = Field(default=None, alias="targetOrderId")
    target_order_number: Optional[str] = Field(default=None, alias="targetOrderNumber")
    target_order_date: Optional[str] = Field(default=None, alias="targetOrderDate")
    stock_check_results: Optional[list[StockCheckResultDTO]] = Field(
        default=None, alias="stockCheckResults"
    )
    auto_purchase_orders: Optional[list[AutoPurchaseOrderInfo]] = Field(
        default=None, alias="autoPurchaseOrders"
    )


class ConversionResponse(BaseModel):
    """Response for order conversion."""

    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[ConversionResultDTO] = Field(default=None, alias="data")
    error: Optional[dict] = None
