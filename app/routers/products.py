from app.models import Product, ProductRead
from app.db import SessionDep
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, and_, or_, col

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRead])
async def get_products(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(default=None),
    style: Optional[str] = Query(default=None),
    pieces: Optional[str] = Query(default=None),
    fabric_type: Optional[str] = Query(default=None),
):
    query = select(Product)
    conditions = []
    if category:
        conditions.append(Product.category == category)
    if style:
        conditions.append(Product.style == style)
    if pieces:
        conditions.append(Product.pieces == pieces)
    if fabric_type:
        conditions.append(Product.fabric_type == fabric_type)
    if conditions:
        query = query.where(and_(*conditions))
    return session.exec(query.offset(skip).limit(limit)).all()


@router.get("/meta/filters")
async def get_filter_options(session: SessionDep):
    from sqlmodel import distinct
    categories = session.exec(select(distinct(Product.category))).all()
    styles = session.exec(select(distinct(Product.style))).all()
    pieces = session.exec(select(distinct(Product.pieces))).all()
    fabric_types = session.exec(select(distinct(Product.fabric_type))).all()
    return {
        "categories": [c for c in categories if c],
        "styles": [s for s in styles if s],
        "pieces": [p for p in pieces if p],
        "fabric_types": [f for f in fabric_types if f],
    }


@router.get("/search", response_model=list[ProductRead])
async def search_products(
    session: SessionDep,
    q: str = Query(default=""),
    limit: int = 12,
):
    if not q.strip():
        return []
    term = f"%{q.strip()}%"
    query = select(Product).where(
        or_(
            col(Product.product_name).ilike(term),
            col(Product.product_Description).ilike(term),
        )
    ).limit(limit)
    return session.exec(query).all()


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
