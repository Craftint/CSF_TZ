# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
import numpy as np
from frappe import msgprint, _
from frappe.utils.nestedset import get_descendants_of


def execute(filters=None):
    columns = get_columns(filters)

    data = []
    checkin_records = get_checkin_data(filters)
    checkout_records = get_checkout_data(filters)

    if not (checkin_records and checkout_records):
        msgprint(
            "No Record found for the filters From Date: {0},To Date: {1}, Company: {2}, Department: {3} and Employee: {4}\
			you specified...!!!, Please set different filters and Try again..!!!".format(
                frappe.bold(filters.from_date),
				frappe.bold(filters.to_date),
                frappe.bold(filters.company),
                frappe.bold(filters.department),
				frappe.bold(filters.employee),
            )
        )

    else:
        checkin_colnames = [key for key in checkin_records[0].keys()]
        checkin_data = pd.DataFrame.from_records(
            checkin_records, columns=checkin_colnames
        )

        checkout_colnames = [key for key in checkout_records[0].keys()]
        checkout_data = pd.DataFrame.from_records(
            checkout_records, columns=checkout_colnames
        )

        df = checkin_data.merge(
            checkout_data,
            how="inner",
            on=["employee", "employee_name", "department", "shift", "date"],
        )
        df.fillna("empty", inplace=True)

        data += df.values.tolist()

    return columns, data


