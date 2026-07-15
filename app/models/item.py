# item.py

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    color: Mapped[str] = mapped_column(String(100))
    size: Mapped[str] = mapped_column(String(50))