import frappe
from erpnext.buying.doctype.supplier_quotation.supplier_quotation import SupplierQuotation
from frappe.model.mapper import get_mapped_doc

class OncoSupplierQuotation(SupplierQuotation):
    pass

@frappe.whitelist()
def create_modification(source_name, target_doc=None):
    return get_mapped_doc("Supplier Quotation", source_name, {
        "Supplier Quotation": {
            "doctype": "Supplier Quotation",
            "field_map": {
                "name": "custom_importation_approval_ref" 
            },
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Supplier Quotation Item": {
            "doctype": "Supplier Quotation Item",
            "field_map": {
                "parent": "parent"
            }
        }
    }, target_doc, set_modification_fields)

def set_modification_fields(source, target):
    target.naming_series = "EDA-APIMR-.YYYY.-"
    target.custom_aim_of_modify = "Modification"

@frappe.whitelist()
def create_extension(source_name, target_doc=None):
    return get_mapped_doc("Supplier Quotation", source_name, {
        "Supplier Quotation": {
            "doctype": "Supplier Quotation",
            "field_map": {
                "name": "custom_importation_approval_ref"
            }
        },
        "Supplier Quotation Item": {
            "doctype": "Supplier Quotation Item"
        }
    }, target_doc, set_extension_fields)

def set_extension_fields(source, target):
    target.naming_series = "EDA-APIMR-.YYYY.-"
    target.custom_aim_of_extend_ = "Extension"
