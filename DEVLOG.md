---

## Day 15 — Price Range Filters

### Goal

Extend `GET /items` so users can filter their inventory by item price.

Before this phase, users could filter by category, brand, and condition. After this phase, users can also filter by minimum price, maximum price, or a price range.

### Supported Filters

```http
GET /items?min_price=50
GET /items?max_price=150
GET /items?min_price=50&max_price=150
```

### Work Completed

- Added optional `min_price` and `max_price` query parameters.
- Updated the item router to receive price filter values.
- Updated `get_items()` to pass price filters into the SQLAlchemy query.
- Used `Decimal` for price query parameters.
- Added minimum price filtering.
- Added maximum price filtering.
- Added combined price range filtering.
- Added tests proving price filters still respect current-user ownership.

### Query Logic

```txt
min_price → ItemModel.price >= min_price
max_price → ItemModel.price <= max_price
```

Example:

```http
GET /items?min_price=50&max_price=150
```

means:

```txt
user_id == current_user.id
AND price >= 50
AND price <= 150
```

### Important Ownership Rule

Price filtering does not mean:

```txt
Find all items in the database between $50 and $150.
```

It means:

```txt
Find the current user's items between $50 and $150.
```

Ownership remains the first required condition.

### Phase Status

Phase 11B complete: `GET /items` now supports minimum price, maximum price, and price range filtering.

---

## Day 16 — Item Sorting

### Goal

Upgrade `GET /items` so users can control the order of returned inventory items.

Filtering decides which rows are returned. Sorting decides what order those rows come back in.

### Supported Sorting

```http
GET /items?sort_by=name&sort_order=asc
GET /items?sort_by=price&sort_order=desc
GET /items?sort_by=purchase_date&sort_order=desc
```

Supported `sort_by` values:

```txt
name
price
purchase_date
```

Supported `sort_order` values:

```txt
asc
desc
```

### Work Completed

- Added optional `sort_by` query parameter.
- Added `sort_order` query parameter with a default of `asc`.
- Used `Literal` types in the router to validate allowed sort values.
- Added a service-level sort column mapping.
- Added ascending and descending sort behavior.
- Added tests for sorting by price, name, and purchase date.
- Added tests proving invalid sort values return `422 Unprocessable Entity`.

### Sorting Flow

```txt
GET /items?sort_by=price&sort_order=desc
  ↓
Router validates sort_by and sort_order
  ↓
Service maps sort_by to a model column
  ↓
Service applies .order_by()
  ↓
Database returns sorted current-user rows
```

### Query Order

The correct order is:

```txt
ownership
  ↓
filters
  ↓
sorting
```

Sorting should happen after filtering because the API should sort the matching current-user rows, not unrelated database rows.

### Phase Status

Phase 11C complete: `GET /items` now supports sorting by name, price, and purchase date.

---

## Day 17 — Item Pagination

### Goal

Add pagination to `GET /items` so the API does not return an unlimited number of item records at once.

Pagination makes list endpoints safer and more frontend-friendly.

### Supported Pagination

```http
GET /items?limit=20&offset=0
GET /items?limit=20&offset=20
```

### Work Completed

- Added `limit` query parameter.
- Added `offset` query parameter.
- Added validation so `limit` must be between `1` and `100`.
- Added validation so `offset` must be `0` or greater.
- Updated `get_items()` to apply `.limit()` and `.offset()`.
- Added tests for limiting returned items.
- Added tests for skipping items with offset.
- Added tests for invalid pagination values.
- Added a test proving pagination still respects current-user ownership.

### Pagination Meaning

```txt
limit  → how many rows to return
offset → how many rows to skip
```

Example:

```txt
Sorted full result:
0: Alpha Tee
1: Beta Jacket
2: Gamma Shirt

limit=2&offset=1:
skip Alpha Tee
return Beta Jacket and Gamma Shirt
```

### Query Order

Pagination should happen last:

