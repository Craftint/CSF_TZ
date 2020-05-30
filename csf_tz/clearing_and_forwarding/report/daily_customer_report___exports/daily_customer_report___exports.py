# Copyright (c) 2013, Bravo Logisitcs and contributors
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
			"options": "Export",
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
			"fieldname": "booking_received",
			"label": _("Booking Received"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "booking_no",
			"label": _("Booking No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "commodity",
			"label": _("Commodity"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "no_of_containers",
			"label": _("No of Containers"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "weight",
			"label": _("Weight"),
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
			"fieldname": "vessel",
			"label": _("Vessel"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "voyager_no",
			"label": _("Voyager No"),
			"fieldtype": "data",
			"width": 100
		},
		{
			"fieldname": "shipping_line",
			"label": _("Shipping Line"),
			"fieldtype": "data",
			"width": 100
		},
		{
			"fieldname": "eta",
			"label": _("ETA"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "engagement_date",
			"label": _("Engagement Date"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "payment_cutoff",
			"label": _("Payment Cutoff"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "stuffing_date",
			"label": _("Stuffing Date"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "tra_release_obtained",
			"label": _("TRA Release Obtained"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "lodge_port_charges",
			"label": _("Lodge Port Charges"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "port_charges_paid",
			"label": _("Port Charges Paid"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "permit_obtained_date",
			"label": _("Permit Obtained Date"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "delivery_date",
			"label": _("Assigned Delivery Date"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "permit_submited_to_client",
			"label": _("Permit Submited to Client"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "containers_arrived_port",
			"label": _("Containers Delivered to Port"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "file_submitted_to_scanner",
			"label": _("File Submitted to Scanner"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "scanner_report_collected",
			"label": _("Scanner Report Collected"),
			"fieldtype": "date",
			"width": 100
		},
		{
			"fieldname": "scanner_report_sent_to_client",
			"label": _("Scanner Report Sent to Client"),
			"fieldtype": "date",
			"width": 100
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
	
	where = ''
	where_filter = {'today': today, 'yesterday': yesterday, 'day_before': day_before}
	if filters.customer:
		where = 'AND tabExport.client = %(customer)s'
		where_filter.update({'customer': filters.customer})
	
	
	data = frappe.db.sql('''SELECT 
								tabExport.name AS file_number,
								tabExport.client,
								tabExport.booking_received,
								tabExport.booking_number AS booking_no,
								tabExport.material AS commodity,
								(SELECT count(`tabPacking List`.name) FROM `tabPacking List` WHERE `tabPacking List`.parenttype = 'Export' AND `tabPacking List`.parent = `tabExport`.name) AS no_of_containers,
								(SELECT SUM(`tabPacking List`.net_weight) FROM `tabPacking List` WHERE `tabPacking List`.parenttype = 'Export' AND `tabPacking List`.parent = `tabExport`.name) AS weight,
								tabExport.destination,
								tabExport.vessel_name AS vessel,
								tabExport.voyage_no AS voyager_no,
								tabExport.shipping_line,
								tabExport.eta,
								tabExport.engagement_date,
								tabExport.cut_off_date AS payment_cutoff,
								tabExport.stuffing_date,
								tabExport.release_received AS tra_release_obtained,
								tabExport.lodge_port_charges,
								tabExport.port_charges_paid,
								tabExport.loading_permit_received AS permit_obtained_date,
								tabExport.loading_date AS delivery_date,
								tabExport.loading_permit_handover_transporter AS permit_submited_to_client,
								tabExport.containers_arrived_at_port AS containers_arrived_port,
								tabExport.file_submitted_to_scanner,
								tabExport.scanner_report_collected,
								tabExport.scanner_report_sent_to_client,
								(SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE `tabReporting Status Table`.parenttype = 'Export' \
									AND `tabReporting Status Table`.parent = `tabExport`.name ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1) AS remarks
							FROM
								`tabExport`
							WHERE tabExport.status <> 'Closed' AND (`tabExport`.scanner_report_sent_to_client IS NULL OR `tabExport`.scanner_report_sent_to_client IN (%(today)s, %(yesterday)s, %(day_before)s))
							''' + where, where_filter, as_dict=1)
	
	return columns, data
