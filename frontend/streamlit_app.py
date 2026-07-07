"""
Inventory Management System - Streamlit Frontend
================================================
This is the frontend interface for the Inventory Management System.
It provides a user-friendly dashboard for managing inventory items,
including viewing, adding, updating, and reporting on stock levels.

Author: Your Name
Date: 2026
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import base64
from pathlib import Path
import sys
import time

# Add the pages directory to Python path for importing orders module
pages_dir = Path(__file__).parent / "pages"
if str(pages_dir) not in sys.path:
    sys.path.append(str(pages_dir))

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Inventory Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM FONTS WITH MONA-SANS
# ============================================================================

def apply_custom_fonts():
    """
    Apply the Mona-Sans custom font to the entire application.
    
    This function reads the Mona-Sans.var.woff2 font file from the fonts directory,
    encodes it to base64, and injects it into the app's CSS. This ensures the
    font is available even without an internet connection.
    
    If the font file is not found, it falls back to system fonts.
    """
    
    # Construct the path to the font file
    font_path = Path(__file__).parent / "fonts" / "Mona-Sans.var.woff2"
    
    try:
        # Read and encode the font file
        with open(font_path, "rb") as f:
            font_bytes = f.read()
            font_base64 = base64.b64encode(font_bytes).decode()
        
        # Inject the font and styling into the app
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
            
            /* Apply Mona-Sans to all elements */
            * {{
                font-family: 'Mona-Sans', -apple-system, BlinkMacSystemFont, 
                             'Segoe UI', Roboto, sans-serif !important;
            }}
            
            /* Headings with heavier weight */
            h1, h2, h3, h4, h5, h6 {{
                font-family: 'Mona-Sans', sans-serif !important;
                font-weight: 700 !important;
                letter-spacing: -0.02em !important;
            }}
            
            /* Sidebar elements */
            .stSidebar * {{
                font-family: 'Mona-Sans', sans-serif !important;
            }}
            
            /* Metric values (larger numbers) */
            [data-testid="stMetricValue"] {{
                font-family: 'Mona-Sans', sans-serif !important;
                font-weight: 700 !important;
            }}
            
            /* Metric labels */
            [data-testid="stMetricLabel"] {{
                font-family: 'Mona-Sans', sans-serif !important;
                font-weight: 500 !important;
            }}
            
            /* Buttons */
            .stButton button {{
                font-family: 'Mona-Sans', sans-serif !important;
                font-weight: 600 !important;
            }}
            
            /* Dataframe tables */
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
            .stRadio label, 
            .stCheckbox label {{
                font-family: 'Mona-Sans', sans-serif !important;
            }}
            
            /* Alert messages */
            .stAlert div {{
                font-family: 'Mona-Sans', sans-serif !important;
            }}
            
            /* Sidebar styling */
            .css-1d391kg {{
                background-color: #f8f9fa !important;
            }}
            
            /* Sidebar radio button styling */
            .stRadio > div {{
                gap: 4px !important;
            }}
            
            .stRadio label {{
                padding: 8px 12px !important;
                border-radius: 8px !important;
                transition: all 0.2s ease !important;
                width: 100% !important;
            }}
            
            .stRadio label:hover {{
                background-color: #e9ecef !important;
            }}
            
            .stRadio [data-baseweb="radio"] {{
                display: none !important;
            }}
            
            .stRadio .st-emotion-cache-1y4p8pa {{
                padding: 0 !important;
            }}
            </style>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        # Fallback to system fonts if Mona-Sans is not available
        st.warning("Mona-Sans font file not found. Using system fonts instead.")
        st.markdown("""
            <style>
            * { 
                font-family: -apple-system, BlinkMacSystemFont, 
                             'Segoe UI', Roboto, sans-serif !important; 
            }
            </style>
        """, unsafe_allow_html=True)

# Apply the custom font
apply_custom_fonts()

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Base URL for the FastAPI backend
API_URL = "http://localhost:8000/api/v1"


# ============================================================================
# API HELPER FUNCTIONS
# ============================================================================

def get_items():
    """
    Fetch all inventory items from the API.
    
    Returns:
        list: A list of item dictionaries, or an empty list if an error occurs.
    """
    try:
        # Make a GET request to the items endpoint
        response = requests.get(
            f"{API_URL}/items?limit=1000", 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            # Ensure we return a list
            return items if isinstance(items, list) else []
        else:
            # Silent fail - let calling function handle
            return []
            
    except requests.exceptions.ConnectionError:
        # Silent fail - let calling function handle
        return []
    except Exception as e:
        # Silent fail - let calling function handle
        return []

def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


# ============================================================================
# MAIN APPLICATION - FIXED
# ============================================================================

def main():
    """
    Main entry point for the Streamlit application.
    Sets up the sidebar navigation and routes to the appropriate page.
    """
    
    # ===== SIDEBAR BRANDING =====
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <h1 style="font-size: 1.8rem; margin: 0; color: #1a1a2e;">
                Inventory
            </h1>
            <p style="font-size: 0.8rem; color: #6c757d; margin: 0;">
                Management System
            </p>
            <hr style="margin: 10px 0;">
        </div>
    """, unsafe_allow_html=True)
    
    # ===== SESSION STATE FOR NAVIGATION =====
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    # ===== NAVIGATION MENU =====
    nav_options = ["Dashboard", "Inventory", "Add Item", "Orders", "Reports"]
    
    page = st.sidebar.radio(
        "Navigate",
        nav_options,
        index=nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0,
        key="navigation"
    )
    
    # Update session state
    st.session_state.current_page = page
    
    # ===== API STATUS =====
    st.sidebar.divider()
    
    if check_api_health():
        st.sidebar.success("API Connected")
    else:
        st.sidebar.error("API Disconnected")
        st.sidebar.info("Start backend: uvicorn app.main:app --reload")
    
    st.sidebar.divider()
    
    # ===== FOOTER =====
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 10px 0; font-size: 0.7rem; color: #6c757d;">
            v1.0.0<br>
            © 2026 Inventory System
        </div>
    """, unsafe_allow_html=True)
    
    # ===== ROUTE TO SELECTED PAGE =====
    try:
        if page == "Dashboard":
            show_dashboard()
        elif page == "Inventory":
            show_inventory()
        elif page == "Add Item":
            show_add_item()
        elif page == "Orders":
            try:
                import orders
                orders.show()
            except ImportError:
                st.error("Orders page not found.")
                st.info("Please create frontend/pages/orders.py")
            except Exception as e:
                st.error(f"Error loading Orders: {str(e)}")
        elif page == "Reports":
            show_reports()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please try refreshing the page.")


# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

def show_dashboard():
    """
    Display the dashboard page with KPIs and charts.
    
    Shows:
    - Key Performance Indicators (Total Items, Value, Low Stock, Total Quantity)
    - Stock by Category bar chart
    - Low stock alert with item list
    """
    
    st.title("Dashboard")
    
    # Fetch items from the API
    items = get_items()
    
    # Check if there are any items
    if not items:
        st.info("📭 No items found. Add some items to get started!")
        return
    
    # ===== KEY PERFORMANCE INDICATORS =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Items", len(items))
    
    with col2:
        total_value = sum(
            item.get('quantity', 0) * item.get('unit_price', 0) 
            for item in items
        )
        st.metric("Total Inventory Value", f"${total_value:,.2f}")
    
    with col3:
        low_stock = [
            item for item in items 
            if item.get('quantity', 0) <= item.get('reorder_level', 0)
        ]
        st.metric("Low Stock Items", len(low_stock))
    
    with col4:
        total_quantity = sum(item.get('quantity', 0) for item in items)
        st.metric("Total Quantity", total_quantity)
    
    # ===== CHARTS =====
    if items and len(items) > 0:
        try:
            df = pd.DataFrame(items)
            
            # Stock by Category Chart
            if 'category' in df.columns:
                # Filter out empty categories
                df_filtered = df[df['category'].notna() & (df['category'] != '')]
                
                if not df_filtered.empty:
                    category_stock = (
                        df_filtered
                        .groupby('category')['quantity']
                        .sum()
                        .reset_index()
                    )
                    
                    fig = px.bar(
                        category_stock,
                        x='category',
                        y='quantity',
                        title='Stock by Category',
                        color='category',
                        labels={'quantity': 'Quantity', 'category': 'Category'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create chart: {str(e)}")
        
        # ===== LOW STOCK ALERT =====
        if low_stock:
            st.warning(f"{len(low_stock)} items are below reorder level!")
            
            try:
                # Display low stock items in a table
                low_stock_df = pd.DataFrame(low_stock)
                st.dataframe(
                    low_stock_df[['name', 'sku', 'quantity', 'reorder_level']],
                    use_container_width=True,
                    hide_index=True
                )
            except Exception:
                st.write(f"Low stock items: {len(low_stock)}")


# ============================================================================
# PAGE: INVENTORY
# ============================================================================

def show_inventory():
    """
    Display the inventory management page.
    
    Features:
    - Search by name or SKU
    - Filter low stock items
    - Display items in a sortable table
    - Quick stock update functionality
    """
    
    st.title("Inventory Management")
    
    # Fetch items from the API
    items = get_items()
    
    if not items:
        st.info("📭 No items found. Add some items to get started!")
        return
    
    # ===== SEARCH AND FILTER =====
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input(
            "Search items",
            placeholder="Search by name or SKU..."
        )
    
    with col2:
        low_stock_filter = st.checkbox("Show low stock only")
    
    # ===== APPLY FILTERS =====
    filtered_items = items
    
    # Apply search filter
    if search:
        filtered_items = [
            item for item in items 
            if search.lower() in str(item.get('name', '')).lower() or 
               search.lower() in str(item.get('sku', '')).lower()
        ]
    
    # Apply low stock filter
    if low_stock_filter:
        filtered_items = [
            item for item in filtered_items 
            if item.get('quantity', 0) <= item.get('reorder_level', 0)
        ]
    
    # Check if any items match the filters
    if not filtered_items:
        st.info("No items match your filters")
        return
    
    # ===== DISPLAY ITEMS TABLE =====
    df = pd.DataFrame(filtered_items)
    
    # Select columns to display
    display_cols = ['name', 'sku', 'quantity', 'reorder_level', 'unit_price', 'category']
    available_cols = [col for col in display_cols if col in df.columns]
    
    # Create display DataFrame with available columns
    df_display = df[available_cols].copy() if available_cols else df.copy()
    
    # Format price with dollar sign
    if 'unit_price' in df_display.columns:
        df_display['unit_price'] = df_display['unit_price'].apply(
            lambda x: f"${x:.2f}" if x else "$0.00"
        )
    
    # Add status column
    df_display['status'] = df_display.apply(
        lambda row: 'Low Stock' 
        if row.get('quantity', 0) <= row.get('reorder_level', 0) 
        else 'In Stock',
        axis=1
    )
    
    # Display the dataframe
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "status": st.column_config.TextColumn("Status")
        }
    )
    
    # ===== QUICK STOCK UPDATE =====
    st.subheader("Quick Stock Update")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Create dropdown with SKU - Name format
        item_options = [
            f"{item.get('sku', '')} - {item.get('name', '')}" 
            for item in filtered_items 
            if item.get('sku')
        ]
        
        if item_options:
            selected_option = st.selectbox("Select item", item_options)
            # Extract SKU from the selected option
            selected_sku = selected_option.split(" - ")[0] if selected_option else None
        else:
            selected_sku = None
            st.warning("No items available")
    
    with col2:
        quantity_change = st.number_input(
            "Quantity change",
            value=0,
            step=1,
            help="Positive number adds stock, negative removes stock"
        )
    
    with col3:
        if st.button("Update Stock", use_container_width=True):
            if selected_sku:
                # Find the selected item
                selected_item = next(
                    (item for item in filtered_items if item.get('sku') == selected_sku), 
                    None
                )
                
                if selected_item:
                    try:
                        # Make API call to update stock
                        response = requests.patch(
                            f"{API_URL}/items/{selected_item['id']}/stock",
                            params={"quantity_change": quantity_change}
                        )
                        
                        if response.status_code == 200:
                            st.success("Stock updated successfully!")
                            st.rerun()  # Refresh the page
                        else:
                            st.error(f"Failed to update stock: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error updating stock: {str(e)}")


# ============================================================================
# PAGE: ADD ITEM
# ============================================================================

def show_add_item():
    """
    Display the add item form page.
    
    Allows users to add new inventory items with:
    - Name, SKU, Description, Category
    - Quantity, Reorder Level, Unit Price
    """
    
    st.title("Add New Item")
    
    # Check API connection
    if not check_api_health():
        st.warning("Cannot connect to the API. Please make sure the backend is running on port 8000.")
        st.info("Start the backend with: uvicorn app.main:app --reload")
        return
    
    # Create the form
    with st.form("add_item_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Item Name*",
                placeholder="Enter item name",
                help="Required. The name of the item."
            )
            
            sku = st.text_input(
                "SKU*",
                placeholder="Unique SKU code",
                help="Required. Must be unique for each item."
            )
            
            description = st.text_area(
                "Description",
                placeholder="Item description (optional)",
                help="Optional description of the item."
            )
            
            category = st.text_input(
                "Category",
                placeholder="e.g., Electronics, Furniture",
                help="Optional category for grouping items."
            )
        
        with col2:
            quantity = st.number_input(
                "Quantity*",
                min_value=0,
                step=1,
                value=0,
                help="Initial stock quantity."
            )
            
            reorder_level = st.number_input(
                "Reorder Level*",
                min_value=0,
                step=1,
                value=10,
                help="Quantity at which to trigger low stock alerts."
            )
            
            unit_price = st.number_input(
                "Unit Price ($)*",
                min_value=0.0,
                step=0.01,
                value=0.0,
                help="Price per unit in USD."
            )
        
        # Submit button
        submitted = st.form_submit_button("Add Item", type="primary")
        
        if submitted:
            # Validate required fields
            if not name or not sku:
                st.error("Name and SKU are required fields!")
            else:
                # Prepare item data
                item_data = {
                    "name": name.strip(),
                    "sku": sku.strip().upper(),
                    "description": description.strip() if description else None,
                    "quantity": quantity,
                    "reorder_level": reorder_level,
                    "unit_price": unit_price,
                    "category": category.strip() if category else None
                }
                
                try:
                    # Make API call to create item
                    response = requests.post(
                        f"{API_URL}/items",
                        json=item_data,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        st.success("Item added successfully!")
                        st.balloons()
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        # Try to get error details
                        try:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.error(f"Failed to add item: {error_detail}")
                        except:
                            st.error(f"Failed to add item. Status code: {response.status_code}")
                            
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the API. Make sure the backend is running on port 8000.")
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"Error adding item: {str(e)}")


# ============================================================================
# PAGE: REPORTS
# ============================================================================

def show_reports():
    """
    Display the reports and analytics page.
    
    Features:
    - Low stock items report with chart
    - Category distribution pie chart
    - Top 10 items by value
    - Export data to CSV
    """
    
    st.title("Reports")
    
    # Fetch items from the API
    items = get_items()
    
    if not items:
        st.info("📭 No items found. Add some items to get started!")
        return
    
    try:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(items)
        
        # ===== LOW STOCK REPORT =====
        st.subheader("Low Stock Items")
        
        if 'quantity' in df.columns and 'reorder_level' in df.columns:
            low_stock = df[df['quantity'] <= df['reorder_level']]
            
            if not low_stock.empty:
                # Display low stock items
                st.dataframe(
                    low_stock[['name', 'sku', 'quantity', 'reorder_level', 'unit_price']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Create low stock bar chart
                fig = px.bar(
                    low_stock,
                    x='name',
                    y='quantity',
                    title='Low Stock Items',
                    color='reorder_level',
                    labels={
                        'quantity': 'Current Stock', 
                        'reorder_level': 'Reorder Level'
                    },
                    text='quantity'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("All items have sufficient stock!")
        
        # ===== CATEGORY DISTRIBUTION =====
        st.subheader("Category Distribution")
        
        if 'category' in df.columns:
            # Filter out empty categories
            df_filtered = df[df['category'].notna() & (df['category'] != '')]
            
            if not df_filtered.empty:
                category_counts = df_filtered['category'].value_counts()
                
                # Create pie chart
                fig = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title='Items by Category',
                    hole=0.3
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No categories defined")
        
        # ===== VALUE ANALYSIS =====
        st.subheader("Inventory Value Analysis")
        
        if 'quantity' in df.columns and 'unit_price' in df.columns:
            # Calculate total value per item
            df['total_value'] = df['quantity'] * df['unit_price']
            top_items = df.nlargest(10, 'total_value')
            
            if not top_items.empty:
                # Create bar chart of top items by value
                fig = px.bar(
                    top_items,
                    x='name',
                    y='total_value',
                    title='Top 10 Items by Value',
                    labels={'total_value': 'Total Value ($)'},
                    text='total_value',
                    color='total_value',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data for value analysis")
        
        # ===== EXPORT DATA =====
        st.subheader("Export Data")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Export to CSV", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="inventory_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
    except Exception as e:
        st.error(f"Error generating reports: {str(e)}")


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()