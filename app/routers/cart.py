from app.models import Cart, CartItem, CartItemCreate, CartItemUpdate, Product, User
from app.db import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from datetime import datetime, timezone
from app.helpers.dependencies import get_current_user
from fastapi import Depends

router = APIRouter(prefix="/cart", tags=["cart"])


def get_or_create_cart(user_id: int, session: SessionDep) -> Cart:
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart


@router.get("/")
async def get_cart(session: SessionDep, current_user: User = Depends(get_current_user)):
    cart = get_or_create_cart(current_user.id, session)
    items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()

    result = []
    for item in items:
        product = session.get(Product, item.product_id)
        result.append({
            "cart_item_id": item.id,
            "product_id": item.product_id,
            "product_name": product.product_name if product else None,
            "product_price": float(product.price) if product else None,
            "product_img": product.img if product else None,
            "quantity": item.quantity,
            "size": item.size,
            "subtotal": float(product.price * item.quantity) if product else None,
        })

    return {
        "cart_id": cart.id,
        "user_id": current_user.id,
        "items": result,
        "total": sum(i["subtotal"] for i in result if i["subtotal"]),
    }


@router.post("/items")
async def add_to_cart(
    item: CartItemCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    product = session.get(Product, item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.quantity < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    cart = get_or_create_cart(current_user.id, session)

    # Same product + same size = increment quantity; different size = new line
    existing = session.exec(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item.product_id,
            CartItem.size == item.size,
        )
    ).first()

    if existing:
        existing.quantity += item.quantity
        session.add(existing)
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity,
            size=item.size,
        )
        session.add(new_item)

    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)
    session.commit()

    total_count = sum(
        i.quantity for i in session.exec(
            select(CartItem).where(CartItem.cart_id == cart.id)
        ).all()
    )
    return {"message": "Item added to cart", "count": total_count}


@router.patch("/items/{cart_item_id}")
async def update_cart_item(
    cart_item_id: int,
    update: CartItemUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    cart = get_or_create_cart(current_user.id, session)
    item = session.exec(
        select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id,
        )
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = session.get(Product, item.product_id)
    if product and product.quantity < update.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    item.quantity = update.quantity
    cart.updated_at = datetime.now(timezone.utc)
    session.add(item)
    session.add(cart)
    session.commit()
    return {"message": "Cart item updated"}


@router.delete("/items/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    cart = get_or_create_cart(current_user.id, session)
    item = session.exec(
        select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id,
        )
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    session.delete(item)
    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)
    session.commit()
    return {"message": "Item removed from cart"}


@router.delete("/clear")
async def clear_cart(session: SessionDep, current_user: User = Depends(get_current_user)):
    cart = get_or_create_cart(current_user.id, session)
    items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()
    for item in items:
        session.delete(item)
    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)
    session.commit()
    return {"message": "Cart cleared"}


@router.get("/count")
async def get_cart_count(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    cart = get_or_create_cart(current_user.id, session)
    items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()
    return {"count": sum(item.quantity for item in items)}
