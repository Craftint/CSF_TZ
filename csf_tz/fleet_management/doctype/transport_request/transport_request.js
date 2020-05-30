// Copyright (c) 2016, Bravo Logistics and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transport Request', {
	onload: function(frm){
		//Load the buttons
		var html = '<button style="background-color: green; color: #FFF;" class="btn btn-default btn-xs" onclick="cur_frm.cscript.assign_transport(\'' + frm + '\');">Assign Vehicles</button> ';
		$(frm.fields_dict.html1.wrapper).html(html);
	},
		
	refresh: function(frm) {
		console.log(frm);
		
		//Fix assignement details
		frm.events.check_assignment_table(frm);
		
		//If request is from module, disable save, else enable save
		//If the request is from other module, load data from that module
		if(frm.doc.reference_docname)
		{
			cur_frm.cscript.populate_child(frm.doc.reference_doctype, frm.doc.reference_docname);
			frm.page.clear_indicator();
		}
		frm.events.calculate_total_assigned(frm);
		frm.events.hide_show_cargo(frm);
	},
	
	
	//Fix for bug which did copy cargo details in cargo.
	check_assignment_table: function(frm){
		if(frm.doc.cargo_type == 'Container')
		{
			var to_save = false;
			frm.doc.assign_transport.forEach(function(row){
				if(!row.cargo || row.cargo.toUpperCase().indexOf('NEW') > -1)
				{
					//Find the cargo details
					frm.doc.cargo.forEach(function(cargo_row){
						if(cargo_row.container_number == row.container_number)
						{
							frappe.model.set_value('Transport Assignment', row.name, 'cargo', cargo_row.name);
						}
					})
					to_save = true;
				}
			});
			if(to_save)
			{
				frappe.after_ajax(function(){
					frm.save_or_update();
				})
			}
		}
	},
	
	show_submit_button: function(frm){
		/*//If request is from module, save has been disabled hence need to save manually
		if(frm.doc.reference_docname)
		{
			//Show the not saved label in indicator
			frm.page.set_indicator('Not Saved', 'orange');
		
			//Activate the submit button (The label has been changed to save)
			frm.page.set_primary_action(__("Save"), function() {
				//First validate vehicle assign table
				if(frm.events.validate_assignment(frm))
				{
					cur_frm.doc.assign_transport.forEach(function(row){
						frappe.call({
							method: "fleet_management.fleet_management.doctype.transport_request.transport_request.assign_vehicle",
							freeze: true,
							args: {
								reference_doctype: cur_frm.doc.reference_doctype,
								reference_docname: cur_frm.doc.reference_docname,
								cargo_docname: row.cargo,
								//cargo_idx: locals['Cargo Details'][row.cargo].idx,
								assigned_vehicle: row.assigned_vehicle,
								assigned_trailer: row.assigned_trailer,
								assigned_driver: row.assigned_driver,
								assigned_idx: row.idx,
								amount: row.amount,
								expected_loading_date: row.expected_loading_date,
								container_number: row.container_number,
								units: row.units,
								transporter_type: row.transporter_type,
								sub_contractor: row.sub_contractor,
								vehicle_plate_number: row.vehicle_plate_number,
								trailer_plate_number: row.trailer_plate_number,
								driver_name: row.driver_name,
								passport_number: row.passport_number,
								route: row.route,
							},
							callback: function(data){
								console.log(data.message);
							}
						});
					});
					cur_frm.page.clear_indicator();
				}
				else
				{
					//If not all data has been entered
					msgprint("Please fill all required fields in assigned vehicle table", "Error");
				}
			});
		}*/
	},
	
	show_hide_assignment: function(frm, cdt, cdn){
		//Processed row
		var row = frm.fields_dict['assign_transport'].grid.grid_rows_by_docname[cdn];
		
		//Show/hide container specific information
		if(frm.doc.cargo_type == 'Container')
		{
			row.toggle_display('cargo', false);
			row.toggle_display('container_number', true);
			row.toggle_display('amount', false);
			row.toggle_display('units', false);
		}
		else
		{
			row.toggle_display('cargo', false);
			row.toggle_display('container_number', false);
			row.toggle_display('amount', true);
			row.toggle_display('units', true);
		}
		
		//Make editable according to request origin
		if(frm.doc.reference_docname)
		{
			row.toggle_editable('cargo', false);
			row.toggle_editable('container_number', false);
			row.toggle_editable('expected_loading_date', false);

		}
		
		//Hide the extra info section
		row.toggle_display('section_extra', false);
		
		//Show, hide and enable entries according to the transporter type
		if(locals[cdt][cdn].transporter_type == "Sub-Contractor" || locals[cdt][cdn].transporter_type == "Self Drive")
		{
			//Show the sub-contractor select box
			row.toggle_display("sub_contractor", (locals[cdt][cdn].transporter_type == "Sub-Contractor"));
			//Enter vehicle details
			row.toggle_display("assigned_vehicle", false);
			row.toggle_editable("vehicle_plate_number", true);
			//Vehicle Documents
			//row.toggle_display("section_vehicle_attachments", true);
			for(var i = 1; i < 5; i++)
			{
				row.toggle_editable("attach_" + i, true);
				row.toggle_editable("description_" + i, true);
			}
			//Trailor Details
			row.toggle_display("assigned_trailer", false);
			row.toggle_editable("trailer_plate_number", (locals[cdt][cdn].transporter_type == "Sub-Contractor"));
			//Driver Details
			row.toggle_display("assigned_driver", false);
			row.toggle_editable("driver_name", true);
			row.toggle_editable("passport_number", true);
			row.toggle_editable("driver_licence", true);
			row.toggle_editable("driver_contact", true);
		}
		else if(locals[cdt][cdn].transporter_type == "Bravo")
		{
			//Hide the sub-contractor select box
			row.toggle_display("sub_contractor", false);
			//Enter vehicle details
			row.toggle_display("assigned_vehicle", true);
			row.toggle_editable("assigned_vehicle", true);
			row.toggle_editable("vehicle_plate_number", false);
			//Vehicle Documents
			//row.toggle_display("section_vehicle_attachments", true);
			for(var i = 1; i < 5; i++)
			{
				row.toggle_editable("attach_" + i, false);
				row.toggle_editable("description_" + i, false);
			}
			//Trailor Details
			row.toggle_display("assigned_trailer", true);
			row.toggle_editable("assigned_trailer", true);
			row.toggle_editable("trailer_plate_number", false);
			//Driver Details
			row.toggle_display("assigned_driver", true);
			row.toggle_editable("assigned_driver", true);
			row.toggle_editable("driver_name", false);
			row.toggle_editable("passport_number", false);
			row.toggle_editable("driver_licence", true);
			row.toggle_editable("driver_contact", true);
		}
		else
		{
			//Hide the sub-contractor select box
			row.toggle_display("sub_contractor", false);
			//Enter vehicle details
			row.toggle_display("assigned_vehicle", true);
			row.toggle_editable("assigned_vehicle", true);
			row.toggle_editable("vehicle_plate_number", false);
			//Vehicle Documents
			for(var i = 1; i < 5; i++)
			{
				row.toggle_editable("attach_" + i, false);
				row.toggle_editable("description_" + i, false);
			}
			//Trailor Details
			row.toggle_display("assigned_trailer", true);
			row.toggle_editable("assigned_trailer", true);
			//Driver Details
			row.toggle_display("assigned_driver", true);
			row.toggle_editable("assigned_driver", true);
		}
	},
	
	cargo_type: function(frm){
		frm.events.hide_show_cargo(frm);
	},
	
	hide_show_cargo: function(frm){
		if(frm.doc.cargo_type == "")
		{
			frm.toggle_display('cargo', false);
			frm.toggle_display('amount', false);
			frm.toggle_display('unit', false);
			frm.toggle_display('number_of_vehicles', false);
			frm.toggle_display('html1', false);
			frm.toggle_display('goods_description', false);
			frm.toggle_display('cargo_description', false);
			frm.toggle_display('section_vehicle_assignment', false);
		}
		else if(frm.doc.cargo_type == "Container")
		{
			frm.toggle_display('cargo', true);
			frm.toggle_display('amount', false);
			frm.toggle_display('unit', false);
			frm.toggle_display('number_of_vehicles', false);
			frm.toggle_display('html1', true);
			frm.toggle_display('goods_description', true);
			frm.toggle_display('cargo_description', true);
			frm.toggle_display('section_vehicle_assignment', true);
		}
		else
		{
			frm.toggle_display('cargo', false);
			frm.toggle_display('amount', true);
			frm.toggle_display('unit', true);
			frm.toggle_display('number_of_vehicles', true);
			frm.toggle_display('html1', false);
			frm.toggle_display('goods_description', true);
			frm.toggle_display('cargo_description', true);
			frm.toggle_display('section_vehicle_assignment', true);
		}
	},
	
	validate: function(frm){
		if(!frm.events.validate_assignment(frm))
		{
			frappe.msgprint("Please enter all required fields in vehicle assignement table.");
			frappe.validated = false;
		}
	},
	
	validate_assignment: function(frm){
		var valid = true;
		//Validate that all required entries are entered in vehicle assignment table
		console.log(frm.doc.assign_transport.length);
		frm.doc.assign_transport.forEach(function(row){
			if(frm.doc.cargo_type == 'Container')
			{
				if(row.cargo && row.route)  //Check cargo and route entered
				{
					if(row.transporter_type == "Sub-Contractor")
					{
						if(row.vehicle_plate_number && row.trailer_plate_number && row.driver_name && row.passport_number)
						{
							//Its all good, go to the next row
						}
						else
						{
							valid = false;
							return false;
						}
					}
					else if(row.transporter_type == "Self Drive")
					{
						if(row.vehicle_plate_number && row.driver_name && row.passport_number)
						{
							//Its all good, go to the next row
						}
						else
						{
							valid = false;
							return false;
						}
					}
					else
					{
						if(row.assigned_vehicle && row.assigned_trailer && row.assigned_driver)
						{
							//Its all good, go to the next row
						}
						else
						{
							valid = false;
							return false;
						}
					}
				}
				else
				{
					valid = false;
					return false;
				}
			}
			else
			{
				if(row.amount > 0 && row.units && row.route)  //Check cargo and route entered
				{
					if(row.transporter_type == "Sub-Contractor")
					{
						if(row.vehicle_plate_number && row.trailer_plate_number && row.driver_name && row.passport_number)
						{
							//Its all good, go to the next row
						}
						else
						{
							valid = false;
							return false;
						}
					}
					else if(row.transporter_type == "Self Drive")
					{
						if(row.vehicle_plate_number && row.driver_name && row.passport_number)
						{
							//Its all good, go to the next row
						}
						else
						{
							valid = false;
							return false;
						}
					}
					else
					{
						if(row.assigned_vehicle && row.assigned_trailer && row.assigned_driver)
						{
							//Its all good, go to the next row
						}
						else
						{
							valid = false;
							return false;
						}
					}
				}
				else
				{
					valid = false;
					return false;
				}
			}
		});
		
		//If the process is not interrupted, then all is well and return true
		if(valid == true)
		{
			return true;
		}
		else
		{
			return false;
		}
	},
	
	calculate_total_assigned: function(frm){
		if(frm.doc.cargo_type == 'Loose Cargo' && frm.doc.assign_transport.length > 0)
		{
			frm.toggle_display('total_assigned', true);
			var total = 0;
			frm.doc.assign_transport.forEach(function(row){
				total = total + row.amount;
			});
			frm.set_value('total_assigned', total + ' ' + frm.doc.unit);
		}
		else
		{
			frm.toggle_display('total_assigned', false);
		}
	}
});


