frappe.ui.form.on("Authority Good Release", {
    shipment_no: function (frm) {
        if (frm.doc.shipment_no) {
            frappe.db.get_doc("Shipments", frm.doc.shipment_no)
                .then(shipment => {
                    frm.set_value("invoice_no", shipment.invoice_no);
                    frm.set_value("batch_no", shipment.batch_no);
                    frm.set_value("manufacturing_date_", shipment.manufacturing_date_);
                    frm.set_value("expiry_date", shipment.expiry_date);

                    frm.trigger("populate_items_from_report_or_invoice");
                });
        }
    },

    populate_items_from_report_or_invoice: function (frm) {
        if (!frm.doc.shipment_no) return;

        // Try to fetch from Purchase Receipt Report first
        frappe.db.get_value("Purchase Receipt Report", { custom_shipment_ref: frm.doc.shipment_no, docstatus: 1 }, "name")
            .then(r => {
                if (r.message && r.message.name) {
                    frappe.db.get_doc("Purchase Receipt Report", r.message.name)
                        .then(report => {
                            frm.clear_table("items");
                            report.items.forEach(item => {
                                let row = frm.add_child("items");
                                row.item_code = item.item_code || ""; // Need to ensure item_code exists in report
                                row.item_name = item.item_name;
                                row.batch_no = item.batch_no || frm.doc.batch_no;
                                row.actual_qty = item.accepted_qty;
                                row.released_qty = item.accepted_qty; // Default to full release
                                row.release_status = "Released";
                            });
                            frm.refresh_field("items");
                        });
                } else {
                    // Fallback to Purchase Invoice
                    frm.trigger("populate_items_from_invoice");
                }
            });
    },

    populate_items_from_invoice: function (frm) {
        // Fetch items from the primary purchase invoice of the shipment
        frappe.db.get_value("Shipments", frm.doc.shipment_no, "purchase_invoice")
            .then(r => {
                if (r.message && r.message.purchase_invoice) {
                    frappe.db.get_doc("Purchase Invoice", r.message.purchase_invoice)
                        .then(invoice => {
                            frm.clear_table("items");
                            invoice.items.forEach(item => {
                                let row = frm.add_child("items");
                                row.item_code = item.item_code;
                                row.item_name = item.item_name;
                                row.batch_no = frm.doc.batch_no;
                                row.actual_qty = item.qty;
                                row.released_qty = item.qty;
                                row.release_status = "Released";
                            });
                            frm.refresh_field("items");
                        });
                }
            });
    }
});

frappe.ui.form.on("Authority Good Release Item", {
    released_qty: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (frm.doc.lot_release_subtype == "Lot Release Batch with Shortage Control Quantity") {
            frappe.model.set_value(cdt, cdn, "shortage_control_qty", (row.actual_qty || 0) - (row.released_qty || 0));
        } else {
            frappe.model.set_value(cdt, cdn, "shortage_control_qty", 0);
        }
        frappe.model.set_value(cdt, cdn, "net_released_qty", row.released_qty || 0);
    },
    actual_qty: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frm.script_manager.trigger("released_qty", cdt, cdn);
    }
});
