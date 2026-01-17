frappe.ui.form.on('Purchase Order', {
    refresh: function (frm) {
        // Optional: Filter the Link field to show only 'Approved' Supplier Quotations or specific series
        if (frm.fields_dict['custom_importation_approval']) {
            frm.set_query('custom_importation_approval', function () {
                return {
                    filters: [
                        ['Supplier Quotation', 'naming_series', 'in', ['EDA-SPIMA-.YYYY.-', 'EDA-APIMA-.YYYY.-']],
                        ['Supplier Quotation', 'docstatus', '!=', 2] // Not cancelled
                    ]
                };
            });
        }
    },

    custom_importation_approval: function (frm) {
        if (frm.doc.custom_importation_approval) {
            // Auto-fill IMP No (aian) with the ID of the selected Approval
            // Assuming 'aian' is the field for IMP No as per previous analysis
            frm.set_value('aian', frm.doc.custom_importation_approval);

            // Optionally fetch other details if needed, e.g. Supplier
            frappe.db.get_value('Supplier Quotation', frm.doc.custom_importation_approval, 'supplier')
                .then(r => {
                    if (r.message && r.message.supplier && !frm.doc.supplier) {
                        frm.set_value('supplier', r.message.supplier);
                    }
                });
        } else {
            frm.set_value('aian', '');
        }
    }
});
