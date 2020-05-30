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
			"fieldname": "reference",
			"label": _("Reference"),
			"fieldtype": "Link",
			"options": "Vehicle Trip",
			"width": 100
		},
		{
			"fieldname": "trip_type",
			"label": _("Trip Type"),
			"fieldtype": "Data",
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
			"fieldname": "transporter_type",
			"label": _("Transporter Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "transporter_name",
			"label": _("Transporter Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "vehicle_plate_number",
			"label": _("Vehicle"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "trailer_plate_number",
			"label": _("Trailer"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "driver_name",
			"label": _("Driver"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "cargo",
			"label": _("Cargo"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "source_location",
			"label": _("Source"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "destination_location",
			"label": _("Destination"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "eta",
			"label": _("ETA"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "trip_expenses_usd",
			"label": _("Trip Expenses (USD)"),
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "trip_expenses_tzs",
			"label": _("Trip Expenses (TZS)"),
			"fieldtype": "Float",
			"width": 120
		}
	]
	
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
		
	where = ""
	where_filter = {"from_date": filters.from_date, "to_date": filters.to_date}
	if filters.status:
		where += 'AND status = %(status)s'
		where_filter.update({"status": filters.status})
	
	data = frappe.db.sql('''SELECT * FROM
				(SELECT
					`tabVehicle Trip`.name AS reference,
					'Main Trip' AS trip_type,
					`tabVehicle Trip`.main_customer AS customer,
					`tabVehicle Trip`.transporter_type,
					CASE
						WHEN `tabVehicle Trip`.transporter_type = 'Bravo' THEN 'Bravo'
						ELSE `tabVehicle Trip`.sub_contractor
					END AS transporter_name,
					`tabVehicle Trip`.vehicle_plate_number,
					`tabVehicle Trip`.trailer_plate_number,
					`tabVehicle Trip`.driver_name,
					`tabVehicle Trip`.main_cargo_category AS cargo,
					CONCAT(`tabVehicle Trip`.main_loading_point, "-",`tabVehicle Trip`.main_cargo_location_city,"-",`tabVehicle Trip`.main_cargo_location_country) AS source_location,
					CONCAT(`tabVehicle Trip`.main_offloading_point, "-",`tabVehicle Trip`.main_cargo_destination_city,"-",`tabVehicle Trip`.main_cargo_destination_country) AS destination_location,
					`tabVehicle Trip`.main_eta AS eta,
					`tabVehicle Trip`.status,
					(SELECT SUM(expense_amount) FROM `tabExpenses`
						WHERE parenttype = 'Vehicle Trip' AND parent = `tabVehicle Trip`.name AND expense_currency = 'USD'
						) AS trip_expenses_usd,
					(SELECT SUM(expense_amount) FROM `tabExpenses`
						WHERE parenttype = 'Vehicle Trip' AND parent = `tabVehicle Trip`.name AND expense_currency = 'TZS'
						) AS trip_expenses_tzs
				FROM
					`tabVehicle Trip`
				WHERE 
					reference_doctype IS NOT NULL AND reference_docname IS NOT NULL ''' + where + ''' AND start_date BETWEEN %(from_date)s AND %(to_date)s
				UNION ALL
				SELECT
					`tabVehicle Trip`.name AS reference,
					'Return Trip' AS trip_type,
					`tabVehicle Trip`.return_customer AS customer,
					`tabVehicle Trip`.transporter_type,
					CASE
						WHEN `tabVehicle Trip`.transporter_type = 'Bravo' THEN 'Bravo'
						ELSE `tabVehicle Trip`.sub_contractor
					END AS transporter_name,
					`tabVehicle Trip`.vehicle_plate_number,
					`tabVehicle Trip`.trailer_plate_number,
					`tabVehicle Trip`.driver_name,
					`tabVehicle Trip`.return_cargo_category AS cargo,
					CONCAT(`tabVehicle Trip`.return_loading_point, "-",`tabVehicle Trip`.return_cargo_location_city,"-",`tabVehicle Trip`.return_cargo_location_country) AS source_location,
					CONCAT(`tabVehicle Trip`.return_offloading_point, "-",`tabVehicle Trip`.return_cargo_destination_city,"-",`tabVehicle Trip`.return_cargo_destination_country) AS destination_location,
					`tabVehicle Trip`.return_eta AS eta,
					`tabVehicle Trip`.status,
					(SELECT SUM(expense_amount) FROM `tabExpenses`
						WHERE parenttype = 'Vehicle Trip' AND parent = `tabVehicle Trip`.name AND expense_currency = 'USD'
						) AS trip_expenses_usd,
					(SELECT SUM(expense_amount) FROM `tabExpenses`
						WHERE parenttype = 'Vehicle Trip' AND parent = `tabVehicle Trip`.name AND expense_currency = 'TZS'
						) AS trip_expenses_tzs
				FROM
					`tabVehicle Trip`
				WHERE 
					return_reference_doctype IS NOT NULL AND return_reference_docname IS NOT NULL ''' + where + ''' AND return_start_date BETWEEN %(from_date)s AND %(to_date)s
				) a
			ORDER BY reference''', where_filter, as_dict=1)
	return columns, data
