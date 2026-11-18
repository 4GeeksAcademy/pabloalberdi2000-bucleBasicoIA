"""
Test script to demonstrate the agent working with the inventory API.
This shows how the agent loop works with function calling.
"""

import os
import json
import csv
import time
import subprocess
import sys
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent
API_SCRIPT = REPO_ROOT / "api" / "app.py"
AGENT_SCRIPT = REPO_ROOT / "agent.py"
CONVERSATION_LOG = REPO_ROOT / "conversation_log.csv"

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_api():
    """Test that the API is running and responding."""
    import httpx
    
    print_header("🧪 Testing API Connectivity")
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get("http://localhost:8000/health")
            response.raise_for_status()
            print("✓ API is running and responding")
            print(f"  Response: {response.json()}")
            return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("   Make sure the API is running in another terminal:")
        print("   python -m uvicorn api.app:app --host 0.0.0.0 --port 8000")
        return False

def test_inventory_endpoints():
    """Test the inventory API endpoints."""
    import httpx
    
    print_header("🧪 Testing Inventory Endpoints")
    
    with httpx.Client(timeout=10.0) as client:
        # Test 1: Add products
        products_to_add = [
            {"name": "Café Arábica", "quantity": 25.5, "unit": "kg"},
            {"name": "Leche de Avena", "quantity": 12, "unit": "litros"},
            {"name": "Chocolate", "quantity": 5, "unit": "kg"},
            {"name": "Vasos", "quantity": 150, "unit": "unidades"},
        ]
        
        print("1️⃣  Adding test products...")
        for product in products_to_add:
            response = client.post("http://localhost:8000/inventory", json=product)
            if response.status_code == 201:
                data = response.json()
                print(f"   ✓ {data['name']} (ID: {data['product_id']}, {data['quantity']} {data['unit']})")
            else:
                print(f"   ❌ Failed to add {product['name']}: {response.text}")
        
        # Test 2: Get inventory
        print("\n2️⃣  Retrieving inventory...")
        response = client.get("http://localhost:8000/inventory")
        if response.status_code == 200:
            inventory = response.json()
            print(f"   ✓ Retrieved {len(inventory)} products")
            for product in inventory:
                print(f"      - {product['name']}: {product['quantity']} {product['unit']}")
        
        # Test 3: Update stock
        print("\n3️⃣  Updating stock (Chocolate: +10 kg)...")
        response = client.patch("http://localhost:8000/inventory/3", json={"delta": 10})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Updated: {data['name']} now has {data['quantity']} {data['unit']}")
        
        # Test 4: Check alerts
        print("\n4️⃣  Checking low-stock alerts...")
        response = client.get("http://localhost:8000/inventory/alerts", params={"threshold": 15})
        if response.status_code == 200:
            alerts = response.json()
            if alerts:
                print(f"   ✓ Found {len(alerts)} products below threshold:")
                for alert in alerts:
                    print(f"      ⚠️  {alert['name']}: {alert['quantity']} {alert['unit']} (threshold: {alert['alert_threshold']})")
            else:
                print("   ✓ No products below threshold")

def show_conversation_log():
    """Display the conversation log if it exists."""
    if not CONVERSATION_LOG.exists():
        print("   (No conversation log yet)")
        return
    
    print_header("📋 Conversation Log (Last 10 entries)")
    
    with open(CONVERSATION_LOG, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Show last 10 entries
    for row in rows[-10:]:
        actor = row["actor"].upper()
        icon = {"USER": "👤", "AGENT": "🤖", "TOOL": "🔧"}.get(actor, "•")
        message = row["message"][:60] + "..." if len(row["message"]) > 60 else row["message"]
        tool_call = f" [{row['tool_call']}]" if row["tool_call"] else ""
        
        print(f"  {icon} {actor}{tool_call}: {message}")

def main():
    print_header("🏪 Inventory Management System - Test Suite")
    
    # Test dependencies
    print("📦 Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import httpx
        print("   ✓ FastAPI, Uvicorn, and httpx installed")
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        sys.exit(1)
    
    # Test API connectivity
    if not test_api():
        print("\n❌ Cannot proceed without API running")
        sys.exit(1)
    
    # Test inventory endpoints
    test_inventory_endpoints()
    
    # Show conversation log
    show_conversation_log()
    
    print_header("✅ Test Suite Completed")
    print("Next steps:")
    print("  1. The API is running on http://localhost:8000")
    print("  2. Run the agent in another terminal:")
    print("     python agent.py")
    print("  3. Chat with the agent about inventory operations")
    print()

if __name__ == "__main__":
    main()
