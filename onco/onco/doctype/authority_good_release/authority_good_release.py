# Copyright (c) 2026, ds and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class AuthorityGoodRelease(Document):
	def validate(self):
		self.calculate_net_quantities()

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
