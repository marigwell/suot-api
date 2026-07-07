from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    category: str
    color: str
    size: str

class Item(ItemCreate):
    id: int