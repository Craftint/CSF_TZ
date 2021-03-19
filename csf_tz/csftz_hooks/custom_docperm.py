import frappe
from frappe import _
from frappe.utils.csvutils import getlink

def grant_dependant_access(doc, method):
    if doc.dependent:
        frappe.msgprint(_("Warning! {0} is a dependant doctype. If you wish to change access to it, remove it and add again.").format(getlink("DocType", doc.parent)))
        return
    fields = frappe.get_meta(doc.parent).fields
    # console(fields)
    doctypes_granted_access = []
    for field in fields:
        if field.get("fieldtype") in ["Link", "Dynamic Link"]:
            doctypes_granted_access += [field.options]
            create_custom_docperm(field.options, doc.role)
        if field.get("fieldtype") in ["Table"]:
            child_fields = frappe.get_meta(field.name).fields
            for child_field in child_fields:
                if child_field.get("fieldtype") in ["Link", "Dynamic Link"]:
                    doctypes_granted_access += [field.options]
                    create_custom_docperm(child_field.options, doc.role)
    if len(doctypes_granted_access) > 0:
        frappe.msgprint(_("Auto granted SELECT access to the following doctypes " + str(doctypes_granted_access)))

def create_custom_docperm(doctype, role):
    is_permission_exists = frappe.get_all("Custom DocPerm", filters = {"parent": doctype, "role": role})
    if len(is_permission_exists) > 0:
        return
    custom_docperm = frappe.new_doc("Custom DocPerm")
    custom_docperm.parent = doctype
    custom_docperm.role = role
    custom_docperm.permlevel = 0
    custom_docperm.select = 1
    custom_docperm.read = 0
    custom_docperm.dependent = 1
    custom_docperm.db_update()
