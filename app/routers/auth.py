"""
load ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY from .env
↓
/login endpoint receives username + password
↓
check if they match the env variables
↓
if yes → create a JWT token with expiry → return it
if no  → raise 401
"""
from jose import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
import os
from dotenv import load_dotenv
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8


router = APIRouter(prefix="/api/admin/auth", tags=["admin auth"])


def create_token():
    payload = {
        "sub": "admin",
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != ADMIN_USERNAME or form.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token()
    return {"access_token": token, "token_type": "bearer"}

"""
load_dotenv() reads your .env file and makes those variables available via 
os.getenv(). OAuth2PasswordRequestForm is a FastAPI built-in that
 automatically expects a username and password in the
 request body — you don't need to build that model yourself.
 create_token() builds the payload dictionary and signs it with your
 secret key using the HS256 algorithm.
"""
