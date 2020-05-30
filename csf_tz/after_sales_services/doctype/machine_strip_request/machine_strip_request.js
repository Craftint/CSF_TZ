// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Machine Strip Request', {
	refresh: function(frm) {
		frm.set_query("stripped_serial_no", function(doc){
			return{
				"filters": {
					"item_code": doc.stripped_item_code,
					"delivery_document_type": ''
				}
			}
		})
		
		frm.set_query("target_serial_no", function(doc){
			return{
				"filters": {
					"item_code": doc.target_item_code,
					"delivery_document_type": ''
				}
			}
		})
		
		//Make job card button
		if (frm.doc.docstatus == 1){
			frm.add_custom_button(__('Make Job Card'),
				function() {
					frm.events.make_job_card();
				}
			);
		}
	},
	
	make_job_card: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.after_sales_services.doctype.machine_strip_request.machine_strip_request.make_job_card",
			frm: cur_frm
		})
	}
});
