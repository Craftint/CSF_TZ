// Copyright (c) 2019, Bravo Logisitcs and contributors
// For license information, please see license.txt

frappe.ui.form.on('Border Processing', {
    refresh: function (frm) {

    },


    new_fund_request: function (frm) {
        new_request = false
        if (frm.doc.requested_funds && frm.doc.requested_funds.length > 0) {
            frm.doc.requested_funds.forEach(function (row) {
                if (row.request_status == "open") {
                    new_request = true
                }
            })
            if (new_request == true) {
                frappe.call({
                    method: "csf_tz.after_sales_services.doctype.requested_payments.requested_payments.request_funds",
                    args: {
                        reference_doctype: "Border Processing",
                        reference_docname: cur_frm.doc.name
                    },
                    callback: function (data) {
                        console.log(data);
                    }
                })
            }
        }
    },


    after_save: function (frm) {
        //If there is unrequested funds
        frm.events.new_fund_request(frm);
        frm.events.toggle_editable_funds_rows(frm);
        frm.reload_doc();
    },


    toggle_editable_funds_rows: function (frm) {
        if (frm.doc.requested_funds && frm.doc.requested_funds.length > 0) {
            frm.doc.requested_funds.forEach(function (row) {
                if (row.request_status.toUpperCase() != "OPEN") {
                    //Make fields read only
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "request_date"
                    })[0].read_only = true;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "request_amount"
                    })[0].read_only = true;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "request_currency"
                    })[0].read_only = true;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "request_description"
                    })[0].read_only = true;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "comment"
                    })[0].read_only = true;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "requested_for"
                    })[0].read_only = true;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "quote_attachment"
                    })[0].read_only = true;
                } else {
                    //Make fields read only
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "request_date"
                    })[0].read_only = false;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "request_amount"
                    })[0].read_only = false;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "request_currency"
                    })[0].read_only = false;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "request_description"
                    })[0].read_only = false;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "comment"
                    })[0].read_only = false;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "requested_for"
                    })[0].read_only = false;
                    frappe.utils.filter_dict(cur_frm.fields_dict["requested_funds"].grid.grid_rows_by_docname[row.name].docfields, {
                        "fieldname": "quote_attachment"
                    })[0].read_only = false;
                }
            })
        }
    }
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
