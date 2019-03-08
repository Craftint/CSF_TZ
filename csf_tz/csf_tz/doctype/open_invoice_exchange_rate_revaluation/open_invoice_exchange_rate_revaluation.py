# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.setup.utils import get_exchange_rate

class OpenInvoiceExchangeRateRevaluation(Document):
	def on_submit(self):
		frappe.msgprint("Call")
		je_item = makeJEItem(self)
		res = makeJournalEntry(self.revaluation_date,je_item)
		frappe.msgprint("Journal Entry Created:"+str(res))



def makeJEItem(self):
	item_dict = []
	for row in self.inv_err_detail:
		first_row_je = getFirstRow(row.invoice_gain_or_loss,row.invoice_type)
		item_dict.append(first_row_je)
		second_row_je=getSecondRow(row.invoice_gain_or_loss,row.invoice_type,row.invoice_number)
		item_dict.append(second_row_je)
	return item_dict


def getFirstRow(invoice_gain_or_loss,invoice_type):
	item_json={}
	item_json["accounts"] = "5222 - Unrealized Exchange Gain or Loss - PMC"
	if flt(invoice_gain_or_loss) > 0:
		if invoice_type == "Sales Invoice":
			item_json["credit_in_account_currency"] = invoice_gain_or_loss
		else:
			item_json["debit_in_account_currency"] = invoice_gain_or_loss
	else:
		if invoice_type == "Sales Invoice":
			item_json["credit_in_account_currency"] = invoice_gain_or_loss
		else:
			item_json["debit_in_account_currency"] = invoice_gain_or_loss
	return item_json


def getSecondRow(invoice_gain_or_loss,invoice_type,invoice_number):
	item_json={}
	item_json["account"] = "1310 - Debtors - PMC"
	item_json["reference_type"] = invoice_type
	item_json["reference_name"] = invoice_number
	if invoice_type == "Sales Invoice":
		item_json["party_type"] = 'Customer'
		item_json["party"] = frappe.db.get_value(invoice_type,invoice_number,"customer")
		if flt(invoice_gain_or_loss) > 0:
			item_json["debit_in_account_currency"] = invoice_gain_or_loss
		else:
			item_json["credit_in_account_currency"] = invoice_gain_or_loss
		
	else:
		item_json["party_type"] = 'Supplier'
		item_json["party"] = frappe.db.get_value(invoice_type,invoice_number,"supplier")
		if flt(invoice_gain_or_loss) > 0:
			item_json["credit_in_account_currency"] = invoice_gain_or_loss
		else:
			item_json["debit_in_account_currency"] = invoice_gain_or_loss
	return item_json


@frappe.whitelist()
def makeJournalEntry(date,je_item):
	propm_setting=frappe.get_doc("Property Management Settings","Property Management Settings")
	j_entry=frappe.get_doc(dict(
		doctype="Journal Entry",
		posting_date=date,
		company=propm_setting.company,
		accounts=je_item
	)).insert()
	return j_entry.name

		
			
