"""
Order Schemas for Inventory Management System
=============================================
Defines Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus, OrderType

# ===== Order Item Schemas =====

class OrderItemBase(BaseModel):
    """Base schema for order items"""
    item_id: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    notes: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    """Schema for creating order items"""
    pass

class OrderItemResponse(OrderItemBase):
    """Schema for responding with order items"""
    id: str
    order_id: str
    total_price: float
    
    model_config = ConfigDict(from_attributes=True)

# ===== Order Schemas =====

class OrderBase(BaseModel):
    """Base schema for orders"""
    order_type: OrderType
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    shipping_address: Optional[str] = None
    tax: float = Field(default=0.0, ge=0)
    discount: float = Field(default=0.0, ge=0)

class OrderCreate(OrderBase):
    """Schema for creating orders"""
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    """Schema for updating orders"""
    status: Optional[OrderStatus] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    shipping_address: Optional[str] = None

class OrderResponse(OrderBase):
    """Schema for responding with orders"""
    id: str
    order_number: str
    status: OrderStatus
    subtotal: float
    tax: float
    discount: float
    total: float
    order_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class OrderListResponse(BaseModel):
    """Schema for paginated order list response"""
    orders: List[OrderResponse]
    total: int
    page: int
    per_page: int

# ===== Order Statistics Schemas =====

class OrderStatistics(BaseModel):
    """Schema for order statistics"""
    total_orders: int
    total_sales: float
    total_purchases: float
    total_profit: float
    pending_orders: int
    completed_orders: int
    cancelled_orders: int