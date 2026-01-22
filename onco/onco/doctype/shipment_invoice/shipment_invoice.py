# Copyright (c) 2026, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ShipmentInvoice(Document):
	def validate(self):
		# Auto-populate invoice details if purchase_invoice is set
		if self.purchase_invoice and not self.invoice_number:
			try:
				invoice = frappe.get_doc("Purchase Invoice", self.purchase_invoice)
				self.invoice_number = invoice.name
				self.invoice_date = invoice.posting_date
				
				# Populate first item if available
				if invoice.items and len(invoice.items) > 0:
					first_item = invoice.items[0]
					self.item = first_item.item_code
					self.quantity = first_item.qty
					
					# Try to get batch from item or stock ledger
					if first_item.batch_no:
						self.batch_number = first_item.batch_no
					else:
						# Fetch from stock ledger directly
						sle = frappe.get_all("Stock Ledger Entry",
							filters={"voucher_no": self.purchase_invoice, "item_code": first_item.item_code},
							fields=["batch_no"],
							order_by="posting_date desc",
							limit=1)
						
						if sle and sle[0].get("batch_no"):
							self.batch_number = sle[0].batch_no
			except Exception as e:
				frappe.log_error(f"Error populating invoice details: {str(e)}")
