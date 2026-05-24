from app.models import Product, ProductCreate, ProductRead, ProductUpdate, User
from app.db import SessionDep
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends
from sqlmodel import select
from app.helpers.dependencies import get_current_admin
from typing import Annotated
from pathlib import Path
from uuid import uuid4
router = APIRouter(
    prefix="/api/admin/products",
    tags=["admin products"],
    dependencies=[Depends(get_current_admin)]
)


@router.post("/", response_model=ProductRead)
async def create_product(product_name: Annotated[str, Form()],
                         product_Description: Annotated[str, Form()],
                         price: Annotated[float, Form()],
                         quantity: Annotated[int, Form()],
                         img: UploadFile = File(...),
                         category: str = Form(None),
                         style: str = Form(None),
                         pieces: str = Form(None),
                         fabric_type: str = Form(None),
                         sizes: str = Form(None),
                         session: SessionDep = None):

    upload_dir = Path("../frontend2/public")
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(img.filename or "").suffix.lower()
    safe_filename = f"{uuid4().hex}{suffix}"
    file_location = upload_dir / safe_filename

    contents = await img.read()
    with open(file_location, "wb") as f:
        f.write(contents)

    new_product = Product(
        product_name=product_name,
        product_Description=product_Description,
        price=price,
        quantity=quantity,
        category=category,
        style=style,
        fabric_type=fabric_type,
        pieces=pieces,
        sizes=sizes or None,
        img=f"/static/public/{safe_filename}"
    )
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product


@router.patch("/{product_id}", response_model=ProductRead)
async def modify_product(product_id: int, session: SessionDep, update: ProductUpdate):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.get("/getallproducts", response_model=list[ProductRead])
async def get_products(session: SessionDep, skip: int = 0, limit: int = 20):
    return session.exec(select(Product).offset(skip).limit(limit)).all()


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/{product_id}/upload-image")
async def upload_product_image(product_id: int, img: UploadFile = File(...), session: SessionDep = None):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    upload_dir = Path("../frontend2/public")
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(img.filename or "").suffix.lower()
    safe_filename = f"{uuid4().hex}{suffix}"
    file_location = upload_dir / safe_filename

    contents = await img.read()
    with open(file_location, "wb") as f:
        f.write(contents)

    product.img = f"/static/public/{safe_filename}"
    session.add(product)
    session.commit()
    session.refresh(product)
    return {"img": product.img}


@router.delete("/{product_id}")
async def delete_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"message": "Product deleted successfully"}
