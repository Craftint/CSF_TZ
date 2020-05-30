# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"fieldname": "delivery_note",
			"label": _("Delivery Note"),
			"fieldtype": "Link",
			"options": "Delivery Note",
			"width": 150		
		},
		{
			"fieldname": "customer_name",
			"label": _("Customer"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "customer_address",
			"label": _("Customer Address"),
			"fieldtype": "Small Text",
			"width": 200
		},
		{
			"fieldname": "phone_number",
			"label": _("Phone Number"),
			"fieldtype": "Data",
			"width": 150
		},
		# {
		# 	"fieldname": "item_name",
		# 	"label": _("Item"),
		# 	"fieldtype": "Data",
		# 	"width": 150		
		# },
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "quantity",
			"label": _("Quantity"),
			"fieldtype": "Float",
			"width": 150
		},
		# {
		# 	"fieldname": "uom",
		# 	"label": _("UOM"),
		# 	"fieldtype": "Data",
		# 	"width": 150
		# },
		{
			"fieldname": "serial_no",
			"label": _("Serial Numbers"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "actual_quantity",
			"label": _("Actual Quantity"),
			"fieldtype": "Float",
			"width": 100
		},
		# {
		# 	"fieldname": "projected_quantity",
		# 	"label": _("Projected Quantity"),
		# 	"fieldtype": "Float",
		# 	"width": 100
		# },
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "sales_invoice",
			"label": _("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150		
		}
	]
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))

	where = ''
	where_filter = {"from_date": filters.from_date, "to_date": filters.to_date}

	if filters.warehouse:
		where += ' AND dni.warehouse = %(warehouse)s'
		where_filter.update({"warehouse": filters.warehouse})
	
	data = frappe.db.sql('''SELECT 
								dn.customer_name,
								CONCAT(ta.address_line1,",", ta.city,',', ta.country) AS customer_address,
 								ta.phone AS phone_number,
 								dn.posting_date,
								dni.item_name,
								dni.item_code,
								dni.serial_no,
								dni.qty AS quantity,
								dni.uom,
								dni.warehouse,
								dn.name AS delivery_note,
								so.name AS sales_invoice,
								`tabBin`.actual_qty AS actual_quantity,
								`tabBin`.projected_qty AS projected_quantity
							FROM
								(`tabDelivery Note Item`dni)
							LEFT JOIN
								(`tabSales Invoice` so)
								ON (dni.against_sales_invoice = so.name)						
							LEFT JOIN
								(`tabDelivery Note` dn)
								ON (dni.parent=dn.name)
							LEFT JOIN 
								`tabBin` ON (`tabBin`.item_code = dni.item_code
									and `tabBin`.warehouse = dni.warehouse)
							LEFT JOIN
								tabItem ON tabItem.item_code = dni.item_code
							LEFT JOIN
								(`tabAddress` ta) ON ta.name=(SELECT dl.parent
								FROM (`tabDynamic Link` dl)
								WHERE 
									dl.parenttype='Address' AND dl.link_doctype='Customer' AND 
									dl.link_name=dn.customer ORDER BY ta.creation LIMIT 1
								)
							WHERE
							 	dn.docstatus = 1 AND dn.status IN ('Completed', 'To Bill', 'Closed')
							 	AND dn.posting_date BETWEEN %(from_date)s AND %(to_date)s
							 	AND (SELECT name FROM `tabDelivery Note` WHERE return_against = dn.name) IS NULL''' + where,
							where_filter, as_dict=1
							);
	return columns, data
