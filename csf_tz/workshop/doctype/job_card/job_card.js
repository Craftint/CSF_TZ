// Copyright (c) 2017, Bravo Logistics and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Card', {
	refresh: function(frm) {
		console.log(frm);
		frm.events.show_hide_sections(frm);
		frm.events.items_request(frm);
		frm.events.toggle_editable_funds_rows(frm);
		frm.events.toggle_editable_rows(frm);
	},
	
	after_save: function(frm){
		frm.events.toggle_editable_funds_rows(frm);
		frm.events.toggle_editable_rows(frm);
		frm.reload_doc();
	},
	
	// Show or Hide sections depending on previously entered information.
	show_hide_sections: function(frm){
		frm.toggle_display("section_used_items", (frm.doc.requested_items && frm.doc.requested_items.length > 0));
		frm.toggle_display("section_expenses", (frm.doc.requested_funds && frm.doc.requested_funds.length > 0));
			
		frm.refresh_fields()
	},
	
	items_request: function(frm){
		var new_request = false
		if(frm.doc.requested_items && frm.doc.requested_items.length > 0)
		{
			frm.doc.requested_items.forEach(function(row){
				if(row.status == "Open")
				{
					new_request = true;
				}
			})
			if(new_request == true)
			{
				frappe.call({
					method: "fleet_management.workshop.doctype.requested_items.requested_items.request_items",
					args: {
						reference_doctype: "Job Card",
						reference_docname: cur_frm.doc.name
					},
					freeze: true,
					callback: function(data){
						if(data.message == ("Request Updated" || "Request Inserted"))
						{
							frm.doc.requested_items.forEach(function(row){
								if(row.status == "Open")
								{
									row.status = "Requested";
								}
							})
							frm.refresh_field('requested_items');
							frm.save_or_update();
						}
					}
				});
			}
		}
	},
	
	toggle_editable_rows: function(frm){
		if(frm.doc.requested_items && frm.doc.requested_items.length > 0)
		{
			frm.doc.requested_items.forEach(function(row){
				if(row.status != "Open")
				{
					//Make fields read only
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_items"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "item"})[0].read_only = true;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_items"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "quantity"})[0].read_only = true;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_items"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "requested_for"})[0].read_only = true;
				}
			})
		}
	},
	
	toggle_editable_funds_rows: function(frm){
		if(frm.doc.requested_funds && frm.doc.requested_funds.length > 0)
		{
			frm.doc.requested_funds.forEach(function(row){
				if(row.request_status.toUpperCase() != "OPEN")
				{
					//Make fields read only
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "request_date"})[0].read_only = true;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "request_amount"})[0].read_only = true;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "request_currency"})[0].read_only = true;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "request_description"})[0].read_only = true;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "comment"})[0].read_only = true;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "requested_for"})[0].read_only = true;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "quote_attachment"})[0].read_only = true;
				}
				else
				{
					//Make fields read only
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "request_date"})[0].read_only = false;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "request_amount"})[0].read_only = false;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "request_currency"})[0].read_only = false;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "request_description"})[0].read_only = false;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "comment"})[0].read_only = false;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "requested_for"})[0].read_only = false;
					frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {"fieldname": "quote_attachment"})[0].read_only = false;
				}
			})
		}
	},
	
	show_hide_subcontractor: function(frm, cdt, cdn){
		var row = frm.fields_dict['services_table'].grid.grid_rows_by_docname[cdn];
		row.toggle_display("subcontractor", row.doc.subcontracted == 1);
		row.toggle_display("technician", row.doc.subcontracted == 0);
		row.toggle_display("billable_hours", row.doc.subcontracted == 1);
		row.toggle_display("rate_per_hour", row.doc.subcontracted == 1);
		row.toggle_display("currency_rate_per_hour", row.doc.subcontracted == 1);
	}
});


frappe.ui.form.on('Requested Funds Details', {
	requested_funds_add: function(frm, cdt, cdn){
		//Make fields editable
		frm.events.toggle_editable_funds_rows(frm);
	},
	
	before_requested_funds_remove: function(frm, doctype, name) {
		var row = frappe.get_doc(doctype, name);
		if(row.request_status != 'open') {
			msgprint(__("Error: Cannot delete a processed request."));
			throw "Error: cannot delete a processed request";
		}
	}
});

frappe.ui.form.on('Requested Items Table', {
	requested_items_add: function(frm, cdt, cdn){
		//Make fields editabe
		frappe.utils.filter_dict(cur_frm.fields_dict["requested_items"].grid.grid_rows_by_docname[cdn].docfields, {"fieldname": "item"})[0].read_only = false;
		frappe.utils.filter_dict(cur_frm.fields_dict["requested_items"].grid.grid_rows_by_docname[cdn].docfields, {"fieldname": "quantity"})[0].read_only = false;
		frappe.utils.filter_dict(cur_frm.fields_dict["requested_items"].grid.grid_rows_by_docname[cdn].docfields, {"fieldname": "requested_for"})[0].read_only = false;
	},
	
	before_requested_items_remove: function(frm, doctype, name) {
		var row = frappe.get_doc(doctype, name);
		if(row.request_status != 'open') {
			msgprint(__("Error: Cannot delete a processed request."));
			throw "Error: cannot delete a processed request";
		}
	},
	
	item: function(frm, cdt, cdn){
		if(locals[cdt][cdn].item) {
			return frappe.call({
				method:"frappe.client.get_value",
				freeze: true,
				args: {
					doctype:"Item",
					filters: {
						name: locals[cdt][cdn].item
					},
					fieldname:["stock_uom", "description"]
				}, 
				callback: function(data){
					frappe.model.set_value(cdt, cdn, 'units', data.message.stock_uom);
					frappe.model.set_value(cdt, cdn, 'description', data.message.description);
				}
			});
		}
	}
});


frappe.ui.form.on('Workshop Services Table', {
	form_render: function(frm, cdt, cdn){
		frm.events.show_hide_subcontractor(frm, cdt, cdn);
	},
	
	subcontracted: function(frm, cdt, cdn){
		frm.events.show_hide_subcontractor(frm, cdt, cdn);
	}
});

