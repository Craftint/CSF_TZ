// Copyright (c) 2016, Bravo Logistics and contributors
// For license information, please see license.txt

frappe.ui.form.on('Assigned Transport Details', {
	refresh: function(frm) {

	},
	
	assigned_driver: function(frm){
		frappe.call({
			'method': 'frappe.client.get',
			args: {
				doctype: 'Employee',
				name: frm.doc.assigned_driver
			},
			callback: function(data){
				frm.set_value("passport_number", data.message.passport_number);
				//alert(data.message.passport_number);
			}
		});
	}
});
