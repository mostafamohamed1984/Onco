frappe.ui.form.on('Purchase Invoice', {
    refresh(frm) {
        if (frm.doc.custom_is_shiped === 0 && frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Create Shipments"), function () {
                let p_inv = frm.doc.name;

                // Fetch the full Purchase Invoice with all items
                frappe.call({
                    method: 'frappe.client.get',
                    args: {
                        doctype: 'Purchase Invoice',
                        name: p_inv
                    },
                    callback: function (r) {
                        if (r.message) {
                            let invoice = r.message;

                            // Check if invoice has items
                            if (!invoice.items || invoice.items.length === 0) {
                                frappe.msgprint(__('No items found in this Purchase Invoice'));
                                return;
                            }

                            // Create new Shipment document
                            frappe.model.with_doctype('Shipments', function () {
                                let shipment = frappe.model.get_new_doc('Shipments');

                                // Add each item from the invoice to the child table
                                // One row per item
                                invoice.items.forEach(function (item) {
                                    let child = frappe.model.add_child(shipment, 'Purchase Invoices', 'custom_invoices');

                                    // Invoice information (same for all rows from this invoice)
                                    child.purchase_invoice = p_inv;
                                    child.invoice_no = invoice.bill_no || invoice.name;
                                    child.invoice_date = invoice.posting_date;

                                    // Item-specific information (different for each row)
                                    child.item_code = item.item_code;
                                    child.item_name = item.item_name;
                                    child.qty = item.qty;
                                    child.uom = item.uom;
                                    child.rate = item.rate;
                                    child.amount = item.amount;
                                    child.batch_no = item.batch_no || '';
                                    child.expiry_date = item.expiry_date || '';
                                });

                                // Navigate to the new Shipment form
                                frappe.set_route('Form', 'Shipments', shipment.name);

                                frappe.show_alert({
                                    message: __('Shipment created with {0} items', [invoice.items.length]),
                                    indicator: 'green'
                                });
                            });
                        }
                    }
                });
            });
        }
    },

    expiry_date(frm) {
        console.log(frm.doc.expiry_date, typeof (frm.doc.expiry_date));
    }
});
