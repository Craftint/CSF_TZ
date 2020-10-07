from __future__ import unicode_literals
import frappe
from frappe import _
# from csf_tz import console


@frappe.whitelist()
def update_slips(payroll_entry):
    ss_list = frappe.get_all("Salary Slip",filters = {"payroll_entry": payroll_entry})
    count = 0
    for salary in ss_list:
        ss_doc = frappe.get_doc("Salary Slip", salary.name)
        if ss_doc.docstatus != 0:
            continue
        # console(salary.name)
        ss_doc.validate()
        ss_doc.save()
        count += 1
    
    frappe.msgprint(_("{0} Payroll Entrys is updated".format(count)))
    return count