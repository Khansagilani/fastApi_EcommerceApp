from app.models import Order, OrderItem, OrderRead, Product, StatusUpdate
from app.db import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.helpers.dependencies import get_current_admin
from fastapi import Depends

router = APIRouter(
    prefix="/api/admin/orders",
    tags=["admin orders"],
    dependencies=[Depends(get_current_admin)]
)


@router.get("/", response_model=list[OrderRead])
async def get_user_orders(session: SessionDep, skip: int = 0, limit: int = 20):
    """Get all orders from all users, newest firs"""
    return session.exec(
        select(Order).order_by(Order.created_at.desc()
                               .offset(skip).limit(limit)
                               )
    ).all()


@router.get("/{user_id}", response_model=list[OrderRead])
async def get_orders_by_user(user_id: int, session: SessionDep):
    """Get all orders for a user, newest first."""
    return session.exec(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
    ).all()


@router.get("/{user_id}/{order_id}")
async def get_order_detail(user_id: int, order_id: int, session: SessionDep):
    """Get a single order with full line item detail."""
    order = session.exec(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()

    item_detail = []
    for item in items:
        product = session.get(Product, item.product_id)
        item_detail.append({
            "product_id": item.product_id,
            "product_name": product.product_name if product else "Deleted product",
            "quantity": item.quantity,
            "unit_price": item.price,
            "subtotal": item.price * item.quantity,
        })

    return {
        "order_id": order.id,
        "status": order.status,
        "total_amount": order.total_amount,
        "shipping_addr": order.shipping_addr,
        "created_at": order.created_at,
        "items": item_detail,
    }


@router.patch("/{order_id}/status")
async def update_order_status(order_id: int, update: StatusUpdate, session: SessionDep):
    """Update order status (admin use). Valid: pending, paid, shipped, delivered, cancelled."""
    valid_statuses = {"pending", "paid", "shipped", "delivered", "cancelled"}
    if update not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = update
    session.add(order)
    session.commit()
    return {"message": f"Order status updated to '{update}'"}
