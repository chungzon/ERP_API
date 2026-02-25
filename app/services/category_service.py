import logging

from app.database.connection import db_manager

logger = logging.getLogger(__name__)


def _get_parent_category(parent_id: str, expected_layer: int) -> dict:
    """Fetch a parent category and verify it exists at the expected layer."""
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT CategoryID, CategoryLayer, CategoryName "
            "FROM ProductCategory "
            "WHERE CategoryID = %s AND CategoryLayer = %s",
            (parent_id, expected_layer),
        )
        row = cursor.fetchone()
    if row is None:
        layer_name = {1: "大類別", 2: "中類別"}[expected_layer]
        raise ValueError(f"父類別不存在：CategoryID={parent_id} (Layer {expected_layer} {layer_name})")
    return row


def _check_duplicate_name(category_name: str, layer: int) -> None:
    """Check if a category with the same name exists at the same layer."""
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM ProductCategory "
            "WHERE CategoryName = %s AND CategoryLayer = %s",
            (category_name, layer),
        )
        if cursor.fetchone() is not None:
            raise ValueError(f"同層級已存在相同名稱的分類：{category_name}")


def _generate_category_id(layer: int) -> str:
    """Generate the next CategoryID for the given layer.

    Layer 1 & 2: 2-digit zero-padded (01, 02, ...)
    Layer 3: 3-digit zero-padded (001, 002, ...)
    IDs are unique within each layer (not grouped by parent).
    """
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT MAX(CAST(CategoryID AS int)) AS max_id "
            "FROM ProductCategory "
            "WHERE CategoryLayer = %s",
            (layer,),
        )
        row = cursor.fetchone()

    max_id = row["max_id"] if row and row["max_id"] is not None else 0
    next_id = max_id + 1

    if layer in (1, 2):
        return str(next_id).zfill(2)
    else:
        return str(next_id).zfill(3)


def create_category(request) -> dict:
    """Create a new product category. Returns dict with category info."""

    level = request.level
    category_name = request.category_name.strip()
    parent_id = request.parent_id

    # Validate level
    if level not in (1, 2, 3):
        raise ValueError("level 必須為 1（大類別）、2（中類別）或 3（小類別）")

    if not category_name:
        raise ValueError("分類名稱不能為空")

    # Validate parent-child relationship
    if level == 1:
        if parent_id is not None:
            raise ValueError("大類別（level=1）不需要指定 parentId")
    elif level == 2:
        if parent_id is None:
            raise ValueError("中類別（level=2）必須指定 parentId（大類別 ID）")
        _get_parent_category(parent_id, expected_layer=1)
    elif level == 3:
        if parent_id is None:
            raise ValueError("小類別（level=3）必須指定 parentId（中類別 ID）")
        _get_parent_category(parent_id, expected_layer=2)

    # Check duplicate name within same layer
    _check_duplicate_name(category_name, level)

    # Generate new CategoryID
    category_id = _generate_category_id(level)

    # Insert into ProductCategory
    with db_manager.cursor() as cursor:
        cursor.execute(
            "INSERT INTO ProductCategory ("
            "CategoryID, CategoryName, CategoryLayer, "
            "DiscountQuantity, Discount, PreferentialDiscount, VipDiscount, "
            "ParentCategoryID"
            ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                category_id,
                category_name,
                level,
                0,    # DiscountQuantity
                1,    # Discount
                1,    # PreferentialDiscount
                1,    # VipDiscount
                parent_id,
            ),
        )

    logger.info(
        "Category created - ID: %s, Name: %s, Layer: %s, ParentID: %s",
        category_id, category_name, level, parent_id,
    )

    return {
        "categoryId": category_id,
        "categoryName": category_name,
        "level": level,
        "parentId": parent_id,
    }
