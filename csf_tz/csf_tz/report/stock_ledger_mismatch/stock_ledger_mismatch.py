# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []

	columns = [
		{"fieldname": "group","label": _("Diff Group"),"fieldtype": "Data","width": 200},
		{"fieldname": "voucher_type","label": _("Voucher Type"),"fieldtype": "Data","width": 200},
		{"fieldname": "voucher_no","label": _("Voucher No"),"fieldtype": "Data","width": 200},
		{"fieldname": "item_code", "label": _("Item Code"), "fieldtype": "Data", "width": 200},
		{"fieldname": "warehouse", "label": _("Warehouse"), "fieldtype": "Data",  "width": 200},
		{"fieldname": "actual_qty",	"label": _("Actual Quantity"), "fieldtype": "Data",	"width": 200},
		{"fieldname": "qty_after_transaction",	"label": _("Actual Qty After Transaction"),	"fieldtype": "Data","width": 200}
	]

	data = []
	total_records = 0

	if not filters:
		return
	item_list = frappe.db.sql("""
		select distinct item_code, warehouse from `tabBin` ORDER BY item_code, warehouse
	""", as_dict = 1)

	for item in item_list:
	# 	item_wh_list = frappe.db.sql("""
	# 	select distinct warehouse from `tabBin where item_code = {0}`
	# """.format(item))
	# 	for item_wh in item_wh_list:
		item_wh_sle_list = frappe.db.get_all("Stock Ledger Entry", 
			filters = [["posting_date", "<=", filters.end_date], ["item_code", "=", item.item_code], ["warehouse", "=", item.warehouse], ["is_cancelled", "=", 0], ["docstatus", "=", 1]],
			fields = ["name", "voucher_type", "voucher_no", "actual_qty", "qty_after_transaction"],
			order_by = "posting_date asc, posting_time asc"
		)
		if not item_wh_sle_list or len(item_wh_sle_list) == 1:
			continue
		total_records += len(item_wh_sle_list) or 0

		prev_quantity = {"actual_qty": 0, "qty_after_transaction": 0, "voucher_no": "", "voucher_type": "First"}
		for item_wh_sle in item_wh_sle_list:
			if prev_quantity["voucher_type"] in ["Stock Reconciliation", "First"] or item_wh_sle.voucher_type == "Stock Reconciliation":
				prev_quantity["voucher_no"] = prev_quantity["voucher_type"]
				continue
			if prev_quantity["qty_after_transaction"] + item_wh_sle.actual_qty != item_wh_sle.qty_after_transaction:
				row = {"group": item_wh_sle.name, "voucher_type": item_wh_sle.voucher_type, "voucher_no": item_wh_sle.voucher_no, "item_code": item.item_code,"warehouse": item.warehouse, "actual_qty": item_wh_sle.actual_qty, "qty_after_transaction": item_wh_sle.qty_after_transaction}

				data.append({"group": item_wh_sle.name, "voucher_type": prev_quantity["voucher_type"], "voucher_no": prev_quantity["voucher_no"], "item_code": item.item_code,"warehouse": item.warehouse, "actual_qty": prev_quantity["actual_qty"], "qty_after_transaction": prev_quantity["qty_after_transaction"]})
				data.append(row)
			prev_quantity["actual_qty"] = item_wh_sle.actual_qty
			prev_quantity["qty_after_transaction"] = item_wh_sle.qty_after_transaction
			prev_quantity["voucher_no"] = item_wh_sle.voucher_no
			prev_quantity["voucher_type"] = item_wh_sle.voucher_type
	frappe.msgprint(_("Total records to be analyzed: " + str(total_records)))

	return columns, data

