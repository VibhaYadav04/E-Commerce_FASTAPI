from pydantic import BaseModel
from typing import List
from datetime import datetime


class OrderSummary(BaseModel):
    order_id: int
    created_at: datetime
    total_amount: float
    status: str

    class Config:
        orm_mode = True


class LineItem(BaseModel):
    product_name: str
    quantity: int
    price_at_purchase: float
    subtotal: float


class OrderDetail(BaseModel):
    order_id: int
    created_at: datetime
    total_amount: float
    status: str
    line_items: List[LineItem]
