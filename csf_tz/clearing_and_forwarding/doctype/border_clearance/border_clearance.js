// Copyright (c) 2017, Bravo Logisitcs and contributors
// For license information, please see license.txt

frappe.ui.form.on('Border Clearance', {
	refresh: function(frm) {
		console.log(frappe);
		frm.events.show_hide_sections(frm);
		frm.events.new_fund_request(frm);
		frm.events.billing_type(frm);
	},
	
	after_save: function(frm){
		frm.reload_doc();
	},
	
	billing_type: function(frm){
		//frm.events.show_hide_sections(frm);
		//If for later billing only show clearance information with no trip references
		/*if(frm.doc.billing_type && frm.doc.billing_type != "")
		{
			frm.toggle_display('trip_reference_no', true);
			frm.toggle_display('main_return_select', true);
			//frm.toggle_display(['section_exit_border', 'section_entry_border', 'section_border3', 'section_border4'], true);
			frm.toggle_display('clearance_type', true);
			frm.toggle_display(['location', 'documents_received', 'documents_submitted_by_driver', 'documents_submitted_by_driver_time', 'cargo_type'], true);
		}*/
	},
	
	no_of_borders: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	clearance_type: function(frm){
		if(frm.doc.clearance_type != "")
		{
			//Load default border procedures
			/*frm.clear_table('procedures');
			frappe.model.with_doc('Border Procedures', 'DEFAULT', function(){
				var reference_doc = frappe.model.get_doc('Border Procedures', 'DEFAULT');
				var table = null;
				if(frm.doc.clearance_type == 'Entry')
				{
					table = reference_doc.border_entry;
				}
				else if(frm.doc.clearance_type == 'Exit')
				{
					table = reference_doc.border_exit;
				}
				table.forEach(function(row){
					var new_row = frm.add_child('procedures');
					new_row.procedure = row.procedure;
				});
			});*/
			
			
			//Load required permits according to cargo details
			if(frm.doc.clearance_type && frm.doc.clearance_type != "")
			{
				frm.clear_table('required_permits');
				var goods_description = null;
				if(frm.doc.cargo_type == "Container")
				{
					goods_description = frm.doc.cargo_category;
				}
				else if(frm.doc.cargo_type == "Loose Cargo")
				{
					goods_description = frm.doc.loose_cargo_category;
				}
				
				if(goods_description)
				{
					frappe.model.with_doc('Cargo Type', goods_description, function(){
						var reference_doc = frappe.model.get_doc('Cargo Type', goods_description);
						var table = null;
						if(frm.doc.clearance_type == "Entry")
						{
							table = reference_doc.border_entry;
						}
						else if(frm.doc.clearance_type == "Exit")
						{
							table = reference_doc.border_exit
						}
						table.forEach(function(row){
							var new_row = frm.add_child('required_permits');
							new_row.description = row.permit_name;
						});
					});
				}
			}
			
			frappe.after_ajax(function(){
				frm.refresh_fields();
			});
		}
	},
	
	cargo_reference_no: function(frm){
		frm.clear_table('cargo_details');
		frm.clear_table('required_permits');
		var cargo = frm.doc.cargo_reference_no;
		
		//Load the cargo details
		frappe.model.with_doc('Cargo Details', cargo, function(){
			var reference_doc = frappe.model.get_doc('Cargo Details', cargo);
			var new_row = frm.add_child('cargo_details');
			new_row.container_number = reference_doc.container_number;
			new_row.container_size = reference_doc.container_size;
			new_row.seal_number = reference_doc.seal_number;
			new_row.cargo_status = reference_doc.cargo_status;
			new_row.no_of_packages = reference_doc.no_of_packages;
			new_row.goods_description = reference_doc.goods_description;
			new_row.gross_weight = reference_doc.gross_weight;
			new_row.net_weight = reference_doc.net_weight;
			new_row.tare_weight = reference_doc.tare_weight;
			
			//Load required permits according to cargo details
			if(frm.doc.clearance_type && frm.doc.clearance_type != "")
			{
				var goods_description = reference_doc.goods_description;
				frappe.model.with_doc('Cargo Type', goods_description, function(){
					var reference_doc = frappe.model.get_doc('Cargo Type', goods_description);
					var table = null;
					if(frm.doc.clearance_type == "Entry")
					{
						table = reference_doc.border_entry;
					}
					else if(frm.doc.clearance_type == "Exit")
					{
						table = reference_doc.border_exit
					}
					table.forEach(function(row){
						var new_row = frm.add_child('required_permits');
						new_row.description = row.permit_name;
					});
				});
			}
		});
		
		frappe.after_ajax(function(){
			frm.refresh_fields();
		});
	},
	
	trip_reference_no: function(frm){
		frm.events.check_trip(frm);
	},
	
	main_return_select: function(frm){
		frm.events.check_trip(frm);
	},
	
	cargo_type: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	cargo_category: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	cargo_description: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	cargo_details: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	loose_cargo_category: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	goods_description: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	goods_quantity: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	goods_unit: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	transporter_type: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	//Check if the referenced trip already has a border clearing record associated with it
	check_trip: function(frm){
		if((frm.doc.trip_reference_no && frm.doc.trip_reference_no != "") && (frm.doc.main_return_select && frm.doc.main_return_select != ""))
		{
			frappe.call({
				method: "csf_tz.clearing_and_forwarding.doctype.border_clearance.border_clearance.check_existing",
				args: {
					"trip_reference": frm.doc.trip_reference_no,
					"main_return_select": frm.doc.main_return_select
				},
				callback: function(data){
					if(data.message == "Exists")
					{
						msgprint("The trip you entered already has a border clearance asociated with it.", "Error");
					}
					else if(data.message == "Not Exist")
					{
						//Load cargo information
						frappe.model.with_doc('Vehicle Trip', cur_frm.doc.trip_reference_no, function(){
							var reference_doc = frappe.model.get_doc('Vehicle Trip', cur_frm.doc.trip_reference_no);
							
							//Load transporter information
							if(reference_doc.transporter_type == "Bravo")
							{
								cur_frm.set_value('transporter_type', 'Bravo');
								cur_frm.toggle_display('transporter_name', false);
							}
							else
							{
								cur_frm.set_value('transporter_type', 'Other');
								cur_frm.set_value('transporter_name', reference_doc.sub_contractor);
								cur_frm.toggle_display('transporter_name', true);
							}
							
							//Load vehicle and trailer information
							cur_frm.set_value('vehicle_plate_number', reference_doc.vehicle_plate_number);
							cur_frm.set_value('driver_name', reference_doc.driver_name);
							cur_frm.set_value('trailer_plate_number', reference_doc.trailer_plate_number);
							
							//Load the variables depending if it is main or return trip
							if(frm.doc.main_return_select == "Main Trip")
							{
								cur_frm.set_value('cargo_type', reference_doc.main_cargo_type);
								cur_frm.set_value('reference_trip_route', reference_doc.main_route);
								cur_frm.set_value('cargo_category', reference_doc.main_cargo_category);
								cur_frm.set_value('cargo_description', reference_doc.main_goods_description);
								cur_frm.set_value('border1_clearing_agent', reference_doc.main_border1_clearing);
								cur_frm.set_value('border2_clearing_agent', reference_doc.main_border2_clearing);
								cur_frm.set_value('border3_clearing_agent', reference_doc.main_border3_clearing);
								if(reference_doc.main_cargo_type == "Container")
								{
									cur_frm.clear_table('cargo_details');
									var new_row = cur_frm.add_child('cargo_details');
									reference_doc.main_cargo.forEach(function(row){
										new_row.container_number = row.container_number;
										new_row.container_size = row.container_size;
										new_row.seal_number = row.seal_number;
										new_row.status = row.status;
										new_row.no_of_packages = row.no_of_packages;
										new_row.gross_weight = row.gross_weight;
										new_row.net_weight = row.net_weight;
										new_row.tare_weight = row.tare_weight;
									});
								}
								else if(reference_doc.main_cargo_type == "Loose Cargo")
								{
									cur_frm.set_value('loose_cargo_category', reference_doc.main_cargo_category);
									cur_frm.set_value('goods_description', reference_doc.main_goods_description);
									cur_frm.set_value('goods_quantity', reference_doc.main_amount);
									cur_frm.set_value('goods_unit', reference_doc.main_unit);
								}
							}
							else if(frm.doc.main_return_select == "Return Trip")
							{
								cur_frm.set_value('cargo_type', reference_doc.return_cargo_type);
								cur_frm.set_value('reference_trip_route', reference_doc.return_route);
								cur_frm.set_value('cargo_category', reference_doc.return_cargo_category);
								cur_frm.set_value('cargo_description', reference_doc.return_goods_description);
								cur_frm.set_value('border1_clearing_agent', reference_doc.return_border1_clearing);
								cur_frm.set_value('border2_clearing_agent', reference_doc.return_border2_clearing);
								cur_frm.set_value('border3_clearing_agent', reference_doc.return_border3_clearing);
								if(reference_doc.return_cargo_type == "Container")
								{
									cur_frm.clear_table('cargo_details');
									var new_row = cur_frm.add_child('cargo_details');
									reference_doc.return_cargo.forEach(function(row){
										new_row.container_number = row.container_number;
										new_row.container_size = row.container_size;
										new_row.seal_number = row.seal_number;
										new_row.status = row.status;
										new_row.no_of_packages = row.no_of_packages;
										new_row.gross_weight = row.gross_weight;
										new_row.net_weight = row.net_weight;
										new_row.tare_weight = row.tare_weight;
									});
								}
								else if(reference_doc.return_cargo_type == "Loose Cargo")
								{
									cur_frm.set_value('loose_cargo_category', reference_doc.main_cargo_category);
									cur_frm.set_value('goods_description', reference_doc.return_goods_description);
									cur_frm.set_value('goods_quantity', reference_doc.return_amount);
									cur_frm.set_value('goods_unit', reference_doc.return_unit);
								}
							}							
						});
					}
				}
			});
			
			frappe.after_ajax(function(){
				cur_frm.refresh_fields();
				cur_frm.events.reference_trip_route(cur_frm);
			});
		}
		
		frm.events.show_hide_sections(frm);
		frm.events.clearance_type(frm);
	},
	
	reference_trip_route: function(frm){
		if(frm.doc.reference_trip_route && frm.doc.reference_trip_route != "")
		{
			var no_of_borders = 0;
			frappe.model.with_doc('Trip Route', frm.doc.reference_trip_route, function(){
				var reference_doc = frappe.model.get_doc('Trip Route', frm.doc.reference_trip_route);
				reference_doc.trip_steps.forEach(function(row){
					if(1 == row.is_local_border)
					{
						no_of_borders++;
						cur_frm.set_value('local_border', 'Border ' + no_of_borders);
						cur_frm.set_value('border' + no_of_borders + '_name', row.location);
					}
					else if(1 == row.is_international_border)
					{
						no_of_borders++;
						cur_frm.set_value('border' + no_of_borders + '_name', row.location);
					}
				});
			});
			cur_frm.set_value('no_of_borders', no_of_borders);
		}
		frm.events.show_hide_sections(frm);
	},
	
	show_hide_sections: function(frm){
		//frm.toggle_display('section_basic_details', (frm.doc.billing_type && frm.doc.billing_type != ''));
		
		//if cargo is not entered
		var cargo_entered = false;
		if(frm.doc.cargo_type && frm.doc.cargo_type == 'Loose Cargo' && frm.doc.loose_cargo_category && frm.doc.goods_description && frm.doc.goods_quantity && frm.doc.goods_unit)
		{
			cargo_entered = true;
		}
		else if(frm.doc.cargo_type && frm.doc.cargo_type == "Container" && frm.doc.cargo_category && frm.doc.cargo_description && frm.doc.cargo_details && frm.doc.cargo_details.length > 0)
		{
			cargo_entered = true;
		}
		frm.toggle_display(['section_extra_details', 'section_reporting_status'], cargo_entered);
		frm.toggle_display('section_container_cargo_details', (frm.doc.cargo_type && frm.doc.cargo_type == 'Container'));
		frm.toggle_display('section_loose_cargo_details', (frm.doc.cargo_type && frm.doc.cargo_type == 'Loose Cargo'));
		frm.toggle_display('section_exit_border', (frm.doc.no_of_borders && frm.doc.no_of_borders > 0) && cargo_entered);
		frm.toggle_display('section_entry_border', (frm.doc.no_of_borders && frm.doc.no_of_borders > 1) && cargo_entered);
		frm.toggle_display('section_border3', (frm.doc.no_of_borders && frm.doc.no_of_borders > 2) && cargo_entered);
		frm.toggle_display('section_border4', (frm.doc.no_of_borders && frm.doc.no_of_borders > 3) && cargo_entered);
		frm.toggle_display(['section_required_permits', 'section_bond_information', 'section_requested_funds', 'section_expenses', 'section_attachments', 'section_customer_consignee', 'section_transporter_details', 'section_cargo_origin_destination', 'section_clearing_procedures'], (frm.doc.billing_type && frm.doc.billing_type != ""));
		frm.toggle_display(['section_required_permits', 'section_bond_information', 'section_requested_funds', 'section_expenses', 'section_attachments', 'section_customer_consignee', 'section_transporter_details', 'section_cargo_origin_destination', 'section_clearing_procedures'], cargo_entered);
		frm.toggle_display('section_expenses', (frm.doc.requested_funds && frm.doc.requested_funds.length > 0));
		frm.toggle_display('transporter_name', (frm.doc.transporter_type && frm.doc.transporter_type != "Bravo"));
	}
	
});

frappe.ui.form.on('Cargo Details', {
	cargo_details_add: function(frm){
		frm.events.show_hide_sections(frm);
	}
});

cur_frm.set_query('location', function(frm){
	return{
		filters: [
			['Locations', 'location_type', '=', 'Border Post']
		]
	}
});

cur_frm.set_query('trip_reference_no', function(frm){
	return{
		filters: [
			['Vehicle Trip', 'status', '!=', 'Closed']
		]
	}
});
