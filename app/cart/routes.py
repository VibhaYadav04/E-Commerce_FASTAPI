from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.cart import models, schemas
from app.core.database import get_db
from app.utils.jwt import get_current_user
from typing import List

router = APIRouter()

# Add to Cart
@router.post("", response_model=schemas.CartOut)
def add_to_cart(
    item: schemas.CartAdd,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    existing = db.query(models.Cart).filter_by(user_id=user.id, product_id=item.product_id).first()
    if existing:
        existing.quantity += item.quantity
    else:
        existing = models.Cart(user_id=user.id, product_id=item.product_id, quantity=item.quantity)
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return existing

# View Cart
@router.get("", response_model=List[schemas.CartOut])
def view_cart(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Cart).filter_by(user_id=user.id).all()

# Remove from Cart
@router.delete("/{product_id}")
def remove_from_cart(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    item = db.query(models.Cart).filter_by(user_id=user.id, product_id=product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}

# Update Quantity
@router.put("/{product_id}", response_model=schemas.CartOut)
def update_cart_quantity(
    product_id: int,
    data: schemas.CartUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    item = db.query(models.Cart).filter_by(user_id=user.id, product_id=product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    return item
