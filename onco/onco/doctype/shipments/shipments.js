
// Custom Logic for Shipments
frappe.ui.form.on("Shipments", {
  refresh: function (frm) {
    frm.trigger("render_dashboard");
    frm.trigger("update_awb_swb_labels");
    
    if (frm.doc.docstatus === 1 && frm.doc.status === "Completed") {
      frm.add_custom_button(__("Purchase Receipt"), function () {
        frappe.model.open_mapped_doc({
          method: "onco.onco.doctype.shipments.shipments.make_purchase_receipt",
          frm: frm
        })
      }, __("Create"));
    }

    if (frm.doc.docstatus === 0 && !frm.doc.source_warehouse) {
      frm.set_value("source_warehouse", "Imported Finished Phr Incoming Warehouse - Onco");
      frm.set_value("target_warehouse", "Imported Finished Phr Receipt and Inspection Warehouse - Onco");
    }
  },

  mode_of_shipping: function (frm) {
    frm.trigger("set_naming_series");
    frm.trigger("update_awb_swb_labels");
  },

  update_awb_swb_labels: function (frm) {
    // Update AWB/SWB labels dynamically based on mode of shipping
    if (frm.doc.mode_of_shipping === "Air freight") {
      // Show AWB fields
      frm.set_df_property("awb", "label", "AWB");
      if (frm.fields_dict.awb_no) {
        frm.set_df_property("awb_no", "label", "AWB No");
        frm.set_df_property("awb_no", "hidden", 0);
        frm.set_df_property("awb_no", "reqd", 1);
      }
      if (frm.fields_dict.swb_no) {
        frm.set_df_property("swb_no", "hidden", 1);
        frm.set_df_property("swb_no", "reqd", 0);
      }
      if (frm.fields_dict.awb_date) {
        frm.set_df_property("awb_date", "label", "AWB Date");
        frm.set_df_property("awb_date", "hidden", 0);
        frm.set_df_property("awb_date", "reqd", 1);
      }
    } else if (frm.doc.mode_of_shipping === "Sea freight") {
      // Show SWB fields
      frm.set_df_property("awb", "label", "SWB");
      if (frm.fields_dict.swb_no) {
        frm.set_df_property("swb_no", "label", "SWB No");
        frm.set_df_property("swb_no", "hidden", 0);
        frm.set_df_property("swb_no", "reqd", 1);
      }
      if (frm.fields_dict.awb_no) {
        frm.set_df_property("awb_no", "hidden", 1);
        frm.set_df_property("awb_no", "reqd", 0);
      }
      if (frm.fields_dict.awb_date) {
        frm.set_df_property("awb_date", "label", "SWB Date");
        frm.set_df_property("awb_date", "hidden", 0);
        frm.set_df_property("awb_date", "reqd", 1);
      }
    }
    frm.refresh_fields();
  },

  awb_no: function (frm) {
    frm.trigger("set_naming_series");
  },

  swb_no: function (frm) {
    frm.trigger("set_naming_series");
  },

  set_naming_series: function (frm) {
    if (frm.doc.mode_of_shipping && (frm.doc.awb_no || frm.doc.swb_no)) {
      let suffix = frm.doc.mode_of_shipping === "Air freight" ? "AWB-" + (frm.doc.awb_no || "") : "SWB-" + (frm.doc.swb_no || "");
      // Note: In Frappe, we can't easily change the name if it's already saved, 
      // but we can set the naming series if we have multiple.
      // The requirement says "SHIP-IMP-AWB-00000000".
      // We will assume the user has a custom naming series or we use a field to display it.
      // For now, let's just make sure the fields are clear.
    }
  },

  purchase_invoice: function (frm) {
    if (frm.doc.purchase_invoice) {
      frappe.db.get_value("Purchase Invoice", frm.doc.purchase_invoice, "custom_importation_approval")
        .then(r => {
          if (r.message && r.message.custom_importation_approval) {
            frm.set_value("custom_importation_approval", r.message.custom_importation_approval);
          }
        });
    }
  },

  custom_invoices: function (frm, cdt, cdn) {
    // Auto-populate invoice details when invoices are added
    let row = locals[cdt][cdn];
    if (row.purchase_invoice) {
      frm.trigger("populate_invoice_details", row);
    }
  },

  populate_invoice_details: function (frm, row) {
    if (!row || !row.purchase_invoice) {
      return;
    }

    // Fetch invoice details with items and batches
    frappe.call({
      method: "onco.onco.doctype.shipments.shipments.get_invoice_items_with_batches",
      args: {
        purchase_invoice: row.purchase_invoice
      },
      callback: function(r) {
        if (r.message) {
          let invoice_data = r.message;
          
          // Set invoice number and date
          frappe.model.set_value(row.doctype, row.name, "invoice_number", invoice_data.invoice_number);
          frappe.model.set_value(row.doctype, row.name, "invoice_date", invoice_data.invoice_date);
          
          // For now, populate with first item (can be enhanced to show all items)
          if (invoice_data.items && invoice_data.items.length > 0) {
            let first_item = invoice_data.items[0];
            frappe.model.set_value(row.doctype, row.name, "item", first_item.item_code);
            frappe.model.set_value(row.doctype, row.name, "quantity", first_item.quantity);
            frappe.model.set_value(row.doctype, row.name, "batch_number", first_item.batch_no || "");
          }
          
          frm.refresh_field("custom_invoices");
        }
      }
    });
  },

  validate: function (frm) {
    if (frm.doc.cold_chain && !frm.doc.cold_chain_equipment_ready) {
      frappe.throw(__("Cold Chain Equipment must be ready for Cold Chain shipments."));
    }
    
    // Validate status sequence (client-side check)
    frm.trigger("validate_status_sequence");
  },

  validate_status_sequence: function (frm) {
    // Client-side validation for status sequence
    const stages = [
      { field: "arrived", label: "Arrival Status" },
      { field: "bank_authenticated", label: "Bank Authentication" },
      { field: "restricted_release_status", label: "Restricted Release Status" },
      { field: "customs_release_status", label: "Customs Release Status" },
      { field: "received_at_warehouse", label: "Received at Warehouse" }
    ];
    
    let previous_completed = true; // Acceptance is always first
    
    for (let i = 0; i < stages.length; i++) {
      const stage = stages[i];
      const current_value = frm.doc[stage.field];
      
      if (current_value && !previous_completed) {
        const prev_label = i > 0 ? stages[i - 1].label : "Shipment Acceptance";
        frappe.throw(__("Cannot complete '{0}' stage. Please complete '{1}' stage first.").format(stage.label, prev_label));
      }
      
      previous_completed = current_value || false;
    }
  },

  arrived: function (frm) { frm.trigger("render_dashboard"); },
  bank_authenticated: function (frm) {
    if (frm.doc.bank_authenticated && !frm.doc.date_of_submission_bank) {
      frm.set_value("date_of_submission_bank", frappe.datetime.get_today());
    }
    frm.trigger("render_dashboard");
  },
  restricted_release_status: function (frm) {
    if (frm.doc.restricted_release_status && !frm.doc.date_of_submission_restricted) {
      frm.set_value("date_of_submission_restricted", frappe.datetime.get_today());
    }
    frm.trigger("render_dashboard");
  },
  customs_release_status: function (frm) {
    if (frm.doc.customs_release_status && !frm.doc.date_of_submission_customs) {
      frm.set_value("date_of_submission_customs", frappe.datetime.get_today());
    }
    frm.trigger("render_dashboard");
  },
  received_at_warehouse: function (frm) {
    if (frm.doc.received_at_warehouse) {
      frm.set_value("received_date", frappe.datetime.get_today());
      frm.set_value("time_of_received", frappe.datetime.now_time());
    }
    frm.trigger("render_dashboard");
  },

  render_dashboard: function (frm) {
    // Steps Mapping
    const steps = [
      { label: "Acceptance", done: has_attachments(frm) },
      { label: "Arrival", done: frm.doc.arrived },
      { label: "Bank Auth", done: frm.doc.bank_authenticated },
      { label: "Restricted Release", done: frm.doc.restricted_release_status },
      { label: "Customs Release", done: frm.doc.customs_release_status },
      { label: "Warehouse Receipt", done: frm.doc.received_at_warehouse }
    ];

    let html = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background-color: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
        `;

    steps.forEach((step, index) => {
      let color = step.done ? "#48bb78" : "#a0aec0"; // Green vs Gray
      let icon = step.done ? "✓" : (index + 1);
      let weight = step.done ? "bold" : "normal";

      html += `
                <div style="text-align: center; flex: 1;">
                    <div style="
                        width: 30px; 
                        height: 30px; 
                        background-color: ${color}; 
                        color: white; 
                        border-radius: 50%; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center;
                        margin: 0 auto 8px;
                        font-weight: bold;
                    ">
                        ${icon}
                    </div>
                    <div style="font-size: 12px; color: ${step.done ? '#2d3748' : '#718096'}; font-weight: ${weight};">
                        ${step.label}
                    </div>
                </div >
  `;

      // Add connector line except for last item
      if (index < steps.length - 1) {
        html += `<div style="flex: 1; height: 2px; background-color: #e2e8f0; margin-top: -20px;"></div>`;
      }
    });

    html += `</div>`;

    frm.fields_dict['shipment_status_dashboard'].wrapper.innerHTML = html;
  }
});

function has_attachments(frm) {
  // Basic check if AWB or Invoice is attached 
  // Ideally we check specific fields or attachment service
  return frm.doc.awb || frm.doc.invoice;
}
