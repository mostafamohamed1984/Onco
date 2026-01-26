# Copyright (c) 2026, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class AuthorityGoodRelease(Document):
	def validate(self):
		self.calculate_net_quantities()
		self.calculate_totals()

	def calculate_totals(self):
		"""Calculate total quantities from items"""
		total_requested = 0
		total_released = 0
		total_actual = 0
		total_net_released = 0
		total_shortage_control = 0
		total_sample = 0
		
		for item in self.items:
			total_requested += getattr(item, 'requested_qty', 0) or 0
			total_released += getattr(item, 'released_qty', 0) or 0
			total_actual += getattr(item, 'actual_qty', 0) or 0
			total_shortage_control += getattr(item, 'shortage_control_qty', 0) or 0
			total_sample += getattr(item, 'sample_qty', 0) or 0
			total_net_released += getattr(item, 'net_released_qty', 0) or 0
		
		self.total_requested_qty = total_requested
		self.total_released_qty = total_released
		self.total_actual_qty = total_actual
		self.total_net_released_qty = total_net_released
		self.total_shortage_control_qty = total_shortage_control
		self.total_sample_qty = total_sample

	def on_submit(self):
		self.create_stock_entries()
		self.update_shipment_status()

	def calculate_net_quantities(self):
		"""Calculate shortage control and net released quantities"""
		for item in self.items:
			# If shortage control is enabled for this type
			if self.lot_release_subtype == "Lot Release Batch with Shortage Control Quantity":
				item.shortage_control_qty = (item.actual_qty or 0) - (item.released_qty or 0)
			else:
				item.shortage_control_qty = 0
			
			# Net Released is what goes to Sale Warehouse now
			item.net_released_qty = item.released_qty or 0

	def update_shipment_status(self):
		"""Update linked Shipment with customs release details"""
		if self.shipment_no:
			frappe.db.set_value("Shipments", self.shipment_no, {
				"customs_release_status": 1,
				"customs_release_date": self.release_date,
				"customs_release_no": self.name
			})
			frappe.msgprint(_("Shipment {0} status updated to Customs Released.").format(self.shipment_no))

	def create_stock_entries(self):
		"""Create Stock Entries for released items and samples"""
		if not self.items: return

		# 1. Transfer to Sale Warehouse (Net Released Quantity)
		self.create_material_transfer(
			target_warehouse="Imported Finished Phr Sales warehouse  - Onco",
			qty_field="net_released_qty",
			purpose="Sale Release"
		)

		# 2. Transfer to Sample Store (if samples exist)
		if self.no_of_samples and self.no_of_samples > 0:
			self.create_sample_transfer()

	def create_material_transfer(self, target_warehouse, qty_field, purpose):
		"""Helper to create a Material Transfer Stock Entry"""
		source_warehouse = "Imported Finished Phr Receipt and Inspection Warehouse  - Onco"
		
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Transfer"
		se.custom_shipment_ref = self.shipment_no
		se.custom_agr_ref = self.name
		
		has_items = False
		for item in self.items:
			qty = getattr(item, qty_field, 0)
			if qty > 0 and item.release_status == "Released":
				se.append("items", {
					"item_code": item.item_code,
					"qty": qty,
					"s_warehouse": source_warehouse,
					"t_warehouse": target_warehouse,
					"batch_no": item.batch_no,
					"uom": frappe.db.get_value("Item", item.item_code, "stock_uom")
				})
				has_items = True

		if has_items:
			se.insert()
			se.submit()
			frappe.msgprint(_("Stock Entry {0} created for {1}.").format(se.name, purpose))

	def create_sample_transfer(self):
		"""Specific transfer for samples to Sample Store"""
		source_warehouse = "Imported Finished Phr Receipt and Inspection Warehouse  - Onco"
		target_warehouse = "Imported Finished Phr Sample warehouse - Onco"
		
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Transfer"
		se.custom_shipment_ref = self.shipment_no
		
		# For samples, we usually take from the first item
		if self.items:
			item = self.items[0]
			se.append("items", {
				"item_code": item.item_code,
				"qty": self.no_of_samples,
				"s_warehouse": source_warehouse,
				"t_warehouse": target_warehouse,
				"batch_no": item.batch_no,
				"uom": frappe.db.get_value("Item", item.item_code, "stock_uom")
			})
			se.insert()
			se.submit()
			frappe.msgprint(_("Sample Stock Entry {0} created.").format(se.name))

	@frappe.whitelist()
	def fetch_items_from_purchase_receipt_report(self):
		"""Fetch items from Purchase Receipt Report"""
		if not self.shipment_no:
			frappe.throw("Please select a Shipment first")
		
		# Find Purchase Receipt Report linked to this shipment
		purchase_receipt_reports = frappe.get_all("Purchase Receipt Report", 
			filters={"custom_shipment_ref": self.shipment_no}, 
			fields=["name"])
		
		if not purchase_receipt_reports:
			frappe.throw("No Purchase Receipt Report found for this shipment")
		
		# Clear existing items
		self.items = []
		
		# This will be enhanced in Phase 3 to actually fetch from Purchase Receipt Report
		frappe.msgprint("Item fetching from Purchase Receipt Report will be implemented in Phase 3")

