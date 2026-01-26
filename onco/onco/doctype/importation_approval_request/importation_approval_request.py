# Copyright (c) 2026, Onco and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ImportationApprovalRequest(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_approval_quantities()
        
        # "After Saving Status Pending" - Auto-set status to Pending on save
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
        """Update status based on approval quantities"""
        self.update_approval_status()
    
    def update_approval_status(self):
        """Update status based on approved vs requested quantities"""
        if self.total_approved_qty == 0:
            self.status = "Refused"
        elif self.total_approved_qty == self.total_requested_qty:
            self.status = "Totally Approved"
        else:
            self.status = "Partially Approved"
        
        # Update item statuses
        for item in self.items:
            if item.approved_qty == 0:
                item.status = "Refused"
            elif item.approved_qty == item.requested_qty:
                item.status = "Totally Approved"
            else:
                item.status = "Partially Approved"

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
        
        # Ensure we have items - if no items with approved qty, include all items
        if not target.items:
            # Get source document and add all items
            source_doc = frappe.get_doc("Importation Approval Request", source_name)
            for source_item in source_doc.items:
                target.append("items", {
                    "item_code": source_item.item_code,
                    "item_name": source_item.item_name,
                    "supplier": source_item.supplier,
                    "requested_qty": source_item.requested_qty,
                    "approved_qty": source_item.approved_qty or source_item.requested_qty,
                    "status": "Approved"
                })
    
    def update_item(source, target, source_parent):
        # Always include items, set approved qty to requested qty if not set
        target.requested_qty = source.requested_qty
        target.approved_qty = source.approved_qty or source.requested_qty
        target.status = source.status or "Approved"
    
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
def create_modification(source_name, modification_reason, requested_modification):
    """Create modification of Importation Approval Request"""
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
    
    # Reset item approval data
    for item in new_doc.items:
        item.approved_qty = 0
        item.status = "Pending"
    
    new_doc.insert()
    
    # Close original document to prevent further Purchase Orders
    source_doc.db_set('status', 'Closed - Modified')
    
    return new_doc.name

@frappe.whitelist()
def create_extension(source_name, extension_reason, extension_details, new_validation_date):
    """Create extension of Importation Approval Request"""
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
    
    # Reset item approval data
    for item in new_doc.items:
        item.approved_qty = 0
        item.status = "Pending"
    
    new_doc.insert()
    
    # Close original document to prevent further Purchase Orders
    source_doc.db_set('status', 'Closed - Extended')
    
    return new_doc.name