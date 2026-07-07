"""
Order Models for Inventory Management System
============================================
Defines the database models for orders and order items.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid
import enum

class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class OrderType(str, enum.Enum):
    """Order type enumeration"""
    SALE = "sale"           # Selling items (outgoing)
    PURCHASE = "purchase"   # Buying items (incoming)
    RETURN = "return"       # Returned items

class Order(Base):
    """
    Order model representing a sales or purchase order.
    """
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    order_type = Column(Enum(OrderType), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # Customer/Supplier information
    customer_name = Column(String(200), nullable=True)
    customer_email = Column(String(100), nullable=True)
    customer_phone = Column(String(20), nullable=True)
    shipping_address = Column(Text, nullable=True)
    
    # Order totals
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Timestamps
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    """
    Order item model representing individual items within an order.
    """
    __tablename__ = "order_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("items.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Optional fields
    notes = Column(Text, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    item = relationship("Item")