frappe.ui.form.on("Transport Assignment", {	
	form_render: function(frm, cdt, cdn){
		frm.events.show_hide_assignment(frm, cdt, cdn);
		locals[cdt][cdn].units = frm.doc.unit;
	},
	
	before_assign_transport_remove: function(frm, cdt, cdn){
		if(locals[cdt][cdn].status && locals[cdt][cdn].status == "Processed")
		{
			frappe.throw("You cannot delete a processed assignment");
		}
	},
	
	before_assign_transport_add: function(frm, cdt, cdn){
		if(cur_frm.doc.cargo_type == "Container")
		{
			frappe.throw('Please use the assign vehicle button to assign vehicles.');
		}
	},
	
	assign_transport_add: function(frm, cdt, cdn){
		if(cur_frm.doc.cargo_type != "Container")
		{
			locals[cdt][cdn].container_number = 'NIL';
			locals[cdt][cdn].cargo_type = frm.doc.cargo_type
			locals[cdt][cdn].file_number = frm.doc.file_number;
			//If units are set, copy units to the assignment
			if(frm.doc.unit)
			{
				locals[cdt][cdn].units = frm.doc.unit;
			}
		}
	},
	
	amount: function(frm, cdt, cdn){
		frm.events.show_submit_button(frm);
		frm.events.calculate_total_assigned(frm);
	},
	
	expected_loading_date: function(frm, cdt, cdn){
		frm.events.show_submit_button(frm);
	},
	
	transporter_type: function(frm, cdt, cdn){
		frm.events.show_hide_assignment(frm, cdt, cdn);
	},
	
	sub_contractor: function(frm, cdt, cdn){
		frm.events.show_submit_button(frm);
	},
		
	assigned_vehicle: function(frm, cdt, cdn){
		//Automatically enter the plate number, trailer and driver
		//For future reference on how to do this the frappe way. FOr some reason I cant get it to work on child table on first value change
		//cur_frm.add_fetch('assigned_vehicle', 'number_plate', 'vehicle_plate_number');
		frappe.call({
			method:"frappe.client.get_value",
			args: {
				doctype:"Vehicle",
				filters: {
					name: locals[cdt][cdn].assigned_vehicle
				},
				fieldname:["number_plate", "driver", "default_trailer"]
			}, 
			callback: function(data) { 
				// set the returned values in cooresponding fields
				frappe.model.set_value(cdt, cdn, 'vehicle_plate_number', data.message.number_plate);
				frappe.model.set_value(cdt, cdn, 'assigned_trailer', data.message.default_trailer);
				frappe.model.set_value(cdt, cdn, 'assigned_driver', data.message.driver);
			}
		})
				
		//For vehicle documents
		frappe.model.with_doc('Vehicle', locals[cdt][cdn].assigned_vehicle, function(){
			var ref_vehicle = frappe.model.get_doc('Vehicle', locals[cdt][cdn].assigned_vehicle);
			var i = 1;
			ref_vehicle.vehicle_documents.forEach(function(row){
				//Fill in the attachments and their descriptions.
				frappe.model.set_value(cdt, cdn, 'attach_' + i, row.attachment);
				frappe.model.set_value(cdt, cdn, 'description_' + i, row.description);
				i++;
			});
		});
		
		
		frm.events.show_submit_button(frm);
		frappe.after_ajax(function(row){
			frm.events.show_hide_assignment(frm, cdt, cdn);
		});
	},
	
	vehicle_plate_number: function(frm, cdt, cdn){
		frm.events.show_submit_button(frm);
	},
	
	assigned_trailer: function(frm, cdt, cdn){
		frappe.call({
			method:"frappe.client.get_value",
			args: {
				doctype:"Trailer",
				filters: {
					name: locals[cdt][cdn].assigned_trailer
				},
				fieldname:["number_plate"]
			}, 
			callback: function(data) { 
				// set the returned values in cooresponding fields
				frappe.model.set_value(cdt, cdn, 'trailer_plate_number', data.message.number_plate);
			}
		})
		frm.events.show_submit_button(frm);
	},
	
	trailer_plate_number: function(frm, cdt, cdn){
		frm.events.show_submit_button(frm);
	},
	
	assigned_driver: function(frm, cdt, cdn){
		frappe.call({
			method:"frappe.client.get_value",
			args: {
				doctype:"Employee",
				filters: {
					name: locals[cdt][cdn].assigned_driver
				},
				fieldname:["employee_name", "passport_number", "cell_number", "driving_licence_number"]
			}, 
			callback: function(data) { 
				// set the returned values in cooresponding fields
				frappe.model.set_value(cdt, cdn, 'driver_name', data.message.employee_name);
				frappe.model.set_value(cdt, cdn, 'passport_number', data.message.passport_number);
				frappe.model.set_value(cdt, cdn, 'driver_licence', data.message.driving_licence_number);
				frappe.model.set_value(cdt, cdn, 'driver_contact', data.message.cell_number);
			}
		})
		frm.events.show_submit_button(frm);
	},
		
	driver_name: function(frm, cdt, cdn){
		frm.events.show_submit_button(frm);
	},
		
	passport_number: function(frm, cdt, cdn){
		frm.events.show_submit_button(frm);
	},
		
	route: function(frm, cdt, cdn){
		frm.events.show_submit_button(frm);
	},
});

