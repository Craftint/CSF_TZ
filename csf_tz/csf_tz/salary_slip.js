frappe.ui.form.on("Salary Slip", {
    setup: function(frm) {
        frm.trigger("create_update_slip_btn");
        
    },
    refresh:function(frm) {
        frm.trigger("create_update_slip_btn");
    },
    create_update_slip_btn: function (frm) {
        if (frm.doc.docstatus != 0 || frm.is_new()) {
            return
        }
        frm.add_custom_button(__("Update Salary Slip"), function() {
            frappe.call({
                method: 'csf_tz.csftz_hooks.payroll.update_slip',
                args: {
                    salary_slip: frm.doc.name,
                },
                callback: function(r) {
                    if (r.message) {
                        frm.reload_doc();
                    }
                }
            });
        });
    },
});