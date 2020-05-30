// Copyright (c) 2016, Bravo Logisitcs and contributors
// For license information, please see license.txt


frappe.ui.form.on('Import', {
	refresh: function(frm){
		console.log(frm);
		frm.events.open_close_buttons(frm);
		
		// Show/hide sections
		frm.events.show_hide_sections(frm);
		//Show or hide elements depending on Import type
		frm.events.import_type(frm);
		frm.events.point_of_entry(frm);
		
		/*
		*  Hide employee link. Note: If the position of the grid is changed 
		*  (e.g another grid is added above it) the grid number needs to change
		*/
		frm.grids[1].grid.set_column_disp('assigned_driver');
		
		//For loading mandatory attachments
		if(!frm.doc.attachments || frm.doc.attachments.length == 0)
		{
			frappe.model.with_doc('Mandatory Attachments', 'Mandatory Attachments', function(){
				var reference_doc = frappe.get_doc('Mandatory Attachments', 'Mandatory Attachments');
				console.log(reference_doc);
				if(reference_doc.common_import.length > 0)
				{
					reference_doc.common_import.forEach(function(row){
						var new_row = frm.add_child('attachments');
						new_row.description = row.attachment_name;
						new_row.mandatory = 1;
					});
					frm.refresh_field('attachments');
				}
			});
		}
	},
	
	onload: function(frm){
		frm.events.disable_enable_fields(frm);	
		
		//Show request transport button only if cargo has been added
		if(frm.doc.cargo_information && frm.doc.cargo_information.length != 0)
		{
			//Check if there is unrequested cargo
			var need_assign = false;
			frm.doc.cargo_information.forEach(function(row){
				if(row.transport_status == 0)
				{
					need_assign = true;
				}
			});
			
			//Check if eta < 10 days
			var today = new Date();
			var eta = frm.doc.eta.split('-');
			var eta_date = new Date(eta[0], eta[1]-1, eta[2]);
			var difference = Math.round(Math.abs((eta_date.getTime()-today.getTime())/(1000*60*60*24)));
			
			//If there is unrequested cargo and eta < 10
			if(need_assign && difference < 10)
			{
				frappe.call({
					method: "fleet_management.fleet_management.doctype.transport_request.transport_request.create_transport_request",
					args: {
						reference_doctype: "Import",
						reference_docname: cur_frm.doc.name,
						file_number: cur_frm.doc.reference_file_number
					},
					callback: function(data){
						//alert(JSON.stringify(data));
						frm.doc.cargo_information.forEach(function(row){
							if(row.transport_status == 0)
							{
								row.transport_status = 1;
							}
						});
						show_alert("Transport Request Sent", 5);
						frm.save_or_update();
					}
				})
			}	
			
			
			frm.events.toggle_editable_funds_rows(frm);	
		}
	},
	
	open_close_buttons: function(frm){
		//if (!frm.doc.__islocal) {
			if(frm.doc.status=="Open") {
				frm.add_custom_button(__("Close"), function() {
					if(frm.events.validate_close(frm))
					{
						frm.set_value("status", "Closed");
						frm.save();
					}
				}, "fa fa-check", "btn-success");
			} else {
				frm.add_custom_button(__("Re-open"), function() {
					frm.set_value("status", "Open");
					frm.save();
				}, null, "btn-default");
			}
		//}
	},
	
	disable_enable_fields: function(frm){
		if(frm.doc.status == "Closed")
		{
			frm.meta.fields.forEach(function(field){
				frm.toggle_enable(field.fieldname, false);
			});
		}
	},
	
	
	validate_close: function(frm){
		var excluded_fields = ["clearing_agent_border_1", "clearing_agent_border_2", "clearing_agent_border_3", "house_bill_of_lading", "assign_transport",
								"required_permits", "requested_funds", "expenses", "attachments", "procedures", "border_customer", "reference_trip", "cargo_type",
								"amended_from", "transport_requested", "special_instructions_to_transporter"];
		var local_excluded_fields = ['t1_generated', 't1_approved']; //For local imports
		var excluded_field_type = ["Table", "Section Break", "Column Break"]
		var error_fields = [];
		frm.meta.fields.forEach(function(field){
			if(!(excluded_field_type.indexOf(field.fieldtype) > -1) && !(excluded_fields.indexOf(field.fieldname) > -1) && !(field.fieldname in frm.doc))
			{
				if(frm.doc.import_type && frm.doc.import_type == 'Local' && local_excluded_fields.indexOf(field.fieldname) != -1)
				{
					return false;
				}
				else
				{
					error_fields.push(field.label);
					return false;
				}				
			}
			
			if(field.fieldtype == "Table" && !(excluded_fields.indexOf(field.fieldname) > -1) && frm.doc[field.fieldname].length == 0)
			{
				error_fields.push(field.label);
				return false;
			}
		})
		
		if(error_fields.length > 0)
		{
			var error_msg = "Mandatory fields required before closing <br><ul>";
			error_fields.forEach(function(error_field){
				error_msg = error_msg + "<li>" + error_field + "</li>";
			})
			error_msg = error_msg + "</ul>";
			frappe.msgprint(error_msg, "Missing Fields");
			return false;
		}
		else
		{
			return true;
		}
	},
	
	
	// Show or Hide sections depending on previously entered information.
	show_hide_sections: function(frm){
		frm.toggle_display('section_border', (frm.doc.point_of_entry == 'Border Post' && frm.doc.location && frm.doc.documents_received_date));
		
		frm.toggle_display("client_information_section", (frm.doc.bl_number &&
				frm.doc.location && frm.doc.documents_received_date));
		frm.toggle_display("shipping_line_information", true);
		
		if(frm.doc.shipper && frm.doc.consignee && frm.doc.notify_party && frm.doc.customer)
		{
			frm.toggle_display("shipping_line_information", true);
			frm.set_df_property("client_information_section", "collapsible", "1");
		}
				
		frm.toggle_display("cargo_information_section", (frm.doc.shipping_line &&
				frm.doc.vessel_name && frm.doc.voyage && frm.doc.port_of_loading && frm.doc.port_of_discharge && frm.doc.eta));
				
		frm.toggle_display('cargo_information', (frm.doc.cargo && frm.doc.cargo != ""));
				
		frm.toggle_display("documentation_information", (frm.doc.cargo_information && frm.doc.cargo_information.length != 0));
		frm.toggle_display("section_required_permits", (frm.doc.cargo_information && frm.doc.cargo_information.length != 0));
		frm.toggle_display("section_customs_processing", (frm.doc.cargo_information && frm.doc.cargo_information.length != 0));
		frm.toggle_display("section_shipping_line_processes", (frm.doc.cargo_information && frm.doc.cargo_information.length != 0));
		frm.toggle_display("section_port_processes", (frm.doc.cargo_information && frm.doc.cargo_information.length != 0));
		frm.toggle_display("section_assigned_transport", (frm.doc.cargo_information && frm.doc.cargo_information.length != 0));
		frm.toggle_display("requested_funds_section", ((frm.doc.cargo_information && frm.doc.cargo_information.length != 0) || (frm.doc.point_of_entry == 'Border Post' && frm.doc.location && frm.doc.documents_received_date)));
		frm.toggle_display("expenses_section", (frm.doc.requested_funds && frm.doc.requested_funds.length != 0));
		frm.toggle_display("closing_information_section", ((frm.doc.requested_funds && frm.doc.requested_funds.length != 0) && (frm.doc.point_of_entry != 'Border Post')));
			
		frm.refresh_fields()
	},
	
	point_of_entry: function(frm){
		if(frm.doc.point_of_entry == "Port")
		{
			frm.toggle_display("bl_number", true);
		}
		
		frm.toggle_display('location', true);
		frm.toggle_display('documents_received_date', true);
		frm.events.show_hide_sections(frm);
	},

	bl_number: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	location: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	documents_received_date: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	cargo_type: function(frm){
		if(frm.doc.cargo_type && frm.doc.cargo_type != "")
		{
			frappe.model.with_doc('Cargo Type', frm.doc.cargo_type, function(frm){
				reference = frappe.model.get_doc('Cargo Type', cur_frm.doc.cargo_type);
				reference.border_procedure.forEach(function(row){
					var new_row = cur_frm.add_child('procedures');
					new_row.procedure = row.procedure;
				});
			});
			frappe.after_ajax(function(frm){
				cur_frm.refresh_field('procedures');
			});
		}
	},
	
	shipper: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	consignee: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	notify_party: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	customer: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	house_bill_of_lading: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	shipping_line: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	vessel_name: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	voyage: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	port_of_loading: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	port_of_discharge: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	eta: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	cargo: function(frm){
		if(frm.doc.cargo && frm.doc.cargo != "")
		{
			frm.toggle_display('cargo_information', true);
		}
		
		//Load required permits
		if(frm.doc.cargo == "")
		{
			frm.clear_table('required_permits');
			frm.refresh_field('required_permits');
		}
		else
		{
			frappe.model.with_doc('Cargo Type', frm.doc.cargo, function(){
				var reference_doc = frappe.get_doc('Cargo Type', frm.doc.cargo);
				
				//Load required permits
				if(frm.doc.import_type == 'Local')
				{
					frm.clear_table('required_permits');
					frm.refresh_field('required_permits');
					if(reference_doc.local_import.length > 0)
					{
						reference_doc.local_import.forEach(function(row){
							var new_row = frm.add_child('required_permits');
							new_row.description = row.permit_name;
							frappe.after_ajax(function(){
								frm.refresh_field("required_permits");
							});
						});
					}
				}
				else if(frm.doc.import_type == 'Transit')
				{
					frm.clear_table('required_permits');
					frm.refresh_field('required_permits');
					if(reference_doc.transit_import.length > 0)
					{
						reference_doc.transit_import.forEach(function(row){
							var new_row = frm.add_child('required_permits');
							new_row.description = row.permit_name;
							frappe.after_ajax(function(){
								frm.refresh_field("required_permits");
							});
						});
					}
				}
			});
		}
	},
	
	import_type: function(frm){
		if(frm.doc.import_type == 'Local')
		{
			frm.toggle_display("t1_generated", false);
			frm.toggle_display("t1_approved", false);
		}
		else
		{
			frm.toggle_display("t1_generated", true);
			frm.toggle_display("t1_approved", true);
		}
		
		//For loading mandatory attachments
		if(frm.doc.attachments && frm.doc.attachments.length > 0)
		{
			frappe.model.with_doc('Mandatory Attachments', 'Mandatory Attachments', function(){
				var reference_doc = frappe.get_doc('Mandatory Attachments', 'Mandatory Attachments');
				var transit_loaded = false;
				var local_loaded = false;
				
				//Check if transit mandatory attachemnts loaded
				if(reference_doc.transit_import.length > 0)  
				{
					frm.doc.attachments.forEach(function(row){
						if(row.description.toUpperCase() == reference_doc.transit_import[0].attachment_name.toUpperCase())  //If transit attachments loaded
						{
							transit_loaded = true;
						}
					});
				}
				
				//Check if local mandatory attachemnts loaded
				if(reference_doc.local_import.length > 0) 
				{
					frm.doc.attachments.forEach(function(row){
						if(row.description.toUpperCase() == reference_doc.local_import[0].attachment_name.toUpperCase())  //If transit attachments loaded
						{
							local_loaded = true;
						}
					});
				}
				
				//Check if import type is local and transit attachments loaded
				if('Local' == frm.doc.import_type && transit_loaded)
				{
					//Delete transit attachments
					reference_doc.transit_import.forEach(function(reference_row){
						frm.get_field('attachments').grid.grid_rows.forEach(function(attachment_row){
							if(reference_row.attachment_name.toUpperCase() == attachment_row.doc.description.toUpperCase())
							{
								attachment_row.remove();
							}
						});
					});
				}
				else if('Transit' == frm.doc.import_type && local_loaded) //If import type is transit and local attachments loaded
				{
					//Delete local attachments
					reference_doc.local_import.forEach(function(reference_row){
						frm.get_field('attachments').grid.grid_rows.forEach(function(attachment_row){
							if(reference_row.attachment_name.toUpperCase() == attachment_row.description.toUpperCase())
							{
								attachment_row.remove();
							}
						});
					});
				}
				
				//Load local attachments
				if('Local' == frm.doc.import_type && !local_loaded && reference_doc.local_import.length > 0)
				{
					reference_doc.local_import.forEach(function(row){
						var new_row = frm.add_child('attachments');
						new_row.description = row.attachment_name;
						new_row.mandatory = 1;
					});
					frm.refresh_field('attachments');
				}
				else if('Transit' == frm.doc.import_type && !transit_loaded && reference_doc.transit_import.length > 0)  //Load transit attachments
				{
					reference_doc.transit_import.forEach(function(row){
						var new_row = frm.add_child('attachments');
						new_row.description = row.attachment_name;
						new_row.mandatory = 1;
					});
					frm.refresh_field('attachments');
				}
			});
		}
	},
	
	new_fund_request: function(frm){
		var new_request = false
		if(frm.doc.requested_funds && frm.doc.requested_funds.length > 0)
		{
			frm.doc.requested_funds.forEach(function(row){
				if(row.request_status == "open")
				{
					new_request = true
				}
			})
			if(new_request == true)
			{
				frappe.call({
					method: "csf_tz.after_sales_services.doctype.requested_payments.requested_payments.request_funds",
					args: {
						reference_doctype: "Import",
						reference_docname: cur_frm.doc.name,
						company: cur_frm.doc.company
					},
					callback: function(data){
						console.log(data);
					}
				})
			}
		}
	},
	
	validate: function(frm){
		//Check if for each bond reference no entered, there is also a bond value entered
		/*if(frm.doc.cargo_information && frm.doc.cargo_information.length > 0)
		{
			frm.doc.cargo_information.forEach(function(row){
				if(row.bond_ref_no != null && row.bond_value == null)
				{
					msgprint('Please enter bond value for cargo with bond reference no', 'Error');
					validated = false;
				}
				else if(row.bond_value != null && row.bond_ref_no == null)
				{
					msgprint('Please enter bond reference no for cargo with bond value', 'Error');
					validated = false;
				}
			});
		}*/
	},
	
	before_save: function(frm){
		if(frm.doc.cargo_information && frm.doc.cargo_information.length > 0)
		{
			var container_numbers = [];
			var closed_containers = [];
			var to_be_added = [];
			var to_be_removed = [];
			
			frm.doc.cargo_information.forEach(function(row){
				container_numbers.push(row.container_number);
			});
			
			if(frm.doc.container_file_closing_information && frm.doc.container_file_closing_information.length > 0)
			{
				frm.doc.container_file_closing_information.forEach(function(row){
					closed_containers.push(row.container_no);
				});
			}
			
			//Container numbers to be added
			container_numbers.forEach(function(container_number){
				if(closed_containers.indexOf(container_number) == -1)
				{
					to_be_added.push(container_number);
				}
			});
			
			//Container numbers to be removed
			var i = 0;
			closed_containers.forEach(function(closed_container){
				if(container_numbers.indexOf(closed_container) == -1)
				{
					to_be_removed.push(i);
				}
				i++;
			});
			
			//Add containers
			to_be_added.forEach(function(container_number){
				var new_row = frappe.model.add_child(frm.doc, "Container File Closing Information", "container_file_closing_information");
				new_row.container_no = container_number;
			});
			
			//Remove containers
			to_be_removed.forEach(function(container_index){
				frm.get_field("container_file_closing_information").grid.grid_rows[container_index].remove();
			});
		}
	},
	
	after_save: function(frm){
		//If there is unrequested funds
		frm.events.new_fund_request(frm);
		frm.events.toggle_editable_funds_rows(frm);
		frm.reload_doc();
		
		/*if(frm.doc.cargo_information && frm.doc.cargo_information.length > 0)
		{
			frm.doc.cargo_information.forEach(function(row){
				if(row.bond_ref_no != null && row.bond_value != null)
				{
					//Send request to create new bond
					frappe.call({
						method: 'csf_tz.clearing_and_forwarding.doctype.bond.bond.create_bond',
						args: {
							reference_no: row.bond_ref_no,
							bond_value: row.bond_value,
							no_of_packages: row.no_of_packages,
							cargo: cur_frm.doc.cargo,
							reference_doctype: 'Import',
							reference_docname: frm.docname
						},
						callback: function(data){
						}
					});
				}
			});
		}*/
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
	}
	
})


