// Copyright (c) 2022, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Email Salary Slips', {
	// refresh: function(frm) {

	// }

	onload: function(frm) {
		frm.get_field("employees").grid.cannot_add_rows = true;
	},

	setup: function(frm) {
		frm.set_query("payroll_entry", function() {
			return {
				filters: [
					["Payroll Entry","docstatus", "=", "1"]
				]
			}
		});
	},

    "payroll_entry": function(frm) {
    	frm.doc.employees = []
    	refresh_field("employees");
        let payroll_entry = frm.doc.payroll_entry;
        if(payroll_entry){
        	frappe.call({
		     method: "csf_tz.custom_api.validate_payroll_entry_field",
		     args: {payroll_entry: payroll_entry}
		    }).done((r) => {
				if(r.message == false){
					frm.fields_dict.payroll_entry.set_input(undefined);
					frappe.msgprint({
					    title: __('Invalid Payroll selection'),
					    indicator: 'red',
					    message: __('Please select the submitted Payroll Entry')
					});
				}
		  	})
        }
    },
	
	get_employees: function(frm) {
		let payroll_entry = frm.doc.payroll_entry;
		if(payroll_entry){
			frappe.call({
		     method: "csf_tz.custom_api.get_payroll_employees",
		     args: {payroll_entry: payroll_entry}
		    }).done((r) => {
				frm.doc.employees = []
				$.each(r.message, function(_i, e){
				   let entry = frm.add_child("employees");
				   entry.employee = e.employee;
				})
				refresh_field("employees")
				frm.dirty();
				frm.save();
				frm.refresh();
		  })
		}
		else{
			frappe.msgprint({
			    title: __('Missing Fields'),
			    indicator: 'red',
			    message: __('Please select the Payroll Entry field')
			});
		}
	}
});
