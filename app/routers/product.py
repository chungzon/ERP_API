import logging
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from app.models.product import ErrorInfo, ProductListResponse
from app.services import product_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/product", tags=["Product"])


@router.get("/list")
def get_product_list(
    isbn: Optional[str] = Query(default=None),
    firmCode: Optional[str] = Query(default=None),
    productName: Optional[str] = Query(default=None),
):
    try:
        products = product_service.get_product_list(isbn=isbn, firm_code=firmCode, product_name=productName)
        response = ProductListResponse(
            success=True,
            message="查詢成功",
            data=products,
            total=len(products),
        )
        return JSONResponse(content=response.model_dump(by_alias=True, exclude_none=True))
    except Exception as e:
        logger.error("Product list query failed: %s", e, exc_info=True)
        response = ProductListResponse(
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
