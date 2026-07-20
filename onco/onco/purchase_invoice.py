import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc

def validate(doc, method):
    """
    Validate Purchase Invoice before save
    Ensure batch numbers are provided for items that require them
    """
    # Bypass strict stock and batch validation during historical Data Imports
    if frappe.flags.in_import:
        return

    # Set use_serial_batch_fields for all items when update_stock is enabled
    if doc.update_stock:
        for item in doc.items:
            if not item.use_serial_batch_fields:
                item.use_serial_batch_fields = 1
            
            # Set warehouse to Incoming Warehouse if not set (for batch creation)
            # Note: 2 spaces after "Imported", 1 space before dash
            if not item.warehouse:
                item.warehouse = "Imported  Finished Phr Incoming Warehouse - Onco"
    
    # Validate batch numbers for items that require them
    for item in doc.items:
        if item.item_code:
            item_doc = frappe.get_cached_doc('Item', item.item_code)
            if item_doc.has_batch_no and doc.update_stock:
                if not item.batch_no and not item.serial_and_batch_bundle:
                    frappe.throw(
                        _("Row #{0}: Batch Number is mandatory for item {1}").format(
                            item.idx, item.item_code
                        )
                    )

def on_submit(doc, method):
    """
    Actions to perform after Purchase Invoice is submitted
    """
    pass

def before_insert(doc, method):
    """
    Actions to perform before inserting a new Purchase Invoice
    """
    # Bypass forcing stock updates during historical Data Imports
    if frappe.flags.in_import:
        return

    # Removed automatic update_stock enforcement as per user request
    # if not doc.update_stock:
    #     doc.update_stock = 1

    # Set use_serial_batch_fields for all items when update_stock is enabled
    if doc.update_stock:
        for item in doc.items:
            if not item.use_serial_batch_fields:
                item.use_serial_batch_fields = 1


@frappe.whitelist()
def make_purchase_receipt_from_pi(source_name, target_doc=None):
    """Create a Purchase Receipt from a submitted Purchase Invoice, reliably
    mapping all items. Intended for locally purchased goods where no Shipment
    exists. The PI's Serial/Batch Bundle is already linked to the invoice, so it
    is cleared here and a fresh bundle is built on PR submit.
    """
    doc = frappe.get_doc("Purchase Invoice", source_name)
    if doc.docstatus != 1:
        frappe.throw(_("Purchase Invoice must be submitted before creating a Purchase Receipt."))

    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    target_doc = get_mapped_doc(
        "Purchase Invoice",
        source_name,
        {
            "Purchase Invoice": {
                "doctype": "Purchase Receipt",
                "validation": {
                    "docstatus": ["=", 1]
                },
            },
            "Purchase Invoice Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    "name": "purchase_invoice_item",
                    "parent": "purchase_invoice",
                    "parenttype": "Purchase Invoice",
                },
            },
        },
        target_doc,
        set_missing_values,
    )

    # A PI-linked Serial/Batch Bundle cannot be reused on the Receipt; clear it
    # and let ERPNext create a new bundle from the serial/batch values.
    for item in (target_doc.items or []):
        if item.serial_and_batch_bundle:
            item.serial_and_batch_bundle = None
        item.use_serial_batch_fields = 1

    return target_doc
