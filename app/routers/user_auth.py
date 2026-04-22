from jose import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.models import User, BlacklistedToken
from app.db import SessionDep
from app.helpers.hashing import verify_password
from dotenv import load_dotenv, find_dotenv
import os
from fastapi import Depends
from app.helpers.dependencies import oauth2_scheme

load_dotenv(find_dotenv())

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

router = APIRouter(prefix="/api/auth", tags=["user auth"])


def create_user_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), session: SessionDep = None):
    user = session.exec(select(User).where(
        User.email == form.username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_user_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    user_token: str = Depends(oauth2_scheme),  # ← grab token from header
    session: SessionDep = None
):
    blacklisted = BlacklistedToken(token=user_token)
    session.add(blacklisted)
    session.commit()
    return {"message": "You have been logged out"}
