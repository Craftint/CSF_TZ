// Copyright (c) 2017, Bravo Logistics and contributors
// For license information, please see license.txt

frappe.ui.form.on('Requested Items', {
	onload: function(frm) {
		//Load the approve and reject buttons
		var html_approve_buttons = '<button style="background-color: green; color: #FFF;" class="btn btn-default btn-xs" onclick="cur_frm.cscript.approve_request(\'' + frm + '\');">Approve</button> ';
		html_approve_buttons += '<button style="background-color: red; color: #FFF;" class="btn btn-default btn-xs" onclick="cur_frm.cscript.reject_request(\'' + frm + '\');">Reject</button>'
		$(frm.fields_dict.html_approve_buttons.wrapper).html(html_approve_buttons);
		
		//Load the recommend and recommend against buttons
		var html_recommend_buttons = '<button style="background-color: green; color: #FFF;" class="btn btn-default btn-xs" onclick="cur_frm.cscript.recommend_request(\'' + frm + '\');">Recommend</button> ';
		html_recommend_buttons += '<button style="background-color: red; color: #FFF;" class="btn btn-default btn-xs" onclick="cur_frm.cscript.recommend_against_request(\'' + frm + '\');">Recommend Against</button>'
		$(frm.fields_dict.html_recommend_buttons.wrapper).html(html_recommend_buttons);
		
	},
	
	refresh: function(frm) {
		//Make stock entry button
		frm.add_custom_button(__('Issue Material'),
			function() {
				frm.events.make_stock_entry();
			}
		);
		
		console.log(frm);
		//If no items to approve, hide approval buttons
		if(frm.doc.requested_items && frm.doc.requested_items.length > 0)
		{
			cur_frm.set_df_property("html_recommend_buttons", "hidden", 0);
			cur_frm.set_df_property("html_approve_buttons", "hidden", 0);
		}
	},
	
	make_stock_entry: function() {
		frappe.model.open_mapped_doc({
			method: "fleet_management.workshop.doctype.requested_items.requested_items.make_from_requested_items",
			frm: cur_frm
		})
	},
});


//For recommend button
cur_frm.cscript.recommend_request = function(frm){
	var selected = cur_frm.get_selected();
	if(selected['requested_items'])
	{
		frappe.confirm(
			'Confirm: Recommend selected requests?',
			function(){
				$.each(selected['requested_items'], function(index, value){
					frappe.call({
						method: "fleet_management.workshop.doctype.requested_items.requested_items.recommend_request",
						freeze: true,
						args: {
							request_doctype: "Requested Items Table",
							request_docname: value,
							user: frappe.user.full_name()
						},
						callback: function(data){
							//alert(JSON.stringify(data));
						}
					});
				});
				location.reload();
			},
			function(){
				//Do nothing
			}
		);
	}
	else
	{
		show_alert("Error: Please select requests to process.");
	}
}


//For recommend against button
cur_frm.cscript.recommend_against_request = function(frm){
	var selected = cur_frm.get_selected();
	if(selected['requested_items'])
	{
		frappe.confirm(
			'Confirm: Recommend against the selected requests?',
			function(){
				$.each(selected['requested_items'], function(index, value){
					frappe.call({
						method: "fleet_management.workshop.doctype.requested_items.requested_items.recommend_against_request",
						freeze: true,
						args: {
							request_doctype: "Requested Items Table",
							request_docname: value,
							user: frappe.user.full_name()
						},
						callback: function(data){
							//alert(JSON.stringify(data));
						}
					});
				});
				location.reload();
			},
			function(){
				//Do nothing
			}
		);
	}
	else
	{
		show_alert("Error: Please select requests to process.");
	}
}


//For approve button
cur_frm.cscript.approve_request = function(frm){
	var selected = cur_frm.get_selected();
	if(selected['requested_items'])
	{
		frappe.confirm(
			'Confirm: Approve selected requests?',
			function(){
				$.each(selected['requested_items'], function(index, value){
					frappe.call({
						method: "fleet_management.workshop.doctype.requested_items.requested_items.approve_request",
						freeze: true,
						args: {
							request_doctype: "Requested Items Table",
							request_docname: value,
							user: frappe.user.full_name()
						},
						callback: function(data){
							//alert(JSON.stringify(data));
						}
					});
				});
				location.reload();
			},
			function(){
				//Do nothing
			}
		);
	}
	else
	{
		show_alert("Error: Please select requests to process.");
	}
}

//For reject button
cur_frm.cscript.reject_request = function(frm){
	//cur_frm.cscript.populate_child(cur_frm.doc.reference_doctype, cur_frm.doc.reference_docname);
	var selected = cur_frm.get_selected();
	if(selected['requested_items'])
	{
		frappe.confirm(
			'Confirm: Reject selected requests?',
			function(){
				$.each(selected['requested_items'], function(index, value){
					frappe.call({
						method: "fleet_management.workshop.doctype.requested_items.requested_items.reject_request",
						freeze: true,
						args: {
							request_doctype: "Requested Items Table",
							request_docname: value,
							user: frappe.user.full_name()
						},
						callback: function(data){
							//alert(JSON.stringify(data));
						}
					});
				});
				location.reload();
			},
			function(){
				//Do nothing
			}
		);
	}
	else
	{
		show_alert("Error: Please select requests to process.");
	}
}
