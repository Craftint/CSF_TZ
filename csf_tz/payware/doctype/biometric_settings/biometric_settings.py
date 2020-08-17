# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import requests
from requests.exceptions import Timeout
import json
from frappe.utils import today, get_datetime, add_to_date, getdate


class BiometricSettings(Document):
	pass


def get_url():
	if frappe.db.get_value("Biometric Settings", None, "server_url"):
		url = frappe.db.get_value("Biometric Settings", None, "server_url")
		return url
	else:
		frappe.throw(_("Please set server URL"))

def get_bio_token():
	if frappe.db.get_value("Biometric Settings", None, "bio_token"):
		bio_token = frappe.db.get_value("Biometric Settings", None, "bio_token")
		return bio_token
	else:
		frappe.throw(_("Please make sure you have Bio Token"))

def get_headers():
	headers = {'Authorization': "Token " +  get_bio_token()}
	return headers

def get_user_name():
	if frappe.db.get_value("Biometric Settings", None, "user_name"):
		user_name = frappe.db.get_value("Biometric Settings", None, "user_name")
		return user_name
	else:
		frappe.throw(_("Please set User Name"))

def get_password():
	if frappe.db.get_value("Biometric Settings", None, "password"):
		password = frappe.db.get_value("Biometric Settings", None, "password")
		return password
	else:
		frappe.throw(_("Please set Password"))

def get_default_shift_type():
	if frappe.db.get_value("Biometric Settings", None, "default_shift_type"):
		default_shift_type = frappe.db.get_value("Biometric Settings", None, "default_shift_type")
		return default_shift_type
	else:
		frappe.throw(_("Please set the Default Shift Type"))

def get_employee_default_shift(employee_name= None):
	if not employee_name:
		return
	else:
		if frappe.db.get_value("Employee", employee_name, "default_shift"):
			default_shift_type = frappe.db.get_value("Employee", employee_name, "default_shift")
			return default_shift_type

def get_shift_type(employee_name=None):
	if not employee_name:
		get_default_shift_type()
	else:
		if get_employee_default_shift(employee_name):
			return get_employee_default_shift(employee_name)
		else:
			return get_default_shift_type()


def get_department():
	if frappe.db.get_value("Biometric Settings", None, "department"):
		department = frappe.db.get_value("Biometric Settings", None, "department")
		if department == 0:
			frappe.throw(_("Please set Default Department Code Other than 0"))
		else:
			return department
	else:
		frappe.throw(_("Please set Default Department Code"))

def get_area_code():
	if frappe.db.get_value("Biometric Settings", None, "area_code"):
		area_code = [frappe.db.get_value("Biometric Settings", None, "area_code")]
		if area_code == [0] :
			frappe.throw(_("Please set Default Area Code Other than 0"))
		else:
			return area_code
	else:
		frappe.throw(_("Please set Default Area Code"))

def get_employee_name_id(id):
	if id :
		employee_name_list = frappe.db.sql_list("""select name from `tabEmployee`
			where biometric_id=%s """, (id))
		if employee_name_list:
			employee_name = employee_name_list[0]
			return employee_name
	else:
		frappe.throw(_("No employee has this identity: ") + str(id))


def check_master_enable():
	enable_biometric_master = frappe.db.get_value("Biometric Settings", None, "enable_biometric_master") or 0
	if int(enable_biometric_master) == 1:
		return True
	else:
		return False


def check_employee_enable(emp):
    if frappe.db.get_value("Employee", emp, "enable_biometric"):
        enable_biometric = frappe.db.get_value("Employee", emp, "enable_biometric") 
        if int(enable_biometric) == 1:
            return True
        else:
            return False
    else:
        return False


@frappe.whitelist()
def auto_shift_assignment_for_active_today():
	if check_master_enable():
		auto_shift = frappe.db.get_value("Biometric Settings", None, "auto_shift")
		if int(auto_shift) == 1:
			creat_shift_assignment_for_active_today()


@frappe.whitelist()
def auto_make_employee_checkin():
	if check_master_enable():
		auto_checkin = frappe.db.get_value("Biometric Settings", None, "auto_checkin")
		if int(auto_checkin) == 1:
			make_employee_checkin()


