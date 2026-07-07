from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services.item_service import ItemService
from app.api.v1.schemas.item import (
    ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
)

router = APIRouter()

@router.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new inventory item"""
    # Check if SKU already exists
    existing = ItemService.get_item_by_sku(db, item.sku)
    if existing:
        raise HTTPException(400, f"Item with SKU '{item.sku}' already exists")
    
    return ItemService.create_item(db, item)

@router.get("/items", response_model=ItemListResponse)
def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    category: Optional[str] = None,
    low_stock: bool = False,
    db: Session = Depends(get_db)
):
    """Get all items with optional filtering"""
    items, total = ItemService.get_items(db, skip, limit, search, category, low_stock)
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "per_page": limit
    }

@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: str, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    item = ItemService.get_item(db, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item

@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: str, item: ItemUpdate, db: Session = Depends(get_db)):
    """Update an item"""
    updated = ItemService.update_item(db, item_id, item)
    if not updated:
        raise HTTPException(404, "Item not found")
    return updated

@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: str, db: Session = Depends(get_db)):
    """Delete an item"""
    deleted = ItemService.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(404, "Item not found")

@router.patch("/items/{item_id}/stock", response_model=ItemResponse)
def update_stock(
    item_id: str,
    quantity_change: int = Query(..., description="Positive for restock, negative for sale"),
    db: Session = Depends(get_db)
):
    """Update stock quantity"""
    try:
        updated = ItemService.update_stock(db, item_id, quantity_change)
        if not updated:
            raise HTTPException(404, "Item not found")
        return updated
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/reports/low-stock", response_model=list[ItemResponse])
def get_low_stock_items(db: Session = Depends(get_db)):
    """Get all items with low stock"""
    return ItemService.get_low_stock_items(db)