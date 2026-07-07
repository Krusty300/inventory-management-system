# seed_data.py
import requests
import json

API_URL = "http://localhost:8000/api/v1/items"

sample_items = [
    {
        "name": "Laptop",
        "sku": "LAP001",
        "description": "High-performance laptop",
        "quantity": 50,
        "reorder_level": 10,
        "unit_price": 999.99,
        "category": "Electronics"
    },
    {
        "name": "Wireless Mouse",
        "sku": "MOU001",
        "description": "Wireless optical mouse",
        "quantity": 30,
        "reorder_level": 5,
        "unit_price": 29.99,
        "category": "Electronics"
    },
    {
        "name": "Office Desk",
        "sku": "DESK001",
        "description": "Large office desk",
        "quantity": 15,
        "reorder_level": 3,
        "unit_price": 299.99,
        "category": "Furniture"
    },
    {
        "name": "Office Chair",
        "sku": "CHA001",
        "description": "Ergonomic office chair",
        "quantity": 20,
        "reorder_level": 5,
        "unit_price": 149.99,
        "category": "Furniture"
    },
    {
        "name": "Printer",
        "sku": "PRI001",
        "description": "Laser printer",
        "quantity": 8,
        "reorder_level": 2,
        "unit_price": 249.99,
        "category": "Electronics"
    },
    {
        "name": "Notebook",
        "sku": "NOT001",
        "description": "Pack of 10 notebooks",
        "quantity": 100,
        "reorder_level": 20,
        "unit_price": 4.99,
        "category": "Stationery"
    }
]

print("Adding sample items to inventory...")

for item in sample_items:
    try:
        response = requests.post(API_URL, json=item)
        if response.status_code == 201:
            print(f"✅ Added: {item['name']} (SKU: {item['sku']})")
        else:
            print(f"❌ Failed to add {item['name']}: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the backend is running on port 8000.")
        break
    except Exception as e:
        print(f"❌ Error adding {item['name']}: {str(e)}")

print("\nDone! Refresh your Streamlit app to see the data.")