@frappe.whitelist()
def auto_get_transactions():
	if check_master_enable():
		auto_transactions = frappe.db.get_value("Biometric Settings", None, "auto_transactions")
		if int(auto_transactions) == 1:
			get_transactions()



@frappe.whitelist()
def get_new_bio_token():
	url = get_url() + "/api-token-auth/"
	data  = {
			"username": get_user_name(),
    		"password": get_password()
			} 
	response = requests.post(url = url, data = data)
	if response.status_code == 200 :
		res = json.loads(response.text)
		bio_token = res["token"]
		return bio_token
	else:
		frappe.throw(_("Please double check your username, password and URL"))


@frappe.whitelist()
def check_employee_bio_info(doc, method):
	if check_master_enable() and check_employee_enable(doc.name):
		if doc.company:
				abbr = frappe.get_cached_value('Company',  doc.company,  'abbr')
		if doc.name :
			emp_code = abbr + "-" + doc.name
			if doc.biometric_id:
				biometric_id = doc.biometric_id
				url = get_url() + "/personnel/api/employees/" + biometric_id +"/"
				try:
					response = requests.get(url = url, headers = get_headers(), timeout=5)
				except Timeout:
					frappe.msgprint(_("Error Please check Biotime server Request timeout"))
				else:
					if response.status_code == 200 :
						res = json.loads(response.text)
						emp_id = str(res["id"])
						doc.biometric_id = emp_id
						if not doc.biometric_code:
							doc.biometric_code = str(res["emp_code"])
						if not doc.area:
							for area_item in res["area"]:
								area_row = doc.append('area',{})
								area_row.area = area_item['area_name']
								area_row.area_code = area_item['area_code']
						update_employee_bio(doc,emp_id)
					else:
						add_employee_bio(doc,emp_code)
			else:
				add_employee_bio(doc,emp_code)


def add_employee_bio(doc,emp_code):
	if doc.name :
		if doc.area:
			area = []
			for row in doc.area:
				area_row = row.area_code
				area.append(area_row)
		else:
			area = get_area_code()
		url = get_url() + "/personnel/api/employees/"
		data  ={
				"emp_code": emp_code,
				"first_name": doc.employee_name,
				"area": area,
				"department": get_department()
				}
		try:
			response = requests.post(url = url, headers = get_headers(), data = data, timeout = 5)
		except Timeout:
			frappe.msgprint(_("Error Please check Biotime server Request timeout"))
		else:	
			if response.status_code == 200 or response.status_code == 201 :
				res = json.loads(response.text)
				first_name = res["first_name"]
				emp_id = res["id"]
				doc.biometric_id = emp_id
				doc.biometric_code = emp_code
				frappe.msgprint(_("Creatin Employee biometric ") + str(emp_code))
				return emp_id
			else:
				frappe.throw(_("Error Creating Employee biometric "))


def update_employee_bio(doc,emp_id):
	if doc.name :
		if doc.area:
			area = []
			for row in doc.area:
				area_row = row.area_code
				area.append(area_row)
		else:
			area = get_area_code()
		url = get_url() + "/personnel/api/employees/" + emp_id +"/"
		data  ={
				"first_name": doc.employee_name,
				"emp_code": doc.biometric_code,
				"area": area,
				"department": get_department()
				}
		try:
			response = requests.patch(url = url, headers = get_headers(), data = data, timeout=5)
		except Timeout:
			frappe.msgprint(_("Error Please check Biotime server Request timeout"))
		else:	
			if response.status_code == 200 :
				return emp_id
			else:
				frappe.throw(_("Error Updating Employee biometric info ") +emp_id)



def check_transactions_id_is_unique(id):
		if id :
			names = frappe.db.sql_list("""select name from `tabTransactions Log`
				where id=%s """, (id))
			if names:
				return False
			else:
				return True


def update_default_shift_type_last_sync(name,datetime):
	frappe.db.set_value("Shift Type", name, "last_sync_of_checkin", datetime)


