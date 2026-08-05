from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, User, UserLogin, Token
from app.services.user_service import (
    create_user, 
    get_user_by_email, 
    get_user_by_username,
    authenticate_user
)
from app.security import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]

@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)

def register_user(user_data: UserCreate, db: DbSession) -> User:
    existing_email = get_user_by_email(db, str(user_data.email))

    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    existing_username = get_user_by_username(db, user_data.username)

    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    return create_user(db, user_data)

@router.post("/login", response_model=Token)
def login_user(user_data: UserLogin, db: DbSession):
    user = authenticate_user(
        db, 
        str(user_data.email), 
        user_data.password
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(subject=str(user.id))

    return {
        "access_token": access_token, 
        "token_type": "bearer"
        }