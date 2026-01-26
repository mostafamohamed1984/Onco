# Copyright (c) 2026, Onco and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ImportationApprovalsItem(Document):
    def validate(self):
        """Validate item data"""
        # Validate pharmaceutical item requirements
        self.validate_pharmaceutical_item()
        
        # Validate that approved quantity doesn't exceed requested quantity
        if self.approved_qty and self.requested_qty and self.approved_qty > self.requested_qty:
            frappe.throw(f"Approved quantity ({self.approved_qty}) cannot exceed requested quantity ({self.requested_qty}) for item {self.item_code}")
        
        # Auto-set status based on approved quantity
        if self.approved_qty == 0:
            self.status = "Refused"
        elif self.approved_qty == self.requested_qty:
            self.status = "Approved"
        elif self.approved_qty > 0 and self.approved_qty < self.requested_qty:
            self.status = "Partially Approved"
    
    def validate_pharmaceutical_item(self):
        """Validate pharmaceutical item requirements for importation approvals"""
        if not self.item_code:
            return
            
        # Get item details
        item_doc = frappe.get_doc("Item", self.item_code)
        
        # Check if this is a pharmaceutical item
        if hasattr(item_doc, 'custom_pharmaceutical_item') and item_doc.custom_pharmaceutical_item:
            # For pharmaceutical items in importation approvals, ensure label verification requirements
            # Based on HTML: "Label verification – product name, strength, batch #, expiry, storage"
            
            if hasattr(item_doc, 'custom_registered') and item_doc.custom_registered:
                # Ensure all label verification fields are present
                verification_fields = []
                
                if not item_doc.item_name:
                    verification_fields.append("Product Name")
                
                if not hasattr(item_doc, 'strength') or not item_doc.strength:
                    verification_fields.append("Strength")
                
                if not hasattr(item_doc, 'custom_batch_no') or not item_doc.custom_batch_no:
                    verification_fields.append("Batch #")
                
                if not hasattr(item_doc, 'custom_expiry_date') or not item_doc.custom_expiry_date:
                    verification_fields.append("Expiry Date")
                
                if not hasattr(item_doc, 'custom_storage_instructions') or not item_doc.custom_storage_instructions:
                    verification_fields.append("Storage Instructions")
                
                if verification_fields:
                    frappe.throw(f"Pharmaceutical item {self.item_code} fails label verification. Missing: {', '.join(verification_fields)}. Required for importation approval.")
                
                # Additional validation for expiry date
                if item_doc.custom_expiry_date and item_doc.custom_expiry_date <= frappe.utils.today():
                    frappe.throw(f"Cannot approve expired pharmaceutical item {self.item_code} (Expiry: {item_doc.custom_expiry_date})")