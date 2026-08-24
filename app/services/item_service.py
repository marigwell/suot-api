# /services/item_service.py
# The service should handle database operations, item creation, item update, and item deletion.

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.item import ItemModel
from app.schemas.item import ItemCreate


def _build_item_filters(
    user_id: int,
    category: str | None = None,
    brand: str | None = None,
    condition: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
) -> list:
    filters = [ItemModel.user_id == user_id]

    if category is not None:
        filters.append(ItemModel.category == category)

    if brand is not None:
        filters.append(ItemModel.brand == brand)

    if condition is not None:
        filters.append(ItemModel.condition == condition)

    if min_price is not None:
        filters.append(ItemModel.price >= min_price)

    if max_price is not None:
        filters.append(ItemModel.price <= max_price)

    return filters


# 1. user ownership
# 2. filters
# 3. sorting
# 4. pagination
def get_items(
    db: Session,
    user_id: int,
    category: str | None = None,
    brand: str | None = None,
    condition: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    limit: int = 20,
    offset: int = 0,
) -> list[ItemModel]:
    filters = _build_item_filters(
        user_id=user_id,
        category=category,
        brand=brand,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
    )

    statement = select(ItemModel).where(*filters)

    sort_columns = {
        "name": ItemModel.name,
        "price": ItemModel.price,
        "purchase_date": ItemModel.purchase_date,
    }

    if sort_by is not None:
        sort_column = sort_columns[sort_by]

        if sort_order == "desc":
            statement = statement.order_by(sort_column.desc())
        else:
            statement = statement.order_by(sort_column.asc())

    statement = statement.limit(limit).offset(offset)

    return list(db.scalars(statement))


def count_items(
    db: Session,
    user_id: int,
    category: str | None = None,
    brand: str | None = None,
    condition: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
) -> int:
    filters = _build_item_filters(
        user_id=user_id,
        category=category,
        brand=brand,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
    )

    statement = select(func.count()).select_from(ItemModel).where(*filters)

    return db.scalar(statement) or 0


def get_item_by_id(
    db: Session,
    item_id: int,
    user_id: int,
) -> ItemModel | None:
    statement = select(ItemModel).where(
        ItemModel.id == item_id,
        ItemModel.user_id == user_id,
    )

    return db.scalar(statement)


def create_item(
    db: Session,
    item_data: ItemCreate,
    user_id: int,
) -> ItemModel:
    item = ItemModel(
        user_id=user_id,
        name=item_data.name,
        brand=item_data.brand,
        category=item_data.category,
        color=item_data.color,
        size=item_data.size,
        price=item_data.price,
        purchase_date=item_data.purchase_date,
        condition=item_data.condition,
        notes=item_data.notes,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def update_item(
    db: Session,
    item_id: int,
    item_data: ItemCreate,
    user_id: int,
) -> ItemModel | None:
    item = get_item_by_id(db, item_id, user_id)

    if item is None:
        return None

    item.name = item_data.name
    item.brand = item_data.brand
    item.category = item_data.category
    item.color = item_data.color
    item.size = item_data.size
    item.price = item_data.price
    item.purchase_date = item_data.purchase_date
    item.condition = item_data.condition
    item.notes = item_data.notes

    db.commit()
    db.refresh(item)

    return item


def delete_item(db: Session, item_id: int, user_id: int) -> bool:
    item = get_item_by_id(db, item_id, user_id)

    if item is None:
        return False

    db.delete(item)
    db.commit()

    return True


def get_item_stats(db: Session, user_id: int) -> dict:
    statement = select(ItemModel).where(ItemModel.user_id == user_id)
    items = list(db.scalars(statement))

    total_items = len(items)
    total_closet_value = Decimal("0.00")
    category_counts: dict[str, int] = {}
    brand_counts: dict[str, int] = {}
    most_expensive_item = None

    for item in items:
        category_counts[item.category] = category_counts.get(item.category, 0) + 1

        if item.brand is not None:
            brand_counts[item.brand] = brand_counts.get(item.brand, 0) + 1

        if item.price is not None:
            total_closet_value += item.price

            if most_expensive_item is None or item.price > most_expensive_item.price:
                most_expensive_item = item

    return {
        "total_items": total_items,
        "total_closet_value": total_closet_value,
        "category_counts": category_counts,
        "brand_counts": brand_counts,
        "most_expensive_item": most_expensive_item,
    }
