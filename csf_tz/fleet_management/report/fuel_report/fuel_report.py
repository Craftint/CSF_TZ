# Copyright (c) 2013, Bravo Logistics and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, cstr
from frappe import _
import ast
from datetime import datetime
from frappe.desk.reportview import export_query
from frappe.desk.query_report import run
from frappe.desk.query_report import get_columns_dict
from six import string_types
import os, json
import openpyxl
from openpyxl.styles import Font
from openpyxl import load_workbook
from six import StringIO, string_types
from frappe.utils.xlsxutils import handle_html

def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"fieldname": "reference_docname",
			"label": _("Reference"),
			"fieldtype": "Link",
			"options": "Vehicle Trip",
			"width": 100
		},
		{
			"fieldname": "vehicle",
			"label": _("Vehicle"),
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 100
		},
		{
			"fieldname": "fuel_type",
			"label": _("Fuel Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "quantity",
			"label": _("Quantity (Litres)"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "cost_per_litre",
			"label": _("Cost Per Litre"),
			"fieldtype": "Currency",
			"width": 150,
			"options": "currency"
		},
		{
			"fieldname": "disburcement_type",
			"label": _("Disburcement Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "supplier",
			"label": _("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150
		},
		{
			"fieldname": "fuel_request",
			"label": _("Fuel Request"),
			"fieldtype": "Link",
			"options": "Fuel Request",
			"width": 150
		}
	]
	
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
		
	where = " WHERE approved_date BETWEEN %(from_date)s AND %(to_date)s "
	where_filter = {"from_date": filters.from_date, "to_date": filters.to_date}
	if filters.vehicle:
		where += 'AND vehicle = %(vehicle)s'
		where_filter.update({"vehicle": filters.vehicle})
		
	if filters.disburcement_type:
		where += ' AND disburcement_type = %(disburcement_type)s'
		where_filter.update({"disburcement_type": filters.disburcement_type})
	
	data = frappe.db.sql('''SELECT
								`tabFuel Request`.reference_docname,
								`tabVehicle Trip`.vehicle,
								`tabFuel Request Table`.fuel_type,
								`tabFuel Request Table`.quantity,
								`tabFuel Request Table`.cost_per_litre,
								`tabFuel Request Table`.disburcement_type,
								`tabFuel Request Table`.supplier,
								`tabFuel Request`.name AS fuel_request
							FROM
								`tabFuel Request`
							LEFT JOIN
								`tabVehicle Trip` ON `tabFuel Request`.reference_docname = `tabVehicle Trip`.name
							LEFT JOIN
								`tabFuel Request Table` ON `tabFuel Request`.reference_docname = `tabFuel Request Table`.parent
							''' + where, where_filter, as_dict=1)
	return columns, data
