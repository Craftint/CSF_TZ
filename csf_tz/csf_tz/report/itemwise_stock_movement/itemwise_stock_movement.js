// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Itemwise Stock Movement"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"default": "DAR - VC",
			"reqd": 1
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"default": "VOUCHERS"
		},
		{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand",
			"default": "HALOTEL"
		},
		{
			"fieldname":"include_uom",
			"label": __("Include UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		}
	]
}

// $(function() {
// 	$(wrapper).bind("show", function() {
// 		frappe.query_report.load();
// 	});
// });