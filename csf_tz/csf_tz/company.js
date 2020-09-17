frappe.ui.form.on("Company", {
	
	setup: function(frm) {
		frm.set_query("default_withholding_payable_account", function() {
			return {
				"filters": {
                    "company": frm.doc.name,
                    "account_type": "Payable",
				}
			};
		});
		frm.set_query("default_withholding_receivable_account", function() {
			return {
				"filters": {
                    "company": frm.doc.name,
                    "account_type": "Receivable",
				}
			};
		});
		frm.set_query("fee_bank_account", function() {
			return {
				"filters": {
                    "company": frm.doc.name,
					"account_type": ["in",["Cash","Bank"]],
					"account_currency": frm.doc.default_currency,
				}
			};
		});
		frm.set_query("student_applicant_fees_revenue_account", function() {
			return {
				"filters": {
                    "company": frm.doc.name,
					"account_type": "Income Account",
					"account_currency": frm.doc.default_currency,
				}
			};
        });
	},
});
