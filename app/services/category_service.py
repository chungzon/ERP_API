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
            "SELECT 1 AS cnt FROM ProductCategory "
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


def _get_category_by_id(category_id: str) -> dict:
    """Fetch a category by its ID. Raises ValueError if not found."""
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT CategoryID, CategoryName, CategoryLayer, ParentCategoryID "
            "FROM ProductCategory "
            "WHERE CategoryID = %s",
            (category_id,),
        )
        row = cursor.fetchone()
    if row is None:
        raise ValueError(f"分類不存在：CategoryID={category_id}")
    return row


def update_category(request) -> dict:
    """Update an existing product category. Returns dict with updated info."""

    category_id = request.category_id.strip()
    if not category_id:
        raise ValueError("categoryId 不能為空")

    # Verify category exists
    existing = _get_category_by_id(category_id)

    category_name = request.category_name
    if category_name is not None:
        category_name = category_name.strip()
        if not category_name:
            raise ValueError("分類名稱不能為空")

        # Check duplicate name within same layer (exclude self)
        layer = existing["CategoryLayer"]
        with db_manager.cursor() as cursor:
            cursor.execute(
                "SELECT 1 AS cnt FROM ProductCategory "
                "WHERE CategoryName = %s AND CategoryLayer = %s AND CategoryID != %s",
                (category_name, layer, category_id),
            )
            if cursor.fetchone() is not None:
                raise ValueError(f"同層級已存在相同名稱的分類：{category_name}")

        # Update
        with db_manager.cursor() as cursor:
            cursor.execute(
                "UPDATE ProductCategory SET CategoryName = %s WHERE CategoryID = %s",
                (category_name, category_id),
            )

        logger.info(
            "Category updated - ID: %s, Name: %s -> %s",
            category_id, existing["CategoryName"], category_name,
        )
    else:
        # Nothing to update
        category_name = existing["CategoryName"]

    return {
        "categoryId": category_id,
        "categoryName": category_name,
        "level": existing["CategoryLayer"],
        "parentId": existing["ParentCategoryID"],
    }


def delete_category(category_id: str) -> None:
    """Delete a category after checking for related products and child categories."""

    category_id = category_id.strip()
    if not category_id:
        raise ValueError("categoryId 不能為空")

    # Verify category exists
    existing = _get_category_by_id(category_id)
    layer = existing["CategoryLayer"]

    # Check for child categories
    with db_manager.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM ProductCategory "
            "WHERE ParentCategoryID = %s",
            (category_id,),
        )
        row = cursor.fetchone()
        if row and row["cnt"] > 0:
            raise ValueError(f"此分類下尚有 {row['cnt']} 個子分類，無法刪除")

    # Check for related products in store_category
    column_map = {1: "FirstCategory_Id", 2: "SecondCategory_Id", 3: "ThirdCategory_Id"}
    column_name = column_map.get(layer)

    if column_name:
        with db_manager.cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) AS cnt FROM store_category "
                f"WHERE {column_name} = %s",
                (category_id,),
            )
            row = cursor.fetchone()
            if row and row["cnt"] > 0:
                raise ValueError(f"此分類下尚有 {row['cnt']} 個關聯商品，無法刪除")

    # Delete the category
    with db_manager.cursor() as cursor:
        cursor.execute(
            "DELETE FROM ProductCategory WHERE CategoryID = %s",
            (category_id,),
        )

    logger.info(
        "Category deleted - ID: %s, Name: %s, Layer: %s",
        category_id, existing["CategoryName"], layer,
    )
