import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import base64
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Inventory Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM FONTS WITH MONA-SANS =====
def apply_custom_fonts():
    """Apply Mona-Sans custom font to the entire app"""
    
    # Read the font file and encode it
    font_path = Path(__file__).parent / "fonts" / "Mona-Sans.var.woff2"
    
    try:
        with open(font_path, "rb") as f:
            font_bytes = f.read()
            font_base64 = base64.b64encode(font_bytes).decode()
        
        st.markdown(f"""
            <style>
            /* ===== MONA-SANS FONT ===== */
            @font-face {{
                font-family: 'Mona-Sans';
                src: url(data:font/woff2;base64,{font_base64}) format('woff2');
                font-weight: 200 900;
                font-stretch: 75% 125%;
                font-style: normal;
                font-display: swap;
            }}
            
            /* Apply Mona-Sans to everything */
            * {{
                font-family: 'Mona-Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            }}
            
            /* Headings with Mona-Sans */
            h1, h2, h3, h4, h5, h6 {{
                font-family: 'Mona-Sans', sans-serif !important;
                font-weight: 700 !important;
                letter-spacing: -0.02em !important;
            }}
            
            /* Sidebar */
            .stSidebar * {{
                font-family: 'Mona-Sans', sans-serif !important;
            }}
            
            /* Metrics */
            [data-testid="stMetricValue"] {{
                font-family: 'Mona-Sans', sans-serif !important;
                font-weight: 700 !important;
            }}
            
            [data-testid="stMetricLabel"] {{
                font-family: 'Mona-Sans', sans-serif !important;
                font-weight: 500 !important;
            }}
            
            /* Buttons */
            .stButton button {{
                font-family: 'Mona-Sans', sans-serif !important;
                font-weight: 600 !important;
            }}
            
            /* Dataframe */
            .stDataFrame * {{
                font-family: 'Mona-Sans', sans-serif !important;
            }}
            
            /* Input fields */
            .stTextInput input, 
            .stNumberInput input, 
            .stSelectbox select, 
            .stTextArea textarea {{
                font-family: 'Mona-Sans', sans-serif !important;
            }}
            
            /* Radio buttons and checkboxes */
            .stRadio label, .stCheckbox label {{
                font-family: 'Mona-Sans', sans-serif !important;
            }}
            
            /* Alert messages */
            .stAlert div {{
                font-family: 'Mona-Sans', sans-serif !important;
            }}
            </style>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.warning("Mona-Sans font file not found. Using system fonts instead.")
        # Fallback styling
        st.markdown("""
            <style>
            * { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; }
            </style>
        """, unsafe_allow_html=True)

# Apply the font
apply_custom_fonts()
# API configuration
API_URL = "http://localhost:8000/api/v1"

def get_items():
    """Fetch items from API"""
    try:
        response = requests.get(f"{API_URL}/items?limit=1000", timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            return items if isinstance(items, list) else []
        else:
            st.error(f"Failed to fetch items: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error(" Cannot connect to the API. Make sure the backend is running on port 8000.")
        return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def main():
    st.sidebar.title("Inventory Management")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Inventory", "Add Item", "Reports"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Inventory":
        show_inventory()
    elif page == "Add Item":
        show_add_item()
    elif page == "Reports":
        show_reports()

def show_dashboard():
    st.title("Dashboard")
    
    # Fetch items directly
    items = get_items()
    
    if not items:
        st.info("📭 No items found. Add some items to get started!")
        return
    
    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Items", len(items))
    
    with col2:
        total_value = sum(item.get('quantity', 0) * item.get('unit_price', 0) for item in items)
        st.metric("Total Inventory Value", f"${total_value:,.2f}")
    
    with col3:
        low_stock = [item for item in items if item.get('quantity', 0) <= item.get('reorder_level', 0)]
        st.metric("Low Stock Items", len(low_stock))
    
    with col4:
        total_quantity = sum(item.get('quantity', 0) for item in items)
        st.metric("Total Quantity", total_quantity)
    
    # Charts
    if items and len(items) > 0:
        try:
            df = pd.DataFrame(items)
            
            # Category chart
            if 'category' in df.columns:
                df_filtered = df[df['category'].notna() & (df['category'] != '')]
                if not df_filtered.empty:
                    category_stock = df_filtered.groupby('category')['quantity'].sum().reset_index()
                    fig = px.bar(category_stock, x='category', y='quantity', title='Stock by Category')
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create chart: {str(e)}")
        
        # Low stock alert
        if low_stock:
            st.warning(f" {len(low_stock)} items are below reorder level!")
            try:
                low_stock_df = pd.DataFrame(low_stock)
                st.dataframe(low_stock_df[['name', 'sku', 'quantity', 'reorder_level']], use_container_width=True)
            except:
                st.write(f"Low stock items: {len(low_stock)}")

def show_inventory():
    st.title("Inventory Management")
    
    # Fetch items
    items = get_items()
    
    if not items:
        st.info("📭 No items found. Add some items to get started!")
        return
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search items", placeholder="Search by name or SKU...")
    with col2:
        low_stock_filter = st.checkbox("Show low stock only")
    
    # Filter items
    filtered_items = items
    if search:
        filtered_items = [
            item for item in items 
            if search.lower() in str(item.get('name', '')).lower() or 
               search.lower() in str(item.get('sku', '')).lower()
        ]
    if low_stock_filter:
        filtered_items = [
            item for item in filtered_items 
            if item.get('quantity', 0) <= item.get('reorder_level', 0)
        ]
    
    if not filtered_items:
        st.info("No items match your filters")
        return
    
    # Display as dataframe
    df = pd.DataFrame(filtered_items)
    
    # Select columns to display
    display_cols = ['name', 'sku', 'quantity', 'reorder_level', 'unit_price', 'category']
    available_cols = [col for col in display_cols if col in df.columns]
    
    # Create display DataFrame
    df_display = df[available_cols].copy() if available_cols else df.copy()
    
    # Format price
    if 'unit_price' in df_display.columns:
        df_display['unit_price'] = df_display['unit_price'].apply(lambda x: f"${x:.2f}" if x else "$0.00")
    
    # Add status column
    df_display['status'] = df_display.apply(
        lambda row: 'Low Stock' if row.get('quantity', 0) <= row.get('reorder_level', 0) else 'In Stock',
        axis=1
    )
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "status": st.column_config.TextColumn("Status")
        }
    )
    
    # Quick stock update
    st.subheader("Quick Stock Update")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        item_options = [f"{item.get('sku', '')} - {item.get('name', '')}" for item in filtered_items if item.get('sku')]
        if item_options:
            selected_option = st.selectbox("Select item", item_options)
            selected_sku = selected_option.split(" - ")[0] if selected_option else None
        else:
            selected_sku = None
            st.warning("No items available")
    
    with col2:
        quantity_change = st.number_input("Quantity change", value=0, step=1)
    
    with col3:
        if st.button("Update Stock", use_container_width=True):
            if selected_sku:
                selected_item = next((item for item in filtered_items if item.get('sku') == selected_sku), None)
                if selected_item:
                    try:
                        response = requests.patch(
                            f"{API_URL}/items/{selected_item['id']}/stock",
                            params={"quantity_change": quantity_change}
                        )
                        if response.status_code == 200:
                            st.success(" Stock updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to update stock: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error updating stock: {str(e)}")

def show_add_item():
    st.title(" Add New Item")
    
    with st.form("add_item_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Item Name*", placeholder="Enter item name")
            sku = st.text_input("SKU*", placeholder="Unique SKU code")
            description = st.text_area("Description", placeholder="Item description")
            category = st.text_input("Category", placeholder="e.g., Electronics, Furniture")
        
        with col2:
            quantity = st.number_input("Quantity*", min_value=0, step=1, value=0)
            reorder_level = st.number_input("Reorder Level*", min_value=0, step=1, value=10)
            unit_price = st.number_input("Unit Price ($)*", min_value=0.0, step=0.01, value=0.0)
        
        submitted = st.form_submit_button("Add Item", type="primary")
        
        if submitted:
            if not name or not sku:
                st.error("Name and SKU are required!")
            else:
                item_data = {
                    "name": name,
                    "sku": sku,
                    "description": description,
                    "quantity": quantity,
                    "reorder_level": reorder_level,
                    "unit_price": unit_price,
                    "category": category
                }
                
                try:
                    response = requests.post(f"{API_URL}/items", json=item_data)
                    if response.status_code == 201:
                        st.success(" Item added successfully!")
                        st.rerun()
                    else:
                        try:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.error(f" Failed to add item: {error_detail}")
                        except:
                            st.error(f" Failed to add item. Status code: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error(" Cannot connect to the API. Make sure the backend is running on port 8000.")
                except Exception as e:
                    st.error(f"Error adding item: {str(e)}")

def show_reports():
    st.title("Reports")
    
    # Fetch items
    items = get_items()
    
    if not items:
        st.info("📭 No items found. Add some items to get started!")
        return
    
    try:
        df = pd.DataFrame(items)
        
        # Low stock report
        st.subheader("Low Stock Items")
        if 'quantity' in df.columns and 'reorder_level' in df.columns:
            low_stock = df[df['quantity'] <= df['reorder_level']]
            
            if not low_stock.empty:
                st.dataframe(
                    low_stock[['name', 'sku', 'quantity', 'reorder_level', 'unit_price']],
                    use_container_width=True,
                    hide_index=True
                )
                
                fig = px.bar(
                    low_stock,
                    x='name',
                    y='quantity',
                    title='Low Stock Items',
                    color='reorder_level',
                    labels={'quantity': 'Current Stock', 'reorder_level': 'Reorder Level'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success(" All items have sufficient stock!")
        
        # Category distribution
        st.subheader("Category Distribution")
        if 'category' in df.columns:
            df_filtered = df[df['category'].notna() & (df['category'] != '')]
            if not df_filtered.empty:
                category_counts = df_filtered['category'].value_counts()
                fig = px.pie(values=category_counts.values, names=category_counts.index, title='Items by Category')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No categories defined")
        
        # Value analysis
        st.subheader(" Inventory Value Analysis")
        if 'quantity' in df.columns and 'unit_price' in df.columns:
            df['total_value'] = df['quantity'] * df['unit_price']
            top_items = df.nlargest(10, 'total_value')
            
            if not top_items.empty:
                fig = px.bar(
                    top_items,
                    x='name',
                    y='total_value',
                    title='Top 10 Items by Value',
                    labels={'total_value': 'Total Value ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data for value analysis")
        
        # Export
        st.subheader(" Export Data")
        if st.button("Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="inventory_report.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Error generating reports: {str(e)}")

if __name__ == "__main__":
    main()