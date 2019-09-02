# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EFDZReport(Document):
	def get_invoices(self):
		return []
		if not (self.bank_account and self.from_date and self.to_date):
			msgprint(_("Bank Account, From Date and To Date are Mandatory"))
			return

		condition = ""
		if not self.include_reconciled_entries:
			condition = " and (clearance_date is null or clearance_date='0000-00-00')"

		account_cond = ""
		if self.bank_account_no:
			account_cond = " and t2.bank_account_no = {0}".format(frappe.db.escape(self.bank_account_no))

		if self.bank_account_no:
			condition = " and bank_account = %(bank_account_no)s"

		invoice_entries = frappe.db.sql("""
			select
				"Payment Entry" as payment_document, name as payment_entry,
				reference_no as cheque_number, reference_date as cheque_date,
				if(paid_from=%(account)s, paid_amount, 0) as credit,
				if(paid_from=%(account)s, 0, received_amount) as debit,
				posting_date, ifnull(party,if(paid_from=%(account)s,paid_to,paid_from)) as against_account, clearance_date,
				if(paid_to=%(account)s, paid_to_account_currency, paid_from_account_currency) as account_currency
			from `tabPayment Entry`
			where
				(paid_from=%(account)s or paid_to=%(account)s) and docstatus=1
				and posting_date >= %(from)s and posting_date <= %(to)s {0}
			order by
				posting_date ASC, name DESC
		""".format(condition),
		        {"account":self.bank_account, "from":self.from_date,
				"to":self.to_date, "bank_account_no": self.bank_account_no}, as_dict=1)

		entries = sorted(list(invoices_entries),
			key=lambda k: k['posting_date'] or getdate(nowdate()))

		for d in entries:
			row = self.append('efd_z_report_invoices', {})

			d.invoice_number = 0
			amount = flt(d.get('debit', 0)) - flt(d.get('credit', 0))

			formatted_amount = fmt_money(abs(amount), 2, d.account_currency)
			d.amount = formatted_amount + " " + (_("Dr") if amount > 0 else _("Cr"))

			d.pop("credit")
			d.pop("debit")
			d.pop("account_currency")
			row.update(d)
			self.total_amount += flt(amount)


