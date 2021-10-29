# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
import numpy as np
import datetime
from frappe import msgprint, _
from frappe.utils.nestedset import get_descendants_of


def execute(filters=None):
    conditions, filters = get_conditions(filters)

    columns = get_columns(filters)

    data = []
    checkin_data = get_data(conditions, filters)

    if checkin_data: data += checkin_data
    
    return columns, data


def get_columns(filters):
    columns = [
        {"fieldname": "employee", "label": _("Employee No"), "fieldtype": "Data"},
        {"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data"},
        {"fieldname": "department", "label": _("Department"), "fieldtype": "Data"},
        {"fieldname": "shift", "label": _("Shift"), "fieldtype": "Data"},
        {"fieldname": "date", "label": _("Date"), "fieldtype": "Date"},

        # for checkin
        {"fieldname": "actual_checkin_time", "label": _("Actual Time to Checkin"), "fieldtype": "Time"},
        {"fieldname": "checkin_time", "label": _("Checkin Time"), "fieldtype": "Time"},
        {"fieldname": "late_grace_time", "label": _("Late Entry Grace Period"), "fieldtype": "Time"},
        {"fieldname": "checkin_status", "label": _("Checkin Status"), "fieldtype": "Data"},

        # for checkout
        # {
        #     "fieldname": "actual_checkout_time",
        #     "label": _("Actual Time to Checkout"),
        #     "fieldtype": "Time",
        # },
        # {
        #     "fieldname": "checkout_time",
        #     "label": _("Checkout Time"),
        #     "fieldtype": "Time",
        # },
        # {
        #     "fieldname": "early_exit",
        #     "label": _("Early Exit Grace Period"),
        #     "fieldtype": "Time",
        # },
        # {
        #     "fieldname": "checkout_status",
        #     "label": _("Checkout Status"),
        #     "fieldtype": "Data",
        # },
    ]
    return columns


def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " AND DATE(chec.time) >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND DATE(chec.time) <= %(to_date)s"
    if filters.get("company"):
        conditions += " AND emp.company = %(company)s"
    if filters.get("department") and filters.get("company"):
        department_list = get_department(
            filters.get("department"), filters.get("company")
        )
        conditions += (
            "AND emp.department in ("
            + ", ".join(("'" + d + "'" for d in department_list))
            + ")"
        )
    if filters.get("employee"):
        conditions += " AND emp.employee = %(employee)s"
    return conditions, filters

def get_department(department, company):
    department_list = get_descendants_of("Department", department)
    department_list.append(department)
    return department_list

def get_data(conditions, filters):
    checkin_data = [],
    # checkout_data = []
    employee_checkin_data = get_employee_data(conditions, filters)

    chift_type_details = frappe.get_all("Shift Type", ["name", "start_time", "end_time", "late_entry_grace_period", "early_exit_grace_period"])
    msgprint("chift_type_details: " + str(chift_type_details))
    
    for employee in employee_checkin_data:
        for shift in chift_type_details:
            if employee.shift == shift.name and employee.log_type == "IN":
                late_grace_time = datetime.time(0, shift.late_entry_grace_period)
                # checkin_time = employee["datetime_as"].strftime("%H:%M:%S")
                time_diff = employee["checkin_time"] - late_grace_time
                if time_diff <= shift.start_time:
                    checkin_status = "Early Checkin"
                else:
                    checkin_status = "Late Checkin"

                complete_row = employee.update({
                    "actual_checkin_time": shift.start_time,
                    "checkin_time": employee.checkin_time,
                    "late_grace_time": late_grace_time,
                    "checkin_status": checkin_status
                })
                checkin_data.append(complete_row)

            if not employee.shift and employee.log_type == "IN":
                employee.update({
                    "checkin_time": employee.checkin_time
                })
                checkin_data.append(employee)

            # if em.shift == shift.name and em.log_type == "OUT":
            #     complete_em = em.update({
            #         "actual_checkout_time": shift.end_time,
            #         "late_checkout_time": shif.early_exit_grace_period
            #     })
            #     checkout_data.append(complete_em)

            # if not em.shift and em.log_type == "OUT":
            #     checkout_data.append(em)
    msgprint("checkin_data: " + str(checkin_data))

    return checkin_data

def get_employee_data(conditions, filters):
    employee_data = []
    checkin_details = get_checkin_details(conditions, filters)
    
    assignment_details = frappe.db.get_all("Shift Assignment", 
        filters=[
            ["start_date", "between", [filters.from_date, filters.to_date]],
            ["company", "=", filters.company], ["department", "=", filters.department], 
            ["employee", "=", filters.employee]
        ],
        fields=["employee", "employee_name", "company", "shift_type", "start_date", "end_date"]
    )
    msgprint("assignment_details: " + str(assignment_details))

    for chec in checkin_details:
        for assignment in assignment_details:
            if (chec["employee"] == assignment["employee"] and 
                (assignment["start_date"] <= chec["date"] <= assignment["end_date"])
                and not chec.shift):
                chec.update({"shift": assignment["shift_type"]})
                employee_data.append(chec)

    msgprint("employee_data: " + str(employee_data))
    return employee_data

def get_checkin_details(conditions, filters):
    msgprint("filters: "+str(filters))
    data = frappe.db.sql("""
        SELECT 
			chec.employee AS employee,
			chec.employee_name AS employee_name,
			emp.department AS department,
			chec.shift AS shift,
			DATE_FORMAT(chec.time, '%%Y-%%m-%%d') AS date,
            DATE_FORMAT(chec.time, '%%T') AS checkin_time,
            chec.log_type
		FROM `tabEmployee Checkin` chec 
			INNER JOIN `tabEmployee` emp ON emp.name = chec.employee and emp.employee_name = chec.employee_name
		WHERE chec.log_type = "IN" {conditions}
    """.format(conditions=conditions), filters, as_dict=1)
    return data


# def gg_data(filters):
#     checkin_records, checkout_records = get_data(conditions, filters)
#     checkin_status = ""
#     for record in checkin_records:
#         if record.late_entry_grace_period:
#             late_grace_time = datetime.time(0, record["late_entry_grace_period"])
#             checkin_time = record["datetime_as"].strftime("%H:%M:%S")
#             time_diff = checkin_time - late_grace_time
#             if time_diff <= record.actual_checkin_time:
#                 checkin_status = "Early Checkin"
#             else:
#                 checkin_status = "Late Checkin"

#             d.update({
#                 "late_grace_time": late_grace_time,
#                 "checkin_status": checkin_status
#             })
#         else:
#             continue
    
#     return 

