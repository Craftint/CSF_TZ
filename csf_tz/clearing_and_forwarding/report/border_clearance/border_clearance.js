// Copyright (c) 2016, Bravo Logisitcs and contributors
// For license information, please see license.txt
/* eslint-disable */
var aday = new Date();
aday.setDate(aday.getDate() - 30);
var from_date = aday.toISOString().split('T')[0];
aday.setDate(aday.getDate() + 60);
var to_date = aday.toISOString().split('T')[0];


frappe.query_reports["Border Clearance"] = {
	"filters": [
		 {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": from_date
        },
        {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": to_date
        },
		{
            "fieldname":"client",
            "label": __("Client"),
            "fieldtype": "Link",
            "options": "Customer",
        },
        {
            "fieldname":"type",
            "label": __("type"),
            "fieldtype": "Select",
            "options": "All\nImport\nExport",
            "default": "All"
        }
	]
}

