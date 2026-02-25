import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

from app.models.category import (
    CategoryData,
    CreateCategoryRequest,
    CreateCategoryResponse,
    DeleteCategoryResponse,
    ErrorInfo,
    UpdateCategoryRequest,
    UpdateCategoryResponse,
)
from app.services import category_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/category", tags=["Category"])


@router.post("/create")
def create_category(request: CreateCategoryRequest):
    try:
        result = category_service.create_category(request)

        response = CreateCategoryResponse(
            success=True,
            message="分類建立成功",
            data=CategoryData(
                categoryId=result["categoryId"],
                categoryName=result["categoryName"],
                level=result["level"],
                parentId=result["parentId"],
            ),
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = CreateCategoryResponse(
            success=False,
            message=f"建立失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Category creation failed: %s", e, exc_info=True)
        response = CreateCategoryResponse(
            success=False,
            message="建立失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.put("/update")
def update_category(request: UpdateCategoryRequest):
    try:
        result = category_service.update_category(request)

        response = UpdateCategoryResponse(
            success=True,
            message="分類修改成功",
            data=CategoryData(
                categoryId=result["categoryId"],
                categoryName=result["categoryName"],
                level=result["level"],
                parentId=result["parentId"],
            ),
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = UpdateCategoryResponse(
            success=False,
            message=f"修改失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Category update failed: %s", e, exc_info=True)
        response = UpdateCategoryResponse(
            success=False,
            message="修改失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.delete("/delete/{category_id}")
def delete_category(category_id: str):
    try:
        category_service.delete_category(category_id)

        response = DeleteCategoryResponse(
            success=True,
            message="分類刪除成功",
        )
        return JSONResponse(
            content=response.model_dump(by_alias=True, exclude_none=True)
        )

    except ValueError as e:
        response = DeleteCategoryResponse(
            success=False,
            message=f"刪除失敗：{e}",
            error=ErrorInfo(code="VALIDATION_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )

    except Exception as e:
        logger.error("Category deletion failed: %s", e, exc_info=True)
        response = DeleteCategoryResponse(
            success=False,
            message="刪除失敗：伺服器內部錯誤",
            error=ErrorInfo(code="INTERNAL_ERROR", details=str(e)),
        )
        return JSONResponse(
            status_code=500,
            content=response.model_dump(by_alias=True, exclude_none=True),
        )


@router.get("/health", response_class=PlainTextResponse)
def health():
    return "OK"
