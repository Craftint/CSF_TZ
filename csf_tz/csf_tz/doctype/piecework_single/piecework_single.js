// Copyright (c) 2021, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Piecework Single', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Single Piecework Employees', {
	task: (frm, cdt, cdn) => {
		const row = locals[cdt][cdn];
		setTotal(frm, row);
	},
	task_rate: (frm, cdt, cdn) => {
		const row = locals[cdt][cdn];
		setTotal(frm, row);
	},
	quantity: (frm, cdt, cdn) => {
		const row = locals[cdt][cdn];
		setTotal(frm, row);
	},
});

const setTotal = (frm, row) => {
	const total = row.task_rate * row.quantity || 0;
	frappe.model.set_value(row.doctype, row.name, "amount", total);
};