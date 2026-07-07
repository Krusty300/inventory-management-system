from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List, Tuple
from app.models.item import Item
from app.api.v1.schemas.item import ItemCreate, ItemUpdate

class ItemService:
    
    @staticmethod
    def create_item(db: Session, item_data: ItemCreate) -> Item:
        """Create a new inventory item"""
        db_item = Item(**item_data.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def get_item(db: Session, item_id: str) -> Optional[Item]:
        """Get an item by ID"""
        return db.query(Item).filter(Item.id == item_id).first()
    
    @staticmethod
    def get_item_by_sku(db: Session, sku: str) -> Optional[Item]:
        """Get an item by SKU"""
        return db.query(Item).filter(Item.sku == sku).first()
    
    @staticmethod
    def get_items(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        low_stock: bool = False
    ) -> Tuple[List[Item], int]:
        """Get items with filtering and pagination"""
        query = db.query(Item)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Item.name.ilike(f"%{search}%"),
                    Item.sku.ilike(f"%{search}%"),
                    Item.description.ilike(f"%{search}%")
                )
            )
        
        if category:
            query = query.filter(Item.category == category)
        
        if low_stock:
            query = query.filter(Item.quantity <= Item.reorder_level)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        items = query.offset(skip).limit(limit).all()
        
        return items, total
    
    @staticmethod
    def update_item(db: Session, item_id: str, item_data: ItemUpdate) -> Optional[Item]:
        """Update an item"""
        db_item = ItemService.get_item(db, item_id)
        if not db_item:
            return None
        
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def delete_item(db: Session, item_id: str) -> bool:
        """Delete an item"""
        db_item = ItemService.get_item(db, item_id)
        if not db_item:
            return False
        
        db.delete(db_item)
        db.commit()
        return True
    
    @staticmethod
    def update_stock(db: Session, item_id: str, quantity_change: int) -> Optional[Item]:
        """Update stock quantity (positive for restock, negative for sale)"""
        db_item = ItemService.get_item(db, item_id)
        if not db_item:
            return None
        
        new_quantity = db_item.quantity + quantity_change
        if new_quantity < 0:
            raise ValueError("Insufficient stock")
        
        db_item.quantity = new_quantity
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def get_low_stock_items(db: Session) -> List[Item]:
        """Get all items with low stock"""
        return db.query(Item).filter(Item.quantity <= Item.reorder_level).all()