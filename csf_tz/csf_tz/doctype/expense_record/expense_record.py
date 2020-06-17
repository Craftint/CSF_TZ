# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe ,erpnext
from frappe import _
from frappe.model.document import Document
from csf_tz.custom_api import get_linked_docs_info,cancle_linked_docs,cancel_doc,delete_doc,delete_linked_docs
from frappe.utils import cint, flt, today, nowdate, add_days, get_datetime_str

class ExpenseRecord(Document):
	# def on_cancel(self):
	# 	linked_doc_list = get_linked_docs_info(self.doctype,self.name)
	# 	cancle_linked_docs(linked_doc_list)
	# 	if self.journal_entry:
	# 		cancel_doc("Journal Entry",self.journal_entry)
			

	# def on_trash(self):
	# 	linked_doc_list = get_linked_docs_info(self.doctype,self.name)
	# 	delete_linked_docs(linked_doc_list)
	# 	if self.journal_entry:
	# 		delete_doc("Journal Entry",self.journal_entry)

	def validate(self):
		self.create_purchase_invoice()
	

	def create_purchase_invoice(self):
		company =  frappe.get_value("Expense Type",self.expense_type,"company")
		items = [{
			"item_code": self.item,
			"rate": self.amount,
			"qty": 1,
		}]
		pi = frappe.get_doc({
			"doctype": "Purchase Invoice",
			"company": company,
			"currency": erpnext.get_company_currency(company),
			"cost_center": frappe.get_value("Section",self.section,"cost_center"),
			# "naming_series": args.naming_series,
			"supplier": self.supplier,
			# "is_return": args.is_return,
			"posting_date": self.date,
			"bill_no": self.bill_no,
			# "buying_price_list": args.buying_price_list,
			"bill_date": self.date,
			# "destination_code": args.destination_code,
			"document_type": self.doctype,
			"disable_rounded_total": 0,
			"items": items,
			# "taxes": args["taxes"],
		})
		frappe.flags.ignore_account_permission = True
		pi.set_missing_values()
		# pi.insert(ignore_mandatory=True,ignore_permissions=True)
		pi.insert(ignore_permissions=True)

		pi.save()
		frappe.msgprint(pi.name)
		return pi.name
