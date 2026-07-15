# Suot API Development Log

This file tracks the learning process, design decisions, and backend concepts explored while building Suot API.

## Day 1 — FastAPI Foundation

### Work Completed

- Created the initial FastAPI project.
- Added a health check endpoint with `GET /health`.
- Started designing the item inventory API.
- Created initial project folders for routers, schemas, services, and models.

### Concepts Learned

- An API acts as the interface between clients and the application.
- Routers handle HTTP requests and route them to the correct logic.
- A health check endpoint confirms that the API is running correctly.

### Endpoints Added

```http
GET /health
```

---

## Day 2 — In-Memory CRUD

### Work Completed

- Added item inventory endpoints.
- Implemented in-memory CRUD using a Python list.
- Added item lookup by ID.
- Added update and delete logic.
- Added 404 error handling.

### Endpoints Added

```http
GET /items
POST /items
GET /items/{item_id}
PUT /items/{item_id}
DELETE /items/{item_id}
```

### Concepts Learned

CRUD means:

```txt
Create  → POST
Read    → GET
Update  → PUT
Delete  → DELETE
```

The first version stored items in memory:

```python
items = []
```

This worked for learning API flow, but data disappeared when the server restarted.

### 404 Error Handling

If an item does not exist, the API returns:

```http
404 Not Found
```

This prevents the server from crashing with a `500 Internal Server Error`.

### PUT Algorithm

```txt
Receive item_id and updated item data

Loop through every item in inventory

If current item ID matches item_id:
    Replace the old item with updated data
    Return the updated item

If no item is found:
    Return None
```

### Why `enumerate()` Was Used

`enumerate()` gives access to both:

```txt
index
item
```

This matters because updating an item in a list requires knowing where the item is located.

Example:

```python
for index, item in enumerate(items):
    ...
```

### DELETE Algorithm

```txt
Receive item_id

Loop through every item in inventory

If current item ID matches item_id:
    Remove the item from the list using its index
    Return success

If no item is found:
    Return failure
```

### ID Design Decision

IDs should not be reused after deletion.

Reason:

```txt
IDs represent stable record identity.
If an old ID is reused, historical references such as orders, favorites, logs, or audit records could accidentally point to the wrong item.
```

### Phase 1 Status

Phase 1 complete: In-memory item CRUD finished.

---

## Day 3 — ORM and Database Concepts

### Goal

Understand how HTTP requests can become data stored in a SQL database, and how that data can be retrieved later.

### What Is an ORM?

ORM means:

```txt
Object Relational Mapper
```

An ORM maps between programming language objects and relational database tables.

It helps with both:

```txt
Python objects → database rows
database rows → Python objects
```

Instead of writing raw SQL for every operation, the application can work with Python objects.

### SQLAlchemy

SQLAlchemy is the ORM being used in this project.

It allows the service layer to create, read, update, and delete database records using Python objects.

### `db.add()` vs `db.commit()`

```python
db.add(item)
```

Stages a new object to be inserted into the database.

```python
db.commit()
```

Permanently saves pending database changes in the current transaction.

Important distinction:

```txt
db.add()    → prepare the change
db.commit() → save the change
```

---

## Day 4 — SQLite Persistence

### Goal

Replace temporary in-memory storage with persistent storage so data survives after restarting the server.

### Work Completed

- Added SQLite database support.
- Added SQLAlchemy database setup.
- Created the `items` table through `ItemModel`.
- Replaced in-memory item storage with database-backed CRUD.
- Added `.gitignore`.
- Switched route handlers from `async def` to `def` because the app currently uses synchronous SQLAlchemy.

### Old Storage

```python
items = []
```

This stored data only in memory.

Problem:

```txt
Restart server → data disappears
```

### New Storage

```txt
SQLite database file
```

Result:

```txt
Restart server → data survives
```

### Request Flow for Creating an Item

```txt
POST /items
  ↓
Router receives request
  ↓
FastAPI creates database session
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
```

### Architecture After Persistence

```txt
Client
  ↓
Router
  ↓
Schema validation
  ↓
Service layer
  ↓
SQLAlchemy Session
  ↓
SQLite database
```

### Phase 2 Status

Phase 2 complete: SQLite persistence with SQLAlchemy finished.

---

## Core Notes

### `database.py`

`database.py` sets up the SQLAlchemy database connection.

It creates:

```txt
engine
SessionLocal
Base
get_db()
```

It is responsible for database infrastructure, not item logic.

### `ItemModel`

`ItemModel` is the SQLAlchemy model that defines how an item is represented in the database.

It maps:

```txt
Python class ItemModel
```

to:

```txt
SQL table items
```

Simple definition:

```txt
ItemModel = blueprint for the items table
```

### `get_db()`

`get_db()` creates a database session for one request, gives it to the route, and closes it after the request finishes.

Flow:

```txt
Request starts
  ↓
get_db() creates session
  ↓
Route/service uses session
  ↓
Request ends
  ↓
get_db() closes session
```

### `Session`

A SQLAlchemy `Session` is the object the application uses to talk to the database.

It can:

```txt
run queries
stage inserts
stage updates
stage deletes
commit transactions
rollback transactions
```

Simple definition:

```txt
Session = active conversation with the database
```

### `db.get()`

```python
db.get(ItemModel, item_id)
```

Finds one row by primary key.

Example:

```txt
Find the item where id == item_id
```

### `select()`

```python
select(ItemModel)
```

Builds a database query.

Current use:

```txt
Select all items from the items table
```

Future use:

```python
select(ItemModel).where(ItemModel.category == "jacket")
```

This would select only items where the category is `"jacket"`.

### `db.scalars()`

```python
db.scalars(statement)
```

Executes a SELECT statement and returns the model objects from the result.

Full pattern:

```python
list(db.scalars(select(ItemModel)).all())
```

Meaning:

```txt
Build query
Run query
Get all ItemModel objects
Convert result into a Python list
```

### `db.add()`

```python
db.add(item)
```

Stages a new object for insertion into the database.

It does not permanently save until `db.commit()` is called.

### Field Assignment

Example:

```python
item.name = item_data.name
item.category = item_data.category
item.color = item_data.color
item.size = item_data.size
```

This changes the values on an existing database object.

SQLAlchemy tracks those changes.

When `db.commit()` is called, the updated values are saved to the database.

### `db.delete()`

```python
db.delete(item)
```

Stages an already-loaded object for deletion.

Typical flow:

```txt
Find item with db.get()
If item exists, pass it to db.delete()
Call db.commit()
```

### `db.commit()`

```python
db.commit()
```

Permanently saves pending changes to the database.

Pending changes can include:

```txt
new item inserted
existing item updated
item deleted
```

### `db.refresh()`

```python
db.refresh(item)
```

Reloads the Python object from the database.

This is useful after creating a new item because the database generates values like:

```txt
id
```

After `db.refresh(item)`, Python has the latest version of that object.

---

## Current Understanding Summary

Suot API currently uses a layered backend structure:

```txt
Router
  ↓
Service
  ↓
SQLAlchemy Session
  ↓
SQLite database
```

The router handles HTTP concerns.

The service handles item logic.

The SQLAlchemy model defines the database table.

The database session handles communication with SQLite.

Pydantic schemas define the shape of incoming and outgoing API data.

The project has moved from temporary in-memory storage to persistent database-backed storage.