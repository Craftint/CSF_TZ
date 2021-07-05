# -*- coding: utf-8 -*-
# Copyright (c) 2021, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


class Piecework(Document):
    def validate(self):
        self.total = self.quantity * frappe.db.get_value(
            "Piecework Type", self.task, "rate"
        )
        employees = []
        amount = self.total / len(self.employees)
        for row in self.employees:
            if row.employee not in employees:
                employees.append(row.employee)
                row.amount = amount
            else:
                frappe.throw(
                    "The employee '{0}' is this duplicate in the table in row {1}".format(
                        row.employee, row.idx
                    )
                )
