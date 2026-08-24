# /schemas/item.py

from pydantic import BaseModel, ConfigDict

from datetime import date
from decimal import Decimal


class ItemCreate(BaseModel):
    name: str
    brand: str | None = None
    category: str
    color: str
    size: str
    price: Decimal | None = None
    purchase_date: date | None = None
    condition: str | None = None
    notes: str | None = None


class Item(ItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class ItemPage(BaseModel):
    items: list[Item]
    total: int
    limit: int
    offset: int
    has_more: bool


class MostExpensiveItem(BaseModel):
    id: int
    name: str
    brand: str | None = None
    price: Decimal


class ItemStats(BaseModel):
    total_items: int
    total_closet_value: Decimal
    category_counts: dict[str, int]
    brand_counts: dict[str, int]
    most_expensive_item: MostExpensiveItem | None
