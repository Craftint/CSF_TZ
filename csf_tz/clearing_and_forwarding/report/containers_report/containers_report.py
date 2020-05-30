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
			"fieldname": "creation_document_no",
			"label": _("Creation Document No"),
			"fieldtype": "Dynamic Link",
			"width": 100
		},
		{
			"fieldname": "shipping_line",
			"label": _("Shipping Line"),
			"fieldtype": "Link",
			"options": "Shipping Line",
			"width": 150
		},
		{
			"fieldname": "export_reference",
			"label": _("Export Reference"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "booking_number",
			"label": _("Booking Number"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "container_no",
			"label": _("Container No"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "container_type",
			"label": _("Container Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "seal_number",
			"label": _("Seal Number"),
			"fieldtype": "Data",
			"width": 100
		},
	]
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))

	where_filter = {"from_date": filters.from_date, "to_date": filters.to_date, }
	where = ""
	if filters.shipping_line:
		where += 'AND tc.shipping_line = %(shipping_line)s '
		where_filter.update({"shipping_line": filters.shipping_line})

	data = frappe.db.sql('''SELECT 
		                                tc.creation_document_no AS creation_document_no,
		                                tc.shipping_line AS shipping_line,
		                                tc.export_reference AS export_reference,
		                                tc.booking_number AS booking_number,
		                                tc.container_no AS container_no,
		                                tc.container_type AS container_type,
		                                tc.seal_number AS seal_number

										FROM 
											(`tabContainer` tc)
											WHERE
	                                tc.container_no IS NOT NULL ''' + where + '''
								''',
						 where_filter, as_dict=1, as_list=1);

	return columns, data