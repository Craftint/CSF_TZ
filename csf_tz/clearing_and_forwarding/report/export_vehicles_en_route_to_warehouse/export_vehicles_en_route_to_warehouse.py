# Copyright (c) 2013, Bravo Logisitcs and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast
import datetime
import time

def execute(filters=None):
	columns, data = [], []
	
	columns = [
		{
			"fieldname": "reference",
			"label": _("Reference"),
			"fieldtype": "Link",
			"options": "Border Clearance",
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
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "transporter",
			"label": _("Transporter"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "truck",
			"label": _("Truck\Trailer"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "cargo",
			"label": _("Cargo"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "border",
			"label": _("Border"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "border_date_time",
			"label": _("Border Crossing Date and Time"),
			"fieldtype": "Datatime",
			"width": 150
		}
	]
	
	
	data = frappe.db.sql('''SELECT
								`tabBorder Clearance`.name AS reference,
								`tabBorder Clearance`.client AS customer,
								`tabBorder Clearance`.cargo_destination_exact AS warehouse,
								CASE
									WHEN `tabBorder Clearance`.transporter_type = 'Other' THEN `tabBorder Clearance`.transporter_name
									ELSE 'Bravo'
								END AS transporter,
								CONCAT(`tabBorder Clearance`.vehicle_plate_number, '/', `tabBorder Clearance`.trailer_plate_number) AS truck,
								`tabBorder Clearance`.cargo_description AS cargo,
								CASE
									WHEN `tabBorder Clearance`.no_of_borders = 1 THEN `tabBorder Clearance`.border1_name
									WHEN `tabBorder Clearance`.no_of_borders = 2 THEN `tabBorder Clearance`.border2_name
									WHEN `tabBorder Clearance`.no_of_borders = 3 THEN `tabBorder Clearance`.border3_name
									WHEN `tabBorder Clearance`.no_of_borders = 4 THEN `tabBorder Clearance`.border4_name
								END AS border,
								CASE
									WHEN `tabBorder Clearance`.no_of_borders = 1 THEN `tabBorder Clearance`.border1_crossing
									WHEN `tabBorder Clearance`.no_of_borders = 2 THEN `tabBorder Clearance`.border2_crossing
									WHEN `tabBorder Clearance`.no_of_borders = 3 THEN `tabBorder Clearance`.border3_crossing
									WHEN `tabBorder Clearance`.no_of_borders = 4 THEN `tabBorder Clearance`.border4_crossing
								END AS border_date_time
							FROM
								`tabBorder Clearance`
							WHERE
								`tabBorder Clearance`.cargo_destination_country = 'Tanzania' AND `tabBorder Clearance`.offloading_datetime IS NULL
						''', as_dict=1)
	
	
	return columns, data
