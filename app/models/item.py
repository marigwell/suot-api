# /models/item.py
from datetime import date
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
