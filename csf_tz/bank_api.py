# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals 
import frappe
from frappe.model.document import Document
from frappe.utils import get_url_to_form, get_url
from frappe import _
import json
import requests
from csf_tz.custom_api import print_out
from frappe.utils import today, format_datetime, now, nowdate, getdate, get_url, get_host_name
from time import sleep
import binascii
import os
from werkzeug import url_fix
import urllib.parse as urlparse
from urllib.parse import parse_qs
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.utils.background_jobs import enqueue
from datetime import datetime
from frappe.utils.password import get_decrypted_password



class ToObject(object):
    def __init__(self, data):
	    self.__dict__ = json.loads(data)


def set_callback_token(doc, method):
    doc.callback_token = binascii.hexlify(os.urandom(14)).decode()
    series = frappe.get_value("Company", doc.company, "nmb_series") or ""
    if not series:
        frappe.throw(_("Please set NMB User Series in Company {0}".format(doc.company)))
    reference = str(series) + 'F' + str(doc.name)
    if not doc.abbr:
        doc.abbr = frappe.get_value("Company", doc.company, "abbr") or ""
    doc.bank_reference = reference.replace('-', '').replace('FEE'+doc.abbr,'')


def get_nmb_token(company):
    username = frappe.get_value("Company",company,"nmb_username")
    if not username:
        frappe.throw(_("Please set NMB User Name in Company {0}".format(company)))
    password = get_decrypted_password("Company",company,"nmb_password")
    if not password:
        frappe.throw(_("Please set NMB Password in Company {0}".format(company)))
    url = frappe.get_value("Company",company,"nmb_url")
    if not url:
        frappe.throw(_("Please set NMB URL in Company {0}".format(company)))
    url = url + str("auth")
    data = {
        "username": username,
        "password": password,
    }
    for i in range(3):
        try:
            r = requests.post(url, data=json.dumps(data), timeout=5)
            r.raise_for_status()
            frappe.logger().debug({"get_nmb_token webhook_success": r.text})
            # print_out(r.text)
            if json.loads(r.text)["status"] == 1:
                return json.loads(r.text)["token"]
            else:
                frappe.throw(json.loads(r.text))
        except Exception as e:
            frappe.logger().debug({"get_nmb_token webhook_error": e, "try": i + 1})
            sleep(3 * i + 1)
            if i != 2:
                continue
            else:
                raise e


def send_nmb(method, data, company):
    url = frappe.get_value("Company",company,"nmb_url")
    if not url:
        frappe.throw(_("Please set NMB URL in Company {0}".format(company)))
    data["token"] = get_nmb_token(company)
    url = url + str(method)
    for i in range(3):
        try:
            r = requests.post(url, data=json.dumps(data), timeout=5)
            r.raise_for_status()
            frappe.logger().debug({"send_nmb webhook_success": r.text})
            if json.loads(r.text)["status"] == 1:
                return json.loads(r.text)
            else:
                frappe.throw(json.loads(r.text))
        except Exception as e:
            frappe.logger().debug({"send_nmb webhook_error": e, "try": i + 1})
            sleep(3 * i + 1)
            if i != 2:
                continue
            else:
                raise e

@frappe.whitelist()
def invoice_submission(doc=None, method=None, fees_name=None):
    if not doc and fees_name:
        doc = frappe.get_doc("Fees", fees_name)
    send_fee_details_to_bank = frappe.get_value("Company", doc.company, "send_fee_details_to_bank") or ""
    if not send_fee_details_to_bank:
        return
    series = frappe.get_value("Company", doc.company, "nmb_series") or ""
    abbr = frappe.get_value("Company", doc.company, "abbr") or ""
    if not series:
        frappe.throw(_("Please set NMB User Series in Company {0}".format(doc.company)))
    data = {
    "reference" : doc.bank_reference,
    "student_name" : doc.student_name, 
    "student_id" :  doc.student,
    "amount" : doc.grand_total,
    "type" : "Fees Invoice",
    "code" : 10,
    "allow_partial" :"TRUE",
    "callback_url" : "https://" + get_host_name() + "/api/method/csf_tz.bank_api.receive_callback?token=" + doc.callback_token,
    }
    send_nmb("invoice_submission", data, doc.company)



