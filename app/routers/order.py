"""Order query endpoints."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

from app.models.order import (
    OrderListRequest,
    OrderResponse,
    ErrorInfo,
)
from app.services import order_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/order", tags=["Order"])


@router.get("/health", response_class=PlainTextResponse)
def health():
    """Health check endpoint."""
    return "OK"


@router.get("/{order_id}")
def get_order(order_id: int):
    """Get order details by ID."""
    try:
        detail = order_service.get_order_detail(order_id)

        if not detail:
            response = OrderResponse(
                success=False,
                message=f"訂單 #{order_id} 不存在",
                error=ErrorInfo(code="NOT_FOUND", details=f"Order {order_id} not found"),
            )
            return JSONResponse(
                status_code=404,
                content=response.model_dump(by_alias=True, exclude_none=True),
            )

        return JSONResponse(
            content={
                "success": True,
                "message": "查詢成功",
                "data": {
                    "order": detail.order.model_dump(by_alias=True, exclude_none=True) if detail.order else None,
                    "items": [item.model_dump(by_alias=True, exclude_none=True) for item in detail.items] if detail.items else [],
                    "references": [ref.model_dump(by_alias=True, exclude_none=True) for ref in detail.references] if detail.references else [],
                },
            }
        )

    except Exception as e:
        logger.error("Failed to get order %d: %s", order_id, e, exc_info=True)
        response = OrderResponse(
            success=False,
            message="查詢失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.post("/list")
def list_orders(request: OrderListRequest):
    """List orders with filtering."""
    try:
        orders, total = order_service.list_orders(
            order_source=request.order_source,
            object_id=request.object_id,
            start_date=request.start_date,
            end_date=request.end_date,
            status=request.status,
            page=request.page or 1,
            page_size=request.page_size or 20,
        )

        return JSONResponse(
            content={
                "success": True,
                "message": "查詢成功",
                "data": {
                    "orders": [order.model_dump(by_alias=True, exclude_none=True) for order in orders],
                    "total": total,
                    "page": request.page or 1,
                    "pageSize": request.page_size or 20,
                },
            }
        )

    except Exception as e:
        logger.error("Failed to list orders: %s", e, exc_info=True)
        response = OrderResponse(
            success=False,
            message="查詢失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.get("/{order_id}/traceability")
def get_order_traceability(order_id: int):
    """Get order traceability chain."""
    try:
        traceability = order_service.get_order_traceability(order_id)

        if not traceability:
            response = OrderResponse(
                success=False,
                message=f"訂單 #{order_id} 不存在",
                error=ErrorInfo(code="NOT_FOUND", details=f"Order {order_id} not found"),
            )
            return JSONResponse(
                status_code=404,
                content=response.model_dump(by_alias=True, exclude_none=True),
            )

        return JSONResponse(
            content={
                "success": True,
                "message": "查詢成功",
                "data": {
                    "currentOrder": traceability.current_order.model_dump(by_alias=True, exclude_none=True) if traceability.current_order else None,
                    "sourceOrders": [order.model_dump(by_alias=True, exclude_none=True) for order in traceability.source_orders] if traceability.source_orders else [],
                    "derivedOrders": [order.model_dump(by_alias=True, exclude_none=True) for order in traceability.derived_orders] if traceability.derived_orders else [],
                },
            }
        )

    except Exception as e:
        logger.error("Failed to get traceability for order %d: %s", order_id, e, exc_info=True)
        response = OrderResponse(
            success=False,
            message="查詢失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )
