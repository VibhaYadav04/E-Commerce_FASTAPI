from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.jwt import get_current_user
from app.orders.models import Order, OrderItem
from app.products.models import Product
from app.orders import schemas
from typing import List

router = APIRouter()

@router.get("", response_model=List[schemas.OrderSummary])
def view_order_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == user.id).all()
    return [
        schemas.OrderSummary(
            order_id=order.id,
            created_at=order.created_at,
            total_amount=order.total_amount,
            status=order.status
        )
        for order in orders
    ]

@router.get("/{order_id}", response_model=schemas.OrderDetail)
def view_order_details(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    line_items = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        line_items.append(schemas.LineItem(
            product_name=product.name if product else "Unknown",
            quantity=item.quantity,
            price_at_purchase=item.price_at_purchase,
            subtotal=item.quantity * item.price_at_purchase
        ))

    return schemas.OrderDetail(
        order_id=order.id,
        created_at=order.created_at,
        total_amount=order.total_amount,
        status=order.status,
        line_items=line_items
    )
