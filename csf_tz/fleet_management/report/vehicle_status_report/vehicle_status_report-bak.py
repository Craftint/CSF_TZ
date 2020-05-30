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
								CONCAT(`tabVehicle`.number_plate, '/', `tabTrailer`.number_plate) AS reg_no,
								`tabEmployee`.employee_name AS driver_name,
								`tabEmployee`.cell_number AS contact,
								CASE
									WHEN main_trip.name IS NOT NULL THEN main_trip.main_goods_description
									WHEN return_trip.name IS NOT NULL THEN return_trip.return_goods_description
									WHEN main_trip_offloaded.name IS NOT NULL THEN main_trip_offloaded.main_goods_description
									WHEN return_trip_offloaded.name IS NOT NULL THEN return_trip_offloaded.return_goods_description
								END AS cargo_type,
								CASE
									WHEN main_trip.name IS NOT NULL THEN main_trip.main_cargo_destination_city
									WHEN return_trip.name IS NOT NULL THEN return_trip.return_cargo_destination_city
									WHEN main_trip_offloaded.name IS NOT NULL THEN main_trip_offloaded.main_cargo_destination_city
									WHEN return_trip_offloaded.name IS NOT NULL THEN return_trip_offloaded.return_cargo_destination_city
								END AS destination,
								CASE
									WHEN main_trip.name IS NOT NULL THEN main_trip.main_customer
									WHEN return_trip.name IS NOT NULL THEN return_trip.return_customer
									WHEN main_trip_offloaded.name IS NOT NULL THEN main_trip_offloaded.main_customer
									WHEN return_trip_offloaded.name IS NOT NULL THEN return_trip_offloaded.return_customer
								END AS client,
								CASE
									WHEN UPPER(main_trip.main_cargo_location_country) = 'TANZANIA' AND UPPER(main_trip.main_cargo_destination_country) <> 'TANZANIA' THEN 'Import'
									WHEN UPPER(return_trip.return_cargo_location_country) = 'TANZANIA' AND UPPER(return_trip.return_cargo_destination_country) <> 'TANZANIA' THEN 'Import'
									WHEN UPPER(main_trip.main_cargo_location_country) <> 'TANZANIA' AND UPPER(main_trip.main_cargo_destination_country) = 'TANZANIA' THEN 'Export'
									WHEN UPPER(return_trip.return_cargo_location_country) <> 'TANZANIA' AND UPPER(return_trip.return_cargo_destination_country) = 'TANZANIA' THEN 'Export'
									WHEN UPPER(main_trip_offloaded.main_cargo_location_country) = 'TANZANIA' AND UPPER(main_trip_offloaded.main_cargo_destination_country) <> 'TANZANIA' THEN 'Import'
									WHEN UPPER(return_trip_offloaded.return_cargo_location_country) = 'TANZANIA' AND UPPER(return_trip_offloaded.return_cargo_destination_country) <> 'TANZANIA' THEN 'Import'
									WHEN UPPER(main_trip_offloaded.main_cargo_location_country) <> 'TANZANIA' AND UPPER(main_trip_offloaded.main_cargo_destination_country) = 'TANZANIA' THEN 'Export'
									WHEN UPPER(return_trip_offloaded.return_cargo_location_country) <> 'TANZANIA' AND UPPER(return_trip_offloaded.return_cargo_destination_country) = 'TANZANIA' THEN 'Export'
								END AS route,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT loading_date FROM `tabRoute Steps Table` WHERE parent = main_trip.name \
										AND parentfield = 'main_route_steps' AND loading_date IS NOT NULL LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT loading_date FROM `tabRoute Steps Table` WHERE parent = return_trip.name \
										AND parentfield = 'return_route_steps' AND loading_date IS NOT NULL LIMIT 1)
									WHEN main_trip_offloaded.name IS NOT NULL THEN (SELECT loading_date FROM `tabRoute Steps Table` WHERE parent = main_trip_offloaded.name \
										AND parentfield = 'main_route_steps' AND loading_date IS NOT NULL LIMIT 1)
									WHEN return_trip_offloaded.name IS NOT NULL THEN (SELECT loading_date FROM `tabRoute Steps Table` WHERE parent = return_trip_offloaded.name \
										AND parentfield = 'return_route_steps' AND loading_date IS NOT NULL LIMIT 1)
								END AS dispatch_date,
								CASE
									WHEN main_trip.name IS NOT NULL AND return_trip.name IS NOT NULL THEN NULL
									WHEN main_trip_offloaded.name IS NOT NULL THEN (SELECT offloading_date FROM `tabRoute Steps Table` WHERE parent = main_trip_offloaded.name \
										AND parentfield = 'main_route_steps' AND offloading_date IS NOT NULL LIMIT 1)
									WHEN return_trip_offloaded.name IS NOT NULL THEN (SELECT offloading_date FROM `tabRoute Steps Table` WHERE parent = return_trip_offloaded.name \
										AND parentfield = 'return_route_steps' AND offloading_date IS NOT NULL LIMIT 1)
								END AS offloading_date,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE \
										`tabReporting Status Table`.parenttype = 'Vehicle Trip' AND `tabReporting Status Table`.parent = main_trip.name AND \
										`tabReporting Status Table`.parentfield = 'main_reporting_status' ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE \
										`tabReporting Status Table`.parenttype = 'Vehicle Trip' AND `tabReporting Status Table`.parent = return_trip.name AND \
										`tabReporting Status Table`.parentfield = 'return_reporting_status' ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1)
									WHEN main_trip_offloaded.name IS NOT NULL THEN (SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE \
										`tabReporting Status Table`.parenttype = 'Vehicle Trip' AND `tabReporting Status Table`.parent = main_trip_offloaded.name AND \
										`tabReporting Status Table`.parentfield = 'main_reporting_status' ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1)
									WHEN return_trip_offloaded.name IS NOT NULL THEN (SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE \
										`tabReporting Status Table`.parenttype = 'Vehicle Trip' AND `tabReporting Status Table`.parent = return_trip_offloaded.name AND \
										`tabReporting Status Table`.parentfield = 'return_reporting_status' ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1)
								END AS position,
								`tabTransport Assignment`.parenttype AS next_assigned_parenttype,
								`tabTransport Assignment`.parent AS next_assigned_parent
							FROM
								`tabVehicle`
							LEFT JOIN
								`tabTrailer` ON `tabTrailer`.name = `tabVehicle`.default_trailer
							LEFT JOIN
								`tabEmployee` ON `tabEmployee`.name = `tabVehicle`.driver
							LEFT JOIN
								`tabVehicle Trip` AS main_trip ON main_trip.vehicle = `tabVehicle`.name AND main_trip.status = 'En Route'
							LEFT JOIN
								`tabVehicle Trip` AS return_trip ON return_trip.vehicle = `tabVehicle`.name AND return_trip.status = 'En Route - Returning'
							LEFT JOIN
								`tabVehicle Trip` AS main_trip_offloaded ON main_trip_offloaded.vehicle = `tabVehicle`.name AND main_trip_offloaded.status = 'Main Trip Offloaded' AND (SELECT loading_date FROM `tabRoute Steps Table` WHERE \
									parent = main_trip_offloaded.name AND parentfield = 'main_route_steps' AND offloading_date IS NOT NULL LIMIT 1) IN (%(today)s, %(yesterday)s, %(day_before)s)
							LEFT JOIN
								`tabVehicle Trip` AS return_trip_offloaded ON return_trip_offloaded.vehicle = `tabVehicle`.name AND return_trip_offloaded.status = 'Main Trip Offloaded' AND (SELECT loading_date FROM `tabRoute Steps Table` WHERE \
									parent = return_trip_offloaded.name AND parentfield = 'return_route_steps' AND offloading_date IS NOT NULL LIMIT 1) IN (%(today)s, %(yesterday)s, %(day_before)s)
							LEFT JOIN
								`tabTransport Assignment` ON `tabTransport Assignment`.name = (SELECT name FROM `tabTransport Assignment` WHERE assigned_vehicle = `tabVehicle`.name \
									AND status = 'Not Processed' ORDER BY expected_loading_date ASC LIMIT 1)
							LEFT JOIN
								`tabTransport Request` ON `tabTransport Request`.name = `tabTransport Assignment`.parent AND `tabTransport Assignment`.parenttype = 'Transport Request'
							''', {'today': today, 'yesterday': yesterday, 'day_before': day_before}, as_dict=1)
	for row in data:
		if row.next_assigned_parenttype and row.next_assigned_parent:
			next_assigned = None
			if row.next_assigned_parenttype == 'Import':
				next_assigned = frappe.get_doc('Import', row.next_assigned_parent).customer
			elif row.next_assigned_parenttype == 'Transport Request':
				next_assigned = frappe.get_doc('Transport Request', row.next_assigned_parent).customer
			row.update({"next_cargo_allocation": next_assigned})
				
	return columns, data
