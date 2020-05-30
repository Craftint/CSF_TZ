// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

var aday = new Date();
var to_date = aday.toISOString().split('T')[0];
aday.setDate(aday.getDate() - 30);
var from_date = aday.toISOString().split('T')[0];

frappe.query_reports["Technicians Performance Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": from_date,
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": to_date,
			"reqd": 1
		},
		{
            "fieldname":"status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": ["", "Open", "Closed"],
        },
        {
            "fieldname":"user",
            "label": __("Technician"),
            "fieldtype": "Link",
			"options": "Employee",
        },
        {
            "fieldname":"workshop",
            "label": __("Warehouse"),
            "fieldtype": "Link",
			"options": "Warehouse",
        },
        {
            "fieldname":"custm",
            "label": __("Customer"),
            "fieldtype": "Link",
			"options": "Customer",
        },
	]
}
