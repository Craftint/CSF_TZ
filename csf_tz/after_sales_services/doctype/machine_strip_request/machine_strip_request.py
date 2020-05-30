# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import _

class MachineStripRequest(Document):
	pass



@frappe.whitelist()
def make_job_card(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, doc):
		doc.job_type = "Machine Parts Strip"
		doc.append('items', {
			"item_code": source.stripped_item_code,
			"requested_for": 'Serial No',
			"serial_number": source.stripped_serial_no
		})
		doc.append('items', {
			"item_code": source.target_item_code,
			"requested_for": 'Serial No',
			"serial_number": source.target_serial_no
		})
		description = 'Parts strip job from {} {} to {} {} for items: \n'.format(source.stripped_item_code, source.stripped_serial_no, source.target_item_code, source.target_serial_no)
		for item in source.stripped_items:
			description += '{} {} {} \n'.format(item.item, item.qty, item.uom)
		doc.job_description = description
		
	docs = get_mapped_doc("Machine Strip Request", source_name, {
        "Machine Strip Request": {
            "doctype": "Job Card",
            "field_map": {
                "name": "machine_strip_request"
            },
        }
    }, target_doc, postprocess, ignore_permissions=ignore_permissions)
	return docs
