// Copyright (c) 2019, Aakvatech Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Record', {
	onload: function(frm,cdt,cdn) {
		
	},
	setup: function(frm) {
		frm.set_query('expense_type', function() {
			return {
				filters: {
					'section': frm.doc.section
				}
			}
		});
	}
});

