# Copyright (c) 2013, Bravo Logisitcs and contributors
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
			"fieldname": "reference",
			"label": _("Reference"),
			"fieldtype": "Link",
			"options": "Files",
			"width": 150
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 250
		},
		{
			"fieldname": "documents_received_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 150
		}
	]
	
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
	
	data = frappe.db.sql('''SELECT
					tabFiles.name AS reference,
					tabFiles.customer,
					tabFiles.documents_received_date
				FROM
					`tabFiles`
				WHERE 
					tabFiles.quotation IS NULL AND tabFiles.documents_received_date BETWEEN %(from_date)s AND %(to_date)s''', 
				{"from_date": filters.from_date, "to_date": filters.to_date}, as_dict=1)
	
	return columns, data
