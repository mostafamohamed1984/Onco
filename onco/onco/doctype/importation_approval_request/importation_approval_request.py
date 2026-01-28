# Copyright (c) 2026, Onco and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ImportationApprovalRequest(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_approval_quantities()
        
        # "After Saving Status Pending" - Auto-set status to Pending on save if not set
        if not self.status or self.status == "":
            self.status = "Pending"
    
    def calculate_totals(self):
        """Calculate total requested and approved quantities"""
        total_requested = 0
        total_approved = 0
        
        for item in self.items:
            total_requested += item.requested_qty or 0
            total_approved += item.approved_qty or 0
        
        self.total_requested_qty = total_requested
        self.total_approved_qty = total_approved
    
    def validate_approval_quantities(self):
        """Validate that approved quantities don't exceed requested quantities"""
        for item in self.items:
            if item.approved_qty and item.approved_qty > item.requested_qty:
                frappe.throw(f"Approved quantity for {item.item_code} cannot exceed requested quantity")
    
    def on_submit(self):
        """On submit, keep status as Pending unless explicitly approved/refused"""
        # Status remains "Pending" after submission
        # Use the "Approve Request" or "Refuse Request" buttons to change status
        pass

# Whitelisted methods must be at module level (not inside class)
@frappe.whitelist()
def approve_request(docname, approval_type="Totally Approved", items_data=None):
    """Approve the importation approval request
    
    Args:
        docname: Name of the Importation Approval Request
        approval_type: Type of approval (Totally Approved, Partially Approved, Refused)
        items_data: JSON string of item codes and their approved quantities (for reuse in Partial Approval)
    """
    import json
    doc = frappe.get_doc("Importation Approval Request", docname)
    
    if doc.docstatus != 1:
        frappe.throw("Document must be submitted before approval")
    
    # Parse items_data if provided
    approved_quantities = {}
    if items_data:
        if isinstance(items_data, str):
            approved_quantities = json.loads(items_data)
        else:
            approved_quantities = items_data

    # Set approval status and date
    doc.db_set('approval_status', approval_type, update_modified=False)
    doc.db_set('approval_date', frappe.utils.today(), update_modified=False)
    doc.db_set('status', approval_type, update_modified=False)
    
    total_approved = 0
    
    # Update item statuses based on quantities
    for item in doc.items:
        # Determine approved qty based on type
        new_approved_qty = 0
        
        if approval_type == 'Refused':
            new_approved_qty = 0
        elif approval_type == 'Totally Approved':
            new_approved_qty = item.requested_qty
        elif approval_type == 'Partially Approved':
            # Use provided data or fall back to existing/0
            if item.item_code in approved_quantities:
                new_approved_qty = approved_quantities[item.item_code]
            else:
                # If not in data, assume 0 for partial approval safety? 
                # Or keep existing? Let's assume 0 if not explicitly approved in the dialog.
                new_approved_qty = 0
        
        # Update the item's approved quantity in DB
        frappe.db.set_value('Importation Approval Request Item', item.name, 'approved_qty', new_approved_qty, update_modified=False)
        
        # Update item status
        item_status = ''
        if new_approved_qty == 0:
            item_status = 'Refused'
        elif new_approved_qty == item.requested_qty:
            item_status = 'Totally Approved'
        else:
            item_status = 'Partially Approved'
            
        frappe.db.set_value('Importation Approval Request Item', item.name, 'status', item_status, update_modified=False)
        
        total_approved += new_approved_qty

    # Update total approved qty on parent
    doc.db_set('total_approved_qty', total_approved, update_modified=False)
    
    frappe.msgprint(f"Request has been marked as {approval_type}")
    
    return doc.name

@frappe.whitelist()
def make_importation_approval(source_name, target_doc=None):
    """Create Importation Approval from Importation Approval Request"""
    from frappe.model.mapper import get_mapped_doc
    
    def set_missing_values(source, target):
        # Set approval type based on request type
        if source.request_type == 'Special Importation (SPIMR)':
            target.approval_type = 'Special Importation (SPIMA)'
            target.naming_series = 'EDA-SPIMA-.YYYY.-.#####'
        elif source.request_type == 'Annual Importation (APIMR)':
            target.approval_type = 'Annual Importation (APIMA)'
            target.naming_series = 'EDA-APIMA-.YYYY.-.#####'
    
    def update_item(source, target, source_parent):
        # Map all item fields and set approved_qty to approved_qty from request
        target.requested_qty = source.requested_qty
        target.approved_qty = source.approved_qty  # Set to the actual approved quantity
        target.status = "Approved"
    
    doclist = get_mapped_doc("Importation Approval Request", source_name, {
        "Importation Approval Request": {
            "doctype": "Importation Approvals",
            "field_map": {
                "name": "importation_approval_request",
                "original_document": None  # Prevent mapping incompatible types
            }
        },
        "Importation Approval Request Item": {
            "doctype": "Importation Approvals Item",
            "postprocess": update_item
        }
    }, target_doc, set_missing_values)
    
    return doclist

