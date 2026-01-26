// Copyright (c) 2026, Onco and contributors
// For license information, please see license.txt

frappe.ui.form.on('Importation Approvals', {
    refresh: function(frm) {
        // Add custom buttons based on document status
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Purchase Order'), function() {
                create_purchase_order(frm);
            }, __('Create'));
            
            frm.add_custom_button(__('Create Modification'), function() {
                create_modification(frm);
            }, __('Create'));
            
            frm.add_custom_button(__('Create Extension'), function() {
                create_extension(frm);
            }, __('Create'));
        }
        
        // Set naming series based on approval type
        if (frm.doc.approval_type && !frm.doc.naming_series) {
            if (frm.doc.approval_type === 'Special Importation (SPIMA)') {
                if (frm.doc.is_modification) {
                    frm.set_value('naming_series', 'EDA-SPIMA-MD-.YYYY.-.#####');
                } else if (frm.doc.is_extension) {
                    frm.set_value('naming_series', 'EDA-SPIMA-EX-.YYYY.-.######');
                } else {
                    frm.set_value('naming_series', 'EDA-SPIMA-.YYYY.-.#####');
                }
            } else if (frm.doc.approval_type === 'Annual Importation (APIMA)') {
                if (frm.doc.is_modification) {
                    frm.set_value('naming_series', 'EDA-APIMA-MD-.YYYY.-.#####');
                } else if (frm.doc.is_extension) {
                    frm.set_value('naming_series', 'EDA-APIMA-EX-.YYYY.-.######');
                } else {
                    frm.set_value('naming_series', 'EDA-APIMA-.YYYY.-.#####');
                }
            }
        }
    },
    
    approval_type: function(frm) {
        // Auto-set naming series based on approval type
        if (frm.doc.approval_type === 'Special Importation (SPIMA)') {
            if (frm.doc.is_modification) {
                frm.set_value('naming_series', 'EDA-SPIMA-MD-.YYYY.-.#####');
            } else if (frm.doc.is_extension) {
                frm.set_value('naming_series', 'EDA-SPIMA-EX-.YYYY.-.######');
            } else {
                frm.set_value('naming_series', 'EDA-SPIMA-.YYYY.-.#####');
            }
        } else if (frm.doc.approval_type === 'Annual Importation (APIMA)') {
            if (frm.doc.is_modification) {
                frm.set_value('naming_series', 'EDA-APIMA-MD-.YYYY.-.#####');
            } else if (frm.doc.is_extension) {
                frm.set_value('naming_series', 'EDA-APIMA-EX-.YYYY.-.######');
            } else {
                frm.set_value('naming_series', 'EDA-APIMA-.YYYY.-.#####');
            }
        }
    },
    
    importation_approval_request: function(frm) {
        if (frm.doc.importation_approval_request) {
            // Fetch items from the linked request
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Importation Approval Request",
                    name: frm.doc.importation_approval_request
                },
                callback: function(r) {
                    if (r.message) {
                        let request_doc = r.message;
                        
                        // Set approval type based on request type
                        if (request_doc.request_type === 'Special Importation (SPIMR)') {
                            frm.set_value('approval_type', 'Special Importation (SPIMA)');
                        } else if (request_doc.request_type === 'Annual Importation (APIMR)') {
                            frm.set_value('approval_type', 'Annual Importation (APIMA)');
                        }
                        
                        // Clear existing items and add from request
                        frm.clear_table('items');
                        
                        request_doc.items.forEach(function(item) {
                            // Add all items from request, not just approved ones
                            let child = frm.add_child('items');
                            child.item_code = item.item_code;
                            child.item_name = item.item_name;
                            child.supplier = item.supplier;
                            child.requested_qty = item.requested_qty;
                            // Auto-populate approved_qty with requested_qty as per HTML requirement
                            child.approved_qty = item.requested_qty;
                            child.status = 'Approved';
                        });
                        
                        frm.refresh_field('items');
                    }
                }
            });
        }
    },
    
    before_submit: function(frm) {
        // Validate that all items have approved quantities
        let has_approved_items = false;
        frm.doc.items.forEach(function(item) {
            if (item.approved_qty > 0) {
                has_approved_items = true;
            }
        });
        
        if (!has_approved_items) {
            frappe.throw(__('Please ensure at least one item has approved quantity'));
        }
        
        // Validate valid date is in the future
        if (frm.doc.valid_date && frm.doc.valid_date <= frappe.datetime.get_today()) {
            frappe.throw(__('Valid Date must be in the future'));
        }
    }
});

