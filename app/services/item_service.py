from app.schemas.item import Item, ItemCreate

items: list[Item] = []
next_id = 1

def get_items() -> list[Item]:
    return items

def create_item(item_data: ItemCreate) -> Item:
    global next_id

    item = Item(
        id=next_id,
        name=item_data.name,
        category=item_data.category,
        color=item_data.color,
        size=item_data.size
    )

    items.append(item)
    next_id += 1
    return item

def get_item_by_id(item_id: int) -> Item | None:
    for item in items:
        if item.id == item_id:
            return item
    return None