@frappe.whitelist()
def create_modification(source_name, modification_reason, requested_modification, items_to_modify=None):
    """Create modification of Importation Approval Request"""
    import json
    
    source_doc = frappe.get_doc("Importation Approval Request", source_name)
    
    # Create new request
    new_doc = frappe.copy_doc(source_doc)
    
    # Determine new naming series and base prefix
    new_series = ""
    target_prefix = ""
    
    if 'SPIMR' in source_doc.naming_series or 'SPIMR' in source_name:
        new_series = 'EDA-SPIMR-MD-.YYYY.-.#####'
        target_prefix = 'EDA-SPIMR-MD'
    elif 'APIMR' in source_doc.naming_series or 'APIMR' in source_name:
        new_series = 'EDA-APIMR-MD-.YYYY.-.#####'
        target_prefix = 'EDA-APIMR-MD'
        
    new_doc.naming_series = new_series
    
    # Custom Naming Logic to preserve sequence number
    # Extract year and sequence from source name or series
    # Expected formats: EDA-SPIMR-2026-00004 or EDA-SPIMR-MD-2026-00004
    
    parts = source_name.split('-')
    # Try to find the numeric part at the end
    seq_number = parts[-1]
    
    # Handle existing suffixes (remove them to get base number)
    if not seq_number.isdigit():
        # Maybe it has a suffix like 00004-1?
        # But split('-') splits 00004 and 1.
        # Let's assume standard format ends with sequence number or sequence-suffix
        if parts[-1].isdigit():
             seq_number = parts[-1]
        elif parts[-2].isdigit():
             seq_number = parts[-2]
    
    # Reconstruct name: PREFIX-YEAR-SEQ
    # We need the Year. Let's assume current year or source year?
    # Usually we want the year from the source series.
    year = frappe.utils.today().split('-')[0]
    # Ideally reuse source year if present in name
    for part in parts:
        if len(part) == 4 and part.isdigit() and part.startswith('20'):
            year = part
            break
            
    base_name = f"{target_prefix}-{year}-{seq_number}"
    
    # Check for availability
    candidate_name = base_name
    suffix = 0
    
    while frappe.db.exists("Importation Approval Request", candidate_name):
        suffix += 1
        candidate_name = f"{base_name}-{suffix}"
        
    new_doc.name = candidate_name
    
    # Add modification details
    new_doc.is_modification = 1
    new_doc.modification_reason = modification_reason
    new_doc.original_document = source_name
    new_doc.status = "Pending"
    
    # Clear approval data for new modification
    new_doc.approval_status = ""
    new_doc.approval_date = ""
    new_doc.total_approved_qty = 0
    
    # If specific items to modify are provided, update them
    if items_to_modify:
        items_data = json.loads(items_to_modify) if isinstance(items_to_modify, str) else items_to_modify
        for item in new_doc.items:
            if item.item_code in items_data:
                item.requested_qty = items_data[item.item_code].get('new_qty', item.requested_qty)
            item.approved_qty = 0
            item.status = "Pending"
    else:
        for item in new_doc.items:
            item.approved_qty = 0
            item.status = "Pending"
    
    new_doc.insert()
    
    # Close original document
    source_doc.db_set('status', 'Closed - Modified')
    
    return new_doc.name

@frappe.whitelist()
def create_extension(source_name, extension_reason, extension_details, new_validation_date=None, additional_qty=None):
    """Create extension of Importation Approval Request"""
    import json
    
    source_doc = frappe.get_doc("Importation Approval Request", source_name)
    
    # Create new request
    new_doc = frappe.copy_doc(source_doc)
    
    # Determine new naming series and base prefix
    new_series = ""
    target_prefix = ""
    
    if 'SPIMR' in source_doc.naming_series or 'SPIMR' in source_name:
        new_series = 'EDA-SPIMR-EX-.YYYY.-.######'
        target_prefix = 'EDA-SPIMR-EX'
    elif 'APIMR' in source_doc.naming_series or 'APIMR' in source_name:
        new_series = 'EDA-APIMR-EX-.YYYY.-.######'
        target_prefix = 'EDA-APIMR-EX'

    new_doc.naming_series = new_series
    
    # Custom Naming Logic
    parts = source_name.split('-')
    seq_number = parts[-1]
    if not seq_number.isdigit() and len(parts) > 1 and parts[-2].isdigit():
        seq_number = parts[-2] # Handle suffix case
        
    year = frappe.utils.today().split('-')[0]
    for part in parts:
        if len(part) == 4 and part.isdigit() and part.startswith('20'):
            year = part
            break
            
    base_name = f"{target_prefix}-{year}-{seq_number}"
    
    candidate_name = base_name
    suffix = 0
    while frappe.db.exists("Importation Approval Request", candidate_name):
        suffix += 1
        candidate_name = f"{base_name}-{suffix}"
    
    new_doc.name = candidate_name
    
    # Add extension details
    new_doc.is_extension = 1
    new_doc.extension_reason = extension_reason
    new_doc.original_document = source_name
    new_doc.status = "Pending"
    
    # Clear approval data
    new_doc.approval_status = ""
    new_doc.approval_date = ""
    new_doc.total_approved_qty = 0
    
    if additional_qty:
        qty_data = json.loads(additional_qty) if isinstance(additional_qty, str) else additional_qty
        for item in new_doc.items:
            if item.item_code in qty_data:
                additional = qty_data[item.item_code].get('additional_qty', 0)
                item.requested_qty = item.requested_qty + additional
            item.approved_qty = 0
            item.status = "Pending"
    else:
        for item in new_doc.items:
            item.approved_qty = 0
            item.status = "Pending"
    
    new_doc.insert()
    
    # Close original document
    source_doc.db_set('status', 'Closed - Extended')
    
    return new_doc.name