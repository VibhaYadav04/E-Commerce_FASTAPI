from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.products import schemas, models
from app.core.database import get_db
from app.utils.jwt import get_current_user, is_admin

router = APIRouter()

# ------------------ Admin-only CRUD ------------------

# Create a new product
@router.post("/admin/products", response_model=schemas.ProductOut)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    is_admin(user)
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Get all products with pagination
@router.get("/admin/products", response_model=List[schemas.ProductOut])
def get_all_products(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    is_admin(user)
    return db.query(models.Product).offset(skip).limit(limit).all()

# Get a single product by ID
@router.get("/admin/products/{product_id}", response_model=schemas.ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    is_admin(user)
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update a product by ID
@router.put("/admin/products/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    updated: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    is_admin(user)
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in updated.dict().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

# Delete a product by ID
@router.delete("/admin/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    is_admin(user)
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Deleted successfully"}

# ------------------ Public APIs ------------------

# Get Products for user based on category, min_price, max_price, sort_by, page, page_size
@router.get("/products", response_model=List[schemas.ProductOut])
def public_list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = Query(default="id"),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    if sort_by in ["price", "name", "id"]:
        query = query.order_by(getattr(models.Product, sort_by))
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()

# Search Products by keyword
@router.get("/products/search", response_model=List[schemas.ProductOut])
def search_products(keyword: str, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.name.ilike(f"%{keyword}%")).all()

# Get a single product detail
@router.get("/products/{product_id}", response_model=schemas.ProductOut)
def public_product_detail(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
