"""
Orders Management Page for Streamlit Frontend
============================================
Provides order creation, viewing, and management interface.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# API configuration
API_URL = "http://localhost:8000/api/v1"

# Cache for item names with size limit
_item_cache = {}
_CACHE_LIMIT = 100

def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_item_name(item_id):
    """Fetch item name by ID with caching"""
    if item_id in _item_cache:
        return _item_cache[item_id]
    
    # Limit cache size to prevent memory growth
    if len(_item_cache) >= _CACHE_LIMIT:
        _item_cache.clear()
    
    try:
        response = requests.get(f"{API_URL}/items/{item_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            name = data.get('name', f"Item {item_id[:8]}")
            _item_cache[item_id] = name
            return name
    except Exception:
        pass
    
    return f"Item {item_id[:8]}"

def fetch_orders(filters=None):
    """Fetch orders from API with optional filters"""
    try:
        params = {}
        if filters:
            params.update(filters)
        
        response = requests.get(
            f"{API_URL}/orders",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('orders', [])
        return []
    except Exception:
        return []

def fetch_order_stats():
    """Fetch order statistics"""
    try:
        response = requests.get(f"{API_URL}/stats/orders", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def fetch_items():
    """Fetch all items for order creation"""
    try:
        response = requests.get(f"{API_URL}/items?limit=1000", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        return []
    except Exception:
        return []

def create_order(order_data):
    """Create a new order"""
    try:
        response = requests.post(f"{API_URL}/orders", json=order_data, timeout=10)
        if response.status_code == 201:
            return True, response.json()
        else:
            try:
                error = response.json().get('detail', 'Unknown error')
                return False, error
            except:
                return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)

def update_order_status(order_id, status):
    """Update order status"""
    try:
        response = requests.patch(
            f"{API_URL}/orders/{order_id}/status",
            params={"status": status},
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)

def show_orders():
    """Main orders page"""
    # Check API connectivity first
    if not check_api_health():
        st.warning("Cannot connect to the API. Please make sure the backend is running on port 8000.")
        st.info("Start the backend with: uvicorn app.main:app --reload")
        return
    
    st.title("Order Management")
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["Orders", "Create Order", "Analytics"])
    
    with tab1:
        show_orders_list()
    
    with tab2:
        show_create_order()
    
    with tab3:
        show_order_analytics()

def show_orders_list():
    """Display list of orders with filters"""
    st.subheader("Order History")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "pending", "completed", "cancelled", "shipped", "delivered"]
        )
    
    with col2:
        type_filter = st.selectbox(
            "Order Type",
            ["All", "sale", "purchase", "return"]
        )
    
    with col3:
        search = st.text_input("Search", placeholder="Order # or customer...")
    
    with col4:
        date_range = st.selectbox(
            "Date Range",
            ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
        )
    
    # Build filters
    filters = {}
    if status_filter != "All":
        filters['status'] = status_filter
    if type_filter != "All":
        filters['order_type'] = type_filter
    if search:
        filters['search'] = search
    
    # Date range filter
    if date_range != "All Time":
        today = datetime.now().date()
        if date_range == "Today":
            start_date = today
        elif date_range == "Last 7 Days":
            start_date = today - timedelta(days=7)
        elif date_range == "Last 30 Days":
            start_date = today - timedelta(days=30)
        elif date_range == "Last 90 Days":
            start_date = today - timedelta(days=90)
        
        filters['start_date'] = start_date.isoformat()
        filters['end_date'] = (today + timedelta(days=1)).isoformat()
    
    # Fetch orders
    orders = fetch_orders(filters)
    
    if not orders:
        st.info("📭 No orders found")
        return
    
    # Display orders in dataframe
    df = pd.DataFrame(orders)
    
    # Prepare display dataframe
    display_cols = ['order_number', 'order_type', 'status', 'customer_name', 
                   'total', 'order_date']
    available_cols = [col for col in display_cols if col in df.columns]
    
    df_display = df[available_cols].copy()
    
    # Format date
    if 'order_date' in df_display.columns:
        df_display['order_date'] = pd.to_datetime(df_display['order_date']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Format total
    if 'total' in df_display.columns:
        df_display['total'] = df_display['total'].apply(lambda x: f"${x:,.2f}")
    
    # Add status badges with colors
    def get_status_badge(status):
        colors = {
            'pending': 'Pending',
            'completed': 'Completed',
            'cancelled': 'Cancelled',
            'shipped': 'Shipped',
            'delivered': 'Delivered'
        }
        return colors.get(status, status)
    
    if 'status' in df_display.columns:
        df_display['status'] = df_display['status'].apply(get_status_badge)
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "order_number": "Order #",
            "order_type": "Type",
            "customer_name": "Customer",
            "total": "Total",
            "order_date": "Date",
            "status": st.column_config.TextColumn("Status")
        }
    )
    
    # Order details on selection
    if orders:
        st.subheader("Order Details")
        selected_order_num = st.selectbox(
            "Select Order to View Details",
            [o.get('order_number', 'N/A') for o in orders if o.get('order_number')]
        )
        
        if selected_order_num:
            order = next((o for o in orders if o.get('order_number') == selected_order_num), None)
            if order:
                show_order_details(order)

def show_order_details(order):
    """Display detailed view of an order"""
    st.divider()
    
    # Display order info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Order #:** {order.get('order_number', 'N/A')}")
        st.write(f"**Type:** {order.get('order_type', 'N/A').title() if order.get('order_type') else 'N/A'}")
        st.write(f"**Status:** {order.get('status', 'N/A').title() if order.get('status') else 'N/A'}")
        st.write(f"**Date:** {order.get('order_date', 'N/A')}")
    
    with col2:
        st.write(f"**Customer:** {order.get('customer_name', 'N/A')}")
        st.write(f"**Email:** {order.get('customer_email', 'N/A')}")
        st.write(f"**Phone:** {order.get('customer_phone', 'N/A')}")
    
    with col3:
        st.write(f"**Subtotal:** ${order.get('subtotal', 0):,.2f}")
        st.write(f"**Tax:** ${order.get('tax', 0):,.2f}")
        st.write(f"**Discount:** ${order.get('discount', 0):,.2f}")
        st.write(f"**Total:** ${order.get('total', 0):,.2f}")
    
    # Status update
    current_status = order.get('status', 'pending')
    if current_status not in ['completed', 'cancelled']:
        col1, col2 = st.columns([1, 3])
        with col1:
            new_status = st.selectbox(
                "Update Status",
                ['pending', 'shipped', 'delivered', 'completed', 'cancelled'],
                index=0,
                key="status_select"
            )
            if st.button("Update Status", key="update_status_btn"):
                success, result = update_order_status(order.get('id'), new_status)
                if success:
                    st.success(f"Status updated to {new_status}")
                    st.rerun()
                else:
                    st.error(f"Failed to update: {result}")
    
    # Show order items
    st.subheader("Order Items")
    
    # Get items - ensure it's a list
    items = order.get('items', [])
    
    if not items or not isinstance(items, list):
        st.info("No items in this order")
        return
    
    # Build items list with names fetched from API
    items_data = []
    total_items = len(items)
    
    with st.spinner(f"Loading item details ({total_items} items)..."):
        for idx, item in enumerate(items):
            try:
                if isinstance(item, dict):
                    # Get item ID
                    item_id = item.get('item_id', '')
                    
                    # Get item name from cache or API
                    if item_id:
                        item_name = get_item_name(item_id)
                    else:
                        item_name = f"Item {idx + 1}"
                    
                    # Get other fields
                    quantity = item.get('quantity', 0)
                    unit_price = item.get('unit_price', 0)
                    total_price = item.get('total_price', quantity * unit_price)
                    
                    items_data.append({
                        'Item': item_name,
                        'Quantity': quantity,
                        'Unit Price': f"${unit_price:,.2f}",
                        'Total': f"${total_price:,.2f}"
                    })
            except Exception:
                continue
    
    if items_data:
        try:
            df_items = pd.DataFrame(items_data)
            st.dataframe(
                df_items,
                use_container_width=True,
                hide_index=True
            )
        except Exception:
            # Fallback: display as list
            for item in items_data:
                st.write(f"**{item['Item']}** - Qty: {item['Quantity']} - {item['Total']}")
    else:
        st.info("Could not display order items")

def show_create_order():
    """Create new order form"""
    st.subheader("Create New Order")
    
    # Order type
    order_type = st.radio(
        "Order Type",
        ["sale", "purchase", "return"],
        horizontal=True,
        help="Sale: Deducts from inventory | Purchase: Adds to inventory | Return: Adds to inventory"
    )
    
    # Customer information
    with st.expander("Customer Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name (Optional)")
            customer_email = st.text_input("Customer Email (Optional)")
        with col2:
            customer_phone = st.text_input("Customer Phone (Optional)")
            shipping_address = st.text_area("Shipping Address (Optional)")
    
    # Order items
    st.subheader("Order Items")
    
    items = fetch_items()
    if not items:
        st.warning("No items available. Please add items to inventory first.")
        return
    
    # Initialize session state for order items
    if 'order_items' not in st.session_state:
        st.session_state.order_items = []
    
    # Add item form
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        item_options = [f"{item['sku']} - {item['name']} (Stock: {item['quantity']})" 
                       for item in items]
        if item_options:
            selected_item_name = st.selectbox(
                "Select Item",
                options=item_options,
                key="select_item"
            )
            selected_item = next(
                (item for item in items if f"{item['sku']} - {item['name']} (Stock: {item['quantity']})" == selected_item_name),
                None
            )
        else:
            selected_item = None
            st.warning("No items available")
    
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key="order_qty")
    
    with col3:
        unit_price = st.number_input(
            "Unit Price", 
            min_value=0.01, 
            value=selected_item['unit_price'] if selected_item else 0.0, 
            step=0.01,
            format="%.2f",
            key="order_price"
        )
    
    with col4:
        if st.button("Add to Order"):
            if selected_item and quantity > 0 and unit_price > 0:
                st.session_state.order_items.append({
                    'item_id': selected_item['id'],
                    'name': selected_item['name'],
                    'sku': selected_item['sku'],
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total': quantity * unit_price
                })
                st.success(f"Added {quantity} of {selected_item['name']}")
            else:
                st.error("Please select an item and enter valid quantity and price")
    
    # Display current order items
    if st.session_state.order_items:
        st.subheader("Order Summary")
        
        df = pd.DataFrame(st.session_state.order_items)
        st.dataframe(
            df[['sku', 'name', 'quantity', 'unit_price', 'total']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "sku": "SKU",
                "name": "Item",
                "quantity": "Qty",
                "unit_price": "Unit Price",
                "total": "Total"
            }
        )
        
        # Calculate totals
        subtotal = sum(item['total'] for item in st.session_state.order_items)
        tax_rate = 0.10
        tax = subtotal * tax_rate
        total = subtotal + tax
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Subtotal", f"${subtotal:,.2f}")
        with col2:
            st.metric(f"Tax ({tax_rate*100:.0f}%)", f"${tax:,.2f}")
        with col3:
            st.metric("Total", f"${total:,.2f}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Order", use_container_width=True):
                st.session_state.order_items = []
                st.rerun()
        
        with col2:
            if st.button("Submit Order", type="primary", use_container_width=True):
                if st.session_state.order_items:
                    order_data = {
                        "order_type": order_type,
                        "customer_name": customer_name or None,
                        "customer_email": customer_email or None,
                        "customer_phone": customer_phone or None,
                        "shipping_address": shipping_address or None,
                        "tax": tax,
                        "discount": 0.0,
                        "items": [
                            {
                                "item_id": item['item_id'],
                                "quantity": item['quantity'],
                                "unit_price": item['unit_price']
                            }
                            for item in st.session_state.order_items
                        ]
                    }
                    
                    success, result = create_order(order_data)
                    
                    if success:
                        st.success(f"Order {result.get('order_number', '')} created successfully!")
                        st.session_state.order_items = []
                        st.rerun()
                    else:
                        st.error(f"Failed to create order: {result}")
                else:
                    st.warning("No items in order")

def show_order_analytics():
    """Display order analytics and statistics"""
    st.subheader("Order Analytics")
    
    stats = fetch_order_stats()
    
    if not stats:
        st.info("No order data available")
        return
    
    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Orders", stats.get('total_orders', 0))
    
    with col2:
        st.metric("Total Sales", f"${stats.get('total_sales', 0):,.2f}")
    
    with col3:
        profit = stats.get('total_profit', 0)
        st.metric("Total Profit", f"${profit:,.2f}")
    
    with col4:
        st.metric("Pending Orders", stats.get('pending_orders', 0))
    
    # Status breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Order Status Distribution")
        status_data = {
            'Pending': stats.get('pending_orders', 0),
            'Completed': stats.get('completed_orders', 0),
            'Cancelled': stats.get('cancelled_orders', 0)
        }
        
        if sum(status_data.values()) > 0:
            fig = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title='Orders by Status',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No order status data available")
    
    with col2:
        st.subheader("Sales vs Purchases")
        total_sales = stats.get('total_sales', 0)
        total_purchases = stats.get('total_purchases', 0)
        
        if total_sales > 0 or total_purchases > 0:
            comparison_data = {
                'Sales': total_sales,
                'Purchases': total_purchases
            }
            
            fig = px.bar(
                x=list(comparison_data.keys()),
                y=list(comparison_data.values()),
                title='Sales vs Purchases',
                labels={'x': 'Type', 'y': 'Amount ($)'},
                color_discrete_sequence=['#2ecc71', '#e74c3c']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales or purchase data available")

# Export function for main app
def show():
    """Entry point for the orders page"""
    show_orders()