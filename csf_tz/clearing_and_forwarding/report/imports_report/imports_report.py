# Copyright (c) 2013, Codes Consult and contributors
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
			"options": "Import",
			"width": 100
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 100
		},
		{
			"fieldname": "bl_number",
			"label": _("BL Number"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "cargo",
			"label": _("Cargo"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "number_of_containers",
			"label": _("No. of Containers"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "total_weight",
			"label": _("Total Weight"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "cargo_value",
			"label": _("Cargo Value"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "shipper",
			"label": _("Shipper"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "vessel_name",
			"label": _("Vessel Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "import_type",
			"label": _("Import Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "shipping_eta",
			"label": _("Shipping ETA"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "shipping_ata",
			"label": _("Shipping ATA"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "destination",
			"label": _("Destination"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "manifest_date",
			"label": _("Manifest Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "tansad_date",
			"label": _("Tansad Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "manifest_comparison",
			"label": _("Manifest Comparison"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "loading_date",
			"label": _("Loading Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "import_expenses_usd",
			"label": _("Import Expenses"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "import_expenses_tzs",
			"label": _("Import Expenses (TZS)"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Data",
			"width": 200
		}
	]
	
	where = ''
	where_filter = {"from_date": filters.from_date, "to_date": filters.to_date, "status": filters.status}
	
	if filters.status:
		where += " AND tabImport.status = %(status)s "
		where_filter.update({'status': filters.status})
			
	if filters.loading_date_from:
		where += " AND tabImport.loading_date >= %(loading_date_from)s "
		where_filter.update({'loading_date_from': filters.loading_date_from})
		
	if filters.loading_date_to:
		where += " AND tabImport.loading_date <= %(loading_date_to)s "
		where_filter.update({'loading_date_to': filters.loading_date_to})
	
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
	
	data = frappe.db.sql('''SELECT
					tabImport.name AS reference,
					tabImport.customer,
					tabImport.bl_number AS bl_number,
					CONCAT(tabImport.cargo, " - ", tabImport.cargo_description) AS cargo,
					count(`tabCargo Details`.name) AS number_of_containers,
					SUM(`tabCargo Details`.net_weight) AS total_weight,
					SUM(`tabCargo Details`.bond_value) AS cargo_value,
					tabImport.shipping_line AS shipper,
					tabImport.vessel_name AS vessel_name,
					tabImport.import_type AS import_type,
					tabImport.eta AS shipping_eta,
					tabImport.ata AS shipping_ata,
					CONCAT(tabImport.cargo_destination_country, " - ", tabImport.cargo_destination_city) AS destination,
					tabImport.manifest_date,
					tabImport.tansad_date,
					tabImport.manifest_comparison_date AS manifest_comparison,
					tabImport.loading_date,
					(SELECT SUM(expense_amount) FROM `tabExpenses`
							WHERE parenttype = 'Import' AND parent = `tabImport`.name AND expense_currency = 'USD'
					) AS import_expenses_usd,
					(SELECT SUM(expense_amount) FROM `tabExpenses`
							WHERE parenttype = 'Import' AND parent = `tabImport`.name AND expense_currency = 'TZS'
					) AS import_expenses_tzs,
					(SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE `tabReporting Status Table`.parenttype = 'Import' \
						AND `tabReporting Status Table`.parent = `tabImport`.name ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1) AS remarks
				FROM
					`tabImport`
				LEFT OUTER JOIN
					`tabCargo Details` ON `tabCargo Details`.parent = `tabImport`.name AND `tabCargo Details`.parenttype = 'Import'
				WHERE 
					tabImport.documents_received_date BETWEEN %(from_date)s AND %(to_date)s ''' + where + 
				''' GROUP BY 
					tabImport.name''', 
				where_filter, as_dict=1)
	
	return columns, data

	
