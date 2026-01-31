frappe.ui.form.on('Shipments', {
    async on_submit(frm) {
        // Get all Purchase Invoices from the child table
        let invoices = [];
        
        if (frm.doc.custom_invoices && frm.doc.custom_invoices.length > 0) {
            // Collect unique invoice names
            frm.doc.custom_invoices.forEach(function(row) {
                if (row.purchase_invoice && !invoices.includes(row.purchase_invoice)) {
                    invoices.push(row.purchase_invoice);
                }
            });
        }

        // Check if any Purchase Invoices exist
        if (invoices.length > 0) {
            try {
                // Update each Purchase Invoice to link back to this Shipment
                for (let inv of invoices) {
                    await frappe.db.set_value("Purchase Invoice", inv, {
                        "custom_shipments": frm.doc.name,
                        "custom_is_shiped": 1
                    });
                }
                
                frappe.show_alert({
                    message: __('Shipment reference updated on {0} Purchase Invoice(s)', [invoices.length]),
                    indicator: 'green'
                });
            } catch (error) {
                console.error("Error updating Purchase Invoice:", error);
                frappe.msgprint(__('Error updating Purchase Invoice: {0}', [error.message]));
            }
        } else {
            frappe.msgprint(__('No Purchase Invoice associated with this Shipment.'));
        }
    },
    
    expiry_date(frm) {
        console.log(frm.doc.expiry_date, typeof(frm.doc.expiry_date));
        frm.set_value("awb_date", frm.doc.expiry_date);
    }
});
