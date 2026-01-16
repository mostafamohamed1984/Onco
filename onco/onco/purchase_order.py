# Copyright (c) 2025, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class CustomPurchaseOrder(Document):
	"""
	Custom Purchase Order class to override autoname method
	Format: PO-YYYY-XXXX-ZZZ
	- YYYY: Year from transaction_date
	- XXXX: Sequential count of POs in that year (4 digits)
	- ZZZ: Count of how many times this item has appeared in any PO (3 digits)
	
	Note: Each Purchase Order should contain exactly one item.
	"""
	
	def autoname(self):
		"""
		Custom autoname method for Purchase Order
		Format: PO-YYYY-XXXX-ZZZ
		"""
		# Validate that there is at least one item
		if not self.items or len(self.items) == 0:
			frappe.throw("Purchase Order must contain at least one item.")
		
		# Get the item code from the first item
		# Since each PO has only one item, we use the first item
		item_code = self.items[0].item_code
		if not item_code:
			frappe.throw("Item code is required in Purchase Order items.")
		
		# Get the year from transaction_date field (required)
		if not self.transaction_date:
			frappe.throw("Transaction Date is required for Purchase Order naming.")
		
		transaction_date = getdate(self.transaction_date)
		year = transaction_date.year
		
		# Format year as YYYY
		year_str = str(year)
		
		# Calculate XXXX: Count of POs created in this year
		# Query existing POs with names matching PO-YYYY-* pattern
		# Count all POs (including drafts and submitted) that match the pattern for this year
		po_count = frappe.db.sql("""
			SELECT COUNT(*) 
			FROM `tabPurchase Order`
			WHERE name LIKE %s
			AND docstatus < 2
		""", (f"PO-{year_str}-%",))[0][0] or 0
		
		# Increment for this new PO
		xxxx = po_count + 1
		xxxx_str = str(xxxx).zfill(4)  # Pad to 4 digits
		
		# Calculate ZZZ: Count of how many times this item has appeared in any PO
		# Query all Purchase Orders (across all years) that have this item
		# Since autoname is called before save, self.name will be None/empty, so we don't need to exclude it
		item_count = frappe.db.sql("""
			SELECT COUNT(DISTINCT poi.parent)
			FROM `tabPurchase Order Item` poi
			INNER JOIN `tabPurchase Order` po ON poi.parent = po.name
			WHERE poi.item_code = %s
			AND po.docstatus < 2
		""", (item_code,))[0][0] or 0
		
		# Increment for this new PO
		zzz = item_count + 1
		zzz_str = str(zzz).zfill(3)  # Pad to 3 digits
		
		# Set the name
		self.name = f"PO-{year_str}-{xxxx_str}-{zzz_str}"

