// Copyright (c) 2026, Onco and contributors
// For license information, please see license.txt

// List View Settings
frappe.listview_settings['Importation Approval Request'] = {
    add_fields: ["request_type", "status", "date", "docstatus"],
    get_indicator: function(doc) {
        if (doc.status === "Totally Approved") {
            return [__("Totally Approved"), "green", "status,=,Totally Approved"];
        } else if (doc.status === "Partially Approved") {
            return [__("Partially Approved"), "orange", "status,=,Partially Approved"];
        } else if (doc.status === "Refused") {
            return [__("Refused"), "red", "status,=,Refused"];
        } else if (doc.status === "Pending") {
            return [__("Pending"), "blue", "status,=,Pending"];
        } else if (doc.status === "Closed - Modified") {
            return [__("Closed - Modified"), "gray", "status,=,Closed - Modified"];
        } else if (doc.status === "Closed - Extended") {
            return [__("Closed - Extended"), "gray", "status,=,Closed - Extended"];
        } else {
            return [__("Draft"), "gray", "docstatus,=,0"];
        }
    }
};

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
        
        // Clear items when request type changes to ensure proper filtration
        if (frm.doc.items && frm.doc.items.length > 0) {
            frm.clear_table('items');
            frm.refresh_field('items');
        }
    },
    
    onload: function(frm) {
        // Set up item filtration based on request type and pharmaceutical requirements
        frm.fields_dict.items.grid.get_field('item_code').get_query = function() {
            let filters = {};
            
            // Filter for pharmaceutical items as per HTML requirements
            filters['custom_pharmaceutical_item'] = 1;
            filters['disabled'] = 0;  // Only active items
            
            // Critical filtration based on pharmaceutical item configuration
            if (frm.doc.request_type === 'Annual Importation (APIMR)') {
                // For annual requests, only registered pharmaceutical items with complete data
                // Based on HTML requirement: registered items need batch, manufacturing date, expiry date
                filters['custom_registered'] = 1;
                // Could add additional filters to ensure complete pharmaceutical data
                // filters['custom_batch_no'] = ['!=', ''];
                // filters['custom_manufacturing_date'] = ['!=', ''];
                // filters['custom_expiry_date'] = ['!=', ''];
            } else if (frm.doc.request_type === 'Special Importation (SPIMR)') {
                // For special requests, allow both registered and non-registered pharmaceutical items
                // This gives more flexibility for special/emergency importations
                // No additional filters beyond pharmaceutical_item = 1
            }
            
            return {
                filters: filters
            };
        };
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
            // Validate pharmaceutical item requirements
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Item',
                    name: row.item_code
                },
                callback: function(r) {
                    if (r.message) {
                        let item = r.message;
                        
                        // Check if it's a pharmaceutical item
                        if (item.custom_pharmaceutical_item) {
                            // Show pharmaceutical item information
                            let info_msg = `<strong>Pharmaceutical Item Details:</strong><br>`;
                            info_msg += `Strength: ${item.strength || 'Not specified'}<br>`;
                            info_msg += `Batch No: ${item.custom_batch_no || 'Not specified'}<br>`;
                            info_msg += `Manufacturing Date: ${item.custom_manufacturing_date || 'Not specified'}<br>`;
                            info_msg += `Expiry Date: ${item.custom_expiry_date || 'Not specified'}<br>`;
                            info_msg += `Registered: ${item.custom_registered ? 'Yes' : 'No'}<br>`;
                            
                            // Check for missing required fields
                            if (item.custom_registered) {
                                let missing = [];
                                if (!item.custom_manufacturing_date) missing.push('Manufacturing Date');
                                if (!item.custom_expiry_date) missing.push('Expiry Date');
                                if (!item.custom_batch_no) missing.push('Batch No');
                                if (!item.strength) missing.push('Strength');
                                
                                if (missing.length > 0) {
                                    info_msg += `<br><span style="color: red;"><strong>Missing Required Fields:</strong> ${missing.join(', ')}</span>`;
                                    frappe.msgprint({
                                        title: 'Pharmaceutical Item Validation',
                                        message: info_msg,
                                        indicator: 'orange'
                                    });
                                } else {
                                    // Check expiry date
                                    if (item.custom_expiry_date && item.custom_expiry_date <= frappe.datetime.get_today()) {
                                        info_msg += `<br><span style="color: red;"><strong>Warning:</strong> Item has expired!</span>`;
                                        frappe.msgprint({
                                            title: 'Pharmaceutical Item Validation',
                                            message: info_msg,
                                            indicator: 'red'
                                        });
                                    } else {
                                        frappe.msgprint({
                                            title: 'Pharmaceutical Item Information',
                                            message: info_msg,
                                            indicator: 'green'
                                        });
                                    }
                                }
                            }
                        }
                    }
                }
            });
        }
    },
    
    requested_qty: function(frm) {
        calculate_totals(frm);
    },
    
    approved_qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Critical validation: "لا يمكن الكتابة في الكميات الا في حاله الموافقة الجزئية"
        // (Can only edit quantities in partial approval case)
        
        // If document is submitted, prevent any quantity editing
        if (frm.doc.docstatus === 1) {
            frappe.msgprint(__('Cannot edit quantities in submitted document'));
            frappe.model.set_value(cdt, cdn, 'approved_qty', row.approved_qty || 0);
            return;
        }
        
        // Enforce quantity editing restrictions based on approval status
        if (frm.doc.approval_status === 'Totally Approved') {
            // In total approval, quantity transfers automatically
            frappe.model.set_value(cdt, cdn, 'approved_qty', row.requested_qty);
            frappe.msgprint(__('In total approval, quantity transfers automatically. Cannot edit approved quantity.'));
            return;
        }
        
        if (frm.doc.approval_status === 'Refused') {
            // In refused status, quantity must be 0
            frappe.model.set_value(cdt, cdn, 'approved_qty', 0);
            frappe.msgprint(__('Cannot edit quantities for refused requests.'));
            return;
        }
        
        // Only allow editing in partial approval or pending status
        if (frm.doc.approval_status && 
            frm.doc.approval_status !== 'Partially Approved' && 
            frm.doc.approval_status !== 'Pending' && 
            frm.doc.approval_status !== '') {
            frappe.msgprint(__('Quantity editing is only allowed in partial approval cases or pending status.'));
            // Revert to previous value
            frappe.model.set_value(cdt, cdn, 'approved_qty', row.approved_qty || 0);
            return;
        }
        
        // Validate approved quantity doesn't exceed requested quantity
        if (row.approved_qty > row.requested_qty) {
            frappe.msgprint(__('Approved quantity cannot exceed requested quantity'));
            frappe.model.set_value(cdt, cdn, 'approved_qty', row.requested_qty);
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