@frappe.whitelist()
def fetch_items_from_purchase_receipt_report(shipment_no):
	"""Fetch items from Purchase Receipt Report for Authority Good Release"""
	# Find Purchase Receipt Report linked to this shipment
	purchase_receipt_reports = frappe.get_all("Purchase Receipt Report", 
		filters={"custom_shipment_ref": shipment_no}, 
		fields=["name"])
	
	if not purchase_receipt_reports:
		frappe.throw("No Purchase Receipt Report found for this shipment")
	
	# Get the first Purchase Receipt Report (assuming one per shipment for now)
	prr_name = purchase_receipt_reports[0].name
	prr_doc = frappe.get_doc("Purchase Receipt Report", prr_name)
	
	items = []
	# This will be enhanced in Phase 3 to fetch actual items from Purchase Receipt Report
	# For now, return empty list
	frappe.msgprint("Item fetching will be implemented in Phase 3")
	return items

@frappe.whitelist()
def create_stock_entry(authority_good_release):
	"""Create Stock Entry from Authority Good Release"""
	agr_doc = frappe.get_doc("Authority Good Release", authority_good_release)
	
	if agr_doc.stock_entry_created:
		frappe.throw("Stock Entry already created")
	
	stock_entry = frappe.new_doc("Stock Entry")
	stock_entry.stock_entry_type = "Material Transfer"
	stock_entry.from_warehouse = agr_doc.warehouse_from
	stock_entry.to_warehouse = agr_doc.warehouse_to
	stock_entry.authority_good_release = agr_doc.name
	
	# Add items to stock entry
	for item in agr_doc.items:
		if item.net_released_qty > 0:
			stock_entry.append("items", {
				"item_code": item.item_code,
				"qty": item.net_released_qty,
				"s_warehouse": agr_doc.warehouse_from,
				"t_warehouse": agr_doc.warehouse_to,
				"batch_no": item.batch_no
			})
		
		# Handle sample quantities
		if item.sample_qty and agr_doc.sample_warehouse:
			stock_entry.append("items", {
				"item_code": item.item_code,
				"qty": item.sample_qty,
				"s_warehouse": agr_doc.warehouse_from,
				"t_warehouse": agr_doc.sample_warehouse,
				"batch_no": item.batch_no
			})
	
	if stock_entry.items:
		stock_entry.insert()
		stock_entry.submit()
		
		# Update Authority Good Release
		agr_doc.stock_entry_created = stock_entry.name
		agr_doc.save()
		
		return stock_entry.name
	else:
		frappe.throw("No items to transfer")