//For filtering the driver options in the assign_transport table to only show drivers
cur_frm.set_query("assigned_driver", "assign_transport", function(doc, cdt, cdn){
	return{
		filters: [
			['Employee', 'designation', '=', 'Driver']
		]
	}
});

cur_frm.cscript.assign_transport = function(frm){
	//For setting indicator message
	//cur_frm.page.set_indicator("Unsubmitted Changes", "orange");
	//cur_frm.page.clear_indicator();
	
	//If it is container based cargo
	if(cur_frm.doc.cargo_type == "Container")
	{
		//Add selected rows to assign table
		var selected = cur_frm.get_selected();
		if(selected['cargo'])
		{
			$.each(selected['cargo'], function(index, cargo_nm){
				var container_number = locals["Cargo Details"][cargo_nm].container_number;
				var exists = $('[data-fieldname="assign_transport"]:contains("' + container_number + '")');
				console.log(exists);
				if(exists.length > 0)
				{
					msgprint('Container No. ' + container_number + ' has already been processed.', 'Error')
				}
				else
				{
					var new_row = cur_frm.add_child("assign_transport");
					new_row.cargo_type = cur_frm.doc.cargo_type;
					new_row.cargo = locals["Cargo Details"][cargo_nm].name;
					new_row.container_number = container_number;
					new_row.expected_loading_date = cur_frm.doc.loading_date;
					new_row.file_number = cur_frm.doc.file_number;
					if(cur_frm.doc.reference_doctype == 'Import'){
						new_row['import'] = cur_frm.doc.reference_docname;
					}
					else if(cur_frm.reference_doctype == 'Export'){
						new_row['export'] = cur_frm.doc.reference_docname;
					}
					cur_frm.refresh_field("assign_transport");
				}
			});
		}
		else
		{
			show_alert("Error: Please select cargo to process.");
		}
	}
}

