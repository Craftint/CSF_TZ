# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import binascii
import os
from csf_tz.bank_api import invoice_submission

class StudentApplicantFees(Document):
	def after_insert(self):
		self.callback_token = binascii.hexlify(os.urandom(14)).decode()
		series = frappe.get_value("Company", self.company, "nmb_series") or ""
		if not series:
			frappe.throw(_("Please set NMB User Series in Company {0}".format(self.company)))
		reference = str(series) + 'R' + str(self.name)
		if not self.abbr:
			self.abbr = frappe.get_value("Company", self.company, "abbr") or ""
		self.bank_reference = reference.replace('-', '').replace('RFEE'+self.abbr,'')


	def on_submit(self):
		invoice_submission(self)