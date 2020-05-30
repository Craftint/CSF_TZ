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
			"fieldname": "reference",
			"label": _("Installation Note"),
			"fieldtype": "Link",
			"options": "Installation Note",
			"width": 100
		},
		{
			"fieldname": "inst_date",
			"label": _("Installation Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "data",
			"width": 100
		},
		{
			"fieldname": "item_code",
			"label": _("Item code"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Text",
			"width": 200
		}
	]
	
	
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
	
	where = ''
	where_filter = {"from_date": filters.from_date, "to_date": filters.to_date}

	if filters.branch:
		where += ' AND `tabDelivery Note Item`.warehouse = %(branch)s'
		where_filter.update({"branch": filters.branch})
	
	data = frappe.db.sql('''SELECT
								`tabInstallation Note`.name AS reference,
								`tabInstallation Note`.inst_date AS inst_date,
								`tabInstallation Note`.customer AS customer,
								`tabInstallation Note`.item_code AS item_code,
								`tabInstallation Note`.remarks AS remarks,
								`tabInstallation Note`.status AS status,
								`tabInstallation Note`.delivery_note,
								`tabDelivery Note Item`.warehouse

							FROM
								`tabInstallation Note`
							LEFT JOIN 
								`tabDelivery Note Item`
							ON 
								(`tabDelivery Note Item`.parent = `tabInstallation Note`.delivery_note)
							WHERE 
								`tabInstallation Note`.docstatus <> 2 \
								AND `tabInstallation Note`.inst_date BETWEEN %(from_date)s AND %(to_date)s
						 '''+ where,
							where_filter, as_dict=1,)
						 
	return columns, data
