from app.models import Cart, CartItem, Order, OrderItem, OrderRead, Product, User
from app.db import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from decimal import Decimal
from dependencies import get_current_user
from fastapi import Depends

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderRead)
async def checkout(shipping_addr: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    """
    Convert the user's cart into an order.
    - Validates stock for every item
    - Snapshots each product's current price into order_items
    - Decrements stock
    - Clears the cart
    """
    cart = session.exec(select(Cart).where(
        Cart.user_id == current_user.id)).first()
    if not cart:
        raise HTTPException(
            status_code=400, detail="No cart found for this user")

    cart_items = session.exec(
        select(CartItem).where(CartItem.cart_id == cart.id)
    ).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Validate stock AND store products in dictionary
    products = {}
    for item in cart_items:
        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(
                status_code=400,
                detail=f"Product {item.product_id} no longer exists"
            )
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for '{product.product_name}'"
            )
        products[item.product_id] = product  # store here, reuse below

    # Build the order
    total = Decimal("0.00")
    order_items_to_create = []

    for item in cart_items:
        product = products[item.product_id]  # reuse from dictionary, no DB hit
        line_price = product.price * item.quantity
        total += line_price
        order_items_to_create.append(
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price=product.price,  # snapshot
            )
        )
        product.quantity -= item.quantity
        session.add(product)

    order = Order(
        user_id=current_user.id,
        total_amount=total,
        status="pending",
        shipping_addr=shipping_addr,
    )
    session.add(order)
    session.flush()  # get order.id before adding items

    for oi in order_items_to_create:
        oi.order_id = order.id
        session.add(oi)

    # Clear the cart
    for item in cart_items:
        session.delete(item)

    session.commit()
    session.refresh(order)
    return order


@router.get("/", response_model=list[OrderRead])
async def get_user_orders(session: SessionDep,  current_user: User = Depends(get_current_user)):
    """Get all orders for a user, newest first."""
    return session.exec(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    ).all()
