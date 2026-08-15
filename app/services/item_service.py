# /services/item_service.py
# The service should handle database operations, item creation, item update, and item deletion.

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import ItemModel
from app.schemas.item import ItemCreate


def get_items(db: Session, user_id: int) -> list[ItemModel]:
    statement = select(ItemModel).where(ItemModel.user_id == user_id)
    return list(db.scalars(statement))


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
