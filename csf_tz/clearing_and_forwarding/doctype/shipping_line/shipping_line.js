// Copyright (c) 2016, Bravo Logisitcs and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shipping Line', {
	refresh: function(frm) {
		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Shipping Line'};
		if(!frm.doc.__islocal) {
			frappe.contacts.render_address_and_contact(frm);
		}else {
			frappe.contacts.clear_address_and_contact(frm);
		}
	}
});
