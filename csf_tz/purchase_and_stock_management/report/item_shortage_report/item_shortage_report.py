# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"fieldname": "warehouse",
			"label" : _("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname": "actual_qty",
			"label": _("Actual Quantity"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "ordered_qty",
			"label": _("Ordered Quantity"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "planned_qty",
			"label": _("Planned Quantity"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "reserved_qty",
			"label": _("Reserved Quantity"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "projected_qty",
			"label": _("Projected Quantity"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "description",
			"label": _("Description"),
			"fieldtype": "Data",
			"width": 200
		},
		
	]

	where_filter = {}
	where = ""
	if filters.warehouse:
		where += '  AND bin.warehouse = %(warehouse)s '
		where_filter.update({"warehouse": filters.warehouse})
	if filters.item_code:
		where += '  AND bin.item_code = %(item_code)s '
		where_filter.update({"item_code": filters.item_code})

	data = frappe.db.sql('''SELECT 
								bin.warehouse ,
								bin.item_code,
								bin.actual_qty ,
								bin.ordered_qty,
								bin.planned_qty,
								bin.reserved_qty,
								bin.projected_qty,
								ti.item_name,
								ti.description
							FROM 
								(tabBin AS bin)
							INNER JOIN 
								(tabItem AS ti) ON bin.item_code=ti.name
							WHERE 
								bin.projected_qty<0
							/*ORDER BY 
								bin.projected_qty*/
							 '''+ where,
								where_filter, as_dict=1,as_list=1
							);

	return columns, data
