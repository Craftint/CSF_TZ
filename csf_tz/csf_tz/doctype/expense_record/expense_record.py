# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe ,erpnext
from frappe import _
from frappe.model.document import Document
from csf_tz.custom_api import get_linked_docs_info,cancle_linked_docs,cancel_doc,delete_doc,delete_linked_docs
from frappe.utils import cint, flt, today, nowdate, add_days, get_datetime_str
from erpnext.controllers.accounts_controller import get_taxes_and_charges

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
		pass
	

	def on_submit(self):
		if self.supplier:
			self.create_purchase_invoice()


	def create_purchase_invoice(self):
		company =  frappe.get_value("Expense Type",self.expense_type,"company")
		items = [{
			"item_code": self.item,
			"rate": self.amount,
			"qty": 1,
			"description": self.name +" - "+ self.expense_type
		}]
		pi = frappe.get_doc({
			"doctype": "Purchase Invoice",
			"company": company,
			"currency": erpnext.get_company_currency(company),
			"cost_center": frappe.get_value("Section",self.section,"cost_center"),
			"supplier": self.supplier,
			"posting_date": self.date,
			"bill_no": self.bill_no,
			"bill_date": self.date,
			"document_type": self.doctype,
			"disable_rounded_total": 0,
			"expense_record": self.name,
			"items": items,
			"is_paid": 1,
			"cash_bank_account": frappe.get_value("Section",self.section,"default_cash_account"),
			"taxes_and_charges": frappe.get_value("Section",self.section,"purchase_taxes_and_charges_template"),
		})
		frappe.flags.ignore_account_permission = True
		pi.set_missing_values()
		getTax(pi)
		pi.calculate_taxes_and_totals()
		pi.insert(ignore_permissions=True)
		pi.save()
		self.purchase_invoice = pi.name
		invoice_url = frappe.utils.get_url_to_form(pi.doctype, pi.name)
		si_msgprint = "Purchase Invoice Created <a href='{0}'>{1}</a>".format(invoice_url,pi.name)
		frappe.msgprint(_(si_msgprint))
		return pi.name



def getTax(purchase_invoice):
	taxes = get_taxes_and_charges('Purchase Taxes and Charges Template',purchase_invoice.taxes_and_charges)
	for tax in taxes:
		purchase_invoice.append('taxes', tax)