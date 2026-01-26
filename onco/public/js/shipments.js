console.log("Shipments custom script loaded!");

frappe.ui.form.on('Shipments', {
    refresh: function (frm) {
        // Existing logic
    }
});

frappe.ui.form.on('Shipment Invoice', {
    purchase_invoice: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.purchase_invoice) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Purchase Invoice",
                    name: row.purchase_invoice
                },
                callback: function (r) {
                    if (r.message) {
                        var invoice = r.message;
                        console.log("Fetched Invoice:", invoice);

                        frappe.model.set_value(cdt, cdn, "invoice_no", invoice.bill_no || invoice.name);
                        frappe.model.set_value(cdt, cdn, "invoice_date", invoice.posting_date);

                        // If there are items, fetch the first one (or summarize)
                        if (invoice.items && invoice.items.length > 0) {
                            var item = invoice.items[0];
                            console.log("Fetched First Item:", item);

                            frappe.model.set_value(cdt, cdn, "item_code", item.item_code);
                            frappe.model.set_value(cdt, cdn, "item_name", item.item_name);
                            frappe.model.set_value(cdt, cdn, "qty", item.qty);
                            frappe.model.set_value(cdt, cdn, "uom", item.uom);
                            frappe.model.set_value(cdt, cdn, "rate", item.rate);
                            frappe.model.set_value(cdt, cdn, "amount", item.amount);
                            frappe.model.set_value(cdt, cdn, "batch_no", item.batch_no || "");
                        }
                    }
                }
            });
        }
    }
});
