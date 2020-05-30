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
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname": "vehicle",
			"label": _("Vehicle/Trailer"),
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
			"fieldname": "border_name",
			"label": _("Border Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "eta_at_border",
			"label": _("ETA at Border"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "dispatch_date",
			"label": _("Dispatch Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "last_reported_position",
			"label": _("Last Reported Position"),
			"fieldtype": "Data",
			"width": 450
		}
	]
	
	
	where = ""
	if filters.border:
		where = " HAVING border_name = %(border)s "
	
	data = frappe.db.sql('''SELECT
								CASE
									WHEN main_trip.name IS NOT NULL THEN main_trip.name
									WHEN return_trip.name IS NOT NULL THEN return_trip.name
								END AS trip_no,
								CASE
									WHEN main_trip.name IS NOT NULL THEN main_trip.main_customer
									WHEN return_trip.name IS NOT NULL THEN return_trip.return_customer
								END AS customer,
								CASE
									WHEN main_trip.name IS NOT NULL THEN CONCAT(main_trip.vehicle_plate_number, '/', main_trip.trailer_plate_number)
									WHEN return_trip.name IS NOT NULL THEN CONCAT(return_trip.vehicle_plate_number, '/', return_trip.trailer_plate_number)
								END AS vehicle,
								CASE
									WHEN main_trip.name IS NOT NULL THEN main_trip.main_goods_description
									WHEN return_trip.name IS NOT NULL THEN return_trip.return_goods_description
								END AS cargo,
								`tabRoute Steps Table`.location AS border_name,
								CASE
									WHEN main_trip.name IS NOT NULL THEN main_trip.main_route
									WHEN return_trip.name IS NOT NULL THEN return_trip.return_route
								END AS route,
								CASE
									WHEN main_loading_point.name IS NOT NULL THEN main_loading_point.departure_date 
									WHEN return_loading_point.name IS NOT NULL THEN return_loading_point.departure_date
								END AS dispatch_date,
								CASE
									WHEN main_trip.name IS NOT NULL THEN (SELECT CONCAT(date_format(timestamp, '%%d-%%m-%%Y %%l:%%i'), ' - ', `tabVehicle Trip Location Update`.location) \
										FROM `tabVehicle Trip Location Update` WHERE \
										`tabVehicle Trip Location Update`.parenttype = 'Vehicle Trip' AND `tabVehicle Trip Location Update`.parent = main_trip.name AND \
										`tabVehicle Trip Location Update`.parentfield = 'main_location_update' ORDER BY `tabVehicle Trip Location Update`.timestamp DESC LIMIT 1)
									WHEN return_trip.name IS NOT NULL THEN (SELECT CONCAT(date_format(timestamp, '%%d-%%m-%%Y %%l:%%i'), ' - ', `tabVehicle Trip Location Update`.location) \
										FROM `tabVehicle Trip Location Update` WHERE \
										`tabVehicle Trip Location Update`.parenttype = 'Vehicle Trip' AND `tabVehicle Trip Location Update`.parent = return_trip.name AND \
										`tabVehicle Trip Location Update`.parentfield = 'return_location_update' ORDER BY `tabVehicle Trip Location Update`.timestamp DESC LIMIT 1)
								END AS last_reported_position
							FROM
								`tabRoute Steps Table`
							LEFT JOIN
								`tabVehicle Trip` AS main_trip ON main_trip.name = `tabRoute Steps Table`.parent AND `tabRoute Steps Table`.parenttype = 'Vehicle Trip'
									AND `tabRoute Steps Table`.parentfield = 'main_route_steps'
							LEFT JOIN
								`tabVehicle Trip` AS return_trip ON return_trip.name = `tabRoute Steps Table`.parent AND `tabRoute Steps Table`.parenttype = 'Vehicle Trip'
									AND `tabRoute Steps Table`.parentfield = 'return_route_steps'
							LEFT JOIN
								`tabRoute Steps Table` AS main_loading_point ON main_loading_point.name = (SELECT name FROM `tabRoute Steps Table` WHERE \
									parent = main_trip.name AND main_loading_point.parentfield = 'main_route_steps' AND upper(main_loading_point.location_type) = 'LOADING POINT'
									ORDER BY idx ASC LIMIT 1)
							LEFT JOIN
								`tabRoute Steps Table` AS return_loading_point ON return_loading_point.name = (SELECT name FROM `tabRoute Steps Table` WHERE \
									parent = return_trip.name AND return_loading_point.parentfield = 'return_route_steps' AND upper(return_loading_point.location_type) = 'LOADING POINT'
									ORDER BY idx ASC LIMIT 1)
							WHERE
								upper(`tabRoute Steps Table`.location_type) = 'BORDER' AND `tabRoute Steps Table`.arrival_date IS NULL AND \
								(main_trip.status = 'En Route' OR return_trip.status = 'En Route - Returning')
							''' + where +
							'''
							ORDER BY
								dispatch_date ASC
							''', {"border": filters.border}, as_dict=1)
							
	for row in data:
		if row.route:
			route = frappe.get_doc('Trip Route', row.route)
			for location in route.trip_steps:
				if location.location == row.border_name:
					if location.distance and location.distance != 0:
						days_to_add = location.distance/340
						if row.dispatch_date:
							row.update({"eta_at_border": row.dispatch_date + datetime.timedelta(days=days_to_add)})
	
	return columns, data
