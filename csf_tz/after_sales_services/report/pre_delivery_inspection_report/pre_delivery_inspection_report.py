# Copyright (c) 2013, Bravo Logistics and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, cstr
from frappe import _
import ast
import datetime

def execute(filters=None):
	columns, data = [], []
	
	columns = [
		{
			"fieldname": "reference",
			"label": _("Pre Delivery Inspection Reference"),
			"fieldtype": "Link",
			"options": "Pre Delivery Inspection",
			"width": 100
		},
		{
			"fieldname": "report_date",
			"label": _("Done On"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "data",
			"width": 100
		},
		{
			"fieldname": "inspection_type",
			"label": _("Inspection Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "item_code",
			"label": _("Item code"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "item_serial_no",
			"label": _("Serial no"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "inspected_by",
			"label": _("Inspected By"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "verified_by",
			"label": _("Verified By"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Text",
			"width": 200
		}
	]
	
	
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
		
	where = ''
	where_filter = {"from_date": filters.from_date, "to_date": filters.to_date}

	if filters.branch:
		where += ' AND sit.warehouse = %(branch)s'
		where_filter.update({"branch": filters.branch})
	
	data = frappe.db.sql('''SELECT
								`tabPre Delivery Inspection`.name AS reference,
								`tabPre Delivery Inspection`.report_date,
								`tabPre Delivery Inspection`.customer,
								`tabPre Delivery Inspection`.inspection_type,
								`tabPre Delivery Inspection`.item_code,
								`tabPre Delivery Inspection`.item_serial_no,
								`tabPre Delivery Inspection`.inspected_by,
								`tabPre Delivery Inspection`.verified_by,
								`tabPre Delivery Inspection`.reference_name,
								`tabPre Delivery Inspection`.remarks,
								sit.warehouse

							FROM
								`tabPre Delivery Inspection`
							LEFT JOIN
								(`tabSales Invoice Item` sit)
								ON (`tabPre Delivery Inspection`.sales_invoice = sit.parent)
							WHERE 
								`tabPre Delivery Inspection`.docstatus <> 2 \
								AND `tabPre Delivery Inspection`.report_date BETWEEN %(from_date)s AND %(to_date)s
						 '''+ where,
							where_filter, as_dict=1)
						 
	return columns, data