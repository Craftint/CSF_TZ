# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.query_report import add_total_row
import datetime

def execute(filters=None):
	return _execute(filters)

def _execute(filters=None, additional_table_columns=None, additional_query_columns=None):
	if not filters: filters = {}
	columns = get_columns(additional_table_columns)
	item_list = get_items(filters, additional_query_columns)

	data = []
	for d in item_list:
		#For actual hours time calculation = date difference in hours + time difference. There may be a simpler way to do it but ......
		time_difference = 0
		if d.end_date == d.start_date:
			time_difference = (d.end_time.seconds - d.start_time.seconds) / 3600
		else:
			time_difference = ((86400 - d.start_time.seconds) + d.end_time.seconds) / 3600
		date_difference = (d.end_date - d.start_date).total_seconds() / 3600
		actual_hrs = date_difference + time_difference
		
		service_value = d.billable_hours * d.standard_cost
		hrs_difference = actual_hrs - d.standard_hours
		row = [d.name, d.technician, d.employee_name, d.start_date, d.start_time, d.end_date, d.end_time, d.service, d.standard_hours, 
				actual_hrs, hrs_difference, d.billable_hours, d.standard_cost, service_value, d.warehouse, d.customer]
		data.append(row)
	return columns, data

def get_columns(additional_table_columns):
	columns = [
		_("Job Card") + ":Link/Job Card:120",
		_("Technician") + ":Link/User:100",
		_("Technician Name") + ":Data:100",
		_("Start Date") + ":Date:80",
		_("Start Time") + ":Time:80", 
		_("End Date") + ":Date:80",
		_("End Time") + ":Time:80",
		_("Service") + ":Link/Maintenance Service:120",
		_("Standard Hrs") + ":Float:120",
		_("Actual Hrs") + ":Float:120",
		_("Hrs Difference") + ":Float:120",
		_("Billable Hrs") + ":Float:120",
		_("Standard Rate") + ":Currency/currency:120",
		_("Service Value") + ":Currency/currency:120",
		_("Warehouse") + ":Link/Warehouse:120",
		_("Customer") + ":Link/Customer:120"]

	return columns

def get_conditions(filters):
	conditions = ""

	for opts in (("custm", " and `tabJob Card`.customer=%(custm)s"),
		("workshop", " and `tabJob Card`.warehouse = %(workshop)s"),
		("user", " and `tabMaintenance Services Table`.technician = %(user)s"),
		("from_date", " and `tabMaintenance Services Table`.start_date>=%(from_date)s"),
		("to_date", " and `tabMaintenance Services Table`.start_date<=%(to_date)s")):
			if filters.get(opts[0]):
				conditions += opts[1]

	return conditions

def get_items(filters, additional_query_columns):
	conditions = get_conditions(filters)
	match_conditions = frappe.build_match_conditions("Job Card")
	
	if match_conditions:
		match_conditions = " and {0} ".format(match_conditions)
	
	if additional_query_columns:
		additional_query_columns = ', ' + ', '.join(additional_query_columns)

	return frappe.db.sql("""
		select
			`tabJob Card`.name,
			`tabMaintenance Services Table`.start_date,
			`tabMaintenance Services Table`.end_date, 
			`tabMaintenance Services Table`.start_time,
			`tabMaintenance Services Table`.end_time,
			`tabJob Card`.name, 
			`tabJob Card`.customer, 
			`tabJob Card`.status,
			`tabJob Card`.warehouse, 
			`tabEmployee`.employee_name,
			`tabMaintenance Services Table`.service, 
			`tabMaintenance Services Table`.billable_hours,
			`tabMaintenance Services Table`.standard_hours,
			`tabMaintenance Services Table`.technician, 
			`tabMaintenance Services Table`.standard_cost	
		from 
			`tabJob Card`, `tabMaintenance Services Table`
		left join 
			`tabEmployee` on `tabEmployee`.name = `tabMaintenance Services Table`.technician
		where 
			`tabJob Card`.name = `tabMaintenance Services Table`.parent and `tabJob Card`.docstatus = 1 %s %s
		order by 
			`tabMaintenance Services Table`.start_date
		""".format(additional_query_columns or '') % (conditions, match_conditions), filters, as_dict=1)

