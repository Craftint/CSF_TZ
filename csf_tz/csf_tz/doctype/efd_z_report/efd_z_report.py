# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import *
from frappe.utils import flt
class EFDZReport(Document):
	def validate(self):
		if not self.efd_z_report_invoices:
			frappe.throw(_("No Sales Invoie Found in the table"))
		if flt(self.total_turnover,2) != flt(self.total_turnover_ticked,2):
			frappe.throw(_("Sales Invoice Amount is not equal to Money Entered"))
		if flt(self.net_amount,2) != flt(self.total_excluding_vat_ticked,2):
			frappe.throw(_("Total Excluding VAT is not equal to Total Excluding VAT (Ticked)"))
		if flt(self.total_vat,2) != flt(self.total_vat_ticked,2):
			frappe.throw(_("Total VAT is not equal to Total VAT (Ticked)"))
		if flt(self.total_turnover_ex_sr,2) != flt(self.total_turnover_exempted__sp_relief_ticked,2):
			frappe.throw(_("Total Turnover Exempted / Sp. Relief is not equal to Total Turnover Exempted / Sp. Relief (Ticked)"))
		if self.get_number_of_ticked() != self.receipts_issued:
			frappe.throw(_("The Number of Sales Invoice (Include is checked) in the table is not equal to Receipts Issued"))
	

	def get_number_of_ticked(self):
		total_checked = 0
		for i in self.efd_z_report_invoices:
			if i.include:
				total_checked += 1
		return total_checked
	
	
	def get_sales_invoice(self):

		date = datetime.strptime(str(self.z_report_date_time), "%Y-%m-%d %H:%M:%S").date()
		time = datetime.strptime(str(self.z_report_date_time), "%Y-%m-%d %H:%M:%S").time()

		pos_profile = frappe.get_value("Electronic Fiscal Device", self.electronic_fiscal_device, "pos_profile")

		is_pos = "1" if pos_profile else "0"

		condition = "docstatus = 1 and is_pos = " + is_pos + " and (efd_z_report = '' OR efd_z_report is null) and status !='Return' and posting_date <= '" + str(
			date) + "' and IF(IF(posting_date = '" + str(date) + "', IF(posting_time < '" + str(
			time) + "',1,'PostingTime'),'PostingDate') = 1 or IF(posting_date = '" + str(
			date) + "',IF(posting_time < '" + str(time) + "',1,'PostingTime'),'PostingDate') = 'PostingDate',1,0)"

		if pos_profile:
			condition += " and pos_profile = '" + pos_profile + "'"

		query = """ select *
		 				from `tabSales Invoice`
		 				where {0}""".format(condition)

		sales_invoices = frappe.db.sql(query, as_dict=True)

		if not sales_invoices:
			frappe.throw("No Sales Invoice Fetch")

		for i in sales_invoices:
			if i.base_total_taxes_and_charges == 0:
				amt_ex__sr = i.base_total
			else:
				if i.base_net_total != i.base_total:
					amt_ex__sr = i.base_grand_total - (i.base_net_total + i.base_total_taxes_and_charges)
				else:
					amt_ex__sr = i.base_grand_total - ((i.base_total_taxes_and_charges / 0.18) + i.base_total_taxes_and_charges)
			if amt_ex__sr <0:
				amt_ex__sr =0
			self.append("efd_z_report_invoices",{
				"invoice_number" : i.name,
				"invoice_date" : i.posting_date,
				"amt_excl_vat" : flt(i.base_net_total,2),
				"vat" : flt(i.base_total_taxes_and_charges,2),
				"amt_ex__sr" : amt_ex__sr,
				"invoice_amount" : flt(i.base_rounded_total,2),
				"invoice_currency" : i.currency
			})
		return True


	def on_submit(self):
		to_remove= []
		for invoice in self.efd_z_report_invoices:
			if not invoice.include:
				to_remove.append(invoice)
			else:
				invoice_doc = frappe.get_doc("Sales Invoice",invoice.invoice_number)
				if  invoice_doc.efd_z_report:
					frappe.throw(_("The Sales Invoice {0} is linked to EFD Z Report {1}".format(invoice.invoice_number,invoice_doc.efd_z_report)))
				else:
					invoice_doc.efd_z_report = self.name
					invoice_doc.flags.ignore_permissions=True
					invoice_doc.save()
		[self.remove(invoice) for invoice in to_remove]
		

	def on_cancel(self):
		for invoice in self.efd_z_report_invoices:
			if invoice.include:
				invoice_doc = frappe.get_doc("Sales Invoice",invoice.invoice_number)
				if  invoice_doc.efd_z_report:
					invoice_doc.efd_z_report = ""
					invoice_doc.flags.ignore_permissions=True
					invoice_doc.save()












	# def get_invoices(self):
	# 	return []
	# 	if not (self.bank_account and self.from_date and self.to_date):
	# 		msgprint(_("Bank Account, From Date and To Date are Mandatory"))
	# 		return
    #
	# 	condition = ""
	# 	if not self.include_reconciled_entries:
	# 		condition = " and (clearance_date is null or clearance_date='0000-00-00')"
    #
	# 	account_cond = ""
	# 	if self.bank_account_no:
	# 		account_cond = " and t2.bank_account_no = {0}".format(frappe.db.escape(self.bank_account_no))
    #
	# 	if self.bank_account_no:
	# 		condition = " and bank_account = %(bank_account_no)s"
    #
	# 	invoice_entries = frappe.db.sql("""
	# 		select
	# 			"Payment Entry" as payment_document, name as payment_entry,
	# 			reference_no as cheque_number, reference_date as cheque_date,
	# 			if(paid_from=%(account)s, paid_amount, 0) as credit,
	# 			if(paid_from=%(account)s, 0, received_amount) as debit,
	# 			posting_date, ifnull(party,if(paid_from=%(account)s,paid_to,paid_from)) as against_account, clearance_date,
	# 			if(paid_to=%(account)s, paid_to_account_currency, paid_from_account_currency) as account_currency
	# 		from `tabPayment Entry`
	# 		where
	# 			(paid_from=%(account)s or paid_to=%(account)s) and docstatus=1
	# 			and posting_date >= %(from)s and posting_date <= %(to)s {0}
	# 		order by
	# 			posting_date ASC, name DESC
	# 	""".format(condition),
	# 	        {"account":self.bank_account, "from":self.from_date,
	# 			"to":self.to_date, "bank_account_no": self.bank_account_no}, as_dict=1)
    #
	# 	entries = sorted(list(invoices_entries),
	# 		key=lambda k: k['posting_date'] or getdate(nowdate()))
    #
	# 	for d in entries:
	# 		row = self.append('efd_z_report_invoices', {})
    #
	# 		d.invoice_number = 0
	# 		amount = flt(d.get('debit', 0)) - flt(d.get('credit', 0))
    #
	# 		formatted_amount = fmt_money(abs(amount), 2, d.account_currency)
	# 		d.amount = formatted_amount + " " + (_("Dr") if amount > 0 else _("Cr"))
    #
	# 		d.pop("credit")
	# 		d.pop("debit")
	# 		d.pop("account_currency")
	# 		row.update(d)
	# 		self.total_amount += flt(amount)

