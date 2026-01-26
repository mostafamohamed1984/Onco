// Copyright (c) 2026, Onco and contributors
// For license information, please see license.txt

// Child table JavaScript for Importation Approval Request Item
frappe.ui.form.on('Importation Approval Request Item', {
    before_items_add: function(frm, cdt, cdn) {
        // Set up item filtration based on parent request type
        let grid_row = frm.fields_dict.items.grid.grid_rows_by_docname[cdn];
        if (grid_row) {
            grid_row.get_field('item_code').get_query = function() {
                let filters = {};
                
                // Filter for pharmaceutical items as per HTML requirements
                filters['custom_pharmaceutical_item'] = 1;
                filters['disabled'] = 0;  // Only active items
                
                // Additional filtration based on request type
                if (frm.doc.request_type === 'Annual Importation (APIMR)') {
                    // For annual requests, could filter based on annual plan items
                    // This ensures only relevant items are shown for annual importation
                    filters['custom_registered'] = 1;  // Only registered pharmaceutical items
                } else if (frm.doc.request_type === 'Special Importation (SPIMR)') {
                    // For special requests, allow all pharmaceutical items
                    // Could include both registered and non-registered items
                }
                
                return {
                    filters: filters
                };
            };
        }
    },
    
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code) {
            // Validate item compatibility with request type
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Item',
                    name: row.item_code
                },
                callback: function(r) {
                    if (r.message) {
                        let item = r.message;
                        
                        // Validate pharmaceutical item requirements
                        if (!item.custom_pharmaceutical_item) {
                            frappe.msgprint(__('Only pharmaceutical items are allowed in importation requests'));
                            frappe.model.set_value(cdt, cdn, 'item_code', '');
                            return;
                        }
                        
                        // Additional validation based on request type
                        if (frm.doc.request_type === 'Annual Importation (APIMR)') {
                            if (!item.custom_registered) {
                                frappe.msgprint(__('Annual importation requests require registered pharmaceutical items'));
                                frappe.model.set_value(cdt, cdn, 'item_code', '');
                                return;
                            }
                            
                            // Validate that registered pharmaceutical items have complete data
                            let missing_fields = [];
                            if (!item.custom_batch_no) missing_fields.push('Batch No');
                            if (!item.custom_manufacturing_date) missing_fields.push('Manufacturing Date');
                            if (!item.custom_expiry_date) missing_fields.push('Expiry Date');
                            if (!item.strength) missing_fields.push('Strength');
                            
                            if (missing_fields.length > 0) {
                                frappe.msgprint({
                                    title: __('Incomplete Pharmaceutical Data'),
                                    message: __('This registered pharmaceutical item is missing required fields: {0}. Please complete the item master data first.', [missing_fields.join(', ')]),
                                    indicator: 'red'
                                });
                                frappe.model.set_value(cdt, cdn, 'item_code', '');
                                return;
                            }
                        } else if (frm.doc.request_type === 'Special Importation (SPIMR)') {
                            // For special importation, allow both registered and non-registered items
                            // But still validate registered items have complete data if they are registered
                            if (item.custom_registered) {
                                let missing_fields = [];
                                if (!item.custom_batch_no) missing_fields.push('Batch No');
                                if (!item.custom_manufacturing_date) missing_fields.push('Manufacturing Date');
                                if (!item.custom_expiry_date) missing_fields.push('Expiry Date');
                                if (!item.strength) missing_fields.push('Strength');
                                
                                if (missing_fields.length > 0) {
                                    frappe.msgprint({
                                        title: __('Incomplete Pharmaceutical Data'),
                                        message: __('This registered pharmaceutical item is missing required fields: {0}. Please complete the item master data first.', [missing_fields.join(', ')]),
                                        indicator: 'orange'
                                    });
                                }
                            }
                        }
                        
                        // Validate expiry date for all pharmaceutical items
                        if (item.custom_expiry_date && item.custom_expiry_date <= frappe.datetime.get_today()) {
                            frappe.msgprint({
                                title: __('Expired Item Warning'),
                                message: __('This pharmaceutical item has expired. Please verify before proceeding.'),
                                indicator: 'red'
                            });
                        }
                        
                        // Show pharmaceutical item information
                        if (item.custom_pharmaceutical_item) {
                            let info_msg = `<strong>Pharmaceutical Item Details:</strong><br>`;
                            info_msg += `Strength: ${item.strength || 'Not specified'}<br>`;
                            info_msg += `Batch No: ${item.custom_batch_no || 'Not specified'}<br>`;
                            info_msg += `Manufacturing Date: ${item.custom_manufacturing_date || 'Not specified'}<br>`;
                            info_msg += `Expiry Date: ${item.custom_expiry_date || 'Not specified'}<br>`;
                            info_msg += `Registered: ${item.custom_registered ? 'Yes' : 'No'}<br>`;
                            info_msg += `Storage Instructions: ${item.custom_storage_instructions || 'Not specified'}<br>`;
                            
                            frappe.msgprint({
                                title: 'Pharmaceutical Item Information',
                                message: info_msg,
                                indicator: 'blue'
                            });
                        }
                    }
                }
            });
        }
    }
});