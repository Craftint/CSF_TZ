# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw
import json

class PreDeliveryInspection(Document):
	def onload(self):
		""" Load delivery Note link """
		dashboard_links_html = self.load_delivery_note()
		self.set_onload("dashboard_links_html", {"display": dashboard_links_html})

	def load_delivery_note(self):
		delivery_note_links = []
		delivery_note_links = frappe.db.sql("""
			SELECT
				tdni.item_code,
				tdni.parent,
				tdni.serial_no,
				tdni.against_sales_invoice,
				tip.name As installation
			FROM 
				(`tabDelivery Note Item` tdni)
			LEFT JOIN
				(`tabInstallation Note` tip)
			ON tdni.parent = tip.delivery_note
			where 
				tdni.against_sales_invoice = %(inv)s
			AND
				tdni.item_code = %(item)s
			AND
				tdni.serial_no = %(serial)s		
			""",{'inv':self.reference_name, 'item':self.item_code, 'serial':self.item_serial_no}, as_dict=True)
		self.set_onload("delivery_note_links", delivery_note_links)
		#frappe.msgprint(_(json.dumps(delivery_note_links)))

		return frappe.render_template("templates/pre_delivery_links.html", {"delivery_note_links": delivery_note_links})
