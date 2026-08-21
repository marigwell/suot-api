# /routers/items.py
# Router should handle HTTP route, request body, path parameters,
# 404 exceptions, response model

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from app.database import get_db
from app.models.user import UserModel
from app.routers.auth import get_current_user
from app.schemas.item import Item, ItemCreate, ItemStats
from app.services.item_service import (
    create_item,
    delete_item,
    get_item_by_id,
    get_items,
    update_item,
    get_item_stats,
)

router = APIRouter(prefix="/items", tags=["Items"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]


@router.get("", response_model=list[Item])
def list_items(
    db: DbSession,
    current_user: CurrentUser,
    category: str | None = None,
    brand: str | None = None,
    condition: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
):
    """
    Return items owned by the current user with options to be filtered by category, brand, condition, or price range.
    """
    return get_items(
        db,
        user_id=current_user.id,
        category=category,
        brand=brand,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
    )


@router.post("", response_model=Item)
def add_item(
    item: ItemCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Create a new clothing item owned by the current user.
    """
    return create_item(db, item, user_id=current_user.id)


@router.get("/stats", response_model=ItemStats)
def get_stats(
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Return closet analytics for the current user.
    """
    return get_item_stats(db, user_id=current_user.id)


@router.get("/{item_id}", response_model=Item)
def get_item(
    item_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Retrieve an item by its ID if it belongs to the current user.
    """
    item = get_item_by_id(db, item_id, user_id=current_user.id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.put("/{item_id}", response_model=Item)
def update_existing_item(
    item_id: int,
    item_data: ItemCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Update an existing clothing item if it belongs to the current user.
    """
    updated_item = update_item(db, item_id, item_data, user_id=current_user.id)

    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return updated_item


@router.delete("/{item_id}", response_model=bool)
def remove_item(
    item_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Delete an item by its ID if it belongs to the current user.
    """
    deleted = delete_item(db, item_id, user_id=current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    return deleted
