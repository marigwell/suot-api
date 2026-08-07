# /schemas/item.py

from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    name: str
    brand: str | None = None
    category: str
    color: str
    size: str


class Item(ItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
