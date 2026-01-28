# Copyright (c) 2026, Onco and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ImportationApprovals(Document):
    def validate(self):
        self.validate_items_table()
        self.validate_approval_quantities()
    
    def validate_items_table(self):
        """Ensure items table is not empty and populated from request if needed"""
        if not self.items and self.importation_approval_request:
            # Auto-populate items from the linked request
            self.fetch_request_data()
        
        if not self.items:
            if self.importation_approval_request:
                frappe.throw("No items found in the linked Importation Approval Request. Please check the request document.")
            else:
                frappe.throw("Items table cannot be empty. Please link an Importation Approval Request.")
    
    def fetch_request_data(self):
        """Fetch data from linked Importation Approval Request"""
        if not self.importation_approval_request:
            return
            
        request_doc = frappe.get_doc("Importation Approval Request", self.importation_approval_request)
        
        if not request_doc.items:
            return
        
        # Clear existing items and add all items from request
        self.items = []
        
        for request_item in request_doc.items:
            self.append("items", {
                "item_code": request_item.item_code,
                "item_name": request_item.item_name,
                "supplier": request_item.supplier,
                "requested_qty": request_item.requested_qty,
                # As per HTML: "QUANTIY: AUTIMATICALLY FROM PERVIOUS STEP"
                "approved_qty": request_item.approved_qty,
                "status": "Approved"
            })
    
    def validate_approval_quantities(self):
        """Validate that approval quantities match the request"""
        if not self.importation_approval_request:
            return
            
        request_doc = frappe.get_doc("Importation Approval Request", self.importation_approval_request)
        
        for item in self.items:
            # Find corresponding item in request
            request_item = None
            for req_item in request_doc.items:
                if req_item.item_code == item.item_code:
                    request_item = req_item
                    break
            
            if not request_item:
                frappe.throw(f"Item {item.item_code} not found in the original request")
            
            if item.approved_qty > request_item.requested_qty:
                frappe.throw(f"Approved quantity for {item.item_code} cannot exceed requested quantity")
    
    def on_submit(self):
        """Create approval record and enable further actions"""
        # Check if this is an extension/modification of a closed document
        if self.original_document:
            original_doc = frappe.get_doc("Importation Approvals", self.original_document)
            if original_doc.docstatus == 2:  # Cancelled/Closed
                frappe.msgprint("Original document has been closed. This is the new active approval.")
        
        frappe.msgprint("Importation Approval created successfully. You can now create Purchase Orders, Modifications, or Extensions.")
    
    def before_submit(self):
        """Validate before submission"""
        # Prevent submission if this is not the latest version
        if self.original_document:
            # Check if there are newer versions
            newer_versions = frappe.get_all("Importation Approvals", 
                filters={
                    "original_document": self.original_document,
                    "creation": [">", self.creation],
                    "docstatus": ["!=", 2]
                })
            if newer_versions:
                frappe.throw("Cannot submit - newer version exists. Please use the latest version.")
    
    def validate_purchase_order_creation(self):
        """Validate if Purchase Order can be created from this document"""
        if self.docstatus != 1:
            frappe.throw("Document must be submitted before creating Purchase Order")
        
        # Check if document is closed due to modification/extension
        if self.docstatus == 2:
            frappe.throw("Cannot create Purchase Order from closed document. Use the latest version.")
        
        return True
    
    def validate_approval_quantities(self):
        """Validate that approval quantities match the request"""
        if not self.importation_approval_request:
            return
            
        request_doc = frappe.get_doc("Importation Approval Request", self.importation_approval_request)
        
        for item in self.items:
            # Find corresponding item in request
            request_item = None
            for req_item in request_doc.items:
                if req_item.item_code == item.item_code:
                    request_item = req_item
                    break
            
            if not request_item:
                frappe.throw(f"Item {item.item_code} not found in the original request")
            
            if item.approved_qty > request_item.requested_qty:
                frappe.throw(f"Approved quantity for {item.item_code} cannot exceed requested quantity")

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
    """Create Purchase Order from Importation Approvals"""
    from frappe.model.mapper import get_mapped_doc
    
    # Validate that Purchase Order can be created
    source_doc = frappe.get_doc("Importation Approvals", source_name)
    source_doc.validate_purchase_order_creation()
    
    def set_missing_values(source, target):
        target.importation_approval = source.name
        target.eda_reference = source.name
        # Set supplier from the first item (assuming all items have same supplier)
        if source.items:
            target.supplier = source.items[0].supplier
        
        # Send email notification to supplier if enabled
        if source.send_email_notification and target.supplier:
            custom_email = source.supplier_email if source.supplier_email else None
            send_supplier_notification(target.supplier, source.name, custom_email)
    
    def update_item(source, target, source_parent):
        target.qty = source.approved_qty
        # target.rate = 0  # removed to allow standard pricing logic
        target.item_code = source.item_code
    
    doclist = get_mapped_doc("Importation Approvals", source_name, {
        "Importation Approvals": {
            "doctype": "Purchase Order",
            "field_map": {
                "name": "importation_approval"
            }
        },
        "Importation Approvals Item": {
            "doctype": "Purchase Order Item",
            "postprocess": update_item
        }
    }, target_doc, set_missing_values)
    
    return doclist

