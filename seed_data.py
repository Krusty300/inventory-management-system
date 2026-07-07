"""
Seed Data for Inventory Management System
=========================================
This script populates the database with comprehensive test data including:
- Inventory items with various categories and stock levels
- Customers with different profiles
- Orders (sales, purchases, returns) with different statuses
- Realistic order histories for testing analytics

Author: Your Name
Date: 2026
"""

import requests
import json
import random
from datetime import datetime, timedelta
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:8000/api/v1"
ITEMS_URL = f"{API_URL}/items"
ORDERS_URL = f"{API_URL}/orders"

# ============================================================================
# SAMPLE DATA
# ============================================================================

# Inventory Items
INVENTORY_ITEMS = [
    # Electronics
    {
        "name": "MacBook Pro 16",
        "sku": "MBP001",
        "description": "Apple MacBook Pro 16-inch with M2 Pro chip",
        "quantity": 15,
        "reorder_level": 5,
        "unit_price": 2499.99,
        "category": "Electronics"
    },
    {
        "name": "Dell XPS 15",
        "sku": "XPS001",
        "description": "Dell XPS 15 with Intel Core i7",
        "quantity": 20,
        "reorder_level": 5,
        "unit_price": 1899.99,
        "category": "Electronics"
    },
    {
        "name": "Logitech MX Master 3S",
        "sku": "MOU002",
        "description": "Logitech MX Master 3S Wireless Mouse",
        "quantity": 45,
        "reorder_level": 10,
        "unit_price": 99.99,
        "category": "Electronics"
    },
    {
        "name": "Mechanical Keyboard",
        "sku": "KEY001",
        "description": "Mechanical Gaming Keyboard with RGB",
        "quantity": 35,
        "reorder_level": 8,
        "unit_price": 79.99,
        "category": "Electronics"
    },
    {
        "name": "4K Monitor 32",
        "sku": "MON001",
        "description": "32-inch 4K UHD Monitor",
        "quantity": 12,
        "reorder_level": 3,
        "unit_price": 499.99,
        "category": "Electronics"
    },
    {
        "name": "External SSD 1TB",
        "sku": "SSD001",
        "description": "Portable 1TB External SSD",
        "quantity": 28,
        "reorder_level": 6,
        "unit_price": 149.99,
        "category": "Electronics"
    },
    {
        "name": "Wireless Charger",
        "sku": "CHR001",
        "description": "Fast Wireless Charging Pad",
        "quantity": 50,
        "reorder_level": 10,
        "unit_price": 39.99,
        "category": "Electronics"
    },
    {
        "name": "Smart Watch",
        "sku": "SWT001",
        "description": "Fitness Smart Watch with GPS",
        "quantity": 18,
        "reorder_level": 4,
        "unit_price": 299.99,
        "category": "Electronics"
    },
    
    # Furniture
    {
        "name": "Executive Desk",
        "sku": "DSK002",
        "description": "Executive Office Desk with Drawers",
        "quantity": 8,
        "reorder_level": 2,
        "unit_price": 599.99,
        "category": "Furniture"
    },
    {
        "name": "Ergonomic Chair Pro",
        "sku": "CHA002",
        "description": "Ergonomic Office Chair with Lumbar Support",
        "quantity": 12,
        "reorder_level": 3,
        "unit_price": 349.99,
        "category": "Furniture"
    },
    {
        "name": "Bookshelf 5-Tier",
        "sku": "BOK001",
        "description": "5-Tier Industrial Bookshelf",
        "quantity": 25,
        "reorder_level": 5,
        "unit_price": 129.99,
        "category": "Furniture"
    },
    {
        "name": "Filing Cabinet",
        "sku": "FIL001",
        "description": "2-Drawer Filing Cabinet",
        "quantity": 20,
        "reorder_level": 4,
        "unit_price": 89.99,
        "category": "Furniture"
    },
    
    # Stationery
    {
        "name": "Premium Notebook",
        "sku": "NOT002",
        "description": "Premium Leather Notebook",
        "quantity": 150,
        "reorder_level": 25,
        "unit_price": 14.99,
        "category": "Stationery"
    },
    {
        "name": "Pen Set 5-Pack",
        "sku": "PEN001",
        "description": "Premium Gel Pen Set",
        "quantity": 200,
        "reorder_level": 30,
        "unit_price": 9.99,
        "category": "Stationery"
    },
    {
        "name": "Sticky Notes 3x3",
        "sku": "STK001",
        "description": "Pack of Sticky Notes",
        "quantity": 300,
        "reorder_level": 40,
        "unit_price": 3.99,
        "category": "Stationery"
    },
    {
        "name": "Whiteboard Marker",
        "sku": "MRK001",
        "description": "Whiteboard Marker Set",
        "quantity": 100,
        "reorder_level": 20,
        "unit_price": 7.99,
        "category": "Stationery"
    },
    
    # Office Supplies
    {
        "name": "Paper A4 500 Sheets",
        "sku": "PAP001",
        "description": "500 Sheets A4 Printing Paper",
        "quantity": 120,
        "reorder_level": 20,
        "unit_price": 12.99,
        "category": "Office Supplies"
    },
    {
        "name": "Desk Organizer",
        "sku": "ORG001",
        "description": "Desktop Organizer with Drawers",
        "quantity": 30,
        "reorder_level": 6,
        "unit_price": 24.99,
        "category": "Office Supplies"
    },
    {
        "name": "Paper Shredder",
        "sku": "SHR001",
        "description": "Strip-Cut Paper Shredder",
        "quantity": 10,
        "reorder_level": 2,
        "unit_price": 79.99,
        "category": "Office Supplies"
    },
    {
        "name": "Laminator",
        "sku": "LAM001",
        "description": "A4 Laminator Machine",
        "quantity": 8,
        "reorder_level": 2,
        "unit_price": 59.99,
        "category": "Office Supplies"
    }
]

