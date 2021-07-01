# Copyright (c) 2021, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from csf_tz import console

class SQLCommand(Document):
	def on_submit(self):
		delete_allowed = frappe.get_value("CSF TZ Settings", "CSF TZ Settings", "allow_delete_in_sql_command")
		if "DELETE" in self.sql_text:
			return

		if self.doctype:
			if delete_allowed and not self.sql_text and self.doctype_name and self.names:
				frappe.db.sql("DELETE FROM `tab" + self.doctype_name + "` WHERE NAME IN (" + self.names + ")")
				# frappe.db.sql("select * from `tabBin` where warehouse = %s", self.name, as_dict=1)
				frappe.db.commit()
		else:
			if "UPDATE tab" in self.sql_text or "UPDATE `tab" in self.sql_text:
				return
			frappe.msgprint(str(frappe.db.sql(self.sql_text, as_dict=1)))
