// Copyright (c) 2020, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Biometric Settings', {
	get_token: function(frm) {
		frappe.call({
			method: 'payware.payware.doctype.biometric_settings.biometric_settings.get_new_bio_token',
			callback: (r) => {
				
				cur_frm.set_value("bio_token", r.message);
				
			}
		});
	},

	get_transactions: function(frm) {
		frappe.call({
			method: 'payware.payware.doctype.biometric_settings.biometric_settings.get_transactions',
			args:{
				"start_time":frm.doc.start_time,
				"end_time":frm.doc.end_time,
			},
			callback: (r) => {
				if (r.message){
					// console.log(r.message);
					frappe.msgprint(r.message);
				}
				
			}
		});
	},
	make_employee_checkin: function(frm) {
		frappe.call({
			method: 'payware.payware.doctype.biometric_settings.biometric_settings.make_employee_checkin',
			
			callback: (r) => {
				if (r.message){
					// console.log(r.message);
					frappe.msgprint(r.message);
				}
				
			}
		});
	}	


});
