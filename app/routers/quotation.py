import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.models.quotation import (
    CreateQuotationRequest,
    CreateQuotationResponse,
    ErrorInfo,
    QuotationData,
)
from app.services import quotation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quotation", tags=["Quotation"])


def _validate_request(request: CreateQuotationRequest) -> None:
    """Validate quotation request, matching Java QuotationController.validateRequest."""
    if not request.order_date or not request.order_date.strip():
        raise ValueError("报价日期不能为空")

    if not request.object_id or not request.object_id.strip():
        raise ValueError("客户ID不能为空（客户ID应来自LINE登录时的ID）")

    if not request.products:
        raise ValueError("商品列表不能为空，至少需要一个商品")

    for i, product in enumerate(request.products):
        if not product.product_name or not product.product_name.strip():
            raise ValueError(f"商品{i + 1}的商品名称不能为空")
        if product.quantity is None or product.quantity <= 0:
            raise ValueError(f"商品{i + 1}的数量必须大于0")

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
                    raise ValueError("价格信息格式错误，必须是数字")


@router.post("/create")
def create_quotation(request: CreateQuotationRequest):
    try:
        _validate_request(request)
        result = quotation_service.create_quotation(request)

        response = CreateQuotationResponse(
            success=True,
            message="报价单创建成功",
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
            message=f"创建失败：{e}",
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
            message="创建失败：服务器内部错误",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.get("/health", response_class=PlainTextResponse)
def health():
    return "OK"
