# /routers/items.py
# Router should handle HTTP route, request body, path parameters,
# 404 exceptions, response model

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.item import Item, ItemCreate
from app.services.item_service import (
    create_item,
    delete_item,
    get_item_by_id,
    get_items,
    update_item,
)

router = APIRouter(prefix="/items", tags=["Items"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[Item])
def list_items(db: DbSession):
    """
    Return a list of all items.
    """
    return get_items(db)


@router.post("", response_model=Item)
def add_item(item: ItemCreate, db: DbSession):
    """
    Create a new clothing item.
    """
    return create_item(db, item)


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int, db: DbSession):
    """
    Retrieve an item by its ID.
    """
    item = get_item_by_id(db, item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.put("/{item_id}", response_model=Item)
def update_existing_item(
    item_id: int,
    item_data: ItemCreate,
    db: DbSession,
):
    """
    Update an existing clothing item.
    """
    updated_item = update_item(db, item_id, item_data)

    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return updated_item


@router.delete("/{item_id}", response_model=bool)
def remove_item(item_id: int, db: DbSession):
    """
    Delete an item by its ID.
    """
    deleted = delete_item(db, item_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    return deleted
