from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.jwt import get_current_user
from app.cart.models import Cart
from app.orders.models import Order, OrderItem, OrderStatus
from datetime import datetime

router = APIRouter()

@router.post("")
def dummy_checkout(db: Session = Depends(get_db), user=Depends(get_current_user)):
    # fetch cart items for the user
    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total amount
    total_amount = 0.0
    for item in cart_items:
        total_amount += item.quantity * get_product_price(db, item.product_id)

    # Create order
    order = Order(
        user_id=user.id,
        total_amount=total_amount,
        status=OrderStatus.paid,
        created_at=datetime.utcnow()
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=get_product_price(db, item.product_id)
        )
        db.add(order_item)

    # Clear the cart
    db.query(Cart).filter(Cart.user_id == user.id).delete()

    db.commit()

    return {"message": "Checkout successful", "order_id": order.id}


# Utility function to get product price
def get_product_price(db: Session, product_id: int) -> float:
    from app.products.models import Product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product ID {product_id} not found")
    return product.price