def send_supplier_notification(supplier, approval_reference, custom_email=None):
    """Send email notification to supplier about Purchase Order creation"""
    try:
        supplier_doc = frappe.get_doc("Supplier", supplier)
        email_to_send = custom_email or supplier_doc.email_id
        
        if email_to_send:
            frappe.sendmail(
                recipients=[email_to_send],
                subject=f"Purchase Order Created - Reference: {approval_reference}",
                message=f"""
                Dear {supplier_doc.supplier_name},
                
                A Purchase Order has been created based on Importation Approval: {approval_reference}
                
                Please check your portal for details.
                
                Best regards,
                Onco Pharma Team
                """,
                header="Purchase Order Notification"
            )
            frappe.msgprint(f"Email notification sent to {email_to_send}")
        else:
            frappe.msgprint("No email address found for supplier notification")
    except Exception as e:
        frappe.log_error(f"Failed to send supplier notification: {str(e)}")
        # Don't fail the PO creation if email fails

@frappe.whitelist()
def create_modification(source_name, modification_reason, requested_modification, new_conditions):
    """Create modification of Importation Approvals"""
    source_doc = frappe.get_doc("Importation Approvals", source_name)
    
    # Create new approval with MD naming series
    new_doc = frappe.copy_doc(source_doc)
    
    # Update naming series for modification
    if source_doc.approval_type == 'Special Importation (SPIMA)':
        new_doc.naming_series = 'EDA-SPIMA-MD-.YYYY.-.#####'
    elif source_doc.approval_type == 'Annual Importation (APIMA)':
        new_doc.naming_series = 'EDA-APIMA-MD-.YYYY.-.#####'
    
    # Add modification details
    new_doc.is_modification = 1
    new_doc.modification_reason = modification_reason
    new_doc.original_document = source_name
    new_doc.special_conditions = new_conditions or new_doc.special_conditions
    
    new_doc.insert()
    
    # Close original document to prevent further Purchase Orders
    source_doc.db_set('docstatus', 2)  # Cancel the original
    frappe.db.commit()
    
    return new_doc.name

@frappe.whitelist()
def create_extension(source_name, extension_reason, extension_details, new_validation_date, new_quantity=None):
    """Create extension of Importation Approvals"""
    source_doc = frappe.get_doc("Importation Approvals", source_name)
    
    # Create new approval with EX naming series
    new_doc = frappe.copy_doc(source_doc)
    
    # Update naming series for extension
    if source_doc.approval_type == 'Special Importation (SPIMA)':
        new_doc.naming_series = 'EDA-SPIMA-EX-.YYYY.-.######'
    elif source_doc.approval_type == 'Annual Importation (APIMA)':
        new_doc.naming_series = 'EDA-APIMA-EX-.YYYY.-.######'
    
    # Add extension details
    new_doc.is_extension = 1
    new_doc.extension_reason = extension_reason
    new_doc.valid_date = new_validation_date
    new_doc.original_document = source_name
    
    # Update quantities if provided
    if new_quantity:
        for item in new_doc.items:
            item.approved_qty = new_quantity
    
    new_doc.insert()
    
    # Close original document to prevent further Purchase Orders
    source_doc.db_set('docstatus', 2)  # Cancel the original
    frappe.db.commit()
    
    return new_doc.name