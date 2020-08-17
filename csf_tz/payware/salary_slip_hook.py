from __future__ import unicode_literals
import frappe
from frappe import msgprint,throw, _
import json

@frappe.whitelist()
def generate_component_in_salary_slip_update(doc, method):
	if not doc.name.upper().startswith("NEW") and frappe.db.get_single_value('Payware Settings', 'ot_module'):
		base = None
		list = []

		for component in doc.earnings:
			if str(component.salary_component).upper() == "BASIC":
				base = component.amount / doc.payment_days * doc.total_working_days
				list.append(component)
		if base == None:
			frappe.msgprint("Basic Component not Found for " + str(doc.name))

		for component in doc.salary_slip_ot_component:
			earning_dict = frappe.new_doc("Salary Detail")
			earning_dict.parent = doc.name
			earning_dict.parenttype = doc.doctype
			earning_dict.parentfield = "earnings"
			earning_dict.salary_component = component.salary_component
			earning_dict.amount = calculate_amount(base,component.no_of_hours,component.salary_component)
			list.append(earning_dict)

			doc.earnings = []
			doc.earnings.extend(list)
			doc.calculate_net_pay()

@frappe.whitelist()
def generate_component_in_salary_slip_insert(doc, method):
	if frappe.db.get_single_value('Payware Settings', 'ot_module'):
		doc.salary_slip_ot_component = []
		employee = frappe.get_doc("Employee",doc.employee)
		doc.run_method("get_emp_and_leave_details")
		base = None
		list = []
		for component in doc.earnings:
			if str(component.salary_component).upper() == "BASIC":
				base = component.amount / doc.payment_days * doc.total_working_days
				list.append(component)
		if base == None:
			frappe.throw("Basic Component not Found")
		for component in employee.employee_ot_component:
			component.doctype = "Salary Slip OT Component"
			component.parentfield = "salary_slip_ot_component"
			doc.salary_slip_ot_component.append(component)

			earning_dict = frappe.new_doc("Salary Detail")
			earning_dict.parent = doc.name
			earning_dict.parenttype = doc.doctype
			earning_dict.parentfield = "earnings"
			earning_dict.salary_component = component.salary_component
			earning_dict.amount = calculate_amount(base,component.no_of_hours,component.salary_component)
			list.append(earning_dict)

			doc.earnings = []
			doc.earnings.extend(list)
			doc.calculate_net_pay()

@frappe.whitelist()
def calculate_amount(base,no_of_hours,salary_component):
	working_hours_per_month = frappe.db.get_single_value('Payware Settings', 'working_hours_per_month')
	component = frappe.get_doc("Salary Component",salary_component)
	if component and component.based_on_hourly_rate:
		calc = (float(base)/ float(working_hours_per_month)) *  float(no_of_hours) * (float(component.hourly_rate) / 100)
		return calc
	else:
		frappe.msgprint("Hourly Rate not Found")

@frappe.whitelist()
def test():
	return "hello"
