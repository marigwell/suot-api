from fastapi import APIRouter, HTTPException

from app.schemas.item import Item, ItemCreate
from app.services.item_service import create_item, delete_item, get_item_by_id, get_items, update_item

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
    """
    Retrieve an item by its ID.
    """
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=Item)
async def update_existing_item(item_id: int, item_data: ItemCreate):
    """
    Update an existing clothing item.
    """
    updated_item = update_item(item_id, item_data)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@router.delete("/{item_id}", response_model=bool)
async def remove_item(item_id: int):
    """
    Delete an item by its ID.
    """
    deleted = delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return deleted