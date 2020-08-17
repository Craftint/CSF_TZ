// Copyright (c) 2018, Aakvatech Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Loan', {
	refresh: function(frm) {
		if(!frm.doc.__islocal) {
			frm.add_custom_button(__('Redo Repayment Schedule'), function() {
				redo_repayment_schedule(cur_frm);
			});
		}
	}
});

var redo_repayment_schedule = function(frm){
	var doc = frm.doc;
	frappe.call({
		method: "payware.payware.utils.redo_repayment_schedule",
		args: {
			loan_name: doc.name
		},
		callback: function(){
			cur_frm.reload_doc();
		}
	});
};