# Customers for orders
CUSTOMERS = [
    {"name": "John Smith", "email": "john.smith@company.com", "phone": "555-0101"},
    {"name": "Sarah Johnson", "email": "sarah.j@business.com", "phone": "555-0102"},
    {"name": "Michael Brown", "email": "m.brown@enterprise.com", "phone": "555-0103"},
    {"name": "Emily Davis", "email": "emily.d@startup.com", "phone": "555-0104"},
    {"name": "David Wilson", "email": "d.wilson@corporate.com", "phone": "555-0105"},
    {"name": "Lisa Anderson", "email": "lisa.a@tech.com", "phone": "555-0106"},
    {"name": "James Martinez", "email": "j.martinez@fintech.com", "phone": "555-0107"},
    {"name": "Maria Garcia", "email": "maria.g@retail.com", "phone": "555-0108"},
    {"name": "Robert Taylor", "email": "robert.t@logistics.com", "phone": "555-0109"},
    {"name": "Jennifer Lee", "email": "jennifer.l@ecommerce.com", "phone": "555-0110"}
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_request(method, url, data=None, retries=3):
    """Make a safe API request with retries"""
    for attempt in range(retries):
        try:
            if method == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, params=data, timeout=10)
            elif method == "GET":
                response = requests.get(url, timeout=10)
            else:
                return None
            
            if response.status_code in [200, 201]:
                return response.json() if response.text else True
            
            # If duplicate SKU, skip silently
            if response.status_code == 400 and "already exists" in response.text:
                return None
            
            print(f"⚠️ Error {response.status_code}: {response.text[:100]}")
            return None
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error (attempt {attempt + 1}/{retries})")
            if attempt < retries - 1:
                time.sleep(2)
        except Exception as e:
            print(f"❌ Error: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    
    return None

def get_items():
    """Fetch all items from API"""
    try:
        response = requests.get(f"{ITEMS_URL}?limit=1000", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
    except Exception as e:
        print(f"❌ Error fetching items: {e}")
    return []

def get_item_by_sku(sku):
    """Get item by SKU from API"""
    items = get_items()
    for item in items:
        if item.get('sku') == sku:
            return item
    return None

def create_order(order_data):
    """Create an order via API"""
    try:
        response = requests.post(ORDERS_URL, json=order_data, timeout=10)
        if response.status_code == 201:
            return response.json()
        else:
            print(f"⚠️ Order creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        return None

def generate_order_items(items, max_items=3):
    """Generate random order items from available inventory"""
    selected_items = random.sample(items, min(random.randint(1, max_items), len(items)))
    order_items = []
    
    for item in selected_items:
        quantity = random.randint(1, 5)
        # Ensure we don't exceed stock for sale orders
        if item.get('quantity', 0) >= quantity:
            order_items.append({
                "item_id": item['id'],
                "quantity": quantity,
                "unit_price": item['unit_price']
            })
    
    return order_items

# ============================================================================
# MAIN SEEDING FUNCTIONS
# ============================================================================

def seed_inventory():
    """Seed inventory items"""
    print("\n" + "=" * 60)
    print("📦 SEEDING INVENTORY ITEMS")
    print("=" * 60)
    
    existing_items = get_items()
    existing_skus = {item.get('sku') for item in existing_items}
    
    new_items = 0
    for item in INVENTORY_ITEMS:
        if item['sku'] in existing_skus:
            print(f"⏭️ Skipping existing item: {item['name']} (SKU: {item['sku']})")
            continue
        
        result = safe_request("POST", ITEMS_URL, item)
        if result:
            new_items += 1
            print(f"✅ Added: {item['name']} (SKU: {item['sku']}) - Qty: {item['quantity']}")
        else:
            print(f"❌ Failed to add: {item['name']}")
    
    print(f"\n📊 Added {new_items} new items to inventory")
    return get_items()

def seed_orders(items, num_orders=30):
    """Seed orders with various types and statuses"""
    print("\n" + "=" * 60)
    print("📋 SEEDING ORDERS")
    print("=" * 60)
    
    if not items:
        print("❌ No items available. Please seed inventory first.")
        return 0
    
    # Status distribution
    statuses = ['pending', 'completed', 'shipped', 'delivered', 'cancelled']
    status_weights = [0.15, 0.35, 0.20, 0.20, 0.10]  # Probabilities
    
    created_orders = 0
    
    for i in range(num_orders):
        # Select random customer
        customer = random.choice(CUSTOMERS)
        
        # Order type distribution
        order_types = ['sale', 'sale', 'sale', 'purchase', 'return']
        order_type = random.choice(order_types)
        
        # Generate order items
        order_items = generate_order_items(items, max_items=4)
        if not order_items:
            continue
        
        # Calculate subtotal and tax
        subtotal = sum(item['quantity'] * item['unit_price'] for item in order_items)
        tax_rate = random.uniform(0.08, 0.12)
        tax = subtotal * tax_rate
        discount = random.choice([0, subtotal * 0.05, subtotal * 0.10]) if random.random() > 0.6 else 0
        
        # Select status (with weights)
        status = random.choices(statuses, weights=status_weights)[0]
        
        # Generate date within last 90 days
        days_ago = random.randint(0, 90)
        order_date = datetime.now() - timedelta(days=days_ago)
        
        # Create order data
        order_data = {
            "order_type": order_type,
            "customer_name": customer['name'],
            "customer_email": customer['email'],
            "customer_phone": customer['phone'],
            "shipping_address": f"{random.randint(100, 999)} {random.choice(['Main St', 'Oak Ave', 'Pine Rd', 'Maple Dr', 'Cedar Ln'])}, {random.choice(['City', 'Town', 'Village'])}, {random.choice(['NY', 'CA', 'TX', 'FL', 'IL'])} {random.randint(10000, 99999)}",
            "tax": round(tax, 2),
            "discount": round(discount, 2),
            "items": [
                {
                    "item_id": item['item_id'],
                    "quantity": item['quantity'],
                    "unit_price": item['unit_price']
                }
                for item in order_items
            ]
        }
        
        # Create the order
        result = create_order(order_data)
        
        if result:
            created_orders += 1
            order_num = result.get('order_number', 'N/A')
            print(f"✅ Order {created_orders}: {order_num} - {order_type.upper()} - {status.upper()} - ${result.get('total', 0):.2f}")
            
            # Update status if not pending
            if status != 'pending':
                order_id = result.get('id')
                if order_id:
                    status_update = safe_request("PATCH", f"{ORDERS_URL}/{order_id}/status", {"status": status})
                    if status_update:
                        print(f"   ↳ Status updated to: {status}")
        else:
            print(f"❌ Failed to create order {i + 1}")
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.1)
    
    print(f"\n📊 Created {created_orders} orders")
    return created_orders

def seed_additional_sales():
    """Create some specific sales scenarios for testing"""
    print("\n" + "=" * 60)
    print("🔄 CREATING TEST SCENARIOS")
    print("=" * 60)
    
    items = get_items()
    if not items:
        print("❌ No items available")
        return
    
    # Scenario 1: Large bulk order
    print("\n📦 Scenario 1: Bulk Order")
    bulk_items = []
    for item in random.sample(items, min(3, len(items))):
        if item.get('quantity', 0) >= 10:
            bulk_items.append({
                "item_id": item['id'],
                "quantity": 10,
                "unit_price": item['unit_price']
            })
    
    if bulk_items:
        customer = random.choice(CUSTOMERS)
        order_data = {
            "order_type": "sale",
            "customer_name": f"{customer['name']} (Bulk)",
            "customer_email": customer['email'],
            "customer_phone": customer['phone'],
            "shipping_address": "123 Warehouse Blvd, Industrial Park, NY 10001",
            "tax": 50.00,
            "discount": 100.00,
            "items": bulk_items
        }
        result = create_order(order_data)
        if result:
            print(f"✅ Bulk order created: {result.get('order_number')}")
    
    # Scenario 2: Urgent order (shipped immediately)
    print("\n🚀 Scenario 2: Urgent Order (Shipped)")
    urgent_items = generate_order_items(items, max_items=2)
    if urgent_items:
        customer = random.choice(CUSTOMERS)
        order_data = {
            "order_type": "sale",
            "customer_name": f"URGENT - {customer['name']}",
            "customer_email": customer['email'],
            "customer_phone": customer['phone'],
            "shipping_address": "456 Express Lane, Speed City, CA 90210",
            "tax": 25.00,
            "discount": 0.00,
            "items": urgent_items
        }
        result = create_order(order_data)
        if result:
            order_id = result.get('id')
            if order_id:
                # Update to shipped status
                safe_request("PATCH", f"{ORDERS_URL}/{order_id}/status", {"status": "shipped"})
                print(f"✅ Urgent order created and shipped: {result.get('order_number')}")
    
    # Scenario 3: High-value return
    print("\n🔄 Scenario 3: Return Order")
    return_items = generate_order_items(items, max_items=2)
    if return_items:
        customer = random.choice(CUSTOMERS)
        order_data = {
            "order_type": "return",
            "customer_name": f"RETURN - {customer['name']}",
            "customer_email": customer['email'],
            "customer_phone": customer['phone'],
            "shipping_address": "789 Return Center, Refund City, TX 75001",
            "tax": 0.00,
            "discount": 0.00,
            "items": return_items
        }
        result = create_order(order_data)
        if result:
            print(f"✅ Return order created: {result.get('order_number')}")
    
    # Scenario 4: Purchase order (restocking)
    print("\n📦 Scenario 4: Purchase Order (Restocking)")
    purchase_items = generate_order_items(items, max_items=3)
    if purchase_items:
        customer = {"name": "Supplier Corp", "email": "supplier@distributor.com", "phone": "555-9999"}
        order_data = {
            "order_type": "purchase",
            "customer_name": customer['name'],
            "customer_email": customer['email'],
            "customer_phone": customer['phone'],
            "shipping_address": "123 Supplier Street, Distribution City, OH 44101",
            "tax": 0.00,
            "discount": 0.00,
            "items": purchase_items
        }
        result = create_order(order_data)
        if result:
            # Complete the purchase
            order_id = result.get('id')
            if order_id:
                safe_request("PATCH", f"{ORDERS_URL}/{order_id}/status", {"status": "completed"})
                print(f"✅ Purchase order created and completed: {result.get('order_number')}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main seeding function"""
    print("=" * 70)
    print("🌱 INVENTORY MANAGEMENT SYSTEM - SEED DATA GENERATOR")
    print("=" * 70)
    print("\nThis script will populate your database with:")
    print("  📦 20+ inventory items across categories")
    print("  📋 30+ orders with various statuses")
    print("  🧪 Test scenarios (bulk, urgent, returns, purchases)")
    print("  👥 10 sample customers")
    
    # Check if backend is running
    print("\n🔌 Checking API connection...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API not responding correctly")
            return
    except:
        print("❌ Cannot connect to API. Make sure the backend is running on port 8000.")
        print("   Start the backend with: uvicorn app.main:app --reload")
        return
    
    # Ask for confirmation
    print("\n⚠️ This will add data to your existing database.")
    response = input("Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Seeding cancelled.")
        return
    
    # Seed data
    items = seed_inventory()
    
    if items:
        seed_orders(items, num_orders=35)
        time.sleep(1)
        seed_additional_sales()
    else:
        print("❌ No items available. Seeding orders skipped.")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ SEEDING COMPLETE!")
    print("=" * 70)
    
    # Display summary statistics
    try:
        items = get_items()
        print(f"\n📊 Current Inventory:")
        print(f"   Total Items: {len(items)}")
        
        # Category breakdown
        categories = {}
        for item in items:
            cat = item.get('category', 'Uncategorized')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n   Categories:")
        for cat, count in categories.items():
            print(f"     - {cat}: {count} items")
        
        # Order stats
        try:
            response = requests.get(f"{API_URL}/stats/orders", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                print(f"\n📊 Order Statistics:")
                print(f"   Total Orders: {stats.get('total_orders', 0)}")
                print(f"   Pending: {stats.get('pending_orders', 0)}")
                print(f"   Completed: {stats.get('completed_orders', 0)}")
                print(f"   Cancelled: {stats.get('cancelled_orders', 0)}")
                print(f"   Total Sales: ${stats.get('total_sales', 0):,.2f}")
        except:
            pass
            
    except Exception as e:
        print(f"⚠️ Error fetching stats: {e}")
    
    print("\n🎉 Your database is now seeded with test data!")
    print("   Refresh your Streamlit app to see the data.")
    print("\n🚀 Next steps:")
    print("   1. Open the app: http://localhost:8501")
    print("   2. Explore the Dashboard")
    print("   3. Check the Orders page")
    print("   4. View Reports and Analytics")

if __name__ == "__main__":
    main()