@frappe.whitelist(allow_guest=True)
def receive_callback(*args, **kwargs):
    r = frappe.request
    uri = url_fix(r.url.replace("+"," "))
    # http_method = r.method
    body = r.get_data()
    # headers = r.headers
    message = {}
    if body :
        data = body.decode('utf-8')
        msgs =  ToObject(data)
        atr_list = list(msgs.__dict__)
        for atr in atr_list:
            if getattr(msgs, atr) :
                message[atr] = getattr(msgs, atr)
    else:
        frappe.throw("This has no body!")
    parsed_url = urlparse.urlparse(uri)
    message["fees_token"] = parsed_url[4][6:]
    message["doctype"] = "NMB Callback"
    nmb_doc = frappe.get_doc(message)
    
    if nmb_doc.insert(ignore_permissions=True):
        frappe.response['status'] = 1
        frappe.response['description'] = "success"
    else:
        frappe.response['description'] = "insert failed"
        frappe.response['http_status_code'] = 409

    enqueue(method=make_payment_entry, queue='short', timeout=10000, is_async=True , kwargs =nmb_doc )


def make_payment_entry(**kwargs):
    for key, value in kwargs.items(): 
        nmb_doc = value
        doc_info = get_fee_info(nmb_doc.reference)

        if doc_info["doctype"] == "Fees":
            frappe.set_user("Administrator")
            fees_name = doc_info["name"]
            fees_token = frappe.get_value("Fees", fees_name, "callback_token")
            if fees_token == nmb_doc.fees_token:
                payment_entry = get_payment_entry("Fees", fees_name)
                payment_entry.update({
                    "reference_no": nmb_doc.reference,
                    "reference_date": nmb_doc.timestamp,
                    "remarks": "Payment Entry against {0} {1} via NMB Bank Payment {2}".format("Fees",fees_name, nmb_doc.reference),
                })
                payment_entry.flags.ignore_permissions=True
                frappe.flags.ignore_account_permission = True
                payment_entry.save()
                payment_entry.submit()
            return nmb_doc

        elif doc_info["doctype"] == "Student Applicant Fees":
            doc = frappe.get_doc("Student Applicant Fees",doc_info["name"])
            acounts = get_fees_default_accounts(doc.company)
            if not doc.callback_token == nmb_doc.fees_token:
                return
            jl_rows = []
            debit_row = dict(
                account = acounts["bank"],
                debit_in_account_currency = nmb_doc.amount,
                account_currency = acounts["currency"],
                cost_center =  doc.cost_center,
            )
            jl_rows.append(debit_row)

            credit_row_1 = dict(
                account = acounts["income"],
                credit_in_account_currency = nmb_doc.amount,
                account_currency = acounts["currency"],
                cost_center =  doc.cost_center,
            )
            jl_rows.append(credit_row_1)

            user_remark = "Journal Entry against {0} {1} via NMB Bank Payment {2}".format("Student Applicant Fees",doc_info["name"], nmb_doc.reference)
            jv_doc = frappe.get_doc(dict(
                doctype = "Journal Entry",
                posting_date = nmb_doc.timestamp,
                accounts = jl_rows,
                company = doc.company,
                multi_currency = 0,
                user_remark = user_remark,
            ))

            jv_doc.flags.ignore_permissions = True
            frappe.flags.ignore_account_permission = True
            jv_doc.save()
            jv_doc.submit()
            jv_url = frappe.utils.get_url_to_form(jv_doc.doctype, jv_doc.name)
            si_msgprint = "Journal Entry Created <a href='{0}'>{1}</a>".format(jv_url,jv_doc.name)
            frappe.msgprint(_(si_msgprint))
            frappe.set_value("Student Applicant", doc.student, "application_status", "Approved")
            return nmb_doc