def get_columns(filters):
    columns = [
        {
            "fieldname": "employee",
            "label": _("Employee No"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "employee_name",
            "label": _("Employee Name"),
            "fieldtype": "Data",
        },
        {"fieldname": "department", "label": _("Department"), "fieldtype": "Data"},
        {"fieldname": "shift", "label": _("Shift"), "fieldtype": "Data"},
        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Date",
        },
        # for checkin
        {
            "fieldname": "actual_checkin_time",
            "label": _("Actual Time to Checkin"),
            "fieldtype": "Time",
        },
        {
            "fieldname": "checkin_time",
            "label": _("Checkin Time"),
            "fieldtype": "Time",
        },
        {
            "fieldname": "late_entry",
            "label": _("Late Entry Grace Period"),
            "fieldtype": "Time",
        },
        {
            "fieldname": "checkin_status",
            "label": _("Checkin Status"),
            "fieldtype": "Data",
        },
        # for checkout
        {
            "fieldname": "actual_checkout_time",
            "label": _("Actual Time to Checkout"),
            "fieldtype": "Time",
        },
        {
            "fieldname": "chechout_time",
            "label": _("Checkout Time"),
            "fieldtype": "Time",
        },
        {
            "fieldname": "early_exit",
            "label": _("Early Exit Grace Period"),
            "fieldtype": "Time",
        },
        {
            "fieldname": "checkout_status",
            "label": _("Checkout Status"),
            "fieldtype": "Data",
        },
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
    return conditions


def get_department(department, company):
    department_list = get_descendants_of("Department", department)
    department_list.append(department)
    return department_list


def get_checkin_data(filters):
    conditions = get_conditions(filters)

    checkin_data = frappe.db.sql("""
		SELECT 
			chec.employee AS employee,
			chec.employee_name AS employee_name,
			emp.department AS department,
			chec.shift AS shift,
			DATE_FORMAT(chec.time, '%%Y-%%m-%%d') AS date,
			DATE_FORMAT(sh.start_time, '%%T') AS actual_checkin_time,
			DATE_FORMAT(chec.time, '%%T') AS checkin_time,
			SEC_TO_TIME(sh.late_entry_grace_period * 60) AS late_entry,
			IF((SUBTIME(TIME(chec.time), SEC_TO_TIME(sh.late_entry_grace_period * 60))) <= sh.start_time, "Early Checkin", "Late Checkin") AS checkin_status
		FROM `tabEmployee Checkin` chec 
			INNER JOIN `tabEmployee` emp ON emp.name = chec.employee and emp.employee_name = chec.employee_name
			INNER JOIN `tabShift Type` sh ON chec.shift = sh.name
		WHERE chec.log_type = "IN" 
        AND chec.shift != ""
        AND emp.default_shift != ""
		AND emp.status = "Active" {conditions}

		UNION ALL

        SELECT 
			chec.employee AS employee,
			chec.employee_name AS employee_name,
			emp.department AS department,
			chec.shift AS shift,
			DATE_FORMAT(chec.time, '%%Y-%%m-%%d') AS date,
			DATE_FORMAT(sh.start_time, '%%T') AS actual_checkin_time,
			DATE_FORMAT(chec.time, '%%T') AS checkin_time,
			SEC_TO_TIME(sh.late_entry_grace_period * 60) AS late_entry,
			IF((SUBTIME(TIME(chec.time), SEC_TO_TIME(sh.late_entry_grace_period * 60))) <= sh.start_time, "Early Checkin", "Late Checkin") AS checkin_status
		FROM `tabEmployee Checkin` chec 
			INNER JOIN `tabEmployee` emp ON emp.name = chec.employee and emp.employee_name = chec.employee_name
			INNER JOIN `tabShift Type` sh ON chec.shift = sh.name
		WHERE chec.log_type = "IN" 
        AND  chec.shift != ""
        AND emp.default_shift = ""
		AND emp.status = "Active" {conditions}

        UNION ALL

		SELECT 
			chec.employee AS employee,
			chec.employee_name AS employee_name,
			emp.department AS department,
			sha.shift_type AS shift,
			DATE_FORMAT(chec.time, '%%Y-%%m-%%d') AS date,
			DATE_FORMAT(sh.start_time, '%%T') AS actual_checkin_time,
			DATE_FORMAT(chec.time, '%%T') AS checkin_time,
			SEC_TO_TIME(sh.late_entry_grace_period * 60) AS late_entry,
			IF((SUBTIME(TIME(chec.time), SEC_TO_TIME(sh.late_entry_grace_period * 60))) <= sh.start_time, "Early Checkin", "Late Checkin") AS checkin_status
		FROM `tabEmployee Checkin` chec
			INNER JOIN `tabEmployee` emp ON emp.name = chec.employee and emp.employee_name = chec.employee_name
			LEFT JOIN `tabShift Assignment` sha ON chec.employee = sha.employee AND chec.employee_name = sha.employee_name
			LEFT JOIN `tabShift Type` sh ON sha.shift_type = sh.name
		WHERE chec.log_type = "IN"
        AND chec.shift = ""
        AND emp.default_shift = ""
		AND emp.status = "Active" {conditions}
		AND sha.start_date BETWEEN %(from_date)s AND %(to_date)s
        
		UNION ALL

        SELECT 
			chec.employee AS employee,
			chec.employee_name AS employee_name,
			emp.department AS department,
			sha.shift_type AS shift,
			DATE_FORMAT(chec.time, '%%Y-%%m-%%d') AS date,
			DATE_FORMAT(sh.start_time, '%%T') AS actual_checkin_time,
			DATE_FORMAT(chec.time, '%%T') AS checkin_time,
			SEC_TO_TIME(sh.late_entry_grace_period * 60) AS late_entry,
			IF((SUBTIME(TIME(chec.time), SEC_TO_TIME(sh.late_entry_grace_period * 60))) <= sh.start_time, "Early Checkin", "Late Checkin") AS checkin_status
		FROM `tabEmployee Checkin` chec 
			INNER JOIN `tabEmployee` emp ON emp.name = chec.employee and emp.employee_name = chec.employee_name
			INNER JOIN `tabShift Assignment` sha ON chec.employee = sha.employee AND chec.employee_name = sha.employee_name
			INNER JOIN `tabShift Type` sh ON sha.shift_type = sh.name
		WHERE chec.log_type = "IN"
        AND chec.shift = ""
        AND emp.default_shift != ""
		AND emp.status = "Active" {conditions}
		AND sha.start_date BETWEEN %(from_date)s AND %(to_date)s
		""".format(conditions=conditions), filters, as_dict=1,
    )

    return checkin_data


def get_checkout_data(filters):
    conditions = get_conditions(filters)

    checkout_data = frappe.db.sql(
        """
		SELECT 
			chec.employee AS employee,
			chec.employee_name AS employee_name,
			emp.department AS department,
			chec.shift AS shift,
			DATE_FORMAT(chec.time, '%%Y-%%m-%%d') AS date,
			DATE_FORMAT(sh.end_time, '%%T') AS actual_checkout_time,
			DATE_FORMAT(chec.time, '%%T') AS checkin_time,
			SEC_TO_TIME(sh.early_exit_grace_period * 60) AS early_exit,
			IF((ADDTIME(TIME(chec.time), SEC_TO_TIME(sh.early_exit_grace_period * 60))) >= sh.end_time, "Late Checkout", "Early Checkout") AS checkout_status
		FROM `tabEmployee Checkin` chec 
			INNER JOIN `tabEmployee` emp ON emp.name = chec.employee and emp.employee_name = chec.employee_name
			INNER JOIN `tabShift Type` sh ON chec.shift = sh.name
		WHERE chec.log_type = "OUT" 
        AND chec.shift != ""
        AND emp.default_shift != ""
		AND emp.status = "Active" {conditions}

		UNION ALL

		SELECT 
			chec.employee AS employee,
			chec.employee_name AS employee_name,
			emp.department AS department,
			chec.shift AS shift,
			DATE_FORMAT(chec.time, '%%Y-%%m-%%d') AS date,
			DATE_FORMAT(sh.end_time, '%%T') AS actual_checkout_time,
			DATE_FORMAT(chec.time, '%%T') AS checkin_time,
			SEC_TO_TIME(sh.early_exit_grace_period * 60) AS early_exit,
			IF((ADDTIME(TIME(chec.time), SEC_TO_TIME(sh.early_exit_grace_period * 60))) >= sh.end_time, "Late Checkout", "Early Checkout") AS checkout_status
		FROM `tabEmployee Checkin` chec
			INNER JOIN `tabEmployee` emp ON emp.name = chec.employee and emp.employee_name = chec.employee_name
			INNER JOIN `tabShift Type` sh ON chec.shift = sh.name
		WHERE chec.log_type = "OUT" 
        AND chec.shift != ""
        AND emp.default_shift = ""
		AND emp.status = "Active" {conditions}

        UNION ALL

		SELECT 
			chec.employee AS employee,
			chec.employee_name AS employee_name,
			emp.department AS department,
			sha.shift_type AS shift,
			DATE_FORMAT(chec.time, '%%Y-%%m-%%d') AS date,
			DATE_FORMAT(sh.end_time, '%%T') AS actual_checkout_time,
			DATE_FORMAT(chec.time, '%%T') AS checkin_time,
			SEC_TO_TIME(sh.early_exit_grace_period * 60) AS early_exit,
			if((ADDTIME(TIME(chec.time), SEC_TO_TIME(sh.early_exit_grace_period * 60))) >= sh.end_time, "Late Checkout", "Early Checkout") AS checkout_status
		FROM `tabEmployee Checkin` chec
			INNER JOIN `tabEmployee` emp ON emp.name = chec.employee and emp.employee_name = chec.employee_name
			LEFT JOIN `tabShift Assignment` sha ON chec.employee = sha.employee AND chec.employee_name = sha.employee_name
			LEFT JOIN `tabShift Type` sh ON sha.shift_type = sh.name
		WHERE chec.log_type = "OUT" 
        AND chec.shift = ""
        AND emp.default_shift = ""
		AND emp.status = "Active" {conditions}
		AND sha.start_date BETWEEN %(from_date)s AND %(to_date)s

        UNION ALL

		SELECT 
			chec.employee AS employee,
			chec.employee_name AS employee_name,
			emp.department AS department,
			sha.shift_type AS shift,
			DATE_FORMAT(chec.time, '%%Y-%%m-%%d') AS date,
			DATE_FORMAT(sh.end_time, '%%T') AS actual_checkout_time,
			DATE_FORMAT(chec.time, '%%T') AS checkin_time,
			SEC_TO_TIME(sh.early_exit_grace_period * 60) AS early_exit,
			IF((ADDTIME(TIME(chec.time), SEC_TO_TIME(sh.early_exit_grace_period * 60))) >= sh.end_time, "Late Checkout", "Early Checkout") AS checkout_status
		FROM `tabEmployee Checkin` chec
			INNER JOIN `tabEmployee` emp ON emp.name = chec.employee and emp.employee_name = chec.employee_name
			INNER JOIN `tabShift Assignment` sha ON chec.employee = sha.employee AND chec.employee_name = sha.employee_name
			INNER JOIN `tabShift Type` sh ON sha.shift_type = sh.name
		WHERE chec.log_type = "OUT" 
        AND chec.shift = ""
        AND emp.default_shift != ""
		AND emp.status = "Active" {conditions}
		AND sha.start_date BETWEEN %(from_date)s AND %(to_date)s
		""".format(conditions=conditions), filters, as_dict=1,
    )

    return checkout_data