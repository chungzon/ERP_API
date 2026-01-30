import logging
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from app.models.waiting_product import (
    CreateWaitingProductRequest,
    CreateWaitingProductResponse,
    WaitingProductData,
    WaitingProductListResponse,
)
from app.models.waiting_product import ErrorInfo
from app.services import waiting_product_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/waiting-product", tags=["WaitingProduct"])


def _validate_create_request(request: CreateWaitingProductRequest) -> None:
    """Validate create request, matching Java WaitingProductController.validateCreateRequest."""
    if not request.product_code or not request.product_code.strip():
        raise ValueError("商品碼不能為空")
    if not request.product_name or not request.product_name.strip():
        raise ValueError("品名不能為空")
    if request.vendor_code is None:
        raise ValueError("供應商代碼不能為空")
    if not request.vendor or not request.vendor.strip():
        raise ValueError("供應商名稱不能為空")
    if request.pricing is not None and request.pricing < 0:
        raise ValueError("定價不能為負數")
    if request.single_price is not None and request.single_price < 0:
        raise ValueError("單價不能為負數")
    if request.batch_price is not None and request.batch_price < 0:
        raise ValueError("成本價不能為負數")


@router.post("/create")
def create_waiting_product(request: CreateWaitingProductRequest):
    try:
        _validate_create_request(request)
        result = waiting_product_service.create_waiting_product(request)

        response = CreateWaitingProductResponse(
            success=True,
            message="待上架商品建立成功",
            data=WaitingProductData(
                productCode=result["productCode"],
                productName=result["productName"],
            ),
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = CreateWaitingProductResponse(
            success=False,
            message=f"建立失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Waiting product creation failed: %s", e, exc_info=True)
        response = CreateWaitingProductResponse(
            success=False,
            message="建立失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.get("/list")
def get_waiting_product_list(
    vendorCode: Optional[int] = Query(default=None),
    productName: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
):
    try:
        products = waiting_product_service.get_waiting_product_list(
            vendor_code=vendorCode,
            product_name=productName,
            status=status,
        )
        response = WaitingProductListResponse(
            success=True,
            message="查詢成功",
            data=products,
            total=len(products),
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = WaitingProductListResponse(
            success=False,
            message=f"查詢失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Waiting product list query failed: %s", e, exc_info=True)
        response = WaitingProductListResponse(
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
