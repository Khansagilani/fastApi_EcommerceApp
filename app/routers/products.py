from app.models import Product, ProductCreate, ProductRead
from app.db import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductRead)
async def create_product(product: ProductCreate, session: SessionDep):
    db_product = Product.model_validate(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.get("/", response_model=list[ProductRead])
async def get_products(session: SessionDep, skip: int = 0, limit: int = 20):
    return session.exec(select(Product).offset(skip).limit(limit)).all()


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}")
async def delete_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"message": "Product deleted successfully"}
