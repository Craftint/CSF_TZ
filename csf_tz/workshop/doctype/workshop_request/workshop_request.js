// Copyright (c) 2017, Bravo Logistics and contributors
// For license information, please see license.txt

frappe.ui.form.on('Workshop Request', {
	refresh: function(frm) {
		frm.events.show_hide_sections(frm);				
		frm.set_query("requested_for", function(){
			return{
				"filters": {
					"name": ["in", ['Vehicle', 'Trailer']],
				}
			}
		});
		
		//Make job card button
		frm.add_custom_button(__('Make Job Card'),
			function() {
				frm.events.make_job_card();
			}
		);
	},
	
	request_type: function(frm){
		frm.events.show_hide_sections(frm);
	},
	
	// Show or Hide sections depending on previously entered information.
	show_hide_sections: function(frm){
		frm.toggle_display("previous_job", (frm.doc.request_type && frm.doc.request_type == "Rework"));
		frm.refresh_fields()
	},
	
	make_job_card: function() {
		frappe.model.open_mapped_doc({
			method: "fleet_management.workshop.doctype.job_card.job_card.make_job_card",
			frm: cur_frm
		})
	},
});
