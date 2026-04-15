"""
read token from Authorization header
↓
decode it using SECRET_KEY
↓
if valid and not expired → do nothing, let request through
if invalid or expired   → raise 401
"""

from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/auth/login")


def require_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject != "admin":
            raise HTTPException(status_code=401, detail="Not authorized")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


"""
OAuth2PasswordBearer reads the token 
from the Authorization: Bearer <token> header automatically.
 jwt.decode() verifies the signature AND checks the expiry at
 the same time — if the token is expired or tampered with,
 it throws a JWTError which we catch and turn into a 401.
 We also check that sub equals "admin" so a random valid token
 from somewhere else wouldn't work.
"""
