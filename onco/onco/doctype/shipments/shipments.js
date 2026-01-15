// Copyright (c) 2025, ds and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shipments", {
	after_save(frm) {
    let shipment_id = frm.doc.name;
    frm.call({
      method:"set_shipment_id",
      args:{
        purchase_inv:frm.doc.purchase_invoice,
        ship:shipment_id,
      },
      callback:function(response){
          console.log("Message",response.message)

      }
    })
	},
});
