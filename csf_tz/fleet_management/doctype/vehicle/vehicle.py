# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bravo Logistics and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Vehicle(Document):
	pass


@frappe.whitelist(allow_guest=True)		
def change_status(**args):
	args = frappe._dict(args)
	#Edit vehicle status
	vehicle = frappe.get_doc("Vehicle", args.vehicle)
	if args.status != 'Booked':
		vehicle.status = args.status
		vehicle.hidden_status = args.hidden_status
		vehicle.save()
		return 'Vehicle Status Set'
	if args.status == 'Booked' and vehicle.status == 'Available':
		vehicle.status = "Booked"
		vehicle.hidden_status = args.hidden_status
		vehicle.save()
		return 'Vehicle Status Set'
	
			
