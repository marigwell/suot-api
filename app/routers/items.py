from fastapi import APIRouter

from app.schemas.item import Item, ItemCreate
from app.services.item_service import get_items, create_item

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/", response_model=list[Item])
async def list_items():
    return get_items()

@router.post("/", response_model=Item)
async def add_item(item: ItemCreate):
    return create_item(item)