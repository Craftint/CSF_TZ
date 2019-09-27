// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Reports by Tax Category"] = {
        "filters": [
			{
				"fieldname":"from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
				"reqd": 1,
				"width": "60px"
			},
			{
				"fieldname":"to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"default": frappe.datetime.get_today(),
				"reqd": 1,
				"width": "60px"
			},
			{
				"fieldname": "taxes_and_charges",
				"label": __("Taxes and Charges"),
				"fieldtype": "Link",
				"width": "120",
				"options": "Purchase Taxes and Charges Template",
				"default": "Tanzania Tax - VPL"
			},
        ]
}