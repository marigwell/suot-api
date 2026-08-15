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
