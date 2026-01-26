// Copyright (c) 2026, Onco and contributors
// For license information, please see license.txt

frappe.ui.form.on('Importation Approval Request', {
    refresh: function(frm) {
        // Add custom buttons based on document status
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Importation Approval'), function() {
                create_importation_approval(frm);
            }, __('Create'));
            
            frm.add_custom_button(__('Create Modification'), function() {
                create_modification(frm);
            }, __('Create'));
            
            frm.add_custom_button(__('Create Extension'), function() {
                create_extension(frm);
            }, __('Create'));
        }
        
        // Set naming series based on request type
        if (frm.doc.request_type && !frm.doc.naming_series) {
            if (frm.doc.request_type === 'Special Importation (SPIMR)') {
                if (frm.doc.is_modification) {
                    frm.set_value('naming_series', 'EDA-SPIMR-MD-.YYYY.-.#####');
                } else if (frm.doc.is_extension) {
                    frm.set_value('naming_series', 'EDA-SPIMR-EX-.YYYY.-.######');
                } else {
                    frm.set_value('naming_series', 'EDA-SPIMR-.YYYY.-.#####');
                }
            } else if (frm.doc.request_type === 'Annual Importation (APIMR)') {
                if (frm.doc.is_modification) {
                    frm.set_value('naming_series', 'EDA-APIMR-MD-.YYYY.-.#####');
                } else if (frm.doc.is_extension) {
                    frm.set_value('naming_series', 'EDA-APIMR-EX-.YYYY.-.######');
                } else {
                    frm.set_value('naming_series', 'EDA-APIMR-.YYYY.-.#####');
                }
            }
        }
    },
    
    request_type: function(frm) {
        // Auto-set naming series based on request type
        if (frm.doc.request_type === 'Special Importation (SPIMR)') {
            if (frm.doc.is_modification) {
                frm.set_value('naming_series', 'EDA-SPIMR-MD-.YYYY.-.#####');
            } else if (frm.doc.is_extension) {
                frm.set_value('naming_series', 'EDA-SPIMR-EX-.YYYY.-.######');
            } else {
                frm.set_value('naming_series', 'EDA-SPIMR-.YYYY.-.#####');
            }
        } else if (frm.doc.request_type === 'Annual Importation (APIMR)') {
            if (frm.doc.is_modification) {
                frm.set_value('naming_series', 'EDA-APIMR-MD-.YYYY.-.#####');
            } else if (frm.doc.is_extension) {
                frm.set_value('naming_series', 'EDA-APIMR-EX-.YYYY.-.######');
            } else {
                frm.set_value('naming_series', 'EDA-APIMR-.YYYY.-.#####');
            }
        }
    },
    
    before_submit: function(frm) {
        // Validate that all items have requested quantities
        let has_items = false;
        frm.doc.items.forEach(function(item) {
            if (item.requested_qty > 0) {
                has_items = true;
            }
        });
        
        if (!has_items) {
            frappe.throw(__('Please add at least one item with requested quantity'));
        }
    },
    
    approval_status: function(frm) {
        // Auto-set quantities based on approval status
        // "في حاله الموافقة الكلية ترحل الكمية تلقائي"
        // (In total approval, quantity transfers automatically)
        if (frm.doc.approval_status === 'Totally Approved') {
            frm.doc.items.forEach(function(item) {
                frappe.model.set_value(item.doctype, item.name, 'approved_qty', item.requested_qty);
                frappe.model.set_value(item.doctype, item.name, 'status', 'Totally Approved');
            });
            frm.refresh_field('items');
        } else if (frm.doc.approval_status === 'Refused') {
            frm.doc.items.forEach(function(item) {
                frappe.model.set_value(item.doctype, item.name, 'approved_qty', 0);
                frappe.model.set_value(item.doctype, item.name, 'status', 'Refused');
            });
            frm.refresh_field('items');
        }
        // For partial approval, user must manually set quantities
    }
});

frappe.ui.form.on('Importation Approval Request Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code) {
            // Fetch supplier information
            frappe.db.get_value('Item', row.item_code, 'default_supplier')
                .then(r => {
                    if (r.message && r.message.default_supplier) {
                        frappe.model.set_value(cdt, cdn, 'supplier', r.message.default_supplier);
                    }
                });
        }
    },
    
    requested_qty: function(frm) {
        calculate_totals(frm);
    },
    
    approved_qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Validate quantity editing restrictions based on status
        // "لا يمكن الكتابة في الكميات الا في حاله الموافقة الجزئية"
        // (Can only edit quantities in partial approval case)
        if (frm.doc.approval_status === 'Totally Approved') {
            frappe.model.set_value(cdt, cdn, 'approved_qty', row.requested_qty);
            frappe.msgprint(__('In total approval, quantity transfers automatically. Cannot edit approved quantity.'));
            return;
        }
        
        if (frm.doc.approval_status === 'Refused') {
            frappe.model.set_value(cdt, cdn, 'approved_qty', 0);
            frappe.msgprint(__('Cannot edit quantities for refused requests.'));
            return;
        }
        
        // Only allow editing in partial approval or pending status
        if (frm.doc.approval_status && frm.doc.approval_status !== 'Partially Approved' && frm.doc.approval_status !== '') {
            frappe.msgprint(__('Quantity editing is only allowed in partial approval cases.'));
            return;
        }
        
        calculate_totals(frm);
    },
    
    items_remove: function(frm) {
        calculate_totals(frm);
    }
});

function calculate_totals(frm) {
    let total_requested = 0;
    let total_approved = 0;
    
    frm.doc.items.forEach(function(item) {
        total_requested += item.requested_qty || 0;
        total_approved += item.approved_qty || 0;
    });
    
    frm.set_value('total_requested_qty', total_requested);
    frm.set_value('total_approved_qty', total_approved);
}

function create_importation_approval(frm) {
    frappe.model.open_mapped_doc({
        method: "onco.onco.doctype.importation_approval_request.importation_approval_request.make_importation_approval",
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
        }
    ], function(values) {
        frappe.call({
            method: "onco.onco.doctype.importation_approval_request.importation_approval_request.create_modification",
            args: {
                source_name: frm.doc.name,
                modification_reason: values.modification_reason,
                requested_modification: values.requested_modification
            },
            callback: function(r) {
                if (r.message) {
                    frappe.set_route('Form', 'Importation Approval Request', r.message);
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
        }
    ], function(values) {
        frappe.call({
            method: "onco.onco.doctype.importation_approval_request.importation_approval_request.create_extension",
            args: {
                source_name: frm.doc.name,
                extension_reason: values.extension_reason,
                extension_details: values.extension_details,
                new_validation_date: values.new_validation_date
            },
            callback: function(r) {
                if (r.message) {
                    frappe.set_route('Form', 'Importation Approval Request', r.message);
                }
            }
        });
    }, __('Create Extension'), __('Create'));
}