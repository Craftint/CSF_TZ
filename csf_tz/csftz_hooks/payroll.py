from __future__ import unicode_literals
import frappe
from frappe import _
import frappe
import os
# from frappe.utils.print_format import download_multi_pdf
from frappe.utils.pdf import get_pdf, cleanup
from PyPDF2 import PdfFileWriter
from csf_tz import console


@frappe.whitelist()
def update_slips(payroll_entry):
    ss_list = frappe.get_all("Salary Slip", filters={
                             "payroll_entry": payroll_entry})
    count = 0
    for salary in ss_list:
        ss_doc = frappe.get_doc("Salary Slip", salary.name)
        if ss_doc.docstatus != 0:
            continue
        ss_doc.validate()
        ss_doc.save()
        count += 1

    frappe.msgprint(_("{0} Salary Slips is updated".format(count)))
    return count


@frappe.whitelist()
def update_slip(salary_slip):
    ss_doc = frappe.get_doc("Salary Slip", salary_slip)
    if ss_doc.docstatus != 0:
        return
    ss_doc.validate()
    ss_doc.save()
    frappe.msgprint(_("Salary Slips is updated"))
    return "True"


@frappe.whitelist()
def print_slips(payroll_entry):
    ss_data = frappe.get_all("Salary Slip", filters={
                             "payroll_entry": payroll_entry})
    ss_list = []
    for i in ss_data:
        ss_list.append(i.name)
    doctype = dict(
        {"Salary Slip": ss_list}
    )

    pdf = download_multi_pdf(doctype, payroll_entry,
                             format="Standard", no_letterhead=1)
    if pdf:
        ret = frappe.get_doc({
            "doctype": "File",
            "attached_to_doctype": "Payroll Entry",
            "attached_to_name": payroll_entry,
            "folder": "Home/Attachments",
            "file_name": payroll_entry + ".pdf",
            "file_url": "/files/" + payroll_entry + ".pdf",
            "content": pdf
        })
        ret.save(ignore_permissions=1)
        frappe.msgprint(_("The PDF file is ready in attatchments"))
        return ret


def download_multi_pdf(doctype, name, format=None, no_letterhead=0):
    output = PdfFileWriter()
    if isinstance(doctype, dict):
        for doctype_name in doctype:
            for doc_name in doctype[doctype_name]:
                try:
                    console(doc_name)
                    output = frappe.get_print(
                        doctype_name, doc_name, format, as_pdf=True, output=output, no_letterhead=no_letterhead)
                except Exception:
                    frappe.log_error("Permission Error on doc {} of doctype {}".format(
                        doc_name, doctype_name))
        frappe.local.response.filename = "{}.pdf".format(name)

    return read_multi_pdf(output)


def read_multi_pdf(output):
    fname = os.path.join(
        "/tmp", "frappe-pdf-{0}.pdf".format(frappe.generate_hash()))
    output.write(open(fname, "wb"))

    with open(fname, "rb") as fileobj:
        filedata = fileobj.read()

    return filedata
