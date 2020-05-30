# Copyright (c) 2013, Bravo Logistics and contributors
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
			"fieldname": "trip_no",
			"label": _("Trip No"),
			"fieldtype": "Link",
			"options": "Vehicle Trip",
			"width": 100
		},
		{
			"fieldname": "tcustomer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 100
		},
		{
			"fieldname": "fleet_no",
			"label": _("Fleet No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "truck_no",
			"label": _("Truck No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "trailer_no",
			"label": _("Trailer No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "driver",
			"label": _("Driver"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "contact_no",
			"label": _("Contact Number"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "passport_no",
			"label": _("Passport Number"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "driving_licence",
			"label": _("Driving Licence"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "cargo_description",
			"label": _("Cargo Description"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "quantity",
			"label": _("Quantity"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "loading_date",
			"label": _("Loading Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "departure_date",
			"label": _("Departure Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "eta_border",
			"label": _("ETA Border"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "ata_border",
			"label": _("ATA Border"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "departure_border",
			"label": _("Departure Border"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "days_at_border",
			"label": _("Days at Border"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "offloading_date",
			"label": _("Offloading Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "trip_days",
			"label": _("Trip Days"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "current_position",
			"label": _("Current Position"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Data",
			"width": 200
		}
	]
	
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
	
	having = ''
	if filters.customer:
		having = 'HAVING tcustomer = %(customer)s'
	
	data = frappe.db.sql('''SELECT
								CASE
									WHEN main_trip.name IS NOT NULL THEN main_trip.name
									WHEN return_trip.name IS NOT NULL THEN return_trip.name
								END AS trip_no,
								CASE
									WHEN transport_request.name IS NOT NULL THEN transport_request.customer
									WHEN import_request.name IS NOT NULL THEN import_request.customer
								END AS tcustomer,
								`tabVehicle`.fleet_number AS fleet_no,
								`tabTransport Assignment`.vehicle_plate_number AS truck_no,
								`tabTransport Assignment`.trailer_plate_number AS trailer_no,
								`tabTransport Assignment`.driver_name AS driver,
								`tabTransport Assignment`.passport_number AS passport_no,
								CASE
									WHEN transport_request.name IS NOT NULL THEN transport_request.cargo_description
									WHEN import_request.name IS NOT NULL THEN import_request.cargo_description
								END AS cargo_description,
								CASE
									WHEN transport_request.name IS NOT NULL AND transport_request.cargo_type = 'Container' AND \
										`tabCargo Details`.net_weight IS NOT NULL AND `tabCargo Details`.net_weight > 0 \
										THEN (`tabCargo Details`.net_weight /1000) \
									WHEN transport_request.name IS NOT NULL AND transport_request.cargo_type = 'Loose Cargo' AND transport_request.unit = 'TONNES'
										THEN `tabTransport Assignment`.amount
									WHEN import_request.name IS NOT NULL AND import_request.cargo_type = 'Container' AND \
										`tabCargo Details`.net_weight IS NOT NULL AND `tabCargo Details`.net_weight > 0 \
										THEN (`tabCargo Details`.net_weight/1000) \
									WHEN import_request.name IS NOT NULL AND import_request.cargo_type = 'Loose Cargo' AND import_request.unit = 'TONNES'
										THEN `tabTransport Assignment`.amount
								END AS quantity,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT loading_date FROM `tabRoute Steps Table` WHERE parent = main_trip.name \
										AND parentfield = 'main_route_steps' AND loading_date IS NOT NULL LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT loading_date FROM `tabRoute Steps Table` WHERE parent = return_trip.name \
										AND parentfield = 'return_route_steps' AND loading_date IS NOT NULL LIMIT 1)
								END AS loading_date,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT departure_date FROM `tabRoute Steps Table` WHERE parent = main_trip.name \
										AND parentfield = 'main_route_steps' AND departure_date IS NOT NULL LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT departure_date FROM `tabRoute Steps Table` WHERE parent = return_trip.name \
										AND parentfield = 'return_route_steps' AND departure_date IS NOT NULL LIMIT 1)
								END AS departure_date,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT arrival_date FROM `tabRoute Steps Table` WHERE parent = main_trip.name \
										AND parentfield = 'main_route_steps' AND location_type = 'BORDER' ORDER BY arrival_date ASC LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT arrival_date FROM `tabRoute Steps Table` WHERE parent = return_trip.name \
										AND parentfield = 'return_route_steps' AND location_type = 'BORDER' ORDER BY arrival_date ASC LIMIT 1)
								END AS ata_border,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT departure_date FROM `tabRoute Steps Table` WHERE parent = main_trip.name \
										AND parentfield = 'main_route_steps' AND location_type = 'BORDER' ORDER BY departure_date ASC LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT departure_date FROM `tabRoute Steps Table` WHERE parent = return_trip.name \
										AND parentfield = 'return_route_steps' AND location_type = 'BORDER' ORDER BY departure_date ASC LIMIT 1)
								END AS departure_border,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT offloading_date FROM `tabRoute Steps Table` WHERE parent = main_trip.name \
										AND parentfield = 'main_route_steps' AND offloading_date IS NOT NULL LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT offloading_date FROM `tabRoute Steps Table` WHERE parent = return_trip.name \
										AND parentfield = 'return_route_steps' AND offloading_date IS NOT NULL LIMIT 1)
								END AS offloading_date,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT `tabVehicle Trip Location Update`.location FROM `tabVehicle Trip Location Update` WHERE \
										parent = main_trip.name AND parenttype = 'Vehicle Trip' AND parentfield = 'main_location_update' ORDER BY \
										`tabVehicle Trip Location Update`.timestamp LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT `tabVehicle Trip Location Update`.location FROM `tabVehicle Trip Location Update` WHERE \
										parent = return_trip.name AND parenttype = 'Vehicle Trip' AND parentfield = 'return_location_update' ORDER BY \
										`tabVehicle Trip Location Update`.timestamp LIMIT 1)
								END AS current_position,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE \
										`tabReporting Status Table`.parenttype = 'Vehicle Trip' AND `tabReporting Status Table`.parent = main_trip.name AND \
										`tabReporting Status Table`.parentfield = 'main_reporting_status' ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE \
										`tabReporting Status Table`.parenttype = 'Vehicle Trip' AND `tabReporting Status Table`.parent = return_trip.name AND \
										`tabReporting Status Table`.parentfield = 'return_reporting_status' ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1)
								END AS remarks
							FROM
								`tabTransport Assignment`
							LEFT JOIN
								`tabVehicle Trip` AS main_trip ON main_trip.reference_docname = `tabTransport Assignment`.name
							LEFT JOIN
								`tabVehicle Trip` AS return_trip ON return_trip.return_reference_docname = `tabTransport Assignment`.name
							LEFT JOIN
								`tabTransport Request` AS transport_request ON transport_request.name = `tabTransport Assignment`.parent AND \
								`tabTransport Assignment`.parenttype = 'Transport Request'
							LEFT JOIN
								`tabTransport Request` AS import_request ON import_request.reference_docname = `tabTransport Assignment`.parent AND \
								`tabTransport Assignment`.parenttype = 'Import' AND import_request.file_number IS NOT NULL
							LEFT JOIN
								`tabVehicle` ON `tabVehicle`.name = `tabTransport Assignment`.assigned_vehicle AND `tabTransport Assignment`.transporter_type = 'Bravo'
							LEFT JOIN
								`tabCargo Details` ON `tabCargo Details`.container_number = `tabTransport Assignment`.container_number AND \
								`tabCargo Details`.parent = `tabTransport Assignment`.parent
							WHERE
								`tabTransport Assignment`.expected_loading_date BETWEEN %(from_date)s AND %(to_date)s ''' + having
						, {"from_date": filters.from_date, "to_date": filters.to_date, "customer": filters.customer}, as_dict=1)
						
	for row in data:
		if row.ata_border and row.departure_border:
			row.update({"days_at_border": (row.ata_border-row.departure_border).days})
		
		if row.loading_date and row.offloading_date:
			row.update({"trip_days": (row.offloading_date-row.loading_date).days})
	
	return columns, data
