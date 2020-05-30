// Copyright (c) 2016, Bravo Logistics and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Customer Report - Transport"] = {
	"filters": [
		{
            "fieldname":"customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
        }
	]
}
