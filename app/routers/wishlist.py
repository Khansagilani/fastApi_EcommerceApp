from app.models import WishlistItem, Product, ProductRead, User
from app.db import SessionDep
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.helpers.dependencies import get_current_user
from datetime import datetime, timezone

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("/")
async def get_wishlist(session: SessionDep, current_user: User = Depends(get_current_user)):
    items = session.exec(
        select(WishlistItem).where(WishlistItem.user_id == current_user.id)
    ).all()

    result = []
    for item in items:
        product = session.get(Product, item.product_id)
        if product:
            result.append({
                "wishlist_id": item.id,
                "product_id": product.id,
                "product_name": product.product_name,
                "price": float(product.price),
                "img": product.img,
                "sizes": product.sizes,
                "quantity": product.quantity,
            })
    return result


@router.post("/{product_id}")
async def toggle_wishlist(product_id: int, session: SessionDep,
                          current_user: User = Depends(get_current_user)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = session.exec(
        select(WishlistItem).where(
            WishlistItem.user_id == current_user.id,
            WishlistItem.product_id == product_id
        )
    ).first()

    if existing:
        session.delete(existing)
        session.commit()
        return {"wishlisted": False}

    item = WishlistItem(
        user_id=current_user.id,
        product_id=product_id,
        created_at=datetime.now(timezone.utc),
    )
    session.add(item)
    session.commit()
    return {"wishlisted": True}


@router.get("/ids")
async def get_wishlist_ids(session: SessionDep, current_user: User = Depends(get_current_user)):
    items = session.exec(
        select(WishlistItem.product_id).where(WishlistItem.user_id == current_user.id)
    ).all()
    return {"ids": list(items)}


@router.delete("/{product_id}")
async def remove_from_wishlist(product_id: int, session: SessionDep,
                               current_user: User = Depends(get_current_user)):
    item = session.exec(
        select(WishlistItem).where(
            WishlistItem.user_id == current_user.id,
            WishlistItem.product_id == product_id
        )
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not in wishlist")
    session.delete(item)
    session.commit()
    return {"message": "Removed from wishlist"}
