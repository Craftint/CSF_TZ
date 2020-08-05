frappe.ui.form.on("Company", {
	
	setup: function(frm) {
		frm.set_query("default_withholding_payable_account", function() {
			return {
				"filters": {
                    "company": frm.doc.name,
                    "account_type": "Tax",
				}
			};
		});
		frm.set_query("default_withholding_receivable_account", function() {
			return {
				"filters": {
                    "company": frm.doc.name,
                    "account_type": "Tax",
				}
			};
        });
	},
});
