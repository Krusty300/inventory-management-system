"""
Order Service for Inventory Management System
============================================
Handles business logic for order operations including:
- Creating orders with automatic inventory updates
- Order status management
- Order retrieval and filtering
- Order statistics calculation
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
import uuid

from app.models.order import Order, OrderItem, OrderStatus, OrderType
from app.models.item import Item
from app.services.item_service import ItemService
from app.api.v1.schemas.order import OrderCreate, OrderUpdate

class OrderService:
    """Service class for order operations"""
    
    @staticmethod
    def generate_order_number() -> str:
        """Generate a unique order number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"
    
    @staticmethod
    def create_order(db: Session, order_data: OrderCreate) -> Order:
        """
        Create a new order with automatic inventory updates.
        
        Args:
            db: Database session
            order_data: Order creation data
            
        Returns:
            Order: The created order
            
        Raises:
            ValueError: If insufficient stock for sale order
        """
        # Calculate subtotal
        subtotal = sum(
            item.quantity * item.unit_price 
            for item in order_data.items
        )
        
        # Calculate total
        total = subtotal + order_data.tax - order_data.discount
        
        # Create order
        db_order = Order(
            order_number=OrderService.generate_order_number(),
            order_type=order_data.order_type,
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            customer_phone=order_data.customer_phone,
            shipping_address=order_data.shipping_address,
            subtotal=subtotal,
            tax=order_data.tax,
            discount=order_data.discount,
            total=total,
            status=OrderStatus.PENDING
        )
        
        db.add(db_order)
        db.flush()  # Get the order ID
        
        # Process order items
        for item_data in order_data.items:
            # Get the inventory item
            db_item = ItemService.get_item(db, item_data.item_id)
            if not db_item:
                raise ValueError(f"Item with ID {item_data.item_id} not found")
            
            # For sale orders, check stock availability
            if order_data.order_type == OrderType.SALE:
                if db_item.quantity < item_data.quantity:
                    raise ValueError(
                        f"Insufficient stock for {db_item.name}. "
                        f"Available: {db_item.quantity}, Requested: {item_data.quantity}"
                    )
                
                # Update inventory for sale
                db_item.quantity -= item_data.quantity
            elif order_data.order_type == OrderType.PURCHASE:
                # Update inventory for purchase
                db_item.quantity += item_data.quantity
            elif order_data.order_type == OrderType.RETURN:
                # Update inventory for return
                db_item.quantity += item_data.quantity
            
            # Create order item
            order_item = OrderItem(
                order_id=db_order.id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_data.quantity * item_data.unit_price,
                notes=item_data.notes
            )
            db.add(order_item)
        
        # Commit transaction
        db.commit()
        db.refresh(db_order)
        
        return db_order
    
    @staticmethod
    def get_order(db: Session, order_id: str) -> Optional[Order]:
        """Get an order by ID"""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
        """Get an order by order number"""
        return db.query(Order).filter(Order.order_number == order_number).first()
    
    @staticmethod
    def get_orders(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_type: Optional[OrderType] = None,
        status: Optional[OrderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Order], int]:
        """
        Get orders with filtering and pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            order_type: Filter by order type
            status: Filter by order status
            start_date: Filter by start date
            end_date: Filter by end date
            search: Search in order number or customer name
            
        Returns:
            Tuple of (orders list, total count)
        """
        query = db.query(Order)
        
        # Apply filters
        if order_type:
            query = query.filter(Order.order_type == order_type)
        
        if status:
            query = query.filter(Order.status == status)
        
        if start_date:
            query = query.filter(Order.order_date >= start_date)
        
        if end_date:
            query = query.filter(Order.order_date <= end_date)
        
        if search:
            query = query.filter(
                or_(
                    Order.order_number.ilike(f"%{search}%"),
                    Order.customer_name.ilike(f"%{search}%"),
                    Order.customer_email.ilike(f"%{search}%")
                )
            )
        
        # Order by most recent first
        query = query.order_by(Order.order_date.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        orders = query.offset(skip).limit(limit).all()
        
        return orders, total
    
    @staticmethod
    def update_order_status(db: Session, order_id: str, new_status: OrderStatus) -> Optional[Order]:
        """Update order status"""
        order = OrderService.get_order(db, order_id)
        if not order:
            return None
        
        # For cancellation, restore inventory
        if new_status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
            # Restore inventory for cancelled orders
            for item in order.items:
                db_item = ItemService.get_item(db, item.item_id)
                if db_item:
                    if order.order_type == OrderType.SALE:
                        # Restore stock for cancelled sale
                        db_item.quantity += item.quantity
                    elif order.order_type in [OrderType.PURCHASE, OrderType.RETURN]:
                        # Remove stock for cancelled purchase/return
                        db_item.quantity -= item.quantity
        
        order.status = new_status
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_order_statistics(db: Session) -> dict:
        """
        Get order statistics.
        
        Returns:
            dict: Order statistics including total sales, purchases, and counts
        """
        # Total orders by status
        status_counts = db.query(
            Order.status,
            func.count(Order.id).label('count')
        ).group_by(Order.status).all()
        
        # Total sales amount
        total_sales = db.query(
            func.sum(Order.total)
        ).filter(
            Order.order_type == OrderType.SALE,
            Order.status == OrderStatus.COMPLETED
        ).scalar() or 0.0
        
        # Total purchases amount
        total_purchases = db.query(
            func.sum(Order.total)
        ).filter(
            Order.order_type == OrderType.PURCHASE,
            Order.status == OrderStatus.COMPLETED
        ).scalar() or 0.0
        
        # Total profit (sales - purchases)
        total_profit = total_sales - total_purchases
        
        # Count orders by status
        pending = next((s.count for s in status_counts if s.status == OrderStatus.PENDING), 0)
        completed = next((s.count for s in status_counts if s.status == OrderStatus.COMPLETED), 0)
        cancelled = next((s.count for s in status_counts if s.status == OrderStatus.CANCELLED), 0)
        
        return {
            "total_orders": sum(s.count for s in status_counts),
            "total_sales": total_sales,
            "total_purchases": total_purchases,
            "total_profit": total_profit,
            "pending_orders": pending,
            "completed_orders": completed,
            "cancelled_orders": cancelled
        }
    
    @staticmethod
    def get_recent_orders(db: Session, limit: int = 10) -> List[Order]:
        """Get recent orders"""
        return db.query(Order).order_by(Order.order_date.desc()).limit(limit).all()