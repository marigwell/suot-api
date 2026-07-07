from fastapi import APIRouter, HTTPException

from app.schemas.item import Item, ItemCreate
from app.services.item_service import create_item, get_item_by_id, get_items

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/", response_model=list[Item])
async def list_items():
    """
    Returns a list of all items.
    """
    return get_items()

@router.post("/", response_model=Item)
async def add_item(item: ItemCreate):
    """
    Create a new clothing item.
    """
    return create_item(item)

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
