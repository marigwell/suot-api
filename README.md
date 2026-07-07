uv init

uv add fastapi

uv add --dev ruff pytest

# Day 1

- Making a health check via GET /health
- Possibly adding in data for clothing items: GET /items, POST /items
- Setting up GET and POST and Item template

# Day 2

- Testing POST /items and GET /items
- GET all items
- POST item
- GET one item by id
- 404 errors: Prevents 500 Internal Server Errors since Python tries to do None.name

404 Not Found
200 OK
401 Unauthorized
500 Internal Server Error

- PUT : Updates an item

Algorithm for PUT:

Loop through every item in the inventory

    If the current item's id matches item_id

        Replace the old item with a new updated item

        Return the updated item
    
    If the loop finishes without finding anything

        Return None

Why enumerate?

- Used to be able to access both the index and the item associated with the index

