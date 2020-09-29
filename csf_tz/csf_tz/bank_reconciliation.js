frappe.ui.form.on('Bank Reconciliation', {
    get_payment_entries: function (frm) {
        frappe.call({
            method: 'erpnext.accounts.utils.get_balance_on',
            args: {
                account: frm.doc.account,
                date: frappe.datetime.add_days(frm.doc.from_date, -1),
            },
            async: false,
            callback: function (r) {
                if (r.message) {
                    frm.set_value("opening_balance", r.message || 0);
                }
                else {
                    frm.set_value("opening_balance", 0);
                }
            }
        });
        frm.set_value("closing_balance", frm.doc.total_amount + frm.doc.opening_balance);
    },
});
