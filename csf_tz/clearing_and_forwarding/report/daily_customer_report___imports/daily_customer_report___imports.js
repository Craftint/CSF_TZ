// Copyright (c) 2016, Bravo Logisitcs and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Daily Customer Report - Imports"] = {
	"filters": [
		{
            "fieldname":"customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
        }
	]
}