```txt
ownership
  ↓
filters
  ↓
sorting
  ↓
pagination
```

This order matters because the API should paginate the final matching result set, not the entire database.

### Phase Status

Phase 11D complete: `GET /items` now supports validated offset-based pagination.

---

## Day 18 — Pagination Metadata and Analytics Regression Fix

### Goal

Make `GET /items` more useful for frontend development by returning pagination metadata instead of a raw item list.

Before this phase, `GET /items` returned:

```json
[
  {
    "id": 1,
    "name": "Alpha Tee"
  }
]
```

After this phase, `GET /items` returns:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Alpha Tee"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

### Work Completed

- Added an `ItemPage` response schema.
- Updated `GET /items` to return an object with item results and metadata.
- Added `total`, `limit`, `offset`, and `has_more`.
- Added a `count_items()` service function.
- Added shared filter-building logic so item listing and item counting use the same ownership and filters.
- Updated list endpoint tests to read from `response.json()["items"]`.
- Added tests for pagination metadata.
- Added tests for both `has_more = true` and `has_more = false`.
- Fixed a potential analytics bug caused by reusing paginated item queries.
- Added a regression test proving closet analytics include more than the default page size.

### Pagination Metadata

```txt
items    → current page of item records
total    → total matching rows before pagination
limit    → requested page size
offset   → number of skipped rows
has_more → whether another page exists
```

### `has_more` Logic

```python
has_more = offset + len(items) < total
```

Example with another page:

```txt
total = 2
offset = 0
len(items) = 1

0 + 1 < 2
has_more = true
```

Example on the last page:

```txt
total = 2
offset = 1
len(items) = 1

1 + 1 < 2
has_more = false
```

### Why `count_items()` Was Needed

The list endpoint now needs two related operations:

```txt
get_items()
  → returns the current page

count_items()
  → returns the total number of matching rows before pagination
```

Both operations must use the same ownership and filter conditions.

The count query should not use sorting, limit, or offset.

### Important Real-World Bug Fixed

After pagination, `get_items()` only returns one page of results by default:

```txt
limit=20
offset=0
```

That means analytics should not call:

```python
items = get_items(db, user_id)
```

because that would only analyze the first page of items.

Wrong behavior for a user with 25 items:

```json
{
  "total_items": 20,
  "total_closet_value": "20.00"
}
```

Correct behavior:

```json
{
  "total_items": 25,
  "total_closet_value": "25.00"
}
```

The fix was to make closet analytics query the full current-user item set instead of reusing the paginated list function.

### Core Lesson

A function that returns a page should not be reused when the caller needs the full dataset.

Different parts of the app need different query semantics:

```txt
Inventory page
  → one paginated page

Analytics dashboard
  → full current-user item set

Export
  → all matching rows

Recommendations
  → full closet or a specifically chosen subset
```

### Phase Status

Phase 11E complete: `GET /items` now returns pagination metadata, and closet analytics are protected from pagination-related undercounting.

---

## Current Checkpoint

Suot now includes:

```txt
FastAPI foundation
database-backed CRUD
PostgreSQL and Docker
Alembic migrations
automated tests
user registration and password hashing
JWT login and protected routes
user-owned inventory
cross-user authorization isolation
richer item fields
closet analytics
basic item filtering
price range filtering
sorting
pagination
pagination metadata
analytics protected from pagination bugs
```

The current product-grade item list endpoint supports:

```http
GET /items?category=Shirt&brand=UNIQLO&min_price=50&max_price=150&sort_by=price&sort_order=asc&limit=20&offset=0
```

The query behavior follows this order:

```txt
ownership
  ↓
filters
  ↓
sorting
  ↓
pagination
```

The response shape is:

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

### Next Planned Project Milestone

```txt
Phase 12 — Frontend MVP
```

Goal:

```txt
Log in
  ↓
view your own closet items
  ↓
add new items
  ↓
filter, sort, and paginate inventory
  ↓
view basic closet analytics
```