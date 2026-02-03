"""Core order DTOs for order traceability mechanism."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OrderItemDTO(BaseModel):
    """Order item data transfer object."""

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
    """Order reference data transfer object."""

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = Field(default=None, alias="id")
    order_id: Optional[int] = Field(default=None, alias="orderId")
    order_reference_id: Optional[int] = Field(default=None, alias="orderReferenceId")
    sub_bill_reference_id: Optional[int] = Field(default=None, alias="subBillReferenceId")


class OrderDTO(BaseModel):
    """Order data transfer object."""

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = Field(default=None, alias="id")
    order_number: Optional[str] = Field(default=None, alias="orderNumber")
    order_date: Optional[str] = Field(default=None, alias="orderDate")
    order_source: Optional[int] = Field(default=None, alias="orderSource")
    object_id: Optional[str] = Field(default=None, alias="objectId")
    is_checkout: Optional[bool] = Field(default=None, alias="isCheckout")
    number_of_items: Optional[int] = Field(default=None, alias="numberOfItems")
    establish_source: Optional[int] = Field(default=None, alias="establishSource")
    is_borrowed: Optional[bool] = Field(default=None, alias="isBorrowed")
    is_offset: Optional[bool] = Field(default=None, alias="isOffset")
    remark: Optional[str] = Field(default=None, alias="remark")
    cashier_remark: Optional[str] = Field(default=None, alias="cashierRemark")
    status: Optional[int] = Field(default=None, alias="status")
    waiting_order_date: Optional[str] = Field(default=None, alias="waitingOrderDate")
    waiting_order_number: Optional[str] = Field(default=None, alias="waitingOrderNumber")
    already_order_date: Optional[str] = Field(default=None, alias="alreadyOrderDate")
    already_order_number: Optional[str] = Field(default=None, alias="alreadyOrderNumber")


class OrderDetailDTO(BaseModel):
    """Order detail with items and references."""

    model_config = ConfigDict(populate_by_name=True)

    order: Optional[OrderDTO] = Field(default=None, alias="order")
    items: Optional[list[OrderItemDTO]] = Field(default=None, alias="items")
    references: Optional[list[OrderReferenceDTO]] = Field(default=None, alias="references")


class OrderListRequest(BaseModel):
    """Request for listing orders with filtering."""

    model_config = ConfigDict(populate_by_name=True)

    order_source: Optional[int] = Field(default=None, alias="orderSource")
    object_id: Optional[str] = Field(default=None, alias="objectId")
    start_date: Optional[str] = Field(default=None, alias="startDate")
    end_date: Optional[str] = Field(default=None, alias="endDate")
    status: Optional[int] = Field(default=None, alias="status")
    page: Optional[int] = Field(default=1, alias="page")
    page_size: Optional[int] = Field(default=20, alias="pageSize")


class OrderTraceabilityDTO(BaseModel):
    """Order traceability chain."""

    model_config = ConfigDict(populate_by_name=True)

    current_order: Optional[OrderDTO] = Field(default=None, alias="currentOrder")
    source_orders: Optional[list[OrderDTO]] = Field(default=None, alias="sourceOrders")
    derived_orders: Optional[list[OrderDTO]] = Field(default=None, alias="derivedOrders")


class ErrorInfo(BaseModel):
    """Error information."""

    model_config = ConfigDict(populate_by_name=True)

    code: str = ""
    details: str = ""


class OrderResponse(BaseModel):
    """Generic order response."""

    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[dict] = None
    error: Optional[ErrorInfo] = None
