from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.routers import items_router, orders_router
from app.db.base import Base
from app.db.session import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Inventory Management System API"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items_router, prefix=settings.API_V1_STR, tags=["items"])
app.include_router(orders_router, prefix=settings.API_V1_STR, tags=["orders"])

@app.get("/")
def root():
    return {"message": "Welcome to Inventory Management System"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}