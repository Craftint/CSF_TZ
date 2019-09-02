// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('EFD Z Report', {
	get_invoices: function(frm) {
		return frappe.call({
			method: "get_invoices",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("efd_z_report_invoices");
				frm.refresh_fields();

				$(frm.fields_dict.efd_z_report_invoices.wrapper).find("[data-fieldname=invoice_amount]").each(function(i,v){
					if (i !=0){
						$(v).addClass("text-right")
					}
				})
			}
		});
	}
});
