# /services/item_service.py
# The service should handle database operation, item creation, item update, item deletion

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import ItemModel
from app.schemas.item import ItemCreate


def get_items(db: Session) -> list[ItemModel]:
    statement = select(ItemModel)
    return list(db.scalars(statement).all())


def get_item_by_id(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def create_item(db: Session, item_data: ItemCreate) -> ItemModel:
    item = ItemModel(
        name=item_data.name,
        brand=item_data.brand,
        category=item_data.category,
        color=item_data.color,
        size=item_data.size,
    )

    db.add(item)  # stage object for insert
    db.commit()  # save transaction
    db.refresh(item)  # reload generated database values, like id

    return item


def update_item(
    db: Session,
    item_id: int,
    item_data: ItemCreate,
) -> ItemModel | None:
    item = db.get(ItemModel, item_id)

    if item is None:
        return None

    item.name = item_data.name
    item.brand = item_data.brand
    item.category = item_data.category
    item.color = item_data.color
    item.size = item_data.size

    db.commit()
    db.refresh(item)

    return item


def delete_item(db: Session, item_id: int) -> bool:
    item = db.get(ItemModel, item_id)

    if item is None:
        return False

    db.delete(item)
    db.commit()

    return True