@frappe.whitelist(allow_guest=True)
def receive_validate_reference(*args, **kwargs):
    r = frappe.request
    # uri = url_fix(r.url.replace("+"," "))
    # http_method = r.method
    body = r.get_data()
    # headers = r.headers
    message = {}
    if body :
        data = body.decode('utf-8')
        msgs =  ToObject(data)
        atr_list = list(msgs.__dict__)
        for atr in atr_list:
            if getattr(msgs, atr) :
                message[atr] = getattr(msgs, atr)
    else:
        frappe.throw("This has no body!")

    doc_info = get_fee_info(message["reference"])               
    if doc_info["name"]:
        doc = frappe.get_doc(doc_info["doctype"], doc_info["name"])
        response = dict(
            status = 1,
            reference = doc.bank_reference,
            student_name = doc.student_name,
            student_id = doc.student,
            amount =  doc.grand_total,
            type = "Fees Invoice",
            code = 10,
            allow_partial = "FALSE",
            callback_url = "https://" + get_host_name() + "/api/method/csf_tz.bank_api.receive_callback?token=" + doc.callback_token,
            token = message["token"]
        )
        return response
    else:
        frappe.response['status'] = 0
        frappe.response['description'] = "Not Exist"
    
def cancel_invoice(doc, method):
    data = {
    "reference" : str(doc.bank_reference), 
    }
    message = send_nmb("invoice_cancel", data, doc.company)
    frappe.msgprint(str(message))


def reconciliation(doc=None, method=None):
    companys = frappe.get_all("Company")
    for company in companys:
        if not frappe.get_value("Company", company["name"], "nmb_username"):
            continue
        data = {"reconcile_date" : datetime.today().strftime('%d-%m-%Y')}
        frappe.msgprint(str(data))
        message = send_nmb("reconcilliation", data, company["name"])
        if message["status"] == 1 and len(message["transactions"]) > 0:
            for i in message["transactions"]:
                if len(frappe.get_all("NMB Callback",filters = [["NMB Callback","reference","=",i.reference],["NMB Callback","receipt","=",i.receipt]],fields = ["name"])) == 1:
                    doc_info = get_fee_info(message["reference"])
                    if doc_info["name"]:
                        message["fees_token"] = frappe.get_value(doc_info["doctype"],doc_info["name"],"callback_token")
                        message["doctype"] = "NMB Callback"
                        nmb_doc = frappe.get_doc(message)
                        enqueue(method=make_payment_entry, queue='short', timeout=10000, is_async=True , kwargs =nmb_doc)


def get_fee_info(bank_reference):
    data = {"name":"", "doctype":""}
    doc_list =frappe.get_all("Fees",filters = [["Fees","bank_reference","=",bank_reference],["Fees","docstatus","=",1]])
    if len(doc_list):
        data["name"] = doc_list[0]["name"]
        data["doctype"] = "Fees"
        return data
    else:
        doc_list =frappe.get_all("Student Applicant Fees",filters = [["Student Applicant Fees","bank_reference","=",bank_reference],["Student Applicant Fees","docstatus","=",1]])
        if len(doc_list):
            data["name"] = doc_list[0]["name"]
            data["doctype"] = "Student Applicant Fees"
        return data


def get_fees_default_accounts(company):
    data = {"bank":"", "income":"", "currency":""}
    data["currency"] = frappe.get_value("Company", company, "default_currency") or ""
    data["bank"] = frappe.get_value("Company", company, "fee_bank_account") or ""
    if not data["bank"]:
        data["bank"] = frappe.get_value("Company", company, "default_bank_account") or ""
    data["income"] = frappe.get_value("Company", company, "student_applicant_fees_revenue_account") or ""
    if not data["income"]:
        data["bank"] = frappe.get_value("Company", company, "default_income_account") or ""
    if not data["bank"]:
        frappe.throw(_("Please set Fee Bank Account in Company {0}".format(company)))
    if not data["income"]:
        frappe.throw(_("Please set Student Applicant Fees Revenue Account in Company {0}".format(company)))
    return data