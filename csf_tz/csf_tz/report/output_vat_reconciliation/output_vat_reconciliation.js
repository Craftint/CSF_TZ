// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Output VAT Reconciliation"] = {
	"filters": [
		{
			"fieldname":"efd_report",
			"label": __("EFD Report"),
			"fieldtype": "Link",
			"options": "EFD Z Report",
			"reqd": 1,
			"get_query" : function(){
				return {
					"filters":{
						"docstatus":1,
					}
				}
			}
		}
	],
    "formatter": function(value, row, column, data, default_formatter) {
	    value = default_formatter(value, row, column, data);
	    if (value === "Credit Note - Sales Returns" || value === "Sales - Sales Returns" || value === "Sales as VAT Returns" ){
	        value = '<b style="font-weight:bold">'+value+'</b>';
	    }
	    return value;
	}
};
