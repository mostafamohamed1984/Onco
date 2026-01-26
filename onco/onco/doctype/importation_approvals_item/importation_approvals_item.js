// Copyright (c) 2026, Onco and contributors
// For license information, please see license.txt

// Child table JavaScript for Importation Approvals Item
frappe.ui.form.on('Importation Approvals Item', {
    before_items_add: function(frm, cdt, cdn) {
        // Set up item filtration based on parent approval type
        let grid_row = frm.fields_dict.items.grid.grid_rows_by_docname[cdn];
        if (grid_row) {
            grid_row.get_field('item_code').get_query = function() {
                let filters = {};
                
                // Filter for pharmaceutical items as per HTML requirements
                filters['custom_pharmaceutical_item'] = 1;
                filters['disabled'] = 0;  // Only active items
                
                // Additional filtration based on approval type and pharmaceutical configuration
                if (frm.doc.approval_type === 'Annual Importation (APIMA)') {
                    // For annual approvals, filter based on registered pharmaceutical items
                    filters['custom_registered'] = 1;
                } else if (frm.doc.approval_type === 'Special Importation (SPIMA)') {
                    // For special approvals, allow all pharmaceutical items (registered and non-registered)
                }
                
                // If linked to a specific importation approval request, 
                // only show items from that request
                if (frm.doc.importation_approval_request) {
                    // This would require a custom method to get items from the linked request
                    // For now, we'll rely on the auto-population from the request
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
            // Validate item compatibility with approval type
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
                            frappe.msgprint(__('Only pharmaceutical items are allowed in importation approvals'));
                            frappe.model.set_value(cdt, cdn, 'item_code', '');
                            return;
                        }
                        
                        // Additional validation based on approval type
                        if (frm.doc.approval_type === 'Annual Importation (APIMA)') {
                            if (!item.custom_registered) {
                                frappe.msgprint(__('Annual importation approvals require registered pharmaceutical items'));
                                frappe.model.set_value(cdt, cdn, 'item_code', '');
                                return;
                            }
                        }
                        
                        // Validate expiry date
                        if (item.custom_expiry_date && item.custom_expiry_date <= frappe.datetime.get_today()) {
                            frappe.msgprint({
                                title: __('Expired Item Warning'),
                                message: __('This pharmaceutical item has expired. Please verify before proceeding.'),
                                indicator: 'red'
                            });
                        }
                        
                        // Validate that item exists in the linked request (if applicable)
                        if (frm.doc.importation_approval_request) {
                            let found_in_request = false;
                            frm.doc.items.forEach(function(existing_item) {
                                if (existing_item.item_code === row.item_code && existing_item.name !== row.name) {
                                    found_in_request = true;
                                }
                            });
                            
                            // Check if this item was in the original request
                            frappe.call({
                                method: 'frappe.client.get',
                                args: {
                                    doctype: 'Importation Approval Request',
                                    name: frm.doc.importation_approval_request
                                },
                                callback: function(req_r) {
                                    if (req_r.message) {
                                        let request_doc = req_r.message;
                                        let item_in_request = false;
                                        
                                        request_doc.items.forEach(function(req_item) {
                                            if (req_item.item_code === row.item_code) {
                                                item_in_request = true;
                                                // Auto-populate quantities from request
                                                frappe.model.set_value(cdt, cdn, 'requested_qty', req_item.requested_qty);
                                                frappe.model.set_value(cdt, cdn, 'approved_qty', req_item.requested_qty);
                                            }
                                        });
                                        
                                        if (!item_in_request) {
                                            frappe.msgprint(__('This item was not in the original importation approval request'));
                                        }
                                    }
                                }
                            });
                        }
                    }
                }
            });
        }
    }
});