frappe.ui.form.on('Importation Approvals Item', {
    approved_qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Validate approved quantity doesn't exceed requested quantity
        if (row.approved_qty > row.requested_qty) {
            frappe.model.set_value(cdt, cdn, 'approved_qty', row.requested_qty);
            frappe.msgprint(__('Approved quantity cannot exceed requested quantity'));
        }
        
        // Update status based on approved quantity
        if (row.approved_qty === 0) {
            frappe.model.set_value(cdt, cdn, 'status', 'Refused');
        } else if (row.approved_qty === row.requested_qty) {
            frappe.model.set_value(cdt, cdn, 'status', 'Approved');
        } else {
            frappe.model.set_value(cdt, cdn, 'status', 'Partially Approved');
        }
    },
    
    items_add: function(frm, cdt, cdn) {
        // Prevent adding items if document is submitted
        if (frm.doc.docstatus === 1) {
            frappe.throw(__('Cannot add items to submitted document'));
        }
    }
});

// Prevent editing of quantities after submission
frappe.ui.form.on('Importation Approvals', {
    onload: function(frm) {
        if (frm.doc.docstatus === 1) {
            // Make quantity fields read-only after submission
            frm.fields_dict.items.grid.get_field('approved_qty').read_only = 1;
            frm.refresh_field('items');
        }
    }
});

function create_purchase_order(frm) {
    // Validate document status before creating Purchase Order
    if (frm.doc.docstatus !== 1) {
        frappe.throw(__('Document must be submitted before creating Purchase Order'));
        return;
    }
    
    // Check if document is closed
    if (frm.doc.docstatus === 2) {
        frappe.throw(__('Cannot create Purchase Order from closed document. Use the latest version.'));
        return;
    }
    
    frappe.model.open_mapped_doc({
        method: "onco.onco.doctype.importation_approvals.importation_approvals.make_purchase_order",
        frm: frm
    });
}

function create_modification(frm) {
    frappe.prompt([
        {
            label: 'Modification Reason',
            fieldname: 'modification_reason',
            fieldtype: 'Select',
            options: '\nError\nChange data and conditions',
            reqd: 1
        },
        {
            label: 'Requested Modification',
            fieldname: 'requested_modification',
            fieldtype: 'Text',
            reqd: 1
        },
        {
            label: 'New Conditions',
            fieldname: 'new_conditions',
            fieldtype: 'Text'
        }
    ], function(values) {
        frappe.call({
            method: "onco.onco.doctype.importation_approvals.importation_approvals.create_modification",
            args: {
                source_name: frm.doc.name,
                modification_reason: values.modification_reason,
                requested_modification: values.requested_modification,
                new_conditions: values.new_conditions
            },
            callback: function(r) {
                if (r.message) {
                    frappe.set_route('Form', 'Importation Approvals', r.message);
                }
            }
        });
    }, __('Create Modification'), __('Create'));
}

function create_extension(frm) {
    frappe.prompt([
        {
            label: 'Extension Reason',
            fieldname: 'extension_reason',
            fieldtype: 'Select',
            options: '\nValidation\nOther',
            reqd: 1
        },
        {
            label: 'Extension Details',
            fieldname: 'extension_details',
            fieldtype: 'Text',
            reqd: 1
        },
        {
            label: 'New Validation Date',
            fieldname: 'new_validation_date',
            fieldtype: 'Date',
            reqd: 1
        },
        {
            label: 'New Quantity',
            fieldname: 'new_quantity',
            fieldtype: 'Float'
        }
    ], function(values) {
        frappe.call({
            method: "onco.onco.doctype.importation_approvals.importation_approvals.create_extension",
            args: {
                source_name: frm.doc.name,
                extension_reason: values.extension_reason,
                extension_details: values.extension_details,
                new_validation_date: values.new_validation_date,
                new_quantity: values.new_quantity
            },
            callback: function(r) {
                if (r.message) {
                    frappe.set_route('Form', 'Importation Approvals', r.message);
                }
            }
        });
    }, __('Create Extension'), __('Create'));
}