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
def approve_request(docname, approval_type="Totally Approved"):
    """Approve the importation approval request
    
    Args:
        docname: Name of the Importation Approval Request
        approval_type: Type of approval (Totally Approved, Partially Approved, Refused)
    """
    doc = frappe.get_doc("Importation Approval Request", docname)
    
    if doc.docstatus != 1:
        frappe.throw("Document must be submitted before approval")
    
    # Set approval status and date
    doc.db_set('approval_status', approval_type, update_modified=False)
    doc.db_set('approval_date', frappe.utils.today(), update_modified=False)
    doc.db_set('status', approval_type, update_modified=False)
    
    # Update item statuses based on quantities
    for item in doc.items:
        if item.approved_qty == 0:
            frappe.db.set_value('Importation Approval Request Item', item.name, 'status', 'Refused', update_modified=False)
        elif item.approved_qty == item.requested_qty:
            frappe.db.set_value('Importation Approval Request Item', item.name, 'status', 'Totally Approved', update_modified=False)
        else:
            frappe.db.set_value('Importation Approval Request Item', item.name, 'status', 'Partially Approved', update_modified=False)
    
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
        # Map all item fields and set approved_qty to requested_qty as per HTML requirement
        target.requested_qty = source.requested_qty
        target.approved_qty = source.requested_qty  # "QUANTIY: AUTIMATICALLY FROM PERVIOUS STEP"
        target.status = "Approved"
    
    doclist = get_mapped_doc("Importation Approval Request", source_name, {
        "Importation Approval Request": {
            "doctype": "Importation Approvals",
            "field_map": {
                "name": "importation_approval_request"
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
    """Create modification of Importation Approval Request
    
    Args:
        source_name: Original document name
        modification_reason: Reason for modification (Error or Change data and conditions)
        requested_modification: Description of what needs to be modified
        items_to_modify: Optional JSON string of items with their new quantities
    """
    import json
    
    source_doc = frappe.get_doc("Importation Approval Request", source_name)
    
    # Create new request with MD naming series
    new_doc = frappe.copy_doc(source_doc)
    
    # Update naming series for modification
    if source_doc.request_type == 'Special Importation (SPIMR)':
        new_doc.naming_series = 'EDA-SPIMR-MD-.YYYY.-.#####'
    elif source_doc.request_type == 'Annual Importation (APIMR)':
        new_doc.naming_series = 'EDA-APIMR-MD-.YYYY.-.#####'
    
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
        # Reset item approval data
        for item in new_doc.items:
            item.approved_qty = 0
            item.status = "Pending"
    
    new_doc.insert()
    
    # Close original document to prevent further Purchase Orders
    source_doc.db_set('status', 'Closed - Modified')
    
    return new_doc.name

@frappe.whitelist()
def create_extension(source_name, extension_reason, extension_details, new_validation_date=None, additional_qty=None):
    """Create extension of Importation Approval Request
    
    Args:
        source_name: Original document name
        extension_reason: Reason for extension (Validation or Other)
        extension_details: Description of extension
        new_validation_date: Optional new validation date
        additional_qty: Optional JSON string of items with additional quantities
    """
    import json
    
    source_doc = frappe.get_doc("Importation Approval Request", source_name)
    
    # Create new request with EX naming series
    new_doc = frappe.copy_doc(source_doc)
    
    # Update naming series for extension
    if source_doc.request_type == 'Special Importation (SPIMR)':
        new_doc.naming_series = 'EDA-SPIMR-EX-.YYYY.-.######'
    elif source_doc.request_type == 'Annual Importation (APIMR)':
        new_doc.naming_series = 'EDA-APIMR-EX-.YYYY.-.######'
    
    # Add extension details
    new_doc.is_extension = 1
    new_doc.extension_reason = extension_reason
    new_doc.original_document = source_name
    new_doc.status = "Pending"
    
    # Clear approval data for new extension
    new_doc.approval_status = ""
    new_doc.approval_date = ""
    new_doc.total_approved_qty = 0
    
    # If additional quantities are provided, add them to existing quantities
    if additional_qty:
        qty_data = json.loads(additional_qty) if isinstance(additional_qty, str) else additional_qty
        for item in new_doc.items:
            if item.item_code in qty_data:
                additional = qty_data[item.item_code].get('additional_qty', 0)
                item.requested_qty = item.requested_qty + additional
            item.approved_qty = 0
            item.status = "Pending"
    else:
        # Reset item approval data
        for item in new_doc.items:
            item.approved_qty = 0
            item.status = "Pending"
    
    new_doc.insert()
    
    # Close original document to prevent further Purchase Orders
    source_doc.db_set('status', 'Closed - Extended')
    
    return new_doc.name