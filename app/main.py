from fastapi import FastAPI

# from app.database import Base, engine
from app.models import item  # noqa: F401
from app.routers import health, items

# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Suot API")

app.include_router(health.router)
app.include_router(items.router)