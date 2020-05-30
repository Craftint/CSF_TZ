# Copyright (c) 2013, Bravo Logisitcs and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime

def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"fieldname": "import_no",
			"label": _("Import No"),
			"fieldtype": "Link",
			"options": "Import",
			"width": 150

		},
		{
			"fieldname": "reference_file_number",
			"label": _("Reference File Number"),
			"fieldtype": "Link",
			"options" :"Files",
			"width": 200
		},
		{
			"fieldname": "bl_number",
			"label": _("B/L Number"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "shipping_line",
			"label": _("Shipping Line"),
			"fieldtype": "Link",
			"options": "Shipping Line",
			"width": 200
		},
		{
			"fieldname": "container_owner",
			"label": _("Container Owner"),
			"fieldtype": "Select",
			"options": "SOC (Shipper Owned Container)\nShipping Line Container\nBravo Container\nRental",
			"width": 200
		},
		{
			"fieldname": "container_no",
			"label": _("Container No"),
			"fieldtype": "Data",
			"width": 150
		},

		{
			"fieldname": "container_return_date",
			"label": _("Container Return Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "demurrage_start_date",
			"label": _("Demurrage Start Date"),
			"fieldtype": "Date",
			"width": 150
		}

	]

	where = ""
	where_filter = {}

	if filters.from_date or filters.container_owner or  filters.shipping_line:
		where ="where "

	if filters.from_date:
		where += ' imp.demurrage_start_date >= %(from_date)s'
		where_filter.update({"from_date": filters.from_date})

	if filters.container_owner:
		if filters.from_date:
			where += ' AND '
		where += ' imp.container_owner = %(container_owner)s'
		where_filter.update({"container_owner": filters.container_owner})

	if filters.shipping_line:
		if filters.from_date or filters.container_owner:
			where += ' AND '
		where += '  imp.shipping_line = %(shipping_line)s '
		where_filter.update({"shipping_line":filters.shipping_line})

	data = frappe.db.sql('''SELECT 
								imp.name AS import_no,
								imp.reference_file_number,
								imp.bl_number,
								imp.shipping_line ,
								imp.container_owner ,
								cfci.container_no,
								cfci.container_return_date,
								imp.demurrage_start_date 


								FROM 
									(`tabImport` imp)
								LEFT JOIN `tabContainer File Closing Information` AS cfci
									ON (imp.name=cfci.parent)
								''' + where + '''
									''',
						 where_filter,as_dict=1,as_list=1);
	return columns, data