@frappe.whitelist()
def get_transactions(start_time= None,end_time=None):
	if check_master_enable():
		if not start_time:
			start_time = today()
		if not end_time:
			end_time = 	str(get_datetime())
		if str(get_datetime(start_time)) == end_time:
			start_time = add_to_date(start_time,days=-1)
		space = "\n" * 2
		tf_log_name = creat_transaction_fetch_log(start_time,end_time)
		start = "start_time=" + start_time
		end = "end_time=" + end_time
		url = get_url() + "/iclock/api/transactions/?" + start + "&" + end
		try:
			response = requests.get(url = url, headers = get_headers(), timeout=5)
		except Timeout:
			tf_log_doc = frappe.get_doc("Transaction Fetch Log",tf_log_name)
			tf_log_doc.status = "Error"
			if not tf_log_doc.log:
				tf_log_doc.log = ""
			tf_log_doc.log = tf_log_doc.log + space + str("Timeout Eroor")
			tf_log_doc.save()
			return "Error"
		else:
			if response.status_code == 200 :
				res = json.loads(response.text)
				count = res["count"]
				get_transaction_pages(count,start_time,end_time,tf_log_name)
				tf_log_doc = frappe.get_doc("Transaction Fetch Log",tf_log_name)
				tf_log_doc.status = "Success"
				tf_log_doc.save()
				return "Success" 
			
			else:
				tf_log_doc.status = "Error"
				res = json.loads(response.text)
				if not tf_log_doc.log:
					tf_log_doc.log = ""
				tf_log_doc.log = tf_log_doc.log + space + str(res)
				tf_log_doc.save()
				return "Error"


def get_transaction_pages(count,start_time,end_time,tf_log_name):
	unique_list = []
	repeated_list =[]
	space = "\n" * 2
	tf_log_doc = frappe.get_doc("Transaction Fetch Log",tf_log_name)
	if count%10 :
		times = count//10 + 1
	else:
		times = count//10
	n = 1
	tf_log_doc.count = count
	tf_log_doc.page = times
	tf_log_doc.save()
	while n <= times:
		start = "start_time=" + start_time
		end = "end_time=" + end_time
		page ="page=" +  str(n)
		url = get_url() + "/iclock/api/transactions/?" + start + "&" + end + "&" + page
		response = requests.get(url = url, headers = get_headers())
		if response.status_code == 200 :
			res = json.loads(response.text)
			data = res["data"]
			creat_transaction_log(data,tf_log_name,unique_list,repeated_list)		
		else:
			res = json.loads(response.text)
			tf_log_doc = frappe.get_doc("Transaction Fetch Log",tf_log_name)
			tf_log_doc.status = "Error"
			if not tf_log_doc.log:
				tf_log_doc.log = ""	
			tf_log_doc.log = tf_log_doc.log + space + str(res)
			tf_log_doc.save()
		n += 1
	tf_log_doc = frappe.get_doc("Transaction Fetch Log",tf_log_name)
	if not tf_log_doc.log:
			tf_log_doc.log = ""
	if unique_list:
		tf_log_doc.log = tf_log_doc.log + space + "  Unique Recorde ID : " + str(unique_list)
	if repeated_list:
		tf_log_doc.log = tf_log_doc.log + space + "  Repeated Recorde ID : " + str(repeated_list)
	tf_log_doc.save()


def creat_transaction_fetch_log(start_time,end_time,times=None,count=None):
	transaction_fetch_log_doc = frappe.get_doc(dict(
			doctype = "Transaction Fetch Log",
			start_time = start_time,
			end_time = end_time,
			count = count,
			page = times,
		)).insert(ignore_permissions = True)
	if transaction_fetch_log_doc:
		frappe.flags.ignore_account_permission = True
		update_default_shift_type_last_sync(get_default_shift_type(),end_time)
		return transaction_fetch_log_doc.name



def creat_shift_assignment_for_active_today():
	active_emp_list = frappe.db.sql_list("""select name from `tabEmployee`
				where status=%s """, "Active")
	if active_emp_list:
		for emp in active_emp_list:
			if check_employee_enable(emp):
				if frappe.db.get_value("Employee", emp, "biometric_id"):
					date = today()
					shift_type = get_shift_type(emp)
					creat_shift_assignment(emp,date,shift_type)


