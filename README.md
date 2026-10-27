# Suot API

Suot is a personal wardrobe app for keeping track of clothing and closet value. This repository contains its backend: account registration, login, and a private clothing collection for each user. The [Next.js frontend](https://github.com/marigwell/suot-web) lives in a separate repository.

This is a solo learning project for practicing backend development with Python, FastAPI, SQLAlchemy, and PostgreSQL.

## What it does

- Create an account, sign in, and manage your own clothing items.
- Filter items by category, brand, condition, or price; sort results and browse them in pages.
- View closet statistics, including total value and the most expensive item.

Wardrobe recommendations are planned but are not implemented yet.

## Start here

| I want to… | Read |
| --- | --- |
| Run the API locally | [Local setup](docs/API.md#running-locally) |
| Sign in and try requests | [Using the API](docs/API.md#using-the-api) |
| Understand how requests and ownership work | [Architecture and data flow](docs/ARCHITECTURE.md) |
| Run the tests and code checks | [Testing](docs/API.md#testing) |
| See what still needs work | [Current limitations](docs/API.md#current-limitations) |

Local setup uses Python 3.14 and uv, with PostgreSQL running in Docker. After setup, [Swagger UI](http://localhost:8000/docs) lets you try the endpoints in your browser.

For a quick project review, start with the architecture guide. It walks through creating an item, links to the code, and explains the main design choices and tradeoffs.

## Development notes

[DEVLOG.md](DEVLOG.md) records development history. [NOTES.md](NOTES.md) contains personal backend learning notes. These include earlier stages of the project; the guides above describe the current API.
