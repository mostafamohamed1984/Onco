#!/usr/bin/env python3
"""
Setup Test Data for Importation Cycle Testing
Run this script to create the necessary master data for testing
"""

import frappe

def setup_test_data():
    """Create test data for importation cycle testing"""
    
    print("Setting up test data for Importation Cycle testing...")
    
    # Create Test Suppliers
    suppliers = [
        {
            "supplier_name": "Test Supplier A",
            "supplier_group": "All Supplier Groups",
            "email_id": "supplier.a@test.com",
            "country": "Egypt"
        },
        {
            "supplier_name": "Test Supplier B", 
            "supplier_group": "All Supplier Groups",
            "email_id": "supplier.b@test.com",
            "country": "Egypt"
        }
    ]
    
    for supplier_data in suppliers:
        if not frappe.db.exists("Supplier", supplier_data["supplier_name"]):
            supplier = frappe.get_doc({
                "doctype": "Supplier",
                **supplier_data
            })
            supplier.insert()
            print(f"✅ Created Supplier: {supplier_data['supplier_name']}")
        else:
            print(f"⚠️  Supplier already exists: {supplier_data['supplier_name']}")
    
    # Create Test Customers
    customers = [
        {
            "customer_name": "Test Customer 1",
            "customer_group": "All Customer Groups",
            "territory": "All Territories",
            "customer_type": "Company"
        },
        {
            "customer_name": "Test Customer 2",
            "customer_group": "All Customer Groups", 
            "territory": "All Territories",
            "customer_type": "Company"
        }
    ]
    
    for customer_data in customers:
        if not frappe.db.exists("Customer", customer_data["customer_name"]):
            customer = frappe.get_doc({
                "doctype": "Customer",
                **customer_data
            })
            customer.insert()
            print(f"✅ Created Customer: {customer_data['customer_name']}")
        else:
            print(f"⚠️  Customer already exists: {customer_data['customer_name']}")
    
    # Create Test Items
    items = [
        {
            "item_code": "TEST-ITEM-001",
            "item_name": "Test Pharmaceutical Item 001",
            "item_group": "All Item Groups",
            "stock_uom": "Nos",
            "default_supplier": "Test Supplier A",
            "is_stock_item": 1
        },
        {
            "item_code": "TEST-ITEM-002", 
            "item_name": "Test Pharmaceutical Item 002",
            "item_group": "All Item Groups",
            "stock_uom": "Nos",
            "default_supplier": "Test Supplier B",
            "is_stock_item": 1
        },
        {
            "item_code": "TEST-ITEM-003",
            "item_name": "Test Pharmaceutical Item 003", 
            "item_group": "All Item Groups",
            "stock_uom": "Nos",
            "default_supplier": "Test Supplier A",
            "is_stock_item": 1
        }
    ]
    
    for item_data in items:
        if not frappe.db.exists("Item", item_data["item_code"]):
            item = frappe.get_doc({
                "doctype": "Item",
                **item_data
            })
            item.insert()
            print(f"✅ Created Item: {item_data['item_code']}")
        else:
            print(f"⚠️  Item already exists: {item_data['item_code']}")
    
    frappe.db.commit()
    print("\n🎉 Test data setup completed!")
    print("\nYou can now start testing with:")
    print("- Items: TEST-ITEM-001, TEST-ITEM-002, TEST-ITEM-003")
    print("- Suppliers: Test Supplier A, Test Supplier B")
    print("- Customers: Test Customer 1, Test Customer 2")
    print("\nNext steps:")
    print("1. Go to Onco > Importation Approval Request > New")
    print("2. Follow the testing guide in IMPORTATION_CYCLE_TESTING_GUIDE.md")

if __name__ == "__main__":
    setup_test_data()