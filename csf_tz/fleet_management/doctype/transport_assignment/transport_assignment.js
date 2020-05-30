// Copyright (c) 2016, Bravo Logistics and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transport Assignment', {
	onload: function(frm){
		
	},
	
	refresh: function(frm) {
		frm.toggle_display('section_extra');
		console.log(cur_frm.fields_dict);
		
		//Show/Hide according to cargo
		if(frm.doc.cargo)
		{
			frm.toggle_display('cargo', true);
			frm.toggle_display('container_number', true);
			frm.toggle_display('amount', false);
			frm.toggle_display('units', false);
		}
		else
		{
			frm.toggle_display('cargo', false);
			frm.toggle_display('container_number', false);
			frm.toggle_display('amount', true);
			frm.toggle_display('units', true);
		}
		
		
		//Show/Hide according to transporter_type
		if(frm.doc.transporter_type == 'Sub-Contractor' || frm.doc.transporter_type == 'Self Drive')
		{
			frm.toggle_display('assigned_vehicle', false);
			frm.toggle_display('assigned_trailer', false);
			frm.toggle_display('assigned_driver', false);
		}
		else
		{
			frm.toggle_display('assigned_vehicle', true);
			frm.toggle_display('assigned_trailer', true);
			frm.toggle_display('assigned_driver', true);
		}
		
		//Disable editing of entries
		frm.toggle_enable(['cargo', 'amount', 'expected_loading_date', 'container_number', 'units', 'transporter_type', 'sub_contractor', 'assigned_vehicle'], false);
		frm.toggle_enable(['vehicle_plate_number', 'assigned_trailer', 'trailer_plate_number', 'assigned_driver', 'driver_name', 'passport_number', 'route', 'vehicle_status'], false);
		frm.toggle_enable(['vehicle_trip', 'status', 'loading_date', 'lodge_permit', 'dispatch_date', 'cargo_type', 'file_number'], false);
		
		
		/*
		 * 
		 * Set vehicle status for determining if it is main or return cargo
		 * hidden_status == 0 (Vehicle Available)
		 * hidden_status == 1 (Vehicle Booked)
		 * hidden_status == 2 (Vehicle En Route - Main Trip)
		 * hidden_status == 3 (Vehicle Offloaded - Main Trip)
		 * hidden_status == 4 (Vehicle En Route - Return Trip)
		 * hidden_status == 5 (Vehicle Offloaded - Return Trip)
		 * 
		 *
		*/
		
		//Create vehicle trip
		frm.add_custom_button(__("Create Vehicle Trip Record"), function(){
			if(frm.doc.vehicle_status == 2 || frm.doc.vehicle_status == 4) //If en route on trip and not offloaded
			{
				frappe.msgprint('The assigned vehicle is En Route on another trip and has not offloaded. Please offload the current cargo before starting new trip.', 'Not Allowed');
			}
			else if(frm.doc.vehicle_status == 3)
			{
				frappe.confirm(
					'The vehicle is En Route on another trip. Set as return cargo? If you select no, a new trip will be created',
					function(){
						frappe.call({
							method: "fleet_management.fleet_management.doctype.vehicle_trip.vehicle_trip.create_return_trip",
							args: {
								reference_doctype: "Transport Assignment",
								reference_docname: cur_frm.doc.name,
								vehicle: cur_frm.doc.assigned_vehicle,
								transporter: cur_frm.doc.transporter_type,
								vehicle_trip: cur_frm.doc.vehicle_trip
							},
							callback: function(data){
								console.log(data);
								//cur_frm.set_value('status', 'Processed');
								//cur_frm.save_or_update();
								frappe.set_route('Form', data.message.doctype, data.message.name);
							}
						})
					},
					function(){
						frappe.call({
							method: "fleet_management.fleet_management.doctype.vehicle_trip.vehicle_trip.create_vehicle_trip",
							args: {
								reference_doctype: "Transport Assignment",
								reference_docname: cur_frm.doc.name,
								vehicle: frm.doc.assigned_vehicle,
								transporter: frm.doc.transporter_type
							},
							callback: function(data){
								console.log(data);
								//frm.set_value('status', 'Processed');
								//frm.save_or_update();
								frappe.set_route('Form', data.message.doctype, data.message.name);
							}
						})
					}
				);
			}
			else
			{
				frappe.call({
					method: "fleet_management.fleet_management.doctype.vehicle_trip.vehicle_trip.create_vehicle_trip",
					args: {
						reference_doctype: "Transport Assignment",
						reference_docname: cur_frm.doc.name,
						vehicle: frm.doc.assigned_vehicle,
						transporter: frm.doc.transporter_type
					},
					callback: function(data){
						console.log(data);
						//frm.set_value('status', 'Processed');
						//frm.save_or_update();
						frappe.set_route('Form', data.message.doctype, data.message.name);
					}
				})
			}
		});
	},

	transporter_type: function(frm){
		if(frm.doc.transporter_type == "Sub-Contractor")
		{
			frm.toggle_display("sub_contractor", true);
			frm.toggle_display("assigned_vehicle", false);
			frm.toggle_display("sub_contractor", true);
			frm.set_df_property("vehicle_plate_number", "read_only", false);
		}
	}
});