cur_frm.cscript.populate_child = function(reference_doctype, reference_docname){
	if(reference_doctype == "Import")
	{
		frappe.model.with_doc(reference_doctype, reference_docname, function(){
			var request_total_amount = null;
			var reference_doc = frappe.get_doc(reference_doctype, reference_docname);
			
			//Load data and set as read only
			cur_frm.set_value('request_received', cur_frm.meta.creation.substr(0, 10));
			cur_frm.set_value('customer', reference_doc.customer);
			cur_frm.set_value('consignee', reference_doc.consignee);
			cur_frm.set_value('shipper', reference_doc.shipper);
			cur_frm.set_value('cargo_location_city', reference_doc.port_of_discharge);
			cur_frm.set_value('loading_date', reference_doc.ata);
			cur_frm.set_value('cargo_destination_country', reference_doc.cargo_destination_country);
			cur_frm.set_value('cargo_destination_city', reference_doc.cargo_destination_city);
			cur_frm.set_value('border1_clearing_agent', reference_doc.clearing_agent_border_1);
			cur_frm.set_value('border2_clearing_agent', reference_doc.clearing_agent_border_2);
			cur_frm.set_value('border3_clearing_agent', reference_doc.clearing_agent_border_3);
			cur_frm.set_value('special_instructions_to_transporter', reference_doc.special_instructions_to_transporter);
			cur_frm.set_value('cargo_type', 'Container');
			cur_frm.set_value('goods_description', reference_doc.cargo);
			cur_frm.set_value('cargo_description', reference_doc.cargo_description);
			cur_frm.set_value('file_number', reference_doc.reference_file_number);
			
			//Set as read only
			cur_frm.toggle_enable(['request_received', 'customer', 'cargo_location_city', 'loading_date', 'cargo_destination_city', 
										'cargo_destination_country', 'cargo_type', 'goods_description', 'cargo_description', 'file_number',
										'consignee', 'shipper', 'special_instructions_to_transporter'], 0);
			cur_frm.toggle_enable(['border1_clearing_agent', 'border2_clearing_agent', 'border3_clearing_agent', 'cargo_location_country', 'transport_type', 'cargo'], 0);
			
			//Get port country
			frappe.model.with_doc('Port', reference_doc.port_of_discharge, function(frm){
				cur_frm.set_value('cargo_location_country', frappe.model.get_doc('Port', reference_doc.port_of_discharge).country);
			});
			
			if(reference_doc.import_type == "Local")
			{
				cur_frm.set_value('transport_type', 'Internal');
			}
			else if(reference_doc.import_type == "Transit")
			{
				cur_frm.set_value('transport_type', 'Cross Border');
			}
		});
		return "done";
	}
};
