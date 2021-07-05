# Copyright (c) 2021, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import random_string
import json


class PieceworkSalaryDisbursement(Document):
    def validate(self):
        self.set_values()

    def before_submit(self):
        self.create_additional_salaries()

    def set_values(self):
        data = {}
        piecework_list = frappe.get_all(
            "Piecework",
            filters={
                "docstatus": 1,
                "company": self.company,
                "date": ["between", [self.start_date, self.end_date]],
            },
        )
        piecework_list = [i.name for i in piecework_list]
        piecework_items_list = frappe.get_all(
            "Piecework Payment Allocation",
            filters={
                "parent": ["in", piecework_list],
                "disbursement_row": ["in", ["", None]],
            },
            fields=["*"],
        )
        for i in piecework_items_list:
            if i.disbursement_row:
                continue
            if not data.get(i.employee):
                data[i.employee] = {"amount": 0, "links": []}
            emp = data[i.employee]
            emp["employee_name"] = i.employee_name
            emp["amount"] += i.amount
            emp["links"].append(
                {
                    "doctype": "Piecework Payment Allocation",
                    "docname": i.name,
                    "amount": i.amount,
                }
            )

        singels_list = frappe.get_all(
            "Piecework Single",
            filters={
                "docstatus": 1,
                "company": self.company,
                "date": ["between", [self.start_date, self.end_date]],
            },
        )
        singels_list = [i.name for i in singels_list]
        singels_items_list = frappe.get_all(
            "Single Piecework Employees",
            filters={
                "parent": ["in", singels_list],
                "disbursement_row": ["in", ["", None]],
            },
            fields=["*"],
        )
        for e in singels_items_list:
            if e.disbursement_row:
                continue
            if not data.get(e.employee):
                data[e.employee] = {"amount": 0, "links": []}
            emp = data[e.employee]
            emp["employee_name"] = e.employee_name
            emp["amount"] += e.amount
            emp["links"].append(
                {
                    "doctype": "Single Piecework Employees",
                    "docname": e.name,
                    "amount": e.amount,
                }
            )

        self.employee = []
        for key, value in data.items():
            row = self.append("employee", {})
            row.employee = key
            row.employee_name = value.get("employee_name")
            row.amount = value.get("amount")
            row.links = json.dumps(value.get("links"))
            row.name = random_string(15)

    def create_additional_salaries(self):
        if self.earning_salary_component:
            for row in self.employee:
                if row.employee and row.amount:
                    as_doc = frappe.new_doc("Additional Salary")
                    as_doc.employee = row.employee
                    as_doc.salary_component = self.earning_salary_component
                    as_doc.amount = row.amount
                    as_doc.payroll_date = self.payroll_date
                    as_doc.company = self.company
                    as_doc.overwrite_salary_structure_amount = 0
                    as_doc.insert(ignore_permissions=True)
                    row.earning_additional_salary = as_doc.name

                    links = json.loads(row.links)
                    for link in links:
                        link_doc = frappe.get_doc(
                            link.get("doctype"), link.get("docname")
                        )
                        link_doc.additional_salary = as_doc.name
                        link_doc.disbursement = self.name

                        link_doc.disbursement_row = row.name
                        link_doc.save(ignore_permissions=True)

                    as_doc.submit()
                    frappe.msgprint(
                        _("Additional Salary {0} created for employee {1}").format(
                            as_doc.name, row.employee
                        ),
                        alert=True,
                    )

        if self.deduction_salary_component:
            for row in self.employee:
                if row.employee and row.amount:
                    as_doc = frappe.new_doc("Additional Salary")
                    as_doc.employee = row.employee
                    as_doc.salary_component = self.deduction_salary_component
                    as_doc.amount = row.amount
                    as_doc.payroll_date = self.payroll_date
                    as_doc.company = self.company
                    as_doc.overwrite_salary_structure_amount = 0
                    as_doc.insert(ignore_permissions=True)
                    row.deduction_additional_salary = as_doc.name
                    as_doc.submit()
                    frappe.msgprint(
                        _("Additional Salary {0} created for employee {1}").format(
                            as_doc.name, row.employee
                        ),
                        alert=True,
                    )
