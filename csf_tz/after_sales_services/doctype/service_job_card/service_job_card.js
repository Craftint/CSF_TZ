// Copyright (c) 2018, Agricom Africa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Job Card', {
	refresh: function(frm) {
		console.log(frm);
		frm.events.show_hide_sections(frm);
		frm.events.toggle_editable_funds_rows(frm);
		frm.events.toggle_editable_rows(frm);

		frm.set_query("serial_number", "items", function(doc, cdt, cdn) {
			return {
				filters: {
					customer: frm.doc.customer,
				}
			};
		});
		
		if(!frm.doc.company || frm.doc.company == '')
		{
			frm.set_value('company', frappe.defaults.get_user_default("company"));
		}
		
		frm.set_query("item", "requested_items", function(doc, cdt, cdn) {
			return {
				filters: {
					is_stock_item: 0,
				}
			};
		});

		if (frm.doc.docstatus==1) {
			frm.add_custom_button(__('Make Sales Invoice'),
				function() {
					frm.events.make_sales_invoice();
				}
			);
		//cur_frm.add_custom_button(__('Registration Card'), this.make_sales_invoice, __("Make"));

		}
	},
	make_sales_invoice: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.after_sales_services.doctype.service_job_card.service_job_card.make_sales_invoice",
			frm: cur_frm
		})
	},
	
	onload: function(frm){
		frm.events.items_request(frm);
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
					method: "erpnext.maintenance.doctype.requested_items.requested_items.request_items",
					args: {
						reference_doctype: "Service Job Card",
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
							frappe.after_ajax(function(){
								frm.save_or_update();
							});
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
		/*if(frm.doc.requested_funds && frm.doc.requested_funds.length > 0)
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
		}*/
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
	},
	
	form_render: function(frm, cdt, cdn){
		var row = frm.fields_dict['requested_funds'].grid.grid_rows_by_docname[cdn];
		row.toggle_editable("recommender_comment", 0);
		row.toggle_editable('approver_comment', 0);
		row.toggle_editable('conversion_rate', 0);
	},
	
	expense_type: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(!frm.doc.company) {
			frappe.model.set_value(cdt, cdn, 'expense_type', '');
			frappe.msgprint(__("Please set the Company"));
			return;
		}

		if(!d.expense_type) {
			return;
		}
		return frappe.call({
			method: "erpnext.hr.doctype.expense_claim.expense_claim.get_expense_claim_account",
			args: {
				"expense_claim_type": d.expense_type,
				"company": frm.doc.company
			},
			callback: function(r) {
				if (r.message) {
					d.expense_account = r.message.account;
					if(r.message.account){
						frappe.call({
							'method': 'frappe.client.get_value',
							'args': {
								'doctype': 'Account',
								'filters': {
									'name': r.message.account
								},
							   'fieldname':'account_currency'
							},
							'callback': function(res){
								frappe.model.set_value(cdt, cdn, 'expense_account_currency', res.message.account_currency);
							}
						});
					}
				}
			}
		});
	},
	
	payable_account: function(frm, cdt, cdn){
		if(locals[cdt][cdn].payable_account){
			frappe.call({
				'method': 'frappe.client.get_value',
				'args': {
					'doctype': 'Account',
					'filters': {
						'name': locals[cdt][cdn].payable_account
					},
				   'fieldname':'account_currency'
				},
				'callback': function(res){
					frappe.model.set_value(cdt, cdn, 'payable_account_currency', res.message.account_currency);
				}
			});
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
		if(row.request_status != 'Open') {
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