def creat_shift_assignment(emp_id,date,shift_type):
	name = "New Shift Assignment"
	d = frappe.db.sql("""
				select name
				from `tabShift Assignment`
				where employee = %(employee)s and docstatus < 2
				and date = %(date)s
				and name != %(name)s""", {
					"employee": emp_id,
					"shift_type": shift_type,
					"date": date,
					"name": name
				}, as_dict = 1)
	for date_overlap in d:
		if date_overlap['name']:
			return

	shift_assignment_doc = frappe.get_doc(dict(
			doctype = "Shift Assignment",
			employee = emp_id,
			shift_type = shift_type,
			date = date,
		)).insert(ignore_permissions = True)
	if shift_assignment_doc:
		frappe.flags.ignore_account_permission = True
		shift_assignment_doc.submit()
		return shift_assignment_doc.name


def creat_transaction_log(data,tf_log_name,unique_list,repeated_list):
	tf_log_doc = frappe.get_doc("Transaction Fetch Log",tf_log_name)
	if tf_log_doc.unique:
		unique = int(tf_log_doc.unique)
	else:
		unique = 0
	if tf_log_doc.repeated:
		repeated = int(tf_log_doc.repeated)
	else:
		repeated = 0
	
	for transaction_row in data:
		if check_transactions_id_is_unique(transaction_row["id"]):
			unique += 1
			unique_list.append(transaction_row["id"])
			if not transaction_row["id"] or not transaction_row["punch_time"] or not transaction_row["punch_state"] or not transaction_row["emp"]:
				status = "Error"
			else:
				status = "Waiting"
			transaction_log_doc = frappe.get_doc(dict(

				doctype = "Transactions Log",
				id = transaction_row["id"],
				emp_code = transaction_row["emp_code"],
				punch_time = transaction_row["punch_time"],
				punch_state = transaction_row["punch_state"],
				verify_type = transaction_row["verify_type"],
				work_code = transaction_row["work_code"],
				terminal_sn = transaction_row["terminal_sn"],
				terminal_alias = transaction_row["terminal_alias"],
				area_alias = transaction_row["area_alias"],
				ilongituded = transaction_row["longitude"],
				latitude = transaction_row["latitude"],
				gps_location = transaction_row["gps_location"],
				mobile = transaction_row["mobile"],
				source = transaction_row["source"],
				purpose = transaction_row["purpose"],
				crc = transaction_row["crc"],
				is_attendance = transaction_row["is_attendance"],
				reserved = transaction_row["reserved"],
				upload_time = transaction_row["upload_time"],
				sync_status = transaction_row["sync_status"],
				sync_statusid = transaction_row["sync_status"],
				sync_time = transaction_row["sync_time"],
				emp = transaction_row["emp"],
				terminal = transaction_row["terminal"],
				transaction_fetch_log = tf_log_name,
				status = status,

			)).insert(ignore_permissions = True)
			if transaction_log_doc:
				frappe.flags.ignore_account_permission = True

		else:
			repeated_list.append(transaction_row["id"])
			repeated += 1
	
	tf_log_doc.unique = unique
	tf_log_doc.repeated = repeated
	tf_log_doc.save()


@frappe.whitelist()
def make_employee_checkin():
	if check_master_enable():
		transactions_log_list = frappe.db.sql_list("""select name from `tabTransactions Log`
					where status=%s """, "Waiting")
		for transaction_item in transactions_log_list:
			transaction_doc = frappe.get_doc("Transactions Log",transaction_item)
			if get_employee_name_id(transaction_doc.emp):
				employee_name_id = get_employee_name_id(transaction_doc.emp)
				if check_employee_enable(employee_name_id):
					shift = get_shift_type(employee_name_id)
					punch_date =getdate(transaction_doc.punch_time)
					creat_shift_assignment(employee_name_id,punch_date,get_default_shift_type())
					if int(transaction_doc.punch_state) == 0 :
						log_type = "IN"
					else:
						log_type = "OUT"
					employee_checkin_doc = frappe.get_doc(dict(
						doctype = "Employee Checkin",
						employee = employee_name_id,
						log_type = log_type,
						time = transaction_doc.punch_time,
						device_id = transaction_doc.terminal_alias,
						shift = shift,
					)).insert(ignore_permissions = True)
					if employee_checkin_doc:
						frappe.flags.ignore_account_permission = True
						transaction_doc.employee_checkin = employee_checkin_doc.name
						transaction_doc.status = "Linked"
						transaction_doc.save()
		return "Success"
		
	
