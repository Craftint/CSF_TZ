// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payware Settings', {
	setup: function(frm) {
        frm.set_query('bank_account_for_tra', function() {
            return {
                filters: {
                    
                }
            }
        });
	}
})