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
			"fieldname": "fleet_no",
			"label": _("Fleet No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "reg_no",
			"label": _("Reg. No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "driver_name",
			"label": _("Driver Name"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "contact",
			"label": _("Contact"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "cargo_type",
			"label": _("Cargo Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "destination",
			"label": _("Destination"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "client",
			"label": _("Client"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "route",
			"label": _("Route"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "dispatch_date",
			"label": _("Dispatch Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "offloading_date",
			"label": _("Offloading Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "position",
			"label": _("Position"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "next_cargo_allocation",
			"label": _("Next Cargo Allocation"),
			"fieldtype": "Data",
			"width": 100
		}
	]
	
	today = datetime.date.today().strftime("%Y-%m-%d")
	yesterday =  datetime.date.today() - datetime.timedelta(1)
	day_before = datetime.date.today() - datetime.timedelta(2)
	yesterday = yesterday.strftime("%Y-%m-%d")
	day_before = day_before.strftime("%Y-%m-%d")
	
	data = frappe.db.sql('''SELECT
								`tabVehicle`.fleet_number AS fleet_no,
								CASE 
									WHEN `tabTrailer`.number_plate THEN CONCAT(`tabVehicle`.number_plate, '/', `tabTrailer`.number_plate)
									ELSE `tabVehicle`.number_plate
								END AS reg_no,
								`tabVehicle`.name,
								`tabEmployee`.employee_name AS driver_name,
								`tabEmployee`.cell_number AS contact,
								`tabTransport Assignment`.parenttype AS next_assigned_parenttype,
								`tabTransport Assignment`.parent AS next_assigned_parent
							FROM
								`tabVehicle`
							LEFT JOIN
								`tabTrailer` ON `tabTrailer`.name = `tabVehicle`.default_trailer
							LEFT JOIN
								`tabEmployee` ON `tabEmployee`.name = `tabVehicle`.driver
							LEFT JOIN
								`tabTransport Assignment` ON `tabTransport Assignment`.name = (SELECT name FROM `tabTransport Assignment` WHERE assigned_vehicle = `tabVehicle`.name \
									AND status = 'Not Processed' ORDER BY expected_loading_date ASC LIMIT 1)
							''', as_dict=1)
	for row in data:
		if row.next_assigned_parenttype and row.next_assigned_parent:
			next_assigned = None
			if row.next_assigned_parenttype == 'Import':
				next_assigned = frappe.get_doc('Import', row.next_assigned_parent).customer
			elif row.next_assigned_parenttype == 'Transport Request':
				next_assigned = frappe.get_doc('Transport Request', row.next_assigned_parent).customer
			row.update({"next_cargo_allocation": next_assigned})
				
	return columns, data
	
def get_trip_info(data):
	if data:
		for vehicle in data:
			main_trip = frappe.db.get_value('Vehcile Trip', {"vehicle": vehicle.name, "status": "En Route"})
			return_trip = frappe.db.get_value('Vehcile Trip', {"vehicle": vehicle.name, "status": "En Route - Returning"})
			main_offloaded = frappe.db.sql('''SELECT parent FROM `tabRoute Steps Table` WHERE parenttype = 'Vehicle Trip' AND parentfield = 'main_route_steps' AND offloading_date IN (%(today)s, %(yesterday)s, %(day_before)s) LIMIT 1''', {'today': today, 'yesterday': yesterday, 'day_before': day_before})
			return_offloaded = frappe.db.sql('''SELECT parent FROM `tabRoute Steps Table` WHERE parenttype = 'Vehicle Trip' AND parentfield = 'return_route_steps' AND offloading_date IN (%(today)s, %(yesterday)s, %(day_before)s) LIMIT 1''', {'today': today, 'yesterday': yesterday, 'day_before': day_before})
