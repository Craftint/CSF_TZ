# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.query_report import add_total_row

def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"fieldname": "technician",
			"label": _("Technician"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 150
		},
		{
			"fieldname": "employee_name",
			"label": _("Technician Name"),
			"fieldtype": "Data",
			"width": 150,
			"hidden": True
		},
		{
			"fieldname": "workshop",
			"label": _("Workshop"),
			"fieldtype": "link",
			"options": "Warehouse",
			"width": 150
		},
		{
			"fieldname": "no_of_jobs_completed",
			"label": _("No of Jobs Completed"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "total_billable_hours",
			"label": _("Total Billable Hours"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "total_standard_hours",
			"label": _("Standard Hours"),
			"fieldtype": "Float",
			"width": 150
		},
		{
			"fieldname": "total_work_value",
			"label": _("Total Work Value"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "job_efficiency",
			"label": _("Technician Efficiency (%)"),
			"fieldtype": "Float",
			"width": 150
		},
	]

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))

	where_filter = {"from_date": filters.from_date,"to_date": filters.to_date,}
	where = ""

	if filters.workshop:
		where += '  AND tjc.warehouse = %(workshop)s '
		where_filter.update({"workshop": filters.workshop})
		
	if filters.technician:
		where += '  AND tmst.technician = %(technician)s '
		where_filter.update({"technician": filters.technician})


	data = frappe.db.sql('''SELECT 
								tmst.technician,
								tabEmployee.employee_name,
								tjc.warehouse AS workshop,
								COUNT(tmst.name) AS no_of_jobs_completed,
								SUM(tmst.billable_hours) AS total_billable_hours,
								SUM(tmst.standard_hours) AS total_standard_hours,
								SUM(tmst.standard_cost * tmst.billable_hours) as total_work_value,
								(SUM(tmst.billable_hours) / SUM(tmst.standard_hours)) * 100 AS job_efficiency							
							FROM 
								(`tabMaintenance Services Table` tmst)
							LEFT JOIN
								(`tabJob Card` tjc) ON (tmst.parent = tjc.name)
							LEFT JOIN 
								tabEmployee ON tabEmployee.name = tmst.technician
							WHERE
							 	tmst.start_date BETWEEN %(from_date)s AND %(to_date)s AND tjc.docstatus = 1
							 	AND tmst.service_status = 'Fully Completed' '''+ where + '''
							GROUP BY 
								tmst.technician, tjc.warehouse
						''',
							where_filter, as_list=1);
	return columns, data
