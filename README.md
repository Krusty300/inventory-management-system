# Inventory Management System

A modern, full-featured inventory management application built with **FastAPI** (backend) and **Streamlit** (frontend). Perfect for small to medium-sized businesses to track inventory, manage orders, and generate reports.

## Features

### Dashboard
- **Real-time KPIs**: Total items, inventory value, low stock alerts, total quantity
- **Interactive Charts**: Stock by category, low stock visualization
- **Clickable Metrics**: Quick access to filtered views
- **Recent Activity**: Track recent inventory changes

### Inventory Management
- **Full CRUD Operations**: Create, Read, Update, Delete inventory items
- **Advanced Search**: Search by name, SKU, or category
- **Filtering**: Category filters, low stock filter
- **Pagination**: Handle large inventories efficiently
- **Bulk Operations**: Select multiple items for bulk actions
- **Quick Stock Update**: Rapid stock adjustments

### Order Management
- **Create Orders**: Sales, Purchases, Returns
- **Order History**: View all orders with filters
- **Status Management**: Track orders through workflow
- **Auto Inventory Updates**: Automatic stock adjustments
- **Order Analytics**: Sales vs purchases analysis

### Reports & Analytics
- **Low Stock Report**: Identify items needing attention
- **Category Distribution**: Visual breakdown by category
- **Value Analysis**: Top items by value, inventory valuation
- **Export Data**: CSV and Excel exports with formatting

### User Experience
- **Dark/Light Mode**: Toggle between themes
- **Custom Font**: Mona-Sans typography
- **Responsive Design**: Works on desktop and mobile
- **Toast Notifications**: Smooth user feedback
- **Interactive UI**: Cards, hover effects, animations

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern Python web framework |
| **SQLAlchemy** | ORM for database operations |
| **SQLite** | Lightweight database (can upgrade to PostgreSQL) |
| **Alembic** | Database migrations |
| **Pydantic** | Data validation |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Streamlit** | Python web framework for data apps |
| **Pandas** | Data manipulation |
| **Plotly** | Interactive charts |
| **Mona-Sans** | Custom variable font |

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

