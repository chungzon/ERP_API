"""Order conversion endpoints."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

from app.models.order import ErrorInfo
from app.models.order_conversion import (
    QuotationToWaitingShipmentRequest,
    PurchaseToWaitingReceiptRequest,
    WaitingShipmentToShipmentRequest,
    WaitingReceiptToReceiptRequest,
    ConversionResponse,
)
from app.models.stock import StockCheckRequest, StockCheckResponse
from app.services import order_conversion_service, stock_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/order-conversion", tags=["OrderConversion"])


@router.post("/check-stock")
def check_stock(request: StockCheckRequest):
    """Check stock availability for items."""
    try:
        items = [
            {"isbn": item.isbn, "quantity": item.quantity}
            for item in request.items
        ]
        results = stock_service.check_stock_for_items(items)

        all_sufficient = all(r.is_sufficient for r in results)

        response = StockCheckResponse(
            success=True,
            message="庫存檢查完成",
            all_sufficient=all_sufficient,
            results=results,
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except Exception as e:
        logger.error("Stock check failed: %s", e, exc_info=True)
        response = StockCheckResponse(
            success=False,
            message="庫存檢查失敗：伺服器內部錯誤",
            error={"code": "INTERNAL_ERROR", "details": str(e)},
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.post("/quotation-to-waiting-shipment")
def quotation_to_waiting_shipment(request: QuotationToWaitingShipmentRequest):
    """Convert quotation to waiting shipment order.

    報價單 → 待出貨單
    """
    try:
        items = None
        if request.items:
            items = [
                {
                    "item_number": item.item_number,
                    "isbn": item.isbn,
                    "quantity": item.quantity,
                }
                for item in request.items
            ]

        result = order_conversion_service.convert_quotation_to_waiting_shipment(
            quotation_id=request.quotation_id,
            items=items,
            auto_generate_purchase=request.auto_generate_purchase if request.auto_generate_purchase is not None else True,
        )

        response = ConversionResponse(
            success=True,
            message=f"報價單已轉換為待出貨單，單號：{result.target_order_number}",
            data=result,
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = ConversionResponse(
            success=False,
            message=f"轉換失敗：{e}",
            error={"code": "VALIDATION_ERROR", "details": str(e)},
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Quotation to waiting shipment failed: %s", e, exc_info=True)
        response = ConversionResponse(
            success=False,
            message="轉換失敗：伺服器內部錯誤",
            error={"code": "INTERNAL_ERROR", "details": str(e)},
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.post("/purchase-to-waiting-receipt")
def purchase_to_waiting_receipt(request: PurchaseToWaitingReceiptRequest):
    """Convert purchase order to waiting receipt order.

    採購單 → 待入倉單
    """
    try:
        items = None
        if request.items:
            items = [
                {
                    "item_number": item.item_number,
                    "isbn": item.isbn,
                    "quantity": item.quantity,
                }
                for item in request.items
            ]

        result = order_conversion_service.convert_purchase_to_waiting_receipt(
            purchase_order_id=request.purchase_order_id,
            items=items,
        )

        response = ConversionResponse(
            success=True,
            message=f"採購單已轉換為待入倉單，單號：{result.target_order_number}",
            data=result,
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = ConversionResponse(
            success=False,
            message=f"轉換失敗：{e}",
            error={"code": "VALIDATION_ERROR", "details": str(e)},
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Purchase to waiting receipt failed: %s", e, exc_info=True)
        response = ConversionResponse(
            success=False,
            message="轉換失敗：伺服器內部錯誤",
            error={"code": "INTERNAL_ERROR", "details": str(e)},
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.post("/waiting-shipment-to-shipment")
def waiting_shipment_to_shipment(request: WaitingShipmentToShipmentRequest):
    """Convert waiting shipment to shipment order.

    待出貨單 → 出貨單
    """
    try:
        items = None
        if request.items:
            items = [
                {
                    "item_number": item.item_number,
                    "isbn": item.isbn,
                    "quantity": item.quantity,
                }
                for item in request.items
            ]

        result = order_conversion_service.convert_waiting_shipment_to_shipment(
            waiting_order_id=request.waiting_order_id,
            items=items,
            is_partial=request.is_partial or False,
        )

        response = ConversionResponse(
            success=True,
            message=f"待出貨單已轉換為出貨單，單號：{result.target_order_number}",
            data=result,
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = ConversionResponse(
            success=False,
            message=f"轉換失敗：{e}",
            error={"code": "VALIDATION_ERROR", "details": str(e)},
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Waiting shipment to shipment failed: %s", e, exc_info=True)
        response = ConversionResponse(
            success=False,
            message="轉換失敗：伺服器內部錯誤",
            error={"code": "INTERNAL_ERROR", "details": str(e)},
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.post("/waiting-receipt-to-receipt")
def waiting_receipt_to_receipt(request: WaitingReceiptToReceiptRequest):
    """Convert waiting receipt to receipt order.

    待入倉單 → 進貨單
    """
    try:
        items = None
        if request.items:
            items = [
                {
                    "item_number": item.item_number,
                    "isbn": item.isbn,
                    "quantity": item.quantity,
                }
                for item in request.items
            ]

        result = order_conversion_service.convert_waiting_receipt_to_receipt(
            waiting_order_id=request.waiting_order_id,
            items=items,
            is_partial=request.is_partial or False,
        )

        response = ConversionResponse(
            success=True,
            message=f"待入倉單已轉換為進貨單，單號：{result.target_order_number}",
            data=result,
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = ConversionResponse(
            success=False,
            message=f"轉換失敗：{e}",
            error={"code": "VALIDATION_ERROR", "details": str(e)},
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Waiting receipt to receipt failed: %s", e, exc_info=True)
        response = ConversionResponse(
            success=False,
            message="轉換失敗：伺服器內部錯誤",
            error={"code": "INTERNAL_ERROR", "details": str(e)},
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.get("/health", response_class=PlainTextResponse)
def health():
    """Health check endpoint."""
    return "OK"
