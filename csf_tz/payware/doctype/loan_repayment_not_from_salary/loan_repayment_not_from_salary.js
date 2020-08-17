// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Loan Repayment Not From Salary', {
	onload: function(frm) {
		frm.set_query("loan", function() {
			return {
				filters: {
					status: "Disbursed",
					docstatus: 1
				}
			}
		})
	}
});
