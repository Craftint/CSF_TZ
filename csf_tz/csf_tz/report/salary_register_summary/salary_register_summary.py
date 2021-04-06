# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe.utils import flt
from frappe import _
from erpnext.hr.doctype.department.department import get_children


def execute(filters=None):
    columns = [{
        "fieldname": "salary_component",
        "label": _("Salary Component"),
        "fieldtype": "Data",
        "width": 300
    },
        {
        "fieldname": "total",
        "label": _("Total"),
        "fieldtype": "Float",
        "width": 300
    }]
    data = get_data(filters)
    return columns, data


def get_data(filters=None):
    if not filters:
        filters = {}
    currency = None
    data = []
    if filters.get('currency'):
        currency = filters.get('currency')
    company_currency = erpnext.get_company_currency(filters.get("company"))
    salary_slips = get_salary_slips(filters, company_currency)
    if not salary_slips:
        return []
    ss_earning_map = get_ss_earning_map(
        salary_slips, currency, company_currency)
    data.extend(ss_earning_map)

    # ss_ded_map = get_ss_ded_map(salary_slips, currency, company_currency)
    # data.extend(ss_ded_map)
    return data


def get_salary_slips(filters, company_currency):
    filters.update({"from_date": filters.get("from_date"),
                    "to_date": filters.get("to_date")})
    conditions, filters = get_conditions(filters, company_currency)
    salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
        order by employee""" % conditions, filters, as_dict=1)

    return salary_slips or []


def get_ss_earning_map(salary_slips, currency, company_currency):
    ss_earnings = frappe.db.sql("""select sd.salary_component, SUM(sd.amount) as total
        from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)
        GROUP BY sd.salary_component """ %
                                (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

    return ss_earnings


def get_ss_ded_map(salary_slips, currency, company_currency):
    ss_deductions = frappe.db.sql("""select sd.salary_component, SUM(sd.amount) as total
        from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)
        GROUP BY sd.salary_component """ %
                                  (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)
    return ss_deductions


def get_conditions(filters, company_currency):
    conditions = ""
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

    if filters.get("docstatus"):
        conditions += "docstatus = {0}".format(
            doc_status[filters.get("docstatus")])

    if filters.get("from_date"):
        conditions += " and start_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " and end_date <= %(to_date)s"
    if filters.get("company"):
        conditions += " and company = %(company)s"
    if filters.get("employee"):
        conditions += " and employee = %(employee)s"
    if filters.get("currency") and filters.get("currency") != company_currency:
        conditions += " and currency = %(currency)s"
    if filters.get("department") and filters.get("company"):
        department_list = get_departments(
            filters.get("department"), filters.get("company"))
        conditions += 'and department in (' + ','.join(
            ("'"+n+"'" for n in department_list)) + ')'

    return conditions, filters


def get_departments(department, company):
    departments_list = [department]
    data = get_children("Department", department, company)
    for el in data:
        departments_list.append(el.get("value"))
    return departments_list
