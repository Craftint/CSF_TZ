// Copyright (c) 2022, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Email Salary Slips', {
	// refresh: function(frm) {

	// }

	// onload: function(frm) {
	// 	frm.get_field("employees").grid.cannot_add_rows = true;
	// },

	setup: function(frm) {
		frm.set_query("payroll_entry", function() {
			return {
				filters: [
					["Payroll Entry","docstatus", "=", "1"]
				]
			}
		});
	}
});
