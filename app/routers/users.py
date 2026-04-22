from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.models import User, UserCreate, UserRead
from app.db import SessionDep
from app.helpers.hashing import hash_password
from app.helpers.dependencies import get_current_user
from fastapi import Depends


router = APIRouter(
    prefix="/users", tags=["Users"])


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, session: SessionDep):
    existing = session.exec(select(User).where(
        User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User.model_validate(user)
    db_user.password = hash_password(user.password)  # save hashed pw in db
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
