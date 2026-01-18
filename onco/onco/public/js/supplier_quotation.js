frappe.ui.form.on('Supplier Quotation', {
    naming_series: function (frm) {
        frm.trigger('toggle_importation_fields');
    },

    refresh: function (frm) {
        frm.trigger('toggle_importation_fields');

        if (frm.doc.docstatus === 1 && frm.doc.naming_series.includes('IMA')) {
            frm.add_custom_button(__('Modify Approval'), function () {
                frm.trigger('create_ima_variant', 'MD');
            }, __('Actions'));

            frm.add_custom_button(__('Extend Approval'), function () {
                frm.trigger('create_ima_variant', 'EX');
            }, __('Actions'));
        }
    },

    create_ima_variant: function (frm, type) {
        const series = frm.doc.naming_series.includes('SPIMA') ? `EDA-SPIMA-${type}-` : `EDA-APIMA-${type}-`;

        frappe.model.with_doctype('Supplier Quotation', function () {
            let new_doc = frappe.model.get_new_doc('Supplier Quotation');
            new_doc.naming_series = series;
            new_doc.supplier = frm.doc.supplier;
            new_doc.items = [];

            // Map items
            frm.doc.items.forEach(item => {
                let row = frappe.model.add_child(new_doc, 'items');
                row.item_code = item.item_code;
                row.qty = item.qty;
                row.rate = item.rate;
                row.uom = item.uom;
            });

            new_doc.custom_importation_approval_ref = frm.doc.name;
            new_doc.custom_requested_quantity = frm.doc.custom_requested_quantity;

            frappe.set_route('Form', 'Supplier Quotation', new_doc.name);
        });
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

        const is_request = frm.doc.naming_series.includes('SPIMR') || frm.doc.naming_series.includes('APIMR');
        const is_approval = frm.doc.naming_series.includes('SPIMA') || frm.doc.naming_series.includes('APIMA');

        frm.toggle_display(['custom_spimr_no', 'custom_apimr_no', 'custom_requested_quantity'], is_request);
        frm.toggle_display(['custom_importation_approval_ref'], is_approval);

        if (is_request) {
            frm.toggle_display('custom_spimr_no', frm.doc.naming_series.includes('SPIMR'));
            frm.toggle_display('custom_apimr_no', frm.doc.naming_series.includes('APIMR'));
        }

        if (is_approval) {
            frm.toggle_reqd('custom_importation_approval_ref', true);
            frm.set_df_property('custom_importation_approval_ref', 'description', 'Link to the original Importation Approval Request');
        }
    }
});
