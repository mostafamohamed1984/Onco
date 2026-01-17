frappe.ui.form.on('Supplier Quotation', {
    refresh: function (frm) {
        // Validation for Naming Series logic
        frm.trigger('toggle_naming_series');

        // Add custom buttons for Importation Cycle
        if (frm.doc.docstatus === 1) {
            // Modification Button
            frm.add_custom_button(__('Create Modification'), function () {
                frappe.model.open_mapped_doc({
                    method: "onco.onco.doctype.supplier_quotation.supplier_quotation.create_modification",
                    frm: frm
                });
            }, __("Actions"));

            // Extension Button
            frm.add_custom_button(__('Create Extension'), function () {
                frappe.model.open_mapped_doc({
                    method: "onco.onco.doctype.supplier_quotation.supplier_quotation.create_extension",
                    frm: frm
                });
            }, __("Actions"));

            // Generate Approval (if approved)
            if (frm.doc.status === "Totally Approved" || frm.doc.status === "Partially Approved") {
                // Logic handled via Workflow mostly, but maybe buttons here?
            }
        }

        // Partial Approval Logic
        if (frm.doc.custom_importation_status === "Partially Approved") {
            frm.trigger('enable_fields_for_partial_approval');
        }
    },

    custom_importation_status: function (frm) {
        if (frm.doc.custom_importation_status === "Partially Approved") {
            frm.trigger('enable_fields_for_partial_approval');
        }
    },

    toggle_naming_series: function (frm) {
        if (frm.doc.naming_series && frm.doc.naming_series.includes("EDA-SPIMR")) {
            // Logic for SPIMR specific fields if any
        }
    },

    enable_fields_for_partial_approval: function (frm) {
        // Unlock Child Table fields for editing
        frm.fields_dict['items'].grid.update_docfield_property('qty', 'read_only', 0);
        frm.fields_dict['items'].grid.update_docfield_property('rate', 'read_only', 0);
    }
});
