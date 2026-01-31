"""
Migration Script for Shipments Module Enhancements

This script migrates existing Shipment records to:
1. Populate item_code field in Purchase Invoices child table
2. Ensure status field is properly set based on milestones

Run this after updating the Shipments doctype.

Usage:
    bench --site [site-name] execute onco.migrate_shipment_invoices.migrate_all
"""

import frappe
from frappe import _


def migrate_all():
    """Main migration function"""
    frappe.flags.in_migrate = True
    
    try:
        print("\n" + "="*60)
        print("Starting Shipments Migration")
        print("="*60 + "\n")
        
        migrate_shipment_invoices()
        recalculate_shipment_status()
        
        print("\n" + "="*60)
        print("Migration Completed Successfully")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        frappe.db.rollback()
        raise
    finally:
        frappe.flags.in_migrate = False


def migrate_shipment_invoices():
    """
    Migrate existing Shipment Invoice records to include item_code
    and ensure all items from Purchase Invoices are included
    """
    print("📦 Migrating Shipment Invoice records...")
    
    # Get all Shipments (excluding cancelled)
    shipments = frappe.get_all("Shipments", 
        filters={"docstatus": ["<", 2]},
        fields=["name", "docstatus"]
    )
    
    total = len(shipments)
    updated = 0
    errors = 0
    
    print(f"Found {total} Shipment records to process\n")
    
    for idx, shipment in enumerate(shipments, 1):
        try:
            doc = frappe.get_doc("Shipments", shipment.name)
            modified = False
            
            # Process each row in custom_invoices child table
            if doc.custom_invoices:
                for row in doc.custom_invoices:
                    # Populate item_code if missing
                    if not row.item_code and row.item_name:
                        item_code = get_item_code_from_invoice(
                            row.purchase_invoice, 
                            row.item_name
                        )
                        if item_code:
                            row.item_code = item_code
                            modified = True
                            print(f"  ✓ Updated item_code for {row.item_name} in {shipment.name}")
            
            # Check if there are missing items from the invoices
            missing_items = check_missing_items(doc)
            if missing_items:
                print(f"  ⚠️  Warning: {shipment.name} has {len(missing_items)} missing items")
                print(f"     Consider re-creating this shipment to include all items")
            
            if modified:
                # Save without triggering validations
                doc.flags.ignore_validate = True
                doc.flags.ignore_mandatory = True
                doc.save()
                updated += 1
                
            if (idx % 10 == 0) or (idx == total):
                print(f"Progress: {idx}/{total} processed")
                frappe.db.commit()
                
        except Exception as e:
            errors += 1
            print(f"  ❌ Error processing {shipment.name}: {str(e)}")
            continue
    
    print(f"\n✅ Migration complete: {updated} updated, {errors} errors\n")


def get_item_code_from_invoice(purchase_invoice, item_name):
    """Get item_code from Purchase Invoice Item"""
    if not purchase_invoice or not item_name:
        return None
    
    try:
        pi_items = frappe.get_all("Purchase Invoice Item",
            filters={
                "parent": purchase_invoice,
                "item_name": item_name
            },
            fields=["item_code"],
            limit=1
        )
        
        if pi_items:
            return pi_items[0].item_code
    except Exception as e:
        print(f"    Error fetching item_code: {str(e)}")
    
    return None


def check_missing_items(shipment_doc):
    """
    Check if there are items in the linked Purchase Invoices
    that are not in the Shipments child table
    """
    if not shipment_doc.custom_invoices:
        return []
    
    # Get unique invoices
    invoices = list(set([row.purchase_invoice for row in shipment_doc.custom_invoices if row.purchase_invoice]))
    
    if not invoices:
        return []
    
    # Get all items from these invoices
    invoice_items = frappe.get_all("Purchase Invoice Item",
        filters={"parent": ["in", invoices]},
        fields=["item_code", "item_name", "parent"]
    )
    
    # Get items in shipment child table
    shipment_items = set([row.item_code for row in shipment_doc.custom_invoices if row.item_code])
    
    # Find missing items
    missing = []
    for item in invoice_items:
        if item.item_code not in shipment_items:
            missing.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "invoice": item.parent
            })
    
    return missing


def recalculate_shipment_status():
    """
    Recalculate status for all Shipments based on milestone completion
    """
    print("🔄 Recalculating Shipment statuses...")
    
    shipments = frappe.get_all("Shipments", 
        filters={"docstatus": ["<", 2]},
        fields=["name"]
    )
    
    total = len(shipments)
    updated = 0
    
    for idx, shipment in enumerate(shipments, 1):
        try:
            doc = frappe.get_doc("Shipments", shipment.name)
            old_status = doc.status
            
            # Recalculate status
            doc.flags.status_updated_by_system = True
            doc.calculate_milestone_completion()
            
            if old_status != doc.status:
                doc.save()
                updated += 1
                print(f"  ✓ Updated {shipment.name}: {old_status} → {doc.status}")
            
            if (idx % 10 == 0) or (idx == total):
                frappe.db.commit()
                
        except Exception as e:
            print(f"  ❌ Error processing {shipment.name}: {str(e)}")
            continue
    
    print(f"\n✅ Status recalculation complete: {updated} updated\n")


def generate_migration_report():
    """
    Generate a report of Shipments that may need attention
    """
    print("📊 Generating Migration Report...\n")
    
    # Shipments with missing item_codes
    shipments_missing_codes = frappe.db.sql("""
        SELECT 
            s.name as shipment,
            si.purchase_invoice,
            si.item_name,
            si.item_code
        FROM `tabShipments` s
        INNER JOIN `tabPurchase Invoices` si ON si.parent = s.name
        WHERE s.docstatus < 2
        AND (si.item_code IS NULL OR si.item_code = '')
    """, as_dict=True)
    
    if shipments_missing_codes:
        print(f"⚠️  Found {len(shipments_missing_codes)} rows with missing item_code:")
        for row in shipments_missing_codes[:10]:  # Show first 10
            print(f"   - {row.shipment}: {row.item_name}")
        if len(shipments_missing_codes) > 10:
            print(f"   ... and {len(shipments_missing_codes) - 10} more")
    else:
        print("✅ All rows have item_code populated")
    
    print()


if __name__ == "__main__":
    migrate_all()
    generate_migration_report()
