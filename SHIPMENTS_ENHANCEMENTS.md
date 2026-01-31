# Shipments Module Enhancements

## Overview
This document describes the enhancements made to the Shipments module to address two critical customer requirements:

1. **Status Field Validation**: Prevent users from manually bypassing the status sequence
2. **Multiple Invoice Items Handling**: Properly fetch and display all items from Purchase Invoices

## Changes Implemented

### 1. Status Field Protection

#### Problem
Users could manually edit the status field and bypass the workflow sequence (Planned → In Progress → Completed), which breaks the business logic.

#### Solution
- Made status field truly read-only with additional properties:
  - `read_only: 1`
  - `no_copy: 1`
  - `allow_on_submit: 0`
  
- Enhanced Python validation in `shipments.py`:
  - Added `validate_status_sequence()` method to check for manual changes
  - Added `before_save()` method to revert any manual status changes
  - Status can only be updated by the system through `calculate_milestone_completion()`
  - System sets `flags.status_updated_by_system = True` when updating status programmatically

#### Files Modified
- `Onco/onco/onco/doctype/shipments/shipments.json`
- `Onco/onco/onco/doctype/shipments/shipments.py`

### 2. Multiple Invoice Items Handling

#### Problem
When creating a Shipment from a Purchase Invoice with multiple items (from multiple Purchase Orders), only the first item was being fetched and displayed in the Shipments child table.

#### Solution

##### A. Child Table Restructuring
- Renamed child table from "Shipment Invoice" to "Purchase Invoices" for clarity
- Added `item_code` field to properly track items
- Structure now supports one row per item per invoice:
  ```
  Invoice A - Item 1
  Invoice A - Item 2
  Invoice A - Item 3
  Invoice B - Item 1
  Invoice B - Item 2
  ```

##### B. Client Script Enhancement
Updated `create_shipments_btn.js` to:
- Fetch complete Purchase Invoice with all items
- Create one row in the child table for each item
- Populate all item details including:
  - `item_code`
  - `item_name`
  - `qty`
  - `uom`
  - `rate`
  - `amount`
  - `batch_no`
  - `expiry_date`

##### C. Purchase Receipt Creation
Enhanced `make_purchase_receipt()` function to:
- Collect all items from the Purchase Invoices child table
- Group items by invoice
- Create Purchase Receipt with all items from all linked invoices
- Properly map item details including warehouse, batch, and expiry information

#### Files Modified
- `Onco/onco/onco/doctype/shipment_invoice/shipment_invoice.json` (renamed to Purchase Invoices)
- `Onco/onco/onco/doctype/shipments/shipments.json`
- `Onco/onco/onco/doctype/shipments/shipments.js`
- `Onco/onco/onco/doctype/shipments/shipments.py`
- `Onco/onco/onco/client scripts/create_shipments_btn.js`

## Data Flow

The complete workflow now properly handles multiple items:

```
Importation Approval Request (EDA-IMAR)
  ↓ Create Importation Approval button
Importation Approvals (EDA-IMA)
  ↓ Create Purchase Order button
Purchase Order (Standard ERPNext) - Multiple POs possible
  ↓ Standard ERPNext workflow
Purchase Invoice (Standard ERPNext) - Can consolidate multiple POs
  ↓ Create Shipments button (ALL items fetched)
Shipments (Enhanced Custom)
  ↓ Purchase Invoices child table (one row per item)
  ↓ Create Purchase Receipt button
Purchase Receipt (Standard ERPNext) - All items included
  ↓ Link to Purchase Receipt Report
Purchase Receipt Report (Existing Custom)
  ↓ Fetch Items button
Authority Good Release (Enhanced)
  ↓ Auto Stock Transfer
Stock Entry (Standard ERPNext)
```

## Key Features

### Purchase Invoices Child Table Fields
- `purchase_invoice` (Link): Reference to Purchase Invoice
- `invoice_no` (Data): Invoice number for display
- `invoice_date` (Date): Invoice date
- `item_code` (Link): Item code reference
- `item_name` (Data): Item name
- `qty` (Float): Quantity
- `uom` (Data): Unit of measure
- `rate` (Currency): Rate per unit
- `amount` (Currency): Total amount
- `batch_no` (Data): Batch number
- `expiry_date` (Date): Expiry date

### Status Workflow Protection
The status field follows this sequence automatically:
1. **Planned**: Initial state when Shipment is created
2. **In Progress**: When any milestone is completed
3. **Completed**: When all milestones are completed
4. **Cancelled**: Manual cancellation only

Milestones tracked:
- Arrived
- Bank Authenticated
- Restricted Release Status
- Customs Release Status
- Received at Warehouse

## Testing Checklist

### Status Validation Testing
- [ ] Create new Shipment - status should be "Planned"
- [ ] Try to manually change status field - should be prevented
- [ ] Complete first milestone - status should auto-update to "In Progress"
- [ ] Complete all milestones - status should auto-update to "Completed"
- [ ] Try to change status via API - should be prevented

### Multiple Items Testing
- [ ] Create Purchase Invoice with multiple items from multiple POs
- [ ] Click "Create Shipments" button
- [ ] Verify all items appear in Purchase Invoices child table
- [ ] Verify each row has correct item_code, qty, rate, etc.
- [ ] Submit Shipment when completed
- [ ] Create Purchase Receipt - verify all items are included
- [ ] Verify warehouse assignments are correct

## Migration Notes

### For Existing Shipments
If you have existing Shipments with the old "Shipment Invoice" child table:

1. The child table has been renamed to "Purchase Invoices"
2. An `item_code` field has been added
3. Existing data should be migrated to populate the `item_code` field

### Migration Script (if needed)
```python
import frappe

def migrate_shipment_invoices():
    """Migrate existing Shipment Invoice records to include item_code"""
    shipments = frappe.get_all("Shipments", filters={"docstatus": ["<", 2]})
    
    for shipment in shipments:
        doc = frappe.get_doc("Shipments", shipment.name)
        
        for row in doc.custom_invoices:
            if not row.item_code and row.item_name:
                # Try to find item_code from Purchase Invoice
                pi_items = frappe.get_all("Purchase Invoice Item",
                    filters={
                        "parent": row.purchase_invoice,
                        "item_name": row.item_name
                    },
                    fields=["item_code"],
                    limit=1
                )
                
                if pi_items:
                    row.item_code = pi_items[0].item_code
        
        doc.save()
        frappe.db.commit()
```

## Benefits

1. **Data Integrity**: Status field cannot be manipulated, ensuring workflow compliance
2. **Complete Item Tracking**: All items from Purchase Invoices are properly tracked
3. **Accurate Stock Management**: Purchase Receipts include all items with correct quantities
4. **Better Traceability**: Each item is individually tracked with batch and expiry information
5. **Scalability**: Supports multiple Purchase Orders consolidated into one Purchase Invoice

## Support

For issues or questions regarding these enhancements, please refer to:
- Shipments workflow documentation: `Onco/onco/onco/importation_cycle_workflow.md`
- Implementation plan: `Onco/IMPORTATION_CYCLE_IMPLEMENTATION_PLAN.md`
