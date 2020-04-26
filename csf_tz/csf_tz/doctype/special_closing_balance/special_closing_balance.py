# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
# from frappe import _
from frappe.utils import today
from frappe.model.document import Document
from erpnext.stock.utils import get_latest_stock_qty

class SpecialClosingBalance(Document):
	def on_submit(self):
		items = []
		user_remarks = "Special Closing Balance - {0}".format(self.name)
		for item_row in self.closing_balance_details:
			if item_row.item and item_row.quantity:
				item_balance = get_latest_stock_qty(item_row.item,self.warehouse)
				item_dict = dict(
					item_code = item_row.item,
					qty = item_row.quantity - item_balance,
					uom = item_row.uom,
					s_warehouse = self.warehouse
				)
				item_row.item_balance = item_balance
				items.append(item_dict)

		stock_entry_doc =frappe.get_doc(dict(
				doctype = "Stock Entry",
				posting_date= today(),
				items = items,
				stock_entry_type='Material Receipt',
				purpose='Material Receipt',
				to_warehouse = self.warehouse,
				company= self.company, 
				remarks = user_remarks,
				)).insert(ignore_permissions = True)
		if stock_entry_doc:
			frappe.flags.ignore_account_permission = True
			stock_entry_doc.submit()
			# return stock_entry_doc.name
			self.stock_entry = stock_entry_doc.name
			url = frappe.utils.get_url_to_form(stock_entry_doc.doctype, stock_entry_doc.name)
			frappe.msgprint("Stock Entry Created <a href='{0}'>{1}</a>".format(url,stock_entry_doc.name))