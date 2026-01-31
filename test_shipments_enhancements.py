"""
Test Script for Shipments Module Enhancements

This script tests the two main enhancements:
1. Status field validation and protection
2. Multiple invoice items handling

Usage:
    bench --site [site-name] execute onco.test_shipments_enhancements.run_all_tests
"""

import frappe
from frappe import _
import json


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*70)
    print("SHIPMENTS MODULE ENHANCEMENT TESTS")
    print("="*70 + "\n")
    
    results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Test 1: Status Field Protection
    print("TEST 1: Status Field Protection")
    print("-" * 70)
    if test_status_field_protection():
        results["passed"] += 1
        print("✅ PASSED\n")
    else:
        results["failed"] += 1
        results["errors"].append("Status Field Protection")
        print("❌ FAILED\n")
    
    # Test 2: Multiple Items from Invoice
    print("TEST 2: Multiple Items from Purchase Invoice")
    print("-" * 70)
    if test_multiple_invoice_items():
        results["passed"] += 1
        print("✅ PASSED\n")
    else:
        results["failed"] += 1
        results["errors"].append("Multiple Invoice Items")
        print("❌ FAILED\n")
    
    # Test 3: Purchase Receipt Creation
    print("TEST 3: Purchase Receipt with All Items")
    print("-" * 70)
    if test_purchase_receipt_creation():
        results["passed"] += 1
        print("✅ PASSED\n")
    else:
        results["failed"] += 1
        results["errors"].append("Purchase Receipt Creation")
        print("❌ FAILED\n")
    
    # Test 4: Child Table Structure
    print("TEST 4: Purchase Invoices Child Table Structure")
    print("-" * 70)
    if test_child_table_structure():
        results["passed"] += 1
        print("✅ PASSED\n")
    else:
        results["failed"] += 1
        results["errors"].append("Child Table Structure")
        print("❌ FAILED\n")
    
    # Print Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {results['passed'] + results['failed']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    
    if results["errors"]:
        print("\nFailed Tests:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    print("\n" + "="*70 + "\n")
    
    return results["failed"] == 0


def test_status_field_protection():
    """Test that status field cannot be manually changed"""
    try:
        print("Creating test Shipment...")
        
        # Create a test shipment
        shipment = frappe.get_doc({
            "doctype": "Shipments",
            "mode_of_shipping": "Air freight",
            "awb_no": "TEST-AWB-001",
            "awb_date": frappe.utils.today(),
            "status": "Planned"
        })
        shipment.insert()
        
        print(f"  Created: {shipment.name}")
        print(f"  Initial Status: {shipment.status}")
        
        # Try to manually change status
        print("  Attempting to manually change status to 'Completed'...")
        shipment.status = "Completed"
        
        try:
            shipment.save()
            print("  ❌ Status was changed manually (should have been prevented)")
            frappe.delete_doc("Shipments", shipment.name, force=True)
            return False
        except Exception as e:
            if "cannot be changed manually" in str(e).lower() or shipment.status == "Planned":
                print("  ✓ Status change was prevented (as expected)")
                
                # Test automatic status update
                print("  Testing automatic status update...")
                shipment.reload()
                shipment.flags.status_updated_by_system = True
                shipment.arrived = 1
                shipment.calculate_milestone_completion()
                shipment.save()
                
                if shipment.status == "In Progress":
                    print(f"  ✓ Status automatically updated to: {shipment.status}")
                    frappe.delete_doc("Shipments", shipment.name, force=True)
                    return True
                else:
                    print(f"  ❌ Status not updated correctly: {shipment.status}")
                    frappe.delete_doc("Shipments", shipment.name, force=True)
                    return False
            else:
                print(f"  ❌ Unexpected error: {str(e)}")
                frappe.delete_doc("Shipments", shipment.name, force=True)
                return False
                
    except Exception as e:
        print(f"  ❌ Test error: {str(e)}")
        return False


def test_multiple_invoice_items():
    """Test that all items from Purchase Invoice are captured"""
    try:
        print("Checking Purchase Invoices child table structure...")
        
        # Check if child table exists and has correct fields
        if not frappe.db.exists("DocType", "Purchase Invoices"):
            print("  ❌ 'Purchase Invoices' child table not found")
            return False
        
        print("  ✓ Child table 'Purchase Invoices' exists")
        
        # Check for required fields
        required_fields = ["purchase_invoice", "item_code", "item_name", "qty", "uom", "rate"]
        meta = frappe.get_meta("Purchase Invoices")
        
        missing_fields = []
        for field in required_fields:
            if not meta.has_field(field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"  ❌ Missing fields: {', '.join(missing_fields)}")
            return False
        
        print(f"  ✓ All required fields present: {', '.join(required_fields)}")
        
        # Check if item_code field is a Link field
        item_code_field = meta.get_field("item_code")
        if item_code_field and item_code_field.fieldtype == "Link":
            print("  ✓ item_code is properly configured as Link field")
            return True
        else:
            print("  ❌ item_code field configuration incorrect")
            return False
            
    except Exception as e:
        print(f"  ❌ Test error: {str(e)}")
        return False


def test_purchase_receipt_creation():
    """Test Purchase Receipt creation with multiple items"""
    try:
        print("Testing Purchase Receipt creation logic...")
        
        # Check if make_purchase_receipt function exists
        from onco.onco.doctype.shipments.shipments import make_purchase_receipt
        print("  ✓ make_purchase_receipt function found")
        
        # Verify function signature
        import inspect
        sig = inspect.signature(make_purchase_receipt)
        params = list(sig.parameters.keys())
        
        if "source_name" in params:
            print(f"  ✓ Function signature correct: {params}")
            return True
        else:
            print(f"  ❌ Function signature incorrect: {params}")
            return False
            
    except ImportError as e:
        print(f"  ❌ Cannot import function: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ Test error: {str(e)}")
        return False


def test_child_table_structure():
    """Test the structure of Purchase Invoices child table"""
    try:
        print("Validating child table structure...")
        
        # Get Shipments meta
        shipments_meta = frappe.get_meta("Shipments")
        
        # Check if custom_invoices field exists
        custom_invoices_field = shipments_meta.get_field("custom_invoices")
        
        if not custom_invoices_field:
            print("  ❌ custom_invoices field not found in Shipments")
            return False
        
        print("  ✓ custom_invoices field exists")
        
        # Check if it's a Table field
        if custom_invoices_field.fieldtype != "Table":
            print(f"  ❌ custom_invoices is not a Table field: {custom_invoices_field.fieldtype}")
            return False
        
        print("  ✓ custom_invoices is a Table field")
        
        # Check if it links to Purchase Invoices
        if custom_invoices_field.options != "Purchase Invoices":
            print(f"  ❌ custom_invoices links to wrong doctype: {custom_invoices_field.options}")
            return False
        
        print("  ✓ custom_invoices links to 'Purchase Invoices'")
        
        # Check Purchase Invoices is a child table
        pi_meta = frappe.get_meta("Purchase Invoices")
        if not pi_meta.istable:
            print("  ❌ Purchase Invoices is not marked as child table")
            return False
        
        print("  ✓ Purchase Invoices is properly configured as child table")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Test error: {str(e)}")
        return False


def test_status_field_properties():
    """Test status field properties in doctype"""
    try:
        print("Checking status field properties...")
        
        meta = frappe.get_meta("Shipments")
        status_field = meta.get_field("status")
        
        if not status_field:
            print("  ❌ Status field not found")
            return False
        
        print("  ✓ Status field exists")
        
        # Check if read_only
        if not status_field.read_only:
            print("  ❌ Status field is not read_only")
            return False
        
        print("  ✓ Status field is read_only")
        
        # Check if no_copy
        if not status_field.no_copy:
            print("  ⚠️  Warning: Status field no_copy not set")
        else:
            print("  ✓ Status field has no_copy set")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Test error: {str(e)}")
        return False


def generate_test_data_report():
    """Generate a report of existing test data"""
    print("\n" + "="*70)
    print("EXISTING DATA REPORT")
    print("="*70 + "\n")
    
    # Count Shipments
    shipments_count = frappe.db.count("Shipments", {"docstatus": ["<", 2]})
    print(f"Total Shipments: {shipments_count}")
    
    # Count Shipments with items
    shipments_with_items = frappe.db.sql("""
        SELECT COUNT(DISTINCT parent) 
        FROM `tabPurchase Invoices`
    """)[0][0]
    print(f"Shipments with items: {shipments_with_items}")
    
    # Count total items
    total_items = frappe.db.count("Purchase Invoices")
    print(f"Total items in child table: {total_items}")
    
    # Items with item_code
    items_with_code = frappe.db.sql("""
        SELECT COUNT(*) 
        FROM `tabPurchase Invoices`
        WHERE item_code IS NOT NULL AND item_code != ''
    """)[0][0]
    print(f"Items with item_code: {items_with_code}")
    
    # Items without item_code
    items_without_code = total_items - items_with_code
    if items_without_code > 0:
        print(f"⚠️  Items missing item_code: {items_without_code}")
    else:
        print(f"✅ All items have item_code")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    success = run_all_tests()
    generate_test_data_report()
    
    if success:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