//To only show office locations
cur_frm.set_query('location', function(frm){
	return{
		filters: [
			['Locations', 'location_type', '!=', 'Border Post']
		]
	}
});

frappe.ui.form.on("Cargo Details", {
	cargo_information_add: function(frm, cdt, cdn){
		frm.events.show_hide_sections(frm);
	},
	
	before_cargo_information_remove: function(frm){
		var selected = frm.get_selected();
		
		//For checking if alert is needed according to transport status so that ones without transport request can just be deleted.
		var alert = false;
		selected['cargo_information'].forEach(function(index){
			if(locals['Cargo Details'][index].transport_status > 0)
			{
				alert = true;
			}
		})
		
		if(alert)
		{
			frappe.confirm(
				'Are you sure you want to delete the cargo information?',
				function(){
					//console.log(selected);
					selected['cargo_information'].forEach(function(index){
						var row = locals['Cargo Details'][index];
						if(row.transport_status < 3)
						{
							//Check if it is the only one with tranport status > 0
							var only_row = true;
							frm.doc.cargo_information.forEach(function(crow){
								if(crow.request_status > 0 && crow.name != row.name)
								{
									only_row = false;
								}
							})
							
							//If it is the only one with tranport request, delete the transport request
							if(only_row)
							{
								frappe.call({
									method: 'frappe.client.get_list',
									args: {
										doctype: 'Transport Request',
										filters: {
											'reference_docname': frm.docname
										}
									},
									callback: function(data){
										console.log(data.message[0].name);
										frappe.call({
											method: 'frappe.model.delete_doc.delete_doc',
											args: {
												doctype: 'Transport Request',
												name: data.message[0].name,
												ignore_permissions:'True',
											},
											callback: function(data){
												console.log(data.message);
											}
										});
										//frappe.delete_doc("Transport Request", data.message[0].name, ignore_permissions=true);
									}
								});
							}
						}
						else
						{
							//If the cargo has already been picked up for transport
							msgprint('You cannot delete cargo that has already been picked up for transport', 'Error');
							throw "Error: cannot delete cargo that has already been picked up for transport";
						}
					})
					return true;
				},
				function(){
					return false;
					//window.close();
					throw "User canceled delete";
				}
			)
		}
		//msgprint(__("Error: Cannot delete a processed request."));
		throw "Wait";
	},
});

frappe.ui.form.on("Requested Funds Details", {
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
});

frappe.ui.form.on("File Attachment", {
	before_attachments_remove: function(frm){
		var selected = frm.get_selected();
		//Checking if attachment is mandatory
		if(selected['attachments'] != null)
		{
			selected['attachments'].forEach(function(index){
				if(locals['File Attachment'][index].mandatory == 1)
				{
					msgprint(__("Error: Cannot delete a mandatory attachment."));
					throw "Error: cannot delete a mandatory attachment";
				}
			})
		}
	}
});







