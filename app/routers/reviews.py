from app.models import Review, ReviewCreate, ReviewRead, Product, User
from app.db import SessionDep
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.helpers.dependencies import get_current_user
from datetime import datetime, timezone

router = APIRouter(tags=["reviews"])


@router.get("/products/{product_id}/reviews", response_model=list[ReviewRead])
async def get_reviews(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return session.exec(
        select(Review).where(Review.product_id == product_id).order_by(Review.created_at.desc())
    ).all()


@router.post("/products/{product_id}/reviews", response_model=ReviewRead)
async def create_review(product_id: int, review_in: ReviewCreate, session: SessionDep,
                        current_user: User = Depends(get_current_user)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = session.exec(
        select(Review).where(
            Review.user_id == current_user.id,
            Review.product_id == product_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")

    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=review_in.rating,
        content=review_in.content,
        reviewer_name=current_user.name,
        created_at=datetime.now(timezone.utc),
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    return review
