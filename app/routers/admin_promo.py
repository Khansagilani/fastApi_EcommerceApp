from app.models import PromoCode, PromoCodeCreate, PromoCodeRead
from app.db import SessionDep
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.helpers.dependencies import get_current_admin
from datetime import datetime, timezone

router = APIRouter(
    prefix="/api/admin/promo",
    tags=["admin promo"],
    dependencies=[Depends(get_current_admin)]
)


@router.get("/", response_model=list[PromoCodeRead])
async def list_promo_codes(session: SessionDep):
    return session.exec(select(PromoCode).order_by(PromoCode.created_at.desc())).all()


@router.post("/", response_model=PromoCodeRead)
async def create_promo_code(promo_in: PromoCodeCreate, session: SessionDep):
    existing = session.exec(
        select(PromoCode).where(PromoCode.code == promo_in.code.upper())
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Promo code already exists")

    promo = PromoCode(
        code=promo_in.code.upper(),
        discount_percent=promo_in.discount_percent,
        uses_remaining=promo_in.uses_remaining,
        active=True,
        created_at=datetime.now(timezone.utc),
    )
    session.add(promo)
    session.commit()
    session.refresh(promo)
    return promo


@router.patch("/{promo_id}/toggle")
async def toggle_promo(promo_id: int, session: SessionDep):
    promo = session.get(PromoCode, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    promo.active = not promo.active
    session.add(promo)
    session.commit()
    return {"active": promo.active}


@router.delete("/{promo_id}")
async def delete_promo(promo_id: int, session: SessionDep):
    promo = session.get(PromoCode, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    session.delete(promo)
    session.commit()
    return {"message": "Promo code deleted"}
