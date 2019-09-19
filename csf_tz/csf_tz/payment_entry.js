frappe.ui.form.on("Payment Entry", {
    payment_type: function(frm) {
        if (frm.doc.payment_type == "Receive") {
            frm.set_value("naming_series","RE-.YYYY.-");
            frm.set_value("party_type", "Customer");
        }
        else if (frm.doc.payment_type == "Pay") {
            frm.set_value("naming_series","PE-.YYYY.-");
            frm.set_value("party_type", "Supplier");
        }
        else if (frm.doc.payment_type == "Internal Transfer") {
            frm.set_value("naming_series","IT-.YYYY.-");
        }
    },
});
