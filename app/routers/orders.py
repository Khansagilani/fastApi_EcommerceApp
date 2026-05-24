from app.models import (Cart, CartItem, Order, OrderItem, OrderRead,
                        OrderDetail, OrderItemDetail, Product, User,
                        CheckoutRequest, PromoCode)
from app.db import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from decimal import Decimal
from app.helpers.dependencies import get_current_user
from fastapi import Depends
from app.helpers import email as mailer

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderRead)
async def checkout(request: CheckoutRequest, session: SessionDep,
                   current_user: User = Depends(get_current_user)):
    cart = session.exec(select(Cart).where(Cart.user_id == current_user.id)).first()
    if not cart:
        raise HTTPException(status_code=400, detail="No cart found for this user")

    cart_items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    products = {}
    for item in cart_items:
        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} no longer exists")
        if product.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for '{product.product_name}'")
        products[item.product_id] = product

    # Apply promo code
    discount_pct = Decimal("0")
    if request.promo_code:
        promo = session.exec(
            select(PromoCode).where(
                PromoCode.code == request.promo_code.upper(),
                PromoCode.active == True
            )
        ).first()
        if not promo:
            raise HTTPException(status_code=400, detail="Invalid or expired promo code.")
        if promo.uses_remaining is not None and promo.uses_remaining <= 0:
            raise HTTPException(status_code=400, detail="This promo code has no uses remaining.")
        discount_pct = Decimal(promo.discount_percent)
        if promo.uses_remaining is not None:
            promo.uses_remaining -= 1
            session.add(promo)

    total = Decimal("0.00")
    order_items_to_create = []
    email_items = []

    for item in cart_items:
        product = products[item.product_id]
        line_price = product.price * item.quantity
        total += line_price
        order_items_to_create.append(OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price,
            size=item.size,
        ))
        email_items.append({
            "product_name": product.product_name,
            "size": item.size,
            "quantity": item.quantity,
            "subtotal": float(product.price * item.quantity),
        })
        product.quantity -= item.quantity
        session.add(product)

    if discount_pct:
        total = total * (1 - discount_pct / 100)

    order = Order(
        user_id=current_user.id,
        total_amount=total,
        status="pending",
        shipping_addr=request.shipping_addr,
    )
    session.add(order)
    session.flush()

    for oi in order_items_to_create:
        oi.order_id = order.id
        session.add(oi)

    for item in cart_items:
        session.delete(item)

    session.commit()
    session.refresh(order)

    mailer.order_confirmation_email(current_user.email, order.id, float(total), email_items)

    return order


@router.get("/", response_model=list[OrderRead])
async def get_user_orders(session: SessionDep, current_user: User = Depends(get_current_user)):
    return session.exec(
        select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    ).all()


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order_detail(order_id: int, session: SessionDep,
                           current_user: User = Depends(get_current_user)):
    order = session.exec(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    item_details = []
    for i in items:
        product = session.get(Product, i.product_id)
        item_details.append(OrderItemDetail(
            product_id=i.product_id,
            product_name=product.product_name if product else "Deleted product",
            product_img=product.img if product else None,
            size=i.size,
            quantity=i.quantity,
            unit_price=float(i.price),
            subtotal=float(i.price * i.quantity),
        ))

    return OrderDetail(
        id=order.id,
        status=order.status,
        total_amount=float(order.total_amount),
        shipping_addr=order.shipping_addr,
        created_at=order.created_at,
        items=item_details,
    )
