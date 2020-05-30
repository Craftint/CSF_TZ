# Copyright (c) 2013, Bravo Logistics and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, cstr
from frappe import _
import ast
import datetime
from datetime import date

def execute(filters=None):
	columns, data = [], []
	
	columns = [
		{
			"fieldname": "reference",
			"label": _("Job Card Reference"),
			"fieldtype": "Link",
			"options": "Job Card",
			"width": 100
		},
		{
			"fieldname": "requested_on",
			"label": _("Requested On"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "started_on",
			"label": _("Started Work On"),
			"fieldtype": "Datetime",
			"width": 100
		},
		{
			"fieldname": "ended_on",
			"label": _("Ended On"),
			"fieldtype": "Datetime",
			"width": 150
		},
		{
			"fieldname": "days_in_workshop",
			"label": _("Days in Workshop"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "job_type",
			"label": _("Job Type"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "work_done_on",
			"label": _("Work Done On"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "plate_number",
			"label": _("Plate NUmber"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "fleet_number",
			"label": _("Fleet NUmber"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "job_description",
			"label": _("Job Description"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "reporting_status",
			"label": _("Reporting Status"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 150
		}
	]
	
	today = datetime.date.today().strftime("%Y-%m-%d")
	
	data = frappe.db.sql('''SELECT
								`tabJob Card`.name AS reference,
								`tabWorkshop Request`.requested_date AS requested_on,
								`tabJob Card`.start_date,
								`tabJob Card`.end_date,
								CONCAT(`tabJob Card`.start_date, ' ' , `tabJob Card`.start_time) AS started_on,
								CONCAT(`tabJob Card`.end_date, ' ' ,`tabJob Card`.end_time) AS ended_on,
								`tabJob Card`.job_type,
								`tabJob Card`.job_done_on AS work_done_on,
								CASE
									WHEN `tabJob Card`.job_done_on = 'Vehicle' THEN `tabJob Card`.job_done_on_docname
									WHEN `tabJob Card`.job_done_on = 'Trailer' THEN `tabTrailer`.number_plate
								END AS plate_number,
								CASE
									WHEN `tabJob Card`.job_done_on = 'Vehicle' THEN `tabVehicle`.fleet_number
									ELSE ''
								END AS fleet_number,
								REPLACE(CONCAT(`tabJob Card`.job_type, ' ', `tabJob Card`.job_description),'\n','. ') AS job_description,
								(SELECT `tabReporting Status Table`.status FROM `tabReporting Status Table` WHERE \
									`tabReporting Status Table`.parenttype = 'Job Card' AND `tabReporting Status Table`.parent = `tabJob Card`.name \
									ORDER BY `tabReporting Status Table`.datetime DESC LIMIT 1)
								AS reporting_status,
								`tabJob Card`.status
							FROM
								`tabJob Card`
							LEFT JOIN
								`tabWorkshop Request` ON `tabWorkshop Request`.name = `tabJob Card`.requested_from
							LEFT JOIN
								`tabTrailer` ON `tabTrailer`.name = `tabJob Card`.job_done_on_docname AND `tabJob Card`.job_done_on = 'Trailer'
							LEFT JOIN
								`tabVehicle` ON `tabVehicle`.name  = `tabJob Card`.job_done_on_docname AND `tabJob Card`.job_done_on = 'Vehicle'
							WHERE `tabJob Card`.docstatus <> 2 AND `tabJob Card`.status = 'Open' OR (`tabJob Card`.status = 'Closed' AND `tabJob Card`.end_date = %(today)s)
						 ''', {"today": today}, as_dict=1)
						 
	for row in data:
		if row.start_date and row.end_date:
			row.update({"days_in_workshop": (row.end_date - row.start_date).days})
		elif row.start_date and not row.end_date:
			row.update({"days_in_workshop": (datetime.date.today() - row.start_date).days})
						 
	return columns, data
