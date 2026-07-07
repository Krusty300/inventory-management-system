"""
Order Routes for Inventory Management System
============================================
API endpoints for order management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.services.order_service import OrderService
from app.api.v1.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    OrderStatistics
)
from app.models.order import OrderStatus, OrderType

router = APIRouter()

@router.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    
    - For SALE orders: Automatically deducts from inventory
    - For PURCHASE orders: Automatically adds to inventory
    - For RETURN orders: Automatically adds to inventory
    """
    try:
        return OrderService.create_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders", response_model=OrderListResponse)
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    order_type: Optional[OrderType] = None,
    status: Optional[OrderStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all orders with optional filtering and pagination.
    """
    orders, total = OrderService.get_orders(
        db, skip, limit, order_type, status, start_date, end_date, search
    )
    
    return {
        "orders": orders,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "per_page": limit
    }

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = OrderService.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/orders/by-number/{order_number}", response_model=OrderResponse)
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    """Get a specific order by order number"""
    order = OrderService.get_order_by_number(db, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    status: OrderStatus,
    db: Session = Depends(get_db)
):
    """Update order status"""
    updated = OrderService.update_order_status(db, order_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated

@router.get("/stats/orders", response_model=OrderStatistics)
def get_order_statistics(db: Session = Depends(get_db)):
    """Get order statistics"""
    return OrderService.get_order_statistics(db)

@router.get("/recent/orders", response_model=list[OrderResponse])
def get_recent_orders(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get recent orders"""
    return OrderService.get_recent_orders(db, limit)