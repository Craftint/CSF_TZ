// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

var aday = new Date();
var from_date = aday.toISOString().split('T')[0];
aday.setDate(aday.getDate() + 30);
var to_date = aday.toISOString().split('T')[0];

frappe.query_reports["Items Marked For Delivery"] = {
	"filters": [
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
	]
}
