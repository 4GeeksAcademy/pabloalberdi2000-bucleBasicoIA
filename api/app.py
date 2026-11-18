"""
FastAPI application for inventory management with CSV persistence.
Handles coffee shop inventory: products, quantities, and stock alerts.
"""

import csv
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import threading

# Configuration
CSV_FILE = Path(__file__).parent.parent / "products.csv"
ALERT_THRESHOLD = 10

# Lock for thread-safe CSV operations
csv_lock = threading.Lock()

app = FastAPI(title="Inventory API", version="1.0.0")


# Pydantic models
class Product(BaseModel):
    product_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    quantity: float = Field(..., ge=0)
    unit: str = Field(..., min_length=1, max_length=20)


class ProductUpdate(BaseModel):
    delta: float = Field(..., description="Change in quantity (positive for delivery, negative for sales)")


class StockAlert(BaseModel):
    product_id: int
    name: str
    quantity: float
    unit: str
    alert_threshold: int


# Helper functions
def _ensure_csv_exists():
    """Ensure the CSV file exists with headers."""
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["product_id", "name", "quantity", "unit"])


def _read_products() -> list[dict]:
    """Read all products from CSV."""
    _ensure_csv_exists()
    with open(CSV_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader) if reader else []


def _write_products(products: list[dict]):
    """Write products to CSV, overwriting the file."""
    with open(CSV_FILE, "w", newline="") as f:
        if products:
            writer = csv.DictWriter(f, fieldnames=["product_id", "name", "quantity", "unit"])
            writer.writeheader()
            writer.writerows(products)
        else:
            writer = csv.writer(f)
            writer.writerow(["product_id", "name", "quantity", "unit"])


def _get_next_product_id() -> int:
    """Get the next available product ID."""
    products = _read_products()
    if not products:
        return 1
    return max(int(p["product_id"]) for p in products) + 1


# API Endpoints
@app.get("/inventory", response_model=list[Product])
def get_inventory():
    """Retrieve all products from inventory."""
    with csv_lock:
        products = _read_products()
    
    return [
        Product(
            product_id=int(p["product_id"]),
            name=p["name"],
            quantity=float(p["quantity"]),
            unit=p["unit"]
        )
        for p in products
    ]


@app.post("/inventory", response_model=Product, status_code=201)
def add_product(product: Product):
    """Add a new product to inventory."""
    with csv_lock:
        products = _read_products()
        
        # Validate name uniqueness
        if any(p["name"].lower() == product.name.lower() for p in products):
            raise HTTPException(status_code=400, detail=f"Product '{product.name}' already exists")
        
        product_id = _get_next_product_id()
        new_product = {
            "product_id": product_id,
            "name": product.name,
            "quantity": product.quantity,
            "unit": product.unit
        }
        products.append(new_product)
        _write_products(products)
    
    return Product(
        product_id=product_id,
        name=product.name,
        quantity=product.quantity,
        unit=product.unit
    )


@app.patch("/inventory/{product_id}", response_model=Product)
def update_product_stock(product_id: int, update: ProductUpdate):
    """Update stock quantity for a product (delta-based: positive for inbound, negative for outbound)."""
    with csv_lock:
        products = _read_products()
        
        product_dict = None
        for p in products:
            if int(p["product_id"]) == product_id:
                product_dict = p
                break
        
        if not product_dict:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        current_qty = float(product_dict["quantity"])
        new_qty = current_qty + update.delta
        
        if new_qty < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Stock cannot be negative. Current: {current_qty}, delta: {update.delta}"
            )
        
        product_dict["quantity"] = str(new_qty)
        _write_products(products)
    
    return Product(
        product_id=product_id,
        name=product_dict["name"],
        quantity=new_qty,
        unit=product_dict["unit"]
    )


@app.get("/inventory/alerts", response_model=list[StockAlert])
def get_stock_alerts(threshold: int = ALERT_THRESHOLD):
    """Retrieve all products with stock below the alert threshold."""
    with csv_lock:
        products = _read_products()
    
    alerts = []
    for p in products:
        qty = float(p["quantity"])
        if qty < threshold:
            alerts.append(
                StockAlert(
                    product_id=int(p["product_id"]),
                    name=p["name"],
                    quantity=qty,
                    unit=p["unit"],
                    alert_threshold=threshold
                )
            )
    
    return alerts


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Inventory API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
