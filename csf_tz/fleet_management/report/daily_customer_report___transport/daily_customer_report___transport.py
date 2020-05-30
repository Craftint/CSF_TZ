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
			"fieldname": "file_number",
			"label": _("File No"),
			"fieldtype": "Link",
			"options": "Vehicle Trip",
			"width": 100
		},
		{
			"fieldname": "client",
			"label": _("Client"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname": "order_date",
			"label": _("Order Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "transporter_name",
			"label": _("Transporter Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "fleet_number",
			"label": _("Fleet Number"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "vehicle_plate_number",
			"label": _("Truck"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "trailer_plate_number",
			"label": _("Trailer"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "loading_capacity",
			"label": _("Loading Capacity"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "cargo_type",
			"label": _("Cargo Type"),
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
			"fieldname": "cargo_reference",
			"label": _("Cargo Ref"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "weight",
			"label": _("Weight"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "driver_name",
			"label": _("Driver Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "passport_number",
			"label": _("Passport Number"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "drivers_licence",
			"label": _("Drivers Licence"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "contact_no",
			"label": _("Contact Number"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "loading_point_arrival_date",
			"label": _("Loading Point Arrival date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "loading_date",
			"label": _("Loading Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "loading_point_dispatch_date",
			"label": _("Loading Point Dispatch date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "border_arrival_date",
			"label": _("Border Arrival date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "border_dispatch_date",
			"label": _("Border Dispatch Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "destination_arrival_date",
			"label": _("Destination Arrival Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "offloading_date",
			"label": _("Offloading Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "offloading_weight",
			"label": _("Offloaded Weight"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "offloading_ref",
			"label": _("Offloading Ref"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "vehicle_position",
			"label": _("Vehicle Position"),
			"fieldtype": "data",
			"width": 150
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "data",
			"width": 150
		}
	]
	
	today = datetime.date.today().strftime("%Y-%m-%d")
	yesterday =  datetime.date.today() - datetime.timedelta(1)
	day_before = datetime.date.today() - datetime.timedelta(2)
	yesterday = yesterday.strftime("%Y-%m-%d")
	day_before = day_before.strftime("%Y-%m-%d")
	
	main_where = ''
	return_where = ''
	where_filter = {'today': today, 'yesterday': yesterday, 'day_before': day_before}
	if filters.customer:
		#For main trip
		main_where = ' AND `tabVehicle Trip`.main_customer = %(customer)s'
		where_filter.update({'customer': filters.customer})
		#For return trip
		return_where = ' AND `tabVehicle Trip`.return_customer = %(customer)s'
		
	
	data_main = frappe.db.sql('''SELECT
					`tabVehicle Trip`.name AS file_number,
					`tabVehicle Trip`.main_customer AS client,
					`tabTransport Request`.request_received AS order_date,
					CASE
						WHEN `tabVehicle Trip`.transporter_type = 'Bravo' THEN 'Bravo Logistics'
						WHEN `tabVehicle Trip`.transporter_type = 'Sub-Contractor' THEN `tabVehicle Trip`.sub_contractor
					END AS transporter_name,
					`tabVehicle Trip`.vehicle_plate_number,
					`tabVehicle Trip`.trailer_plate_number,
					CASE
						WHEN `tabVehicle Trip`.main_cargo_type = 'Loose Cargo' THEN 'Loose'
					ELSE
						`tabVehicle Trip`.main_cargo_type
					END AS cargo_type,
					`tabVehicle Trip`.main_goods_description AS cargo,
					CASE
						WHEN `tabVehicle Trip`.main_cargo_type = 'Loose Cargo' THEN 'Loose'
					ELSE
						(SELECT `tabCargo Details`.container_number FROM `tabCargo Details` WHERE parenttype = 'Vehicle Trip' \
							AND parent = `tabVehicle Trip`.name AND parentfield = 'main_cargo' LIMIT 1)
					END AS cargo_reference,
					CASE
						WHEN `tabVehicle Trip`.main_cargo_type = 'Container' THEN 
						(SELECT SUM(`tabCargo Details`.net_weight) FROM `tabCargo Details` WHERE `tabCargo Details`.parent = `tabVehicle Trip`.name \
						AND `tabCargo Details`.parenttype = 'Vehicle Trip' AND `tabCargo Details`.parentfield = 'main_cargo')
					ELSE `tabVehicle Trip`.main_loose_net_weight
					END AS weight,
					`tabVehicle Trip`.driver_name,
					`tabVehicle Trip`.passport_number,
					`tabVehicle Trip`.main_offloading_weight AS offloading_weight,
					(SELECT `tabVehicle Trip Location Update`.location FROM `tabVehicle Trip Location Update` WHERE parent = `tabVehicle Trip`.name
							AND parenttype = 'Vehicle Trip' AND parentfield = 'main_location_update' ORDER BY `tabVehicle Trip Location Update`.timestamp LIMIT 1) AS vehicle_position,
					(SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE `tabReporting Status Table`.parenttype = 'Vehicle Trip' \
						AND `tabReporting Status Table`.parent = `tabVehicle Trip`.name AND `tabReporting Status Table`.parentfield = 'main_reporting_status' \
						ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1) AS remarks
				FROM
					`tabVehicle Trip`
				LEFT JOIN
					`tabTransport Assignment` ON `tabVehicle Trip`.reference_docname = `tabTransport Assignment`.name
				LEFT JOIN
					`tabTransport Request` ON `tabTransport Request`.name = `tabTransport Assignment`.parent
				WHERE 
					`tabVehicle Trip`.reference_doctype IS NOT NULL AND `tabVehicle Trip`.reference_docname IS NOT NULL ''' + main_where +
				'''
					AND `tabVehicle Trip`.status = 'En Route' ''', where_filter, as_dict=1)
	
	data_return = frappe.db.sql(''' SELECT
					`tabVehicle Trip`.name AS file_number,
					`tabVehicle Trip`.return_customer AS client,
					`tabTransport Request`.request_received AS order_date,
					CASE
						WHEN `tabVehicle Trip`.transporter_type = 'Bravo' THEN 'Bravo Logistics'
						WHEN `tabVehicle Trip`.transporter_type = 'Sub-Contractor' THEN `tabVehicle Trip`.sub_contractor
					END AS transporter_name,
					`tabVehicle Trip`.vehicle_plate_number,
					`tabVehicle Trip`.trailer_plate_number,
					CASE
						WHEN `tabVehicle Trip`.return_cargo_type = 'Loose Cargo' THEN 'Loose'
					ELSE
						`tabVehicle Trip`.return_cargo_type
					END AS cargo_type,
					`tabVehicle Trip`.return_goods_description AS cargo,
					CASE
						WHEN `tabVehicle Trip`.main_cargo_type = 'Loose Cargo' THEN 'Loose'
					ELSE
						(SELECT `tabCargo Details`.container_number FROM `tabCargo Details` WHERE parenttype = 'Vehicle Trip' \
							AND parent = `tabVehicle Trip`.name AND parentfield = 'return_cargo' LIMIT 1)
					END AS cargo_reference,
					CASE
						WHEN `tabVehicle Trip`.return_cargo_type = 'Container' THEN 
						(SELECT SUM(`tabCargo Details`.net_weight) FROM `tabCargo Details` WHERE `tabCargo Details`.parent = `tabVehicle Trip`.name \
						AND `tabCargo Details`.parenttype = 'Vehicle Trip' AND `tabCargo Details`.parentfield = 'return_cargo')
					ELSE `tabVehicle Trip`.return_loose_net_weight
					END AS weight,
					`tabVehicle Trip`.driver_name,
					`tabVehicle Trip`.passport_number,
					`tabVehicle Trip`.return_offloading_weight AS offloading_weight,
					(SELECT `tabVehicle Trip Location Update`.location FROM `tabVehicle Trip Location Update` WHERE parent = `tabVehicle Trip`.name
							AND parenttype = 'Vehicle Trip' AND parentfield = 'return_location_update' ORDER BY `tabVehicle Trip Location Update`.timestamp LIMIT 1) AS vehicle_position,
					(SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE `tabReporting Status Table`.parenttype = 'Vehicle Trip' \
						AND `tabReporting Status Table`.parent = `tabVehicle Trip`.name AND `tabReporting Status Table`.parentfield = 'return_reporting_status' \
						ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1) AS remarks
				FROM
					`tabVehicle Trip`
				LEFT JOIN
					`tabTransport Assignment` ON `tabVehicle Trip`.reference_docname = `tabTransport Assignment`.name
				LEFT JOIN
					`tabTransport Request` ON `tabTransport Request`.name = `tabTransport Assignment`.parent
				WHERE 
					`tabVehicle Trip`.return_reference_doctype IS NOT NULL AND `tabVehicle Trip`.return_reference_docname IS NOT NULL '''
				+ return_where + '''
					AND `tabVehicle Trip`.status = 'En Route - Returning' ''', where_filter, as_dict=1)
	
	
	data_offloaded_main = frappe.db.sql('''SELECT
					`tabVehicle Trip`.name AS file_number,
					`tabVehicle Trip`.main_customer AS client,
					`tabTransport Request`.request_received AS order_date,
					CASE
						WHEN `tabVehicle Trip`.transporter_type = 'Bravo' THEN 'Bravo Logistics'
						WHEN `tabVehicle Trip`.transporter_type = 'Sub-Contractor' THEN `tabVehicle Trip`.sub_contractor
					END AS transporter_name,
					`tabVehicle Trip`.vehicle_plate_number,
					`tabVehicle Trip`.trailer_plate_number,
					CASE
						WHEN `tabVehicle Trip`.main_cargo_type = 'Loose Cargo' THEN 'Loose'
					ELSE
						`tabVehicle Trip`.main_cargo_type
					END AS cargo_type,
					`tabVehicle Trip`.main_goods_description AS cargo,
					CASE
						WHEN `tabVehicle Trip`.main_cargo_type = 'Loose Cargo' THEN 'Loose'
					ELSE
						(SELECT `tabCargo Details`.container_number FROM `tabCargo Details` WHERE parenttype = 'Vehicle Trip' \
							AND parent = `tabVehicle Trip`.name AND parentfield = 'main_cargo' LIMIT 1)
					END AS cargo_reference,
					CASE
						WHEN `tabVehicle Trip`.main_cargo_type = 'Container' THEN 
						(SELECT SUM(`tabCargo Details`.net_weight) FROM `tabCargo Details` WHERE `tabCargo Details`.parent = `tabVehicle Trip`.name \
						AND `tabCargo Details`.parenttype = 'Vehicle Trip' AND `tabCargo Details`.parentfield = 'main_cargo')
					ELSE `tabVehicle Trip`.main_loose_net_weight
					END AS weight,
					`tabVehicle Trip`.driver_name,
					`tabVehicle Trip`.passport_number,
					`tabVehicle Trip`.main_offloading_weight AS offloading_weight,
					(SELECT `tabVehicle Trip Location Update`.location FROM `tabVehicle Trip Location Update` WHERE parent = `tabVehicle Trip`.name
							AND parenttype = 'Vehicle Trip' AND parentfield = 'main_location_update' ORDER BY `tabVehicle Trip Location Update`.timestamp LIMIT 1) AS vehicle_position,
					(SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE `tabReporting Status Table`.parenttype = 'Vehicle Trip' \
						AND `tabReporting Status Table`.parent = `tabVehicle Trip`.name AND `tabReporting Status Table`.parentfield = 'main_reporting_status' \
						ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1) AS remarks
				FROM
					`tabVehicle Trip`
				LEFT JOIN
					`tabTransport Assignment` ON `tabVehicle Trip`.reference_docname = `tabTransport Assignment`.name
				LEFT JOIN
					`tabTransport Request` ON `tabTransport Request`.name = `tabTransport Assignment`.parent
				WHERE 
					`tabVehicle Trip`.name IN (SELECT parent FROM `tabRoute Steps Table` WHERE parenttype = 'Vehicle Trip' AND parentfield = 'main_route_steps' AND offloading_date IN (%(today)s, %(yesterday)s, %(day_before)s)) ''' + main_where +
				'''
					AND `tabVehicle Trip`.status = 'En Route' ''', where_filter, as_dict=1)
	
					
	data_offloaded_return = frappe.db.sql(''' SELECT
					`tabVehicle Trip`.name AS file_number,
					`tabVehicle Trip`.return_customer AS client,
					`tabTransport Request`.request_received AS order_date,
					CASE
						WHEN `tabVehicle Trip`.transporter_type = 'Bravo' THEN 'Bravo Logistics'
						WHEN `tabVehicle Trip`.transporter_type = 'Sub-Contractor' THEN `tabVehicle Trip`.sub_contractor
					END AS transporter_name,
					`tabVehicle Trip`.vehicle_plate_number,
					`tabVehicle Trip`.trailer_plate_number,
					CASE
						WHEN `tabVehicle Trip`.return_cargo_type = 'Loose Cargo' THEN 'Loose'
					ELSE
						`tabVehicle Trip`.return_cargo_type
					END AS cargo_type,
					`tabVehicle Trip`.return_goods_description AS cargo,
					CASE
						WHEN `tabVehicle Trip`.main_cargo_type = 'Loose Cargo' THEN 'Loose'
					ELSE
						(SELECT `tabCargo Details`.container_number FROM `tabCargo Details` WHERE parenttype = 'Vehicle Trip' \
							AND parent = `tabVehicle Trip`.name AND parentfield = 'return_cargo' LIMIT 1)
					END AS cargo_reference,
					CASE
						WHEN `tabVehicle Trip`.return_cargo_type = 'Container' THEN 
						(SELECT SUM(`tabCargo Details`.net_weight) FROM `tabCargo Details` WHERE `tabCargo Details`.parent = `tabVehicle Trip`.name \
						AND `tabCargo Details`.parenttype = 'Vehicle Trip' AND `tabCargo Details`.parentfield = 'return_cargo')
					ELSE `tabVehicle Trip`.return_loose_net_weight
					END AS weight,
					`tabVehicle Trip`.driver_name,
					`tabVehicle Trip`.passport_number,
					`tabVehicle Trip`.return_offloading_weight AS offloading_weight,
					(SELECT `tabVehicle Trip Location Update`.location FROM `tabVehicle Trip Location Update` WHERE parent = `tabVehicle Trip`.name
							AND parenttype = 'Vehicle Trip' AND parentfield = 'return_location_update' ORDER BY `tabVehicle Trip Location Update`.timestamp LIMIT 1) AS vehicle_position,
					(SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE `tabReporting Status Table`.parenttype = 'Vehicle Trip' \
						AND `tabReporting Status Table`.parent = `tabVehicle Trip`.name AND `tabReporting Status Table`.parentfield = 'return_reporting_status' \
						ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1) AS remarks
				FROM
					`tabVehicle Trip`
				LEFT JOIN
					`tabTransport Assignment` ON `tabVehicle Trip`.reference_docname = `tabTransport Assignment`.name
				LEFT JOIN
					`tabTransport Request` ON `tabTransport Request`.name = `tabTransport Assignment`.parent
				WHERE 
					`tabVehicle Trip`.name IN (SELECT parent FROM `tabRoute Steps Table` WHERE parenttype = 'Vehicle Trip' AND parentfield = 'return_route_steps' AND offloading_date IN (%(today)s, %(yesterday)s, %(day_before)s)) '''
				+ return_where + '''
					AND `tabVehicle Trip`.status = 'En Route - Returning' ''', where_filter, as_dict=1)
	
	data_main = get_trip_data(data_main)				
	data_return = get_trip_data(data_return, True)
	data_offloaded_main = get_trip_data(data_offloaded_main)
	data_offloaded_return = get_trip_data(data_offloaded_return, True)
					
	data = data_main + data_return + data_offloaded_main + data_offloaded_return
	
	data = sorted(data, key=lambda k: k['file_number']) 
	
	return columns, data
	
def get_trip_data(trip_data, return_trip=False):
	if trip_data:
		for d in trip_data:
			trip = frappe.get_doc('Vehicle Trip', d.file_number)
			route_steps = []
			if return_trip:
				route_steps = trip.return_route_steps
			else:
				route_steps = trip.main_route_steps
				
			for step in route_steps:
				loading_point, border, offloading_point = False, False, False
				if step.location_type and step.location_type.upper() == 'LOADING POINT' and not loading_point:
					d['loading_point_arrival_date'] = step.get("arrival_date")
					d['loading_date'] = step.get("loading_date")
					d['loading_point_dispatch_date'] = step.get("departure_date")
					loading_point = True
				elif step.location_type and step.location_type.upper() == 'BORDER' and not border:
					d['border_arrival_date'] = step.get("arrival_date")
					d['border_dispatch_date'] = step.get("departure_date")
					border = True
				elif step.location_type and step.location_type.upper() == 'OFFLOADING POINT' and not offloading_point:
					d['offloading_date'] = step.get('offloading_date')
					d['destination_arrival_date'] = step.get('arrival_date')
					offloading_point = True
					
					
	return trip_data
