from app.models import Product, ProductRead
from app.db import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select
router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRead])
async def get_products(session: SessionDep, skip: int = 0, limit: int = 20):
    return session.exec(select(Product).offset(skip).limit(limit)).all()


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
