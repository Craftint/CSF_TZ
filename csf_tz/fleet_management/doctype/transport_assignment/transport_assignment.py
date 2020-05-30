# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bravo Logistics and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TransportAssignment(Document):
	def onload(self):
		if self.transporter_type == 'Bravo':
			previous_trips = frappe.db.sql('''SELECT name, hidden_status FROM `tabVehicle Trip` WHERE vehicle=%s AND transporter_type='Bravo' ORDER BY creation DESC LIMIT 20''', self.assigned_vehicle, as_dict=True)
			if previous_trips:
				self.set("vehicle_status", previous_trips[0].hidden_status)
				self.set("vehicle_trip", previous_trips[0].name)

@frappe.whitelist(allow_guest=True)
def change_assignment_status(**args):
	args = frappe._dict(args)
	doc = frappe.get_doc("Transport Assignment", args.assignment_docname)
	doc.db_set('status', 'Not Processed')
