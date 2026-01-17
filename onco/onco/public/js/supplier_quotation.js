frappe.ui.form.on('Supplier Quotation', {
    naming_series: function (frm) {
        frm.trigger('toggle_importation_fields');
    },

    refresh: function (frm) {
        frm.trigger('toggle_importation_fields');
    },

    custom_importation_approval_ref: function (frm) {
        if (frm.doc.custom_importation_approval_ref) {
            frappe.db.get_value('Supplier Quotation', frm.doc.custom_importation_approval_ref, 'custom_requested_quantity')
                .then(r => {
                    if (r.message && r.message.custom_requested_quantity) {
                        frm.set_value('actual_quantity', r.message.custom_requested_quantity);
                    }
                });
        }
    },

    toggle_importation_fields: function (frm) {
        if (!frm.doc.naming_series) return;

        // Importation Approval Series
        const is_approval = frm.doc.naming_series.includes('EDA-SPIMA') || frm.doc.naming_series.includes('EDA-APIMA');

        frm.toggle_reqd('custom_importation_approval_ref', is_approval);

        if (is_approval) {
            // For Approvals, we expect the Ref to be filled.
            frm.set_df_property('custom_importation_approval_ref', 'description', 'Mandatory for Importation Approvals');
        }
    }
});
