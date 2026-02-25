import logging
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from app.models.vendor import (
    CreateVendorRequest,
    CreateVendorResponse,
    DeleteVendorResponse,
    ErrorInfo,
    UpdateVendorRequest,
    UpdateVendorResponse,
    VendorListResponse,
)
from app.services import vendor_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vendor", tags=["Vendor"])


@router.post("/create")
def create_vendor(request: CreateVendorRequest):
    try:
        result = vendor_service.create_vendor(request)

        response = CreateVendorResponse(
            success=True,
            message="廠商建立成功",
            data=result,
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = CreateVendorResponse(
            success=False,
            message=f"建立失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Vendor creation failed: %s", e, exc_info=True)
        response = CreateVendorResponse(
            success=False,
            message="建立失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.put("/update")
def update_vendor(request: UpdateVendorRequest):
    try:
        result = vendor_service.update_vendor(request)

        response = UpdateVendorResponse(
            success=True,
            message="廠商修改成功",
            data=result,
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = UpdateVendorResponse(
            success=False,
            message=f"修改失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Vendor update failed: %s", e, exc_info=True)
        response = UpdateVendorResponse(
            success=False,
            message="修改失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.delete("/delete/{vendor_code}")
def delete_vendor(vendor_code: str):
    try:
        vendor_service.delete_vendor(vendor_code)

        response = DeleteVendorResponse(
            success=True,
            message="廠商刪除成功",
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = DeleteVendorResponse(
            success=False,
            message=f"刪除失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Vendor deletion failed: %s", e, exc_info=True)
        response = DeleteVendorResponse(
            success=False,
            message="刪除失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.get("/list")
def list_vendors(
    vendorName: Optional[str] = Query(default=None),
    vendorCode: Optional[str] = Query(default=None),
):
    try:
        result = vendor_service.list_vendors(
            vendor_name=vendorName,
            vendor_code=vendorCode,
        )

        response = VendorListResponse(
            success=True,
            message="查詢成功",
            data=result,
            total=len(result),
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = VendorListResponse(
            success=False,
            message=f"查詢失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Vendor list query failed: %s", e, exc_info=True)
        response = VendorListResponse(
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
