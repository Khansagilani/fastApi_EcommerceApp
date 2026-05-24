from app.models import PromoCode
from app.db import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select

router = APIRouter(prefix="/promo", tags=["promo"])


@router.get("/validate")
async def validate_promo(code: str, session: SessionDep):
    promo = session.exec(
        select(PromoCode).where(
            PromoCode.code == code.upper(),
            PromoCode.active == True
        )
    ).first()
    if not promo:
        raise HTTPException(status_code=400, detail="Invalid or expired promo code")
    if promo.uses_remaining is not None and promo.uses_remaining <= 0:
        raise HTTPException(status_code=400, detail="This promo code has no uses remaining")
    return {"code": promo.code, "discount_percent": promo.discount_percent}
