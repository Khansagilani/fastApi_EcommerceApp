from app.models import Cart, CartItem, CartItemCreate, CartItemUpdate, Product
from app.db import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from datetime import datetime

router = APIRouter(prefix="/cart", tags=["cart"])


def get_or_create_cart(user_id: int, session: SessionDep) -> Cart:
    """Get the user's cart, creating one if it doesn't exist yet."""
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart


@router.get("/{user_id}")
async def get_cart(user_id: int, session: SessionDep):
    """Get the user's cart with all items and product details."""
    cart = get_or_create_cart(user_id, session)
    items = session.exec(
        select(CartItem).where(CartItem.cart_id == cart.id)
    ).all()

    result = []
    for item in items:
        product = session.get(Product, item.product_id)
        result.append({
            "cart_item_id": item.id,
            "product_id": item.product_id,
            "product_name": product.product_name if product else None,
            "product_price": product.price if product else None,
            "quantity": item.quantity,
            "subtotal": product.price * item.quantity if product else None,
        })

    return {
        "cart_id": cart.id,
        "user_id": user_id,
        "items": result,
        "total": sum(i["subtotal"] for i in result if i["subtotal"]),
    }


@router.post("/{user_id}/items")
async def add_to_cart(user_id: int, item: CartItemCreate, session: SessionDep):
    """Add a product to the cart. If it already exists, increase quantity."""
    # Validate product exists and has stock
    product = session.get(Product, item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.quantity < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    cart = get_or_create_cart(user_id, session)

    # Check if this product is already in the cart
    existing = session.exec(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item.product_id
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
        )
        session.add(new_item)

    # Update cart timestamp
    cart.updated_at = datetime.utcnow()
    session.add(cart)
    session.commit()
    return {"message": "Item added to cart"}


@router.patch("/{user_id}/items/{cart_item_id}")
async def update_cart_item(
    user_id: int,
    cart_item_id: int,
    update: CartItemUpdate,
    session: SessionDep,
):
    """Update the quantity of a specific cart item."""
    cart = get_or_create_cart(user_id, session)
    item = session.exec(
        select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id
        )
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = session.get(Product, item.product_id)
    if product and product.quantity < update.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    item.quantity = update.quantity
    cart.updated_at = datetime.utcnow()
    session.add(item)
    session.add(cart)
    session.commit()
    return {"message": "Cart item updated"}


@router.delete("/{user_id}/items/{cart_item_id}")
async def remove_from_cart(user_id: int, cart_item_id: int, session: SessionDep):
    """Remove a single item from the cart."""
    cart = get_or_create_cart(user_id, session)
    item = session.exec(
        select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id
        )
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    session.delete(item)
    cart.updated_at = datetime.utcnow()
    session.add(cart)
    session.commit()
    return {"message": "Item removed from cart"}


@router.delete("/{user_id}/clear")
async def clear_cart(user_id: int, session: SessionDep):
    """Remove all items from the cart."""
    cart = get_or_create_cart(user_id, session)
    items = session.exec(select(CartItem).where(
        CartItem.cart_id == cart.id)).all()
    for item in items:
        session.delete(item)
    cart.updated_at = datetime.utcnow()
    session.add(cart)
    session.commit()
    return {"message": "Cart cleared"}
