# -*- coding: utf-8 -*-
# Copyright (c) 2017, Bravo Logistics and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
import time
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
from csf_tz.after_sales_services.doctype.requested_payments.requested_payments import validate_requested_funds
from frappe.model.document import Document

class ServiceJobCard(Document):
	from csf_tz.after_sales_services.doctype.reference_payment_table.reference_payment_table import update_child_table
	def before_save(self):
		validate_requested_funds(self)
		self.set_status(status="Open")
		
	def before_submit(self):
		self.validate_services()
		self.validate_closing_values()
		self.set_status(status="Closed")
		if not self.end_date:
			#Timestamp
			ts = time.time()
			today = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
			self.set('end_date', today)
		
	def on_submit(self):		
		msgprint("This Service Job Card is now closed, please return any funds or items that were issued but not used.")
		
	def on_cancel(self):
		self.set_status(status="Open")
		
	def set_status(self, status):
		if status:
			self.db_set("status", status)
		
	def validate_services(self):
		if not self.services_table:
			frappe.throw(_("Please enter the services performed on this Service Job Card."))
		
		idx = ""
		error = False
		for service in self.services_table:
			if service.subcontracted != 1 and service.service_status == "Fully Completed":
				if not service.technician:
					error = True
					if idx == "":
						idx += str(service.idx)
					else:
						idx += ", {}".format(str(service.idx))
					
					if error:
						frappe.throw(_("Services in rows {} of services table have not been assigned a technician.").format(idx))
			
			if service.service_status != "Fully Completed":
				error = True
				if idx == "":
					idx += str(service.idx)
				else:
					idx += ", {}".format(str(service.idx))
				
				if error:
					frappe.throw(_("Services in rows {} of services table are yet to be completed. Please complete first before submitting.").format(idx))
			
			
		self.validate_subcontracted_services()
		
	
	def validate_closing_values(self):
		if not self.inspected_by or not self.verified_by:
			frappe.throw("Please enter inspection and verification person.")
	
			
	def validate_subcontracted_services(self):
		subcontractor_error = False
		start_end_rate_error = False
		idx = ""
		for service in self.services_table:
			if service.subcontracted == 1 and service.service_status == "Fully Completed":
				pass
			else:
				continue
			
			#Verify that subcontractor added	
			if not service.subcontractor:
				subcontractor_error = True
				if idx == "":
					idx += str(service.idx)
				else:
					idx += ", {}".format(str(service.idx))
			
			if subcontractor_error:
				frappe.throw(_("Please enter subcontractor for services in row {}").format(idx))	
				
			#Verify that start, end and rate details have been added
			if not service.get("start_date") or not service.get("end_date") or not service.get("rate_per_hour") or not service.get("currency_rate_per_hour"):
				start_end_rate_error = True
				if idx == "":
					idx += str(service.idx)
				else:
					idx += ", {}".format(str(service.idx))
			
			if start_end_rate_error:
				frappe.throw(_("Please enter rate, billable hours and start and end date for services in row {}").format(idx))			
		
			
	
@frappe.whitelist()
def make_service_job_card(source_name, target_doc=None, ignore_permissions=False):
	doclist = get_mapped_doc("Workshop Request", source_name, {
		"Workshop Request": {
			"doctype": "Service Job Card",
			"field_map": {
				"requested_for": "job_done_on",
				"requested_for_docname": "job_done_on_docname",
				"request_type": "job_type",
				"details": "job_description",
				"name": "requested_from"
			}
		}
	})

	return doclist

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
	doclist = get_mapped_doc("Service Job Card", source_name, {
		"Service Job Card": {
			"doctype": "Sales Invoice",
			"field_map": {
				"name": "service_job_card",
			}
		}
	})

	return doclist
