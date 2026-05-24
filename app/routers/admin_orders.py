from app.models import Order, OrderItem, OrderRead, OrderWithCustomer, Product, StatusUpdate, User
from app.db import SessionDep
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.helpers.dependencies import get_current_admin
from fastapi import Depends
from app.helpers import email as mailer

router = APIRouter(
    prefix="/api/admin/orders",
    tags=["admin orders"],
    dependencies=[Depends(get_current_admin)]
)


@router.get("/", response_model=list[OrderWithCustomer])
async def get_all_orders(session: SessionDep, skip: int = 0, limit: int = 100):
    orders = session.exec(
        select(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit)
    ).all()

    result = []
    for order in orders:
        user = session.get(User, order.user_id)
        result.append(OrderWithCustomer(
            id=order.id,
            user_id=order.user_id,
            customer_name=user.name if user else None,
            customer_email=user.email if user else None,
            customer_phone=user.phone if user else None,
            total_amount=float(order.total_amount),
            status=order.status,
            shipping_addr=order.shipping_addr,
            created_at=order.created_at,
        ))
    return result


@router.get("/{order_id}")
async def get_order_detail(order_id: int, session: SessionDep):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    user = session.get(User, order.user_id)
    items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()

    item_detail = []
    for item in items:
        product = session.get(Product, item.product_id)
        item_detail.append({
            "product_id": item.product_id,
            "product_name": product.product_name if product else "Deleted product",
            "size": item.size,
            "quantity": item.quantity,
            "unit_price": float(item.price),
            "subtotal": float(item.price * item.quantity),
        })

    return {
        "order_id": order.id,
        "customer_name": user.name if user else None,
        "customer_email": user.email if user else None,
        "customer_phone": user.phone if user else None,
        "status": order.status,
        "total_amount": float(order.total_amount),
        "shipping_addr": order.shipping_addr,
        "created_at": order.created_at,
        "items": item_detail,
    }


@router.patch("/{order_id}/status")
async def update_order_status(order_id: int, update: StatusUpdate, session: SessionDep):
    valid_statuses = {"pending", "paid", "shipped", "delivered", "cancelled"}
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = update.status
    session.add(order)
    session.commit()

    user = session.get(User, order.user_id)
    if user:
        mailer.order_status_email(user.email, order.id, update.status)

    return {"message": f"Order status updated to '{update.status}'"}
