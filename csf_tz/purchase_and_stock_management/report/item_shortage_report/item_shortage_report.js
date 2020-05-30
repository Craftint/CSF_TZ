// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

var aday = new Date();
var from_date = aday.toISOString().split('T')[0];
aday.setDate(aday.getDate() + 7);
var to_date = aday.toISOString().split('T')[0];

frappe.query_reports["Item Shortage Report"] = {
	"filters": [
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
		},
	]
}
