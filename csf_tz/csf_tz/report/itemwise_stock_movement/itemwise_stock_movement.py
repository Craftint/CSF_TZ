# Copyright (c) 2019, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.utils import update_included_uom_in_report
import numpy as np
import pandas as pd

def execute(filters=None):
	# frappe.msgprint(str(filters))
	include_uom = filters.get("include_uom")
	columns = get_columns()
	items = get_items(filters)

	sl_entries = get_stock_ledger_entries(filters, items)
	# item_details = get_item_details(items, sl_entries, include_uom)
	# opening_row = get_item_balance(filters, columns, filters.from_date, "Opening", "Halotel 500")
	# closing_row = get_item_balance(filters, columns, filters.to_date, "Closing", "Halotel 500")
	# frappe.msgprint("sle entries are: " + str(sl_entries))
	# below is to try overcome issue of not getting column names in pivot_table 
	colnames = [key for key in sl_entries[0].keys()]
	# frappe.msgprint("colnames are: " + str(colnames))
	df = pd.DataFrame.from_records(sl_entries, columns=colnames)
	# frappe.msgprint("dataframe columns are is: " + str(df.columns.tolist()))
	pvt = pd.pivot_table(
		df,
		values='actual_qty',
		index=['posting_date', 'Particulars'],
		columns='item_code',
		fill_value=0
	)
	# frappe.msgprint(str(pvt))

	data = pvt.reset_index().values.tolist()
	# frappe.msgprint("Data is: " + str(data))

	columns += pvt.columns.values.tolist()

	# conversion_factors = []
	# if opening_row:
	# 	data.append(opening_row)

	# for sle in sl_entries:
		# item_detail = item_details[sle.item_code]

		# sle.update(item_detail)
		# data.append(sle)

		# if include_uom:
			# conversion_factors.append(item_detail.conversion_factor)

	# update_included_uom_in_report(columns, data, include_uom, conversion_factors)

	# if closing_row:
	# 	data.append(closing_row)

	return columns, data

def get_columns():
	columns = [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 95},
		{"label": _("Particulars"), "fieldname": "particulars", "width": 110},
	]

	return columns

def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ''
	if items:
		item_conditions_sql = 'and sle.item_code in ({})'\
			.format(', '.join(['"' + frappe.db.escape(i) + '"' for i in items]))

	return frappe.db.sql("""SELECT	sle.posting_date, 
									CASE sle.voucher_type 
										WHEN "Purchase Invoice" THEN "Purchase Invoice" 
										WHEN "Purchase Receipt" THEN "Purchase Receipt" 
										WHEN "Sales Invoice" THEN si.customer
										WHEN "Delivery Note" THEN dn.customer
										WHEN "Stock Entry" THEN "Stock Entry"
										ELSE "Other"
									END as "Particulars",
									sle.item_code, 
									sum(sle.actual_qty) as "actual_qty"
							FROM	`tabStock Ledger Entry` sle 
								LEFT OUTER JOIN `tabSales Invoice` si 
												ON sle.voucher_no = si.name
												AND sle.company = si.company
								LEFT OUTER JOIN `tabDelivery Note` dn 
												ON sle.voucher_no = dn.name
												AND sle.company = dn.company
							WHERE sle.actual_qty != 0
									AND sle.company = %(company)s
									AND sle.posting_date BETWEEN %(from_date)s AND %(to_date)s
									{sle_conditions}
									{item_conditions_sql}
							GROUP BY sle.posting_date, `Particulars`, sle.item_code
							ORDER BY sle.posting_date asc"""\
		.format(
			sle_conditions=get_sle_conditions(filters),
			item_conditions_sql = item_conditions_sql
		), filters, as_dict = 1)

def get_items(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")
	else:
		if filters.get("brand"):
			conditions.append("item.brand=%(brand)s")
		if filters.get("item_group"):
			conditions.append(get_item_group_condition(filters.get("item_group")))

	items = []
	if conditions:
		items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
			.format(" and ".join(conditions)), filters)
	return items

def get_item_details(items, sl_entries, include_uom):
	item_details = {}
	if not items:
		items = list(set([d.item_code for d in sl_entries]))

	if not items:
		return item_details

	cf_field = cf_join = ""
	if include_uom:
		cf_field = ", ucd.conversion_factor"
		cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom='%s'" \
			% frappe.db.escape(include_uom)

	item_codes = ', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])
	res = frappe.db.sql("""
		select
			item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom {cf_field}
		from
			`tabItem` item
			{cf_join}
		where
			item.name in ({item_codes})
	""".format(cf_field=cf_field, cf_join=cf_join, item_codes=item_codes), as_dict=1)

	for item in res:
		item_details.setdefault(item.name, item)

	return item_details

def get_sle_conditions(filters):
	conditions = []
	if filters.get("warehouse"):
		warehouse_condition = get_warehouse_condition(filters.get("warehouse"))
		if warehouse_condition:
			conditions.append(warehouse_condition)

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_opening_balance(filters, columns, date, balance_type, item_code):
	if not (item_code and filters.warehouse and date):
		return

	from erpnext.stock.stock_ledger import get_previous_sle
	last_entry = get_previous_sle({
		"item_code": item_code,
		"warehouse_condition": get_warehouse_condition(filters.warehouse),
		"posting_date": date,
		"posting_time": "00:00:00"
	})
	row = {}
	row["voucher_type"] = _(balance_type)
	for dummy, v in ((9, 'actual_qty')):
			row[v] = last_entry.get(v, 0)

	return row

def get_warehouse_condition(warehouse):
	warehouse_details = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"], as_dict=1)
	if warehouse_details:
		return " exists (select name from `tabWarehouse` wh \
			where wh.lft >= %s and wh.rgt <= %s and warehouse = wh.name)"%(warehouse_details.lft,
			warehouse_details.rgt)

	return ''

def get_item_group_condition(item_group):
	item_group_details = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=1)
	if item_group_details:
		return "item.item_group in (select ig.name from `tabItem Group` ig \
			where ig.lft >= %s and ig.rgt <= %s and item.item_group = ig.name)"%(item_group_details.lft,
			item_group_details.rgt)

	return ''

