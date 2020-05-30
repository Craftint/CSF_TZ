// Copyright (c) 2016, Bravo Logistics and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Vehicles En Route to Border"] = {
	"filters": [
		 {
            "fieldname":"border",
            "label": __("Border"),
            "fieldtype": "Link",
            "options": "Trip Location"
        }
	]
}
