from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import UserModel
from app.schemas.user import UserCreate
from app.security import hash_password

def normalize_email(email: str) -> str:
    return email.strip().lower()

def normalize_username(username: str) -> str:
    return username.strip().lower()

def get_user_by_email(db: Session, email: str) -> UserModel | None:
    statement = select(UserModel).where(
        UserModel.email == normalize_email(email)
    )
    return db.scalar(statement)

def get_user_by_username(db: Session, username: str) -> UserModel | None:
    statement = select(UserModel).where(
        UserModel.username == normalize_username(username)
    )
    return db.scalar(statement)

def create_user(db: Session, user_data: UserCreate) -> UserModel:
    user = UserModel(
        email=normalize_email(str(user_data.email)),
        username=normalize_username(user_data.username),
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user