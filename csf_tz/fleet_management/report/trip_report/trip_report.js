// Copyright (c) 2016, Bravo Logistics and contributors
// For license information, please see license.txt
/* eslint-disable */
var aday = new Date();
var to_date = aday.toISOString().split('T')[0];
aday.setDate(aday.getDate() - 30);
var from_date = aday.toISOString().split('T')[0];


frappe.query_reports["Trip Report"] = {
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
            "fieldname":"status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nEn Route\nMain Trip Offloaded\nEn Route - Returning\nReturn Trip Offloaded",
            "default": ""
        }
	]
}
