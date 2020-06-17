// Copyright (c) 2020, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Type', {
	setup: function(frm) {
		frm.set_query('expense_account', function() {
			return {
				filters: {
					'company': frm.doc.company,
					"root_type": "Expense",
					'is_group': 0
				},
				order_by: "name"
			}
		});
	}
});
