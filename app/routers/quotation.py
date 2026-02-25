import logging
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.models.quotation import (
    CreateQuotationRequest,
    CreateQuotationResponse,
    ErrorInfo,
    QuotationData,
    QuotationListResponse,
)
from app.services import quotation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quotation", tags=["Quotation"])


def _validate_request(request: CreateQuotationRequest) -> None:
    """Validate quotation request, matching Java QuotationController.validateRequest."""
    if not request.order_date or not request.order_date.strip():
        raise ValueError("報價日期不能為空")

    if not request.object_id or not request.object_id.strip():
        raise ValueError("客戶ID不能為空（客戶ID應來自LINE登入時的ID）")

    if not request.products:
        raise ValueError("商品列表不能為空，至少需要一個商品")

    for i, product in enumerate(request.products):
        if not product.product_name or not product.product_name.strip():
            raise ValueError(f"商品{i + 1}的商品名稱不能為空")
        if product.quantity is None or product.quantity <= 0:
            raise ValueError(f"商品{i + 1}的數量必須大於0")

    if request.price_info:
        pi = request.price_info
        for field_name, field_val in [
            ("totalPriceNoneTax", pi.total_price_none_tax),
            ("tax", pi.tax),
            ("discount", pi.discount),
            ("totalPriceIncludeTax", pi.total_price_include_tax),
        ]:
            if field_val is not None:
                try:
                    int(field_val)
                except ValueError:
                    raise ValueError("價格資訊格式錯誤，必須是數字")


@router.post("/create")
def create_quotation(request: CreateQuotationRequest):
    try:
        _validate_request(request)
        result = quotation_service.create_quotation(request)

        response = CreateQuotationResponse(
            success=True,
            message=f"報價單建立成功，單號：{result['orderNumber']}",
            data=QuotationData(
                orderId=result["orderId"],
                orderNumber=result["orderNumber"],
                orderDate=result["orderDate"],
            ),
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = CreateQuotationResponse(
            success=False,
            message=f"建立失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Quotation creation failed: %s", e, exc_info=True)
        response = CreateQuotationResponse(
            success=False,
            message="建立失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.get("/list")
def list_quotations(
    objectId: Optional[str] = Query(default=None),
    startDate: Optional[str] = Query(default=None),
    endDate: Optional[str] = Query(default=None),
    status: Optional[int] = Query(default=None),
):
    try:
        result = quotation_service.list_quotations(
            object_id=objectId,
            start_date=startDate,
            end_date=endDate,
            status=status,
        )

        response = QuotationListResponse(
            success=True,
            message="查詢成功",
            data=result,
            total=len(result),
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = QuotationListResponse(
            success=False,
            message=f"查詢失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Quotation list query failed: %s", e, exc_info=True)
        response = QuotationListResponse(
            success=False,
            message="查詢失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.get("/health", response_class=PlainTextResponse)
def health():
    return "OK"
