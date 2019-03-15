// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Open Invoice Exchange Rate Revaluation', {
	refresh: function(frm) {

	},
	currency:function(frm,cdt,cdn){
		var doc=locals[cdt][cdn]
		if(frm.doc.currency && frm.doc.revaluation_date){
			frappe.call({
				method:"csf_tz.custom_api.getInvoiceExchangeRate",
				args:{'currency':frm.doc.currency,'date':frm.doc.revaluation_date},
				callback:function(r){
					console.log(r.message)
					cur_frm.set_value("exchange_rate_to_company_currency",r.message)
					
				}

			})
		}

	},
	get_invoices:function(frm,cdt,cdn){
		if(frm.doc.__islocal) {
			frappe.throw("Save Document Before Get Invoice")
		}
		if(frm.doc.currency && frm.doc.name){
			frappe.call({
				method:"csf_tz.custom_api.getInvoice",
				args:{'currency':frm.doc.currency,'name':frm.doc.name},
				freeze: true,
				freeze_message: "Please Wait...",
				callback:function(data){
					if(data.message){
						frm.clear_table("inv_err_detail");
						frm.refresh_fields("inv_err_detail");
						frm.reload_doc();	
					}
			
				}


			})
		}
		else{

				frappe.msgprint("Currency Mandatory And Document Saved Before Get Invoice")
			}
		
	}
});
