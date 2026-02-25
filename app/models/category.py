from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateCategoryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category_name: str = Field(alias="categoryName")
    level: int = Field(alias="level")
    parent_id: Optional[str] = Field(default=None, alias="parentId")


class CategoryData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category_id: str = Field(alias="categoryId")
    category_name: str = Field(alias="categoryName")
    level: int = Field(alias="level")
    parent_id: Optional[str] = Field(default=None, alias="parentId")


class ErrorInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = ""
    details: str = ""


class CreateCategoryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = False
    message: str = ""
    data: Optional[CategoryData] = None
    error: Optional[ErrorInfo] = None
