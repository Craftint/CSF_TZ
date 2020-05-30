// Copyright (c) 2016, Bravo Logisitcs and contributors
// For license information, please see license.txt

frappe.ui.form.on('Export', {
	onload:function(frm){
		console.log(frm);
	},
	
	refresh: function(frm) {
		frm.events.open_close_buttons(frm);
		//For filtering the cargo type depending on if it is enabled in cargo type settings
		frm.set_query('material', function(){
			if(cur_frm.doc.export_type == 'Local')
			{
				return{
					"filters": {
						"local_export": "1"
					}
				};
			}
		});
		
		//Show or hide sections according to what has been entered
		frm.events.show_hide_sections(frm);
		
		//If there is unrequested funds
		frm.events.new_fund_request(frm);
		
		frappe.after_ajax(function(){
			frm.events.grid_upload_buttons(frm)
		})
		
		frm.events.download_buttons(frm);
		
		if(frm.doc.status == "Closed" || frm.doc.status == "Cancelled")
		{
			frm.meta.fields.forEach(function(field){
				frm.toggle_enable(field.fieldname, false);
			});
		}
	},
	
	open_close_buttons: function(frm){
		if (!frm.doc.__islocal) {
			if(frm.doc.status=="Open") {
				frm.add_custom_button(__("Close"), function() {
					if(frm.events.validate_close(frm))
					{
						frm.set_value("status", "Closed");
						frappe.call({
							doc: frm.doc,
							method: 'validate_containers',
							callback: function(r) {
								frm.save();
								frm.refresh();
								
							}
						})
					}
				}, "fa fa-check", "btn-success");
				
				//Cancel Button
				frm.add_custom_button(__("Cancel Export"), function() {
					//frm.set_value("status", "Cancelled");
                    frm.events.booking_cancellation(frm);

					//frm.save();
                    //frm.refresh_fields();
                    console.log("its cancelled");
				}, "fa fa-check", "btn-success");
			} else {
				frm.add_custom_button(__("Re-open"), function() {
					frm.set_value("status", "Open");
					frappe.call({
						doc: frm.doc,
						method: 'validate_containers',
						callback: function(r) {
							frm.save();
							frm.refresh();
							
						}
					})
				}, null, "btn-default");
			}
		}
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
		var excluded_fields = ['attachments', 'download_buttons', 'required_permits', 'reporting_status', 'bond_reference'];
		if(frm.doc.customs_processing_type && frm.doc.customs_processing_type == 'Old System')
		{
			excluded_fields.push('received_repacking_manifest', 'customs_assessment_submission', 'final_assessment_obtained', 'customs_release_date', 'bt_submission_date',
								'bt_approval_date', 'verification_date', 'declaration_number_approval', 'bt_ref_no');
		}
		else if(frm.doc.customs_processing_type && frm.doc.customs_processing_type == 'New System')
		{
			excluded_fields.push('packing_list_received', 'packing_list_received_by', 'loading_list_sent_new', 'lodge_port_permit', 'receive_port_permit', 'delivery_date',
			'containers', 'cargo_information');
		}
		var excluded_field_type = ["Table", "Section Break", "Column Break"]
		var error_fields = [];
		frm.meta.fields.forEach(function(field){
			if(!(excluded_field_type.indexOf(field.fieldtype) > -1) && !(excluded_fields.indexOf(field.fieldname) > -1) && !(field.fieldname in frm.doc))
			{
				error_fields.push(field.label);
				return false;
			}
			
			if(field.fieldtype == "Table" && !(excluded_fields.indexOf(field.fieldname) > -1) && frm.doc[field.fieldname].length == 0)
			{
				error_fields.push(field.label);
				return false;
			}
		})
		
		//For back compatibility to be able to close field file if either containers or cargo_information entered
		if(frm.doc.cargo_information.length == 0 && frm.doc.containers.length == 0){
			error_fields.push("Container Information")
		}
		
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
	
	
	after_save: function(frm){
		/*if(frm.doc.cargo_information.length > 0)
		{
			frm.doc.cargo_information.forEach(function(row){
				frappe.call({
					method: 'frappe.client.get_list',
					args: {
						doctype: 'Bond',
						filters: {
							'name': row.customs_ref_no,
						}
					},
					callback: function(data){
						if(!data.message)
						{
							frappe.model.set_value('Packing List', row.name, 'customs_ref_no', "");
							msgprint(__('Customs reference no. ' + row.customs_ref_no + ' does not exist.', 'Error'));
						}
						else if(data.message.length > 0)
						{
							console.log(data);
							frappe.model.with_doc('Bond', row.customs_ref_no, function(){
								reference_doc = frappe.model.get_doc('Bond', row.customs_ref_no);
								reference_doc.bond_history.forEach(function(row){
									total_no_of_bundles += row.no_of_bundles;
								})
								
								if((no_of_packages - total_no_of_bundles) > 0) //If the re are no of packages left
								{
									
								}
							});
							
							
						}
					}
				})
			});
		}*/
		frm.reload_doc();
	},
	
	//For the upload buttons on cargo informationa nd bond reference tables
	grid_upload_buttons: function(frm){
		if(frm.doc.cargo_information)
		{
			//Add button for uploading cargo information in the cargo information grid
			frm.fields_dict['cargo_information'].grid.add_custom_button('Upload Information', function(){
				var d = new frappe.ui.Dialog({
					'fields': [
						{'fieldname': 'ht', 'fieldtype': 'HTML'}
					],
					primary_action: function(){
						var fileInput = document.getElementById("csv");
						var reader = new FileReader();
						reader.readAsBinaryString(fileInput.files[0]);
						reader.onload = function () {
							console.log(reader.result);
							cur_frm.events.upload_cargo(cur_frm, reader.result);
						};
						d.hide();
						cur_frm.fields_dict['cargo_information'].grid.clear_custom_buttons();
					
					}
				});
				d.fields_dict.ht.$wrapper.html('<label style="float: left;">Select CSV File:</label> <input style="float: left; margin-left: 10px;" id="csv" type="file" />');
				d.show();
			});
			
			//Add button for uploading bond reference information in the bond referene grid
			frm.fields_dict['bond_reference'].grid.add_custom_button('Upload Information', function(){
				var d = new frappe.ui.Dialog({
					'fields': [
						{'fieldname': 'ht2', 'fieldtype': 'HTML'}
					],
					primary_action: function(){
						var fileInput = document.getElementById("csv2");
						var reader = new FileReader();
						reader.readAsBinaryString(fileInput.files[0]);
						reader.onload = function () {
							console.log(reader.result);
							cur_frm.events.upload_bond_information(cur_frm, reader.result);
						};
						d.hide();
						cur_frm.fields_dict['bond_reference'].grid.clear_custom_buttons();
						
					}
				});
				d.fields_dict.ht2.$wrapper.html('<label style="float: left;">Select CSV File:</label> <input style="float: left; margin-left: 10px;" id="csv2" type="file" />');
				d.show();
			});
		}
	},
	
	//For the cargo information upload button
	upload_cargo: function(frm, str){
		var rows = str.split("\n");
		var row_arrays = [];
		rows.forEach(function(row){
			row_arrays.push(row.split(','));
		});
		row_arrays.forEach(function(row){
			if(row[0] && row[0] != "Container Number")  //If the row is not empty nor a header row
			{
				var new_row = frm.add_child('cargo_information');
				new_row.container_number = row[0];
				new_row.seal_number = row[1];
				new_row.no_of_bundles = row[2];
				new_row.net_weight = row[3];
				new_row.gross_weight = row[4];
			}
		});
		frm.refresh_field('cargo_information');
	},
	
	//For the bond reference upload button
	upload_bond_information: function(frm, str){
		var rows = str.split("\n");
		var row_arrays = [];
		rows.forEach(function(row){
			row_arrays.push(row.split(','));
		});
		row_arrays.forEach(function(row){
			if(row[0] && row[0] != "Customs Reference Number")  //If the row is not empty nor a header row
			{
				var new_row = frm.add_child('bond_reference');
				new_row.customs_ref_number = row[0];
				new_row.number_of_bundles = row[1];
				new_row.weight = row[2];
			}
		});
		frm.refresh_field('bond_reference');
	},
	
	//For loading list download buttons
	download_buttons: function(frm){
		//Load the bttons
		var html = '<button class="btn btn-default btn-xs" onclick="cur_frm.events.download_tra_loading_list(\'' + frm + '\');">Download TRA Loading List</button> &nbsp;&nbsp';
		html += '<button class="btn btn-default btn-xs" onclick="cur_frm.events.download_ticts_loading_list(\'' + frm + '\');">Download TICTS Loading List</button>'
		$(frm.fields_dict.download_buttons.wrapper).html(html);
	},
	
	
	download_tra_loading_list: function(frm){
		window.open("/api/method/csf_tz.clearing_and_forwarding.doctype.export.export.download_ticts_loading_list?args=test1");
	},
	
	
	download_ticts_loading_list: function(frm){
		
	},
	
	material: function(frm) {
		if(frm.doc.material == "")
		{
			frm.clear_table('required_permits');
			frm.refresh_field('required_permits');
		}
		else
		{
			frappe.model.with_doc('Cargo Type', frm.doc.material, function(){
				var reference_doc = frappe.get_doc('Cargo Type', frm.doc.material);
				
				//Load required permits
				if(frm.doc.export_type == 'Local')
				{
					frm.clear_table('required_permits');
					frm.refresh_field('required_permits');
					reference_doc.required_local_export.forEach(function(row){
						var new_row = frm.add_child('required_permits');
						new_row.description = row.permit_name;
						frappe.after_ajax(function(){
							frm.refresh_field("required_permits");
						});
					});
				}
				else if(frm.doc.export_type == 'Transit')
				{
					frm.clear_table('required_permits');
					frm.refresh_field('required_permits');
					reference_doc.required_transit_export.forEach(function(row){
						var new_row = frm.add_child('required_permits');
						new_row.description = row.permit_name;
						frappe.after_ajax(function(){
							frm.refresh_field("required_permits");
						});
					});
				}
			});
		}
		frm.events.show_hide_sections(frm);
	},
	
	booking_received: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	booking_number: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	export_type: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	shipper: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	notify_party: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	consignee: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	client: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	vessel_name: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	voyage_no: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	engagement_date: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	eta: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	cut_off_date: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	shipping_line: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	port_of_loading: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	loading_terminal: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	destination: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	customs_processing_type: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	show_hide_sections: function(frm){
		/*frm.toggle_display('client_information_section', (frm.doc.booking_received && frm.doc.booking_number && frm.doc.export_type));
		frm.toggle_display('shipping_information_section', (frm.doc.shipper && frm.doc.notify_party && frm.doc.consignee && frm.doc.client));
		frm.toggle_display('clearing_documentation_section', (frm.doc.vessel_name && frm.doc.voyage_no && frm.doc.engagement_date && frm.doc.eta && frm.doc.cut_off_date &&
								frm.doc.shipping_line && frm.doc.port_of_loading && frm.doc.loading_terminal && frm.doc.destination));
		frm.toggle_display('clearing_documentation_section', (frm.doc.vessel_name && frm.doc.voyage_no && frm.doc.engagement_date && frm.doc.eta && frm.doc.cut_off_date &&
								frm.doc.shipping_line && frm.doc.port_of_loading && frm.doc.loading_terminal && frm.doc.destination));
		frm.toggle_display('section_required_permits', (frm.doc.shipper && frm.doc.notify_party && frm.doc.consignee && frm.doc.client)); 
		frm.toggle_display('section_containers_information', frm.doc.material);
		frm.toggle_display('documentation_section', (frm.doc.cargo_information && frm.doc.cargo_information.length > 0));
		frm.toggle_display('requested_funds_section', (frm.doc.vessel_name && frm.doc.voyage_no && frm.doc.engagement_date && frm.doc.eta && frm.doc.cut_off_date &&
								frm.doc.shipping_line && frm.doc.port_of_loading && frm.doc.loading_terminal && frm.doc.destination));
		frm.toggle_display('expenses_section', (frm.doc.requested_funds && frm.doc.requested_funds.length > 0));*/
		frm.toggle_display('documentation_section', (frm.doc.customs_processing_type && frm.doc.customs_processing_type == 'Old System'));
		frm.toggle_display('clearing_documentation_section', (frm.doc.customs_processing_type && frm.doc.customs_processing_type == 'New System'));
	},
	
	//For sending funds request
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
						reference_doctype: "Export",
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
    
    //for container when booking is cancelled ,i.e cancel export
    booking_cancellation:function(frm){
        	frappe.call({
					method: "csf_tz.clearing_and_forwarding.doctype.container.container.remove_booking",
					args: {
						booking_number: frm.doc.booking_number,
                        name:frm.doc.name
					},
					callback: function(r){
						console.log(r);
                        frm.set_value("status", "Cancelled");
                        frm.save();
                        frm.clear_table("container_information");


					}
				})
        
    },
    

});

frappe.ui.form.on("Requested Funds Details", {
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
