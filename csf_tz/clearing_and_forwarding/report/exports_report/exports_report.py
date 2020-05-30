# Copyright (c) 2013, Bravo Logisitcs and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, cstr
from frappe import _
import ast
from datetime import datetime

def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"fieldname": "name",
			"label": _("Reference"),
			"fieldtype": "Link",
			"options": "Export",
			"width": 100
		},
		{
			"fieldname": "file_number",
			"label": _("File Number"),
			"fieldtype": "Link",
			"options": "Files",
			"width": 100
		},
		{
			"fieldname": "booking_number",
			"label": _("Booking Number"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "booking_received",
			"label": _("Booking Received"),
			"fieldtype": "Date",
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
			"fieldname": "material",
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
			"label": _("Weight (kg)"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "value",
			"label": _("Cargo Value"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "export_type",
			"label": _("Export Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "eta",
			"label": _("ETA"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "shipper",
			"label": _("Shipper"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "customs_processing_type",
			"label": _("Customs Processing Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "received_repacking_manifest",
			"label": _("Received Repacking Manifest"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "customs_assessment_submission",
			"label": _("Customs Assessment Submission"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "bt_submission_date",
			"label": _("BT Submission Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "bt_approval_date",
			"label": _("BT Approval Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "expenses_usd",
			"label": _("Expenses (USD)"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "expenses_tzs",
			"label": _("Expenses (TZS)"),
			"fieldtype": "Float",
			"width": 100
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
	
	data = frappe.db.sql('''
							SELECT
								tabExport.name,
								tabExport.client AS customer,
								tabExport.file_number,
								tabExport.booking_number,
								tabExport.booking_received,
								tabExport.export_type,
								tabExport.material,
								count(`tabPacking List`.name) AS no_of_containers,
								SUM(`tabPacking List`.net_weight) AS weight,
								SUM(`tabBond Reference Table`.bond_value) AS value,
								tabExport.eta,
								tabExport.shipper,
								tabExport.customs_processing_type,
								tabExport.received_repacking_manifest,
								tabExport.customs_assessment_submission,
								tabExport.bt_submission_date,
								tabExport.bt_approval_date,
								(SELECT SUM(expense_amount) FROM `tabExpenses` WHERE parenttype = 'Export' AND parent = `tabExport`.name AND expense_currency = 'USD') AS expenses_usd,
								(SELECT SUM(expense_amount) FROM `tabExpenses` WHERE parenttype = 'Export' AND parent = `tabExport`.name AND expense_currency = 'TZS') AS expenses_tzs,
								(SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` \
									WHERE `tabReporting Status Table`.parenttype = 'Export' AND `tabReporting Status Table`.parent = `tabExport`.name \
									ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1) \
								AS remarks
							FROM
								tabExport
							LEFT JOIN
								`tabPacking List` ON `tabPacking List`.parenttype = 'Export' AND `tabPacking List`.parent = `tabExport`.name
							LEFT JOIN
								`tabBond Reference Table` ON `tabBond Reference Table`.parenttype = 'Export' AND `tabBond Reference Table`.parent = `tabExport`.name
							WHERE 
								tabExport.status = %(status)s AND tabExport.booking_received BETWEEN %(from_date)s AND %(to_date)s 
							GROUP BY `tabExport`.name
						''', 
						{"from_date": filters.from_date, "to_date": filters.to_date, "status": filters.status}, as_dict=1)
	
	return columns, data
