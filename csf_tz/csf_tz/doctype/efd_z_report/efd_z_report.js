// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

// frappe.ui.form.on('EFD Z Report', {
// 	get_invoices: function(frm) {
// 		return frappe.call({
// 			method: "get_invoices",
// 			doc: frm.doc,
// 			callback: function(r, rt) {
// 				frm.refresh_field("efd_z_report_invoices");
// 				frm.refresh_fields();
//
// 				$(frm.fields_dict.efd_z_report_invoices.wrapper).find("[data-fieldname=invoice_amount]").each(function(i,v){
// 					if (i !=0){
// 						$(v).addClass("text-right")
// 					}
// 				})
// 			}
// 		});
// 	}
// });

cur_frm.cscript.get_invoices = function (frm) {
	cur_frm.clear_table("efd_z_report_invoices")
	frappe.call({
			method: "get_sales_invoice",
			doc: cur_frm.doc,
			args: {
				"electronic_fiscal_device": cur_frm.doc.electronic_fiscal_device,
				"date_and_time": cur_frm.doc.z_report_date_time,
			},
			freeze: true,
			freeze_message: "Fetching Invoices...",
			callback: function(r) {
                cur_frm.refresh_field("efd_z_report_invoices")
            }
		});
}
// cur_frm.cscript.include = function (frm) {
// 	var total = 0
// 	console.log("BEEE")
// 	console.log(cur_frm.doc.efd_z_report_invoices.length)
// 	for(var x=0;x<cur_frm.doc.efd_z_report_invoices.length;x+=1){
// 		console.log(cur_frm.doc.efd_z_report_invoices[x].include)

// 		if(cur_frm.doc.efd_z_report_invoices[x].include){
// 			console.log(cur_frm.doc.efd_z_report_invoices[x].invoice_amount)
// 			total += cur_frm.doc.efd_z_report_invoices[x].invoice_amount
// 		}
// 	}
// 	console.log(total)

// 	cur_frm.doc.efd_z_report_invoices_amountinclude_is_ticked = total
// 	cur_frm.refresh_field("efd_z_report_invoices_amountinclude_is_ticked")
// }

frappe.ui.form.on('EFD Z Report Invoice', {
	include: (frm) => {
		let sum_excluding_vat_ticked = 0
		let sum_vat_ticked = 0
		let sum_turnover_exempted_sp_relief_ticked = 0
		let sum_turnover_ticked = 0
		frm.doc.efd_z_report_invoices.forEach(d => {
			if (d.include){
				sum_excluding_vat_ticked += d.amt_excl_vat;
			sum_vat_ticked += d.vat;
			sum_turnover_exempted_sp_relief_ticked += d.amt_ex__sr;
			sum_turnover_ticked += d.invoice_amount;
			}
		});
		frm.set_value("total_excluding_vat_ticked", sum_excluding_vat_ticked);
		frm.set_value("total_vat_ticked", sum_vat_ticked);
		frm.set_value("total_turnover_exempted__sp_relief_ticked", sum_turnover_exempted_sp_relief_ticked);
		frm.set_value("total_turnover_ticked", sum_turnover_ticked);
		
	}
})