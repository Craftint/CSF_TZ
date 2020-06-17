frappe.ui.form.on('Asset', {
	gross_purchase_amount: function (frm) {
        if (frm.doc.is_existing_asset) {
	        frm.set_value("purchase_receipt_amount",frm.doc.gross_purchase_amount);
	    } else {
	        frm.set_value("purchase_receipt_amount",0);
	    }
	},
	is_existing_asset: function (frm) {
	    if (!frm.doc.is_existing_asset) {
	        frm.set_value("purchase_receipt_amount",0);
	    }
	},
})