from fastapi import FastAPI

# from app.database import Base, engine
from app.models import item  # noqa: F401
from app.routers import health, items, auth
from fastapi.middleware.cors import CORSMiddleware

# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Suot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(items.router)
app.include_router(auth.router)
