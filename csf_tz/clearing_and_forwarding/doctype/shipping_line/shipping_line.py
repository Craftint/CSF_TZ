# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bravo Logisitcs and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact, delete_contact_and_address


class ShippingLine(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self, "customer")
