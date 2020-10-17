from __future__ import unicode_literals 
import frappe
from frappe import _


@frappe.whitelist()
def get_job_cards():
    data = frappe.get_list(
        "Job Card", filters={"status": ["in", ["Open","Work In Progress","Material Transferred","On Hold","Submitted"]]}, fields=["*"], limit_page_length=0, order_by='name')
    return data
