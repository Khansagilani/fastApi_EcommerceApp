from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.models import User, UserCreate, UserRead
from app.db import SessionDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, session: SessionDep):
    existing = session.exec(select(User).where(
        User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
