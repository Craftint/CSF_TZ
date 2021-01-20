frappe.ui.form.on("Landed Cost Voucher", {
    import_file: function (frm) {
        frm.clear_table("taxes");
        if (frm.doc.import_file) {
            frappe.call({
                method: 'csf_tz.csftz_hooks.landed_cost_voucher.get_landed_cost_expenses',
                args: {
                    import_file: frm.doc.import_file,
                },
                async: false,
                callback: function (r) {
                    if (r.message) {
                        r.message.forEach(element => {
                            var child = frm.add_child("taxes");
                            frappe.model.set_value(child.doctype, child.name, "expense_account", element.expense_account);
                            frappe.model.set_value(child.doctype, child.name, "description", element.description);
                            frappe.model.set_value(child.doctype, child.name, "amount", element.amount);
                        })
                    }
                }
            });
        }
        frm.refresh_field("taxes");
    },
});

