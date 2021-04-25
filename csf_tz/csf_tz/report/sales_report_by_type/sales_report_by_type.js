// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Report by Type"] = {
  filters: [
    {
        fieldname: "from_date",
        fieldtype: "Date",
        label: "From Date",
        mandatory: 1,
        wildcard_filter: 0,
    },
    {
        fieldname: "to_date",
        fieldtype: "Date",
        label: "To Date",
        mandatory: 1,
        wildcard_filter: 0,
    },
    {
        fieldname: "is_pos",
        fieldtype: "Select",
        label: "Is POS",
        mandatory: 1,
        options: "No\nYes",
        wildcard_filter: 0,
    }
  ]
}
