# Copyright (c) 2025, ds and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from frappe.model.document import Document
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice as _make_purchase_invoice
class Shipments(Document):
    def validate(self):
        self.calculate_milestone_completion()

    def calculate_milestone_completion(self):
        steps = [
            self.arrived,
            self.bank_authenticated,
            self.restricted_release_status,
            self.customs_release_status,
            self.received_at_warehouse
        ]
        if all(steps):
            self.status = "Completed"
        elif any(steps):
            self.status = "In Progress"

    def on_submit(self):
        if self.received_at_warehouse:
            self.create_stock_transfer()

    def create_stock_transfer(self):
        """Create a Material Transfer Stock Entry from Source to Target Warehouse"""
        if not self.source_warehouse or not self.target_warehouse:
            return

        # Check if transfer already exists
        existing = frappe.get_all("Stock Entry", filters={
            "custom_shipment_ref": self.name,
            "stock_entry_type": "Material Transfer",
            "docstatus": ["<", 2]
        })
        if existing:
            return

        # Fetch items from linked Purchase Receipt or Shipment Items (if we had any)
        # Since we use PI/PR, let's fetch from the PR linked to this shipment
        pr_items = frappe.get_all("Purchase Receipt Item", 
            filters={"parent": ["in", frappe.get_all("Purchase Receipt", filters={"custom_shipment_ref": self.name, "docstatus": 1}, pluck="name")]},
            fields=["item_code", "qty", "uom", "batch_no"])

        if not pr_items:
            # Fallback: check linked PIs
            invoices = [self.purchase_invoice] if self.purchase_invoice else []
            if self.custom_invoices:
                invoices.extend([row.purchase_invoice for row in self.custom_invoices if row.purchase_invoice])
            
            pr_items = frappe.get_all("Purchase Invoice Item",
                filters={"parent": ["in", invoices]},
                fields=["item_code", "qty", "uom"])

        if not pr_items:
            return

        se = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Transfer",
            "custom_shipment_ref": self.name,
            "items": []
        })

        for item in pr_items:
            se.append("items", {
                "item_code": item.item_code,
                "s_warehouse": self.source_warehouse,
                "t_warehouse": self.target_warehouse,
                "qty": item.qty,
                "uom": item.uom,
                "batch_no": item.get("batch_no") or self.batch_no
            })

        se.insert()
        se.submit()
        frappe.msgprint(_("Automated Stock Transfer created: {0}").format(se.name))

@frappe.whitelist()
def set_shipment_id(purchase_inv,ship):
    if ship:
        # Assuming 'ship' is the name or ID of the shipment
        try:
            invoice = frappe.get_doc("Purchase Invoice", purchase_inv)
            invoice.db_set("custom_shipments",ship)
            invoice.db_set("custom_is_shiped",1)
            return invoice
        except frappe.DoesNotExistError:
            frappe.throw(_("Purchase Invoice not found"))
        except Exception as e:
            frappe.throw(str(e))
@frappe.whitelist()
def get_shipment(purchase_invoice,rec):
    invoice = frappe.get_doc("Purchase Invoice", purchase_invoice)
    ship_id = invoice.get("custom_shipments")
    print(f"Shipment\n\n\n{ship_id}")
    shipment = frappe.get_doc("Shipments", ship_id)
    if not shipment:
        frappe.throw(f"No shipment data")
    return shipment
@frappe.whitelist()
def set_shipment(doc_shipments, rec):
    try:
        if isinstance(rec, str): 
            receipt = json.loads(rec)
            shipments = json.loads(doc_shipments)
        else:
            receipt = rec  
        return shipments
    
    except Exception as e:
        frappe.throw(str(e))

from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
	doc = frappe.get_doc("Shipments", source_name)
	
	invoices = []
	if doc.purchase_invoice:
		invoices.append(doc.purchase_invoice)
	
	if doc.custom_invoices:
		for row in doc.custom_invoices:
			if row.purchase_invoice and row.purchase_invoice not in invoices:
				invoices.append(row.purchase_invoice)
				
	if not invoices:
		frappe.throw("Please link at least one Purchase Invoice first")

	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")
		# Link Shipment
		target.custom_shipment_ref = source_name
		
		# Propagate Shipment data to items
		for item in target.items:
			if doc.batch_no:
				item.batch_no = doc.batch_no
			if doc.expiry_date:
				item.expiry_date = doc.expiry_date
			if doc.manufacturing_date_:
				item.manufacturing_date = doc.manufacturing_date_
			if doc.invoice_no:
				item.custom_invoice_no = doc.invoice_no # Added custom field for traceability if needed

	# Map the first invoice to create the target doc
	target_doc = get_mapped_doc("Purchase Invoice", invoices[0], {
		"Purchase Invoice": {
			"doctype": "Purchase Receipt",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Purchase Invoice Item": {
			"doctype": "Purchase Receipt Item",
		},
	}, target_doc, set_missing_values)

	# Map subsequent invoices and append items
	for inv_name in invoices[1:]:
		inv_doc = frappe.get_doc("Purchase Invoice", inv_name)
		for item in inv_doc.items:
			# Manually map item
			target_doc.append("items", {
				"item_code": item.item_code,
				"item_name": item.item_name,
				"description": item.description,
				"qty": item.qty,
				"uom": item.uom,
				"rate": item.rate,
				"purchase_order": item.purchase_order,
				"purchase_invoice_item": item.name,
				"purchase_invoice": inv_name,
				"warehouse": doc.source_warehouse or item.warehouse or target_doc.set_warehouse,
				"batch_no": doc.batch_no,
				"expiry_date": doc.expiry_date,
				"manufacturing_date": doc.manufacturing_date_
			})
	
	return target_doc

def on_purchase_receipt_submit(doc, method):
	"""Update linked Shipment when Purchase Receipt is submitted"""
	if doc.get("custom_shipment_ref"):
		frappe.db.set_value("Shipments", doc.custom_shipment_ref, {
			"received_at_warehouse": 1,
			"received_date": frappe.utils.now()
		})
		frappe.msgprint(f"Shipment {doc.custom_shipment_ref} status updated to Received at Warehouse.")