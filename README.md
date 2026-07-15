uv init

uv add fastapi

uv add --dev ruff pytest

# Goals / MVP checkpoints

Phase 1: In-memory CRUD -
Phase 2: SQLite persistence -
Phase 3: PostgreSQL *
Phase 4: SQLAlchemy models and sessions
Phase 5: authentication
Phase 6: user-owned inventory
Phase 7: recommendation logic
Phase 8: testing
Phase 9: Docker
Phase 10: deployment

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

- DEL : Deletes an item

Algorithm of DEL:

Iterate though every item in the inventory

    If the current item's id matches item_id

        Pop the item from the list based on its index

        Return the updated item list
    
    If the loop finishes without finding anything

        Return None

Designing how IDs should work: IDs should never be reused

i.e. if an item is deleted and a new one is created, the new one should never reuse an ID of a deleted item

This is because the IDs of deleted items act as receipts by users and we do not want to overwrite that with new data

## Phase 1 Done : CRUD Finished

# Day 3

- Learn how to make a real database
- How HTTP requests becomes data stored in a SQL database
- How we can retrieve that data back

## What is an ORM?

ORM = Object Relational Mapper

A tool that lets your code interact with a relational database using programming language objects instead of writing SQL directly.

ORMs are bidirectional -> goes both ways -> posting data and retrieving data

It translates between:
- Python objects → SQL database
- SQL database → Python objects

This lets you work with Python objects instead of wriing raw SQL

db.add() vs. dbcommit()

db.add(item)
- Tells SQLAlchemy to prepare/track an object to be saved.

db.commit()
- Permanently saves all pending changes to the database.

# Day 4

We want storage persistence -> data survives after restarting locally

- Add SQLite + SQLAlchemy
- Create 'items' table

POST /items
  ↓
Router receives request
  ↓
FastAPI creates DB session
  ↓
Service creates ItemModel
  ↓
SQLAlchemy inserts row into SQLite
  ↓
db.commit() saves it
  ↓
db.refresh() gets the generated ID
  ↓
API returns JSON

## Phase 2 Done

