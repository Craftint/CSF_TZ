# Copyright (c) 2013, Bravo Logisitcs and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, cstr
from frappe import _
import ast
from datetime import datetime

def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"fieldname": "file_no",
			"label": _("File No"),
			"fieldtype": "Link",
			"options": "Files",
			"width": 100
		},
		{
			"fieldname": "file_type",
			"label": _("File Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "documents_received_date",
			"label": _("Document Received"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname": "location",
			"label": _("Opening Location"),
			"fieldtype": "Link",
			"options": "Locations",
			"width": 200
		},
		{
			"fieldname": "expenses_usd",
			"label": _("Expenses(USD)"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "expenses_tzs",
			"label": _("Expenses(TZS)"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "invoiced_amount_usd",
			"label": _("Invoiced Amount(USD)"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "invoiced_amount_tzs",
			"label": _("Invoiced Amount(TZS)"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "paid_amount_usd",
			"label": _("Paid Amount(USD)"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "paid_amount_tzs",
			"label": _("Paid Amount(TZS)"),
			"fieldtype": "Float",
			"width": 150
		}
	]
	
	
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
	
	data = frappe.db.sql('''SELECT
			tabFiles.name as file_no,
			CASE
				WHEN tabFiles.import_transit = 1 THEN 'Importation - Transit'
				WHEN tabFiles.import_local = 1 THEN 'Importation - Local'
				WHEN tabFiles.export_transit = 1 THEN 'Export - Transit'
				WHEN tabFiles.export_local = 1 THEN 'Export Local'
				WHEN tabFiles.transport_transit = 1 THEN 'Transport - Transit'
				WHEN tabFiles.transport_local = 1 THEN 'Transport - Local'
				WHEN tabFiles.border_clearance = 1 THEN 'Border Clearance'
			END AS file_type,
			tabFiles.documents_received_date,
			tabFiles.customer,
			tabFiles.location,
			(SELECT SUM(expense_amount) FROM `tabExpenses` WHERE expense_currency = 'USD' AND (
				(parenttype = 'Import' AND parent IN (SELECT name FROM `tabImport` WHERE reference_file_number = tabFiles.name )) OR
				(parenttype = 'Export' AND parent IN (SELECT name FROM `tabExport` WHERE file_number = tabFiles.name )) OR
				(parenttype = 'Vehicle Trip' AND parent IN (SELECT name FROM `tabVehicle Trip` WHERE main_file_number = tabFiles.name )) OR
				(parenttype = 'Vehicle Trip' AND parent IN (SELECT name FROM `tabVehicle Trip` WHERE return_file_number = tabFiles.name )) OR
				(parenttype = 'Border Clearance' AND parent IN (SELECT name FROM `tabBorder Clearance` WHERE file_number = tabFiles.name )) OR
				(parenttype = 'Files' AND parent = tabFiles.name))
			) AS expenses_usd,
			(SELECT SUM(expense_amount) FROM `tabExpenses` WHERE expense_currency = 'TZS' AND (
				(parenttype = 'Import' AND parent IN (SELECT name FROM `tabImport` WHERE reference_file_number = tabFiles.name )) OR
				(parenttype = 'Export' AND parent IN (SELECT name FROM `tabExport` WHERE file_number = tabFiles.name )) OR
				(parenttype = 'Vehicle Trip' AND parent IN (SELECT name FROM `tabVehicle Trip` WHERE main_file_number = tabFiles.name )) OR
				(parenttype = 'Vehicle Trip' AND parent IN (SELECT name FROM `tabVehicle Trip` WHERE return_file_number = tabFiles.name )) OR
				(parenttype = 'Border Clearance' AND parent IN (SELECT name FROM `tabBorder Clearance` WHERE file_number = tabFiles.name )) OR
				(parenttype = 'Files' AND parent = tabFiles.name))
			) AS expenses_tzs,
			(SELECT SUM(grand_total) FROM `tabSales Invoice` WHERE currency = 'USD' AND reference_doctype = 'Files' AND reference_docname = tabFiles.name) 
				AS invoiced_amount_usd,
			(SELECT SUM(grand_total) FROM `tabSales Invoice` WHERE currency = 'TZS' AND reference_doctype = 'Files' AND reference_docname = tabFiles.name) 
				AS invoiced_amount_tzs,
			(SELECT credit_in_account_currency FROM `tabGL Entry` WHERE credit_in_account_currency > 0 AND account_currency = 'USD' 
				AND against_voucher_type = 'Sales Invoice' AND against_voucher 
					IN (SELECT name FROM `tabSales Invoice` where reference_doctype = 'Files' AND reference_docname = tabFiles.name))
				AS paid_amount_usd,
			(SELECT credit_in_account_currency FROM `tabGL Entry` WHERE credit_in_account_currency > 0 AND account_currency = 'TZS' 
				AND against_voucher_type = 'Sales Invoice' AND against_voucher 
					IN (SELECT name FROM `tabSales Invoice` where reference_doctype = 'Files' AND reference_docname = tabFiles.name))
				AS paid_amount_tzs			
		FROM tabFiles
		WHERE
			tabFiles.documents_received_date BETWEEN  %(from_date)s AND %(to_date)s''', {"from_date": filters.from_date, "to_date": filters.to_date}, as_dict=1)
	return columns, data
