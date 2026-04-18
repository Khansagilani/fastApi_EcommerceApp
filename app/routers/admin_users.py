from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.models import User, UserCreate, UserRead
from app.db import SessionDep
from dependencies import get_current_admin
from fastapi import Depends

router = APIRouter(
    prefix="/api/admin/users",
    tags=["admin users"],
    dependencies=[Depends(get_current_admin)]
)


@router.get("/", response_model=list[UserRead])
async def get_all_users(session: SessionDep):
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
