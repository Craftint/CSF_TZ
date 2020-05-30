# Copyright (c) 2013, Bravo Logisitcs and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import flt, getdate, cstr
from frappe import _
import ast
import datetime
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
			"fieldname": "file_number",
			"label": _("File No"),
			"fieldtype": "Link",
			"options": "Border Clearance",
			"width": 100
		},
		{
			"fieldname": "client",
			"label": _("Client"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 100
		},
		{
			"fieldname": "consignee",
			"label": _("Consignee"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "crn_reference_number",
			"label": _("CRN Reference No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "documents_received",
			"label": _("Documents Received"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "transporter",
			"label": _("Transporter"),
			"fieldtype": "Data",
			"width": 100
		},		
		{
			"fieldname": "trip_number",
			"label": _("Trip Number"),
			"fieldtype": "Link",
			"options": "Vehicle Trip",
			"width": 100
		},		
		{
			"fieldname": "vehicle_reg",
			"label": _("Vehicle Reg"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "trailer_reg",
			"label": _("Trailer Reg"),
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
			"fieldname": "cargo",
			"label": _("Cargo"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "container_size",
			"label": _("Container Size"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "weight",
			"label": _("Weight (kg)"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "bond_reference",
			"label": _("Bond Reference"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "cargo_origin",
			"label": _("Cargo Origin"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "cargo_destination",
			"label": _("Cargo Destination"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "border1_name",
			"label": _("Border 1 Name"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "border1_arrival",
			"label": _("Border 1 Arrival"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "border1_departure",
			"label": _("Border 1 Departure"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "border1_crossing",
			"label": _("Border 1 Crossing"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "border2_name",
			"label": _("Border 2 Name"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "border2_arrival",
			"label": _("Border 2 Arrival"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "border2_departure",
			"label": _("Border 2 Departure"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "border2_crossing",
			"label": _("Border 2 Crossing"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "arrival_offloading_point",
			"label": _("Arrival Offloading Point"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "offloading_datetime",
			"label": _("Offloading Date and Time"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Data",
			"width": 100
		}
	]
	
	where = ''
	where_filter = {}
	
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
	else:
		where = " WHERE `tabBorder Clearance`.documents_received >= %(from_date)s AND `tabBorder Clearance`.documents_received <= %(to_date)s"
		where_filter.update({"from_date": filters.from_date, "to_date": filters.to_date})
		
	if filters.client:
		where += 'AND `tabBorder Clearance`.client = %(client)s'
		where_filter.update({"client": filters.client})
		
	if filters.type and filters.type == 'Import':
		where += "AND `tabBorder Clearance`.clearance_type = 'Exit'"
	elif filters.type and filters.type == 'Export':
		where += "AND `tabBorder Clearance`.clearance_type = 'Entry'"
		
	
	data = frappe.db.sql('''
		SELECT
			`tabBorder Clearance`.name AS file_number,
			`tabBorder Clearance`.client AS client,
			`tabBorder Clearance`.consignee,
			CASE
				WHEN `tabBorder Clearance`.clearance_type = 'Entry' THEN 'Export'
				WHEN `tabBorder Clearance`.clearance_type = 'Exit' THEN 'Import'
				WHEN `tabBorder Clearance`.clearance_type = 'Pass Through' THEN 'Pass Through'
			END AS type,
			`tabBorder Clearance`.crn_reference_number,
			`tabBorder Clearance`.documents_received AS documents_received,
			CASE
				WHEN `tabBorder Clearance`.transporter_type = 'Bravo' THEN 'Bravo'
				ELSE `tabBorder Clearance`.transporter_name
			END AS transporter,
			`tabBorder Clearance`.trip_reference_no AS trip_number,
			`tabBorder Clearance`.vehicle_plate_number AS vehicle_reg,
			`tabBorder Clearance`.trailer_plate_number AS trailer_reg,
			`tabBorder Clearance`.driver_name AS driver_name,
			`tabBorder Clearance`.cargo_category AS cargo,
			CASE
				WHEN `tabBorder Clearance`.cargo_type = 'Container' AND `tabCargo Details`.container_size IN ('40 FT GP', '40 OT', '40RF', '40 FT Heavy') THEN '40'
				WHEN `tabBorder Clearance`.cargo_type = 'Container' AND `tabCargo Details`.container_size IN ('20 FT GP', '20 OT', '20RF') THEN '20'
				WHEN `tabBorder Clearance`.cargo_type = 'Loose Cargo' THEN 'Loose Cargo'
			END AS container_size,
			CASE
				WHEN `tabBorder Clearance`.cargo_type = 'Container' THEN `tabCargo Details`.net_weight
				WHEN `tabBorder Clearance`.cargo_type = 'Loose Cargo' THEN `tabBorder Clearance`.loose_net_weight
			END AS weight,
			`tabBorder Clearance`.bond_ref_no AS bond_reference,
			`tabBorder Clearance`.cargo_origin_country AS cargo_origin,
			`tabBorder Clearance`.cargo_destination_exact AS cargo_destination,
			`tabBorder Clearance`.border1_name AS border1_name,
			`tabBorder Clearance`.border1_arrival AS border1_arrival,
			`tabBorder Clearance`.border1_departure AS border1_departure,
			`tabBorder Clearance`.border1_crossing AS border1_crossing,
			`tabBorder Clearance`.border2_name AS border2_name,
			`tabBorder Clearance`.border2_arrival AS border2_arrival,
			`tabBorder Clearance`.border2_departure AS border2_departure,
			`tabBorder Clearance`.border2_crossing AS border2_crossing,
			`tabBorder Clearance`.offloading_point_arrival AS arrival_offloading_point,
			`tabBorder Clearance`.offloading_datetime AS offloading_datetime,
			(SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` \
				WHERE `tabReporting Status Table`.parenttype = 'Border Clearance' AND \
				`tabReporting Status Table`.parent = `tabBorder Clearance`.name ORDER BY \
				`tabReporting Status Table`.datetime DESC LIMIT 1) AS remarks \
		FROM \
			`tabBorder Clearance`
		LEFT JOIN
			`tabCargo Details` ON `tabCargo Details`.name = (SELECT name FROM `tabCargo Details` WHERE `tabCargo Details`.parent = `tabBorder Clearance`.name LIMIT 1)''' + where, where_filter, as_dict=True)
	return columns, data
