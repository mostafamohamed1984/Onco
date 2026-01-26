# Copyright (c) 2026, Onco and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ImportationApprovalsItem(Document):
    def validate(self):
        """Validate item data"""
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