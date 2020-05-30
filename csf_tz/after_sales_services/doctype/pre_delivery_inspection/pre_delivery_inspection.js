// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

var data = sessionStorage.getItem("item_code_stored_predelivery");
var data2 = sessionStorage.getItem("serial_stored_predelivery");


frappe.ui.form.on('Pre Delivery Inspection', {
	refresh: function(frm) {
		//console.log(cur_frm)
		//console.log(data);
		if (!frm.doc.item_code) {
			frm.set_value("item_code", data);
		}
		if (!frm.doc.item_serial_no) {
			frm.set_value("item_serial_no", data2);		
		}
		/*frm.set_value("quality_inspection_template", data);
		frappe.after_ajax(function(){
			frm.events.quality_inspection_template(frm);
		});*/

		frm.events.load_delivery_note(frm);

	},
	
	item_code: function(frm) {
		if (frm.doc.item_code && frm.doc.item_code != '') {
			frappe.model.with_doc("Sales Invoice", frm.doc.sales_invoice_ref, function(){
				var ref_doc = frappe.get_doc("Sales Invoice", frm.doc.sales_invoice_ref);
				//console.log(ref_doc);

				if (ref_doc.items && ref_doc.items.length > 0) {
					ref_doc.items.forEach(function(row){

						if(row.item_code == data){
							frm.doc.item_name = row.item_name;
							frm.doc.description = row.description;
							frm.doc.batch_no = row.batch_no;
							frm.set_value("quality_inspection_template", row.item_code);
							//frm.doc.quality_inspection_template = row.item_code;
						}
						
					})
				}

			});	
		}
		
		frappe.after_ajax(function(){
			frm.refresh_field("item_name")
			frm.refresh_field("description")
			frm.refresh_field("batch_no")
			frm.events.quality_inspection_template(frm);
		})
	},
	
	quality_inspection_template: function(frm){
		if(frm.doc.quality_inspection_template){
			frappe.model.with_doc("Pre Delivery Inspection Template", frm.doc.quality_inspection_template, function(){
				var ref_doc = frappe.get_doc("Pre Delivery Inspection Template", frm.doc.quality_inspection_template);
				if(ref_doc && ref_doc.item_quality_inspection_parameter){
					frm.clear_table("readings");
					ref_doc.item_quality_inspection_parameter.forEach(function(row){
						var new_row = frm.add_child("readings");
						new_row.specification = row.specification;
					})
				}
			});
			frappe.after_ajax(function(){
				frm.refresh_field('readings');
			})
		}
	},

	load_delivery_note: function(frm){
		if(frm.fields_dict['dashboard_links_html'] && "dashboard_links_html" in frm.doc.__onload) {
			frm.fields_dict['dashboard_links_html'].wrapper.innerHTML = frm.doc.__onload.dashboard_links_html.display;	
		}
	},
});
