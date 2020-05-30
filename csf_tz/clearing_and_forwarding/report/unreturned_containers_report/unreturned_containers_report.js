// Copyright (c) 2016, Bravo Logisitcs and contributors
// For license information, please see license.txt
/* eslint-disable */



var aday = new Date();
aday.setDate(aday.getDate() - 30);
var from_date = aday.toISOString().split('T')[0];


frappe.query_reports["Unreturned Containers Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default":""
        },
        {
            "fieldname": "container_owner",
            "label": __("Container Owner"),
            "fieldtype": "Select",
            "options": "\nSOC (Shipper Owned Container)\nShipping Line Container\nBravo Container\nRental",
            "default": ""
		},
        {
            "fieldname": "shipping_line",
            "label": __("Shipping Line"),
            "fieldtype": "Link",
            "options": "Shipping Line",
		}
	]
}
