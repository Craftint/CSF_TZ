# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ReferencePaymentTable(Document):
	pass
	

def update_child_table(self, fieldname, df=None):
	'''Updated function to prevent saving of approved or rejected funds request'''
	'''sync child table for given fieldname'''
	rows = []
	if not df:
		df = self.meta.get_field(fieldname)

	for d in self.get(df.fieldname):
		if df.fieldname in ["requested_funds", "main_requested_funds", "return_requested_funds"]:
			if d.get("request_status") not in ["Approved", "Rejected"]:
				d.db_update()
		else:
			d.db_update()
		rows.append(d.name)

	if df.options in (self.flags.ignore_children_type or []):
		# do not delete rows for this because of flags
		# hack for docperm :(
		return

	if rows:
		# select rows that do not match the ones in the document
		deleted_rows = frappe.db.sql("""select name from `tab{0}` where parent=%s
			and parenttype=%s and parentfield=%s
			and name not in ({1})""".format(df.options, ','.join(['%s'] * len(rows))),
				[self.name, self.doctype, fieldname] + rows)
		if len(deleted_rows) > 0:
			# delete rows that do not match the ones in the document
			frappe.db.sql("""delete from `tab{0}` where name in ({1})""".format(df.options,
				','.join(['%s'] * len(deleted_rows))), tuple(row[0] for row in deleted_rows))

	else:
		# no rows found, delete all rows
		frappe.db.sql("""delete from `tab{0}` where parent=%s
			and parenttype=%s and parentfield=%s""".format(df.options),
			(self.name, self.doctype, fieldname))
