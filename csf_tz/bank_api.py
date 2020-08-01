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


class ToObject(object):
    def __init__(self, data):
	    self.__dict__ = json.loads(data)


def set_callback_token(doc, method):
    doc.callback_token = binascii.hexlify(os.urandom(14)).decode()


def get_nmb_token(company):
    username ,password = frappe.get_value("Company",company,["nmb_username","nmb_password"])
    if not username or not password:
        frappe.throw(_("Please set User Name and Password in Company {0}".format(company)))
    url = "https://wip.mpayafrica.co.tz/v2/auth"
    data = {
        "username": username,
        "password": password,
    }
    for i in range(3):
        try:
            r = requests.post(url, data=json.dumps(data), timeout=5)
            r.raise_for_status()
            frappe.logger().debug({"webhook_success": r.text})
            # print_out(r.text)
            if json.loads(r.text)["status"] == 1:
                return json.loads(r.text)["token"]
            else:
                frappe.throw(json.loads(r.text))
        except Exception as e:
            frappe.logger().debug({"webhook_error": e, "try": i + 1})
            sleep(3 * i + 1)
            if i != 2:
                continue
            else:
                raise e


def send_nmb(method, data, company):
        data["token"] = get_nmb_token(company)
        url = "https://wip.mpayafrica.co.tz/v2/" + str(method)
        for i in range(3):
            try:
                r = requests.post(url, data=json.dumps(data), timeout=5)
                r.raise_for_status()
                frappe.logger().debug({"webhook_success": r.text})
                if json.loads(r.text)["status"] == 1:
                    return json.loads(r.text)
                else:
                    frappe.throw(json.loads(r.text))
            except Exception as e:
                frappe.logger().debug({"webhook_error": e, "try": i + 1})
                sleep(3 * i + 1)
                if i != 2:
                    continue
                else:
                    raise e

@frappe.whitelist()
def invoice_submission(doc=None, method=None, fees_name=None):
    if not doc and fees_name:
        doc = frappe.get_doc("Fees", fees_name)
    series = frappe.get_value("Company", doc.company, "nmb_series") or ""
    abbr = frappe.get_value("Company", doc.company, "abbr") or ""
    if not series:
        frappe.throw(_("Please set User Series in Company {0}".format(doc.company)))
    reference = str(series) + str(doc.name)
    reference = reference.replace('-', '').replace('FEE'+abbr+'20','')
        frappe.throw(_("Please set NMB User Series in Company {0}".format(doc.company)))
    data = {
    "reference" : reference,
    "student_name" : doc.student_name, 
    "student_id" :  doc.student,
    "amount" : doc.grand_total,
    "type" : "Fees Invoice",
    "code" : 10,
    "allow_partial" :"TRUE",
    "callback_url" : "https://" + get_host_name() + "/api/method/csf_tz.bank_api.receive_callback?token=" + doc.callback_token,
    }
    send_nmb("invoice_submission", data, doc.company)
    # frappe.msgprint(str(message))
    # return message



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
        frappe.set_user("Administrator")
        fees_name = str(nmb_doc.reference)[7:]
        fees_token = frappe.get_value("Fees", fees_name, "callback_token")
        if fees_token == nmb_doc.fees_token:
            payment_entry = get_payment_entry("Fees", fees_name)
            payment_entry.update({
                "reference_no": nmb_doc.reference,
                "reference_date": nmb_doc.timestamp,
                "remarks": "Payment Entry against {0} {1} via NMB Bank Payment {2}".format("Fees",
                    fees_name, nmb_doc.reference),
            })
            payment_entry.flags.ignore_permissions=True
            frappe.flags.ignore_account_permission = True
            payment_entry.save()
            payment_entry.submit()
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
    doc_exist = frappe.db.exists("Fees",message["reference"][7:])
    if doc_exist:
        doc = frappe.get_doc("Fees",message["reference"][7:])
        response = dict(
            status = 1,
            reference = message["reference"],
            student_name = doc.student_name,
            student_id = doc.student,
            amount =  doc.grand_total,
            type = "Fees Invoice",
            code = 10,
            allow_partial = "TRUE",
            callback_url = "https://" + get_host_name() + "/api/method/csf_tz.bank_api.receive_callback?token=" + doc.callback_token,
            token = message["token"]
        )
        return response
    else:
        frappe.response['status'] = 0
        frappe.response['description'] = "Not Exist"
    
def cancel_invoice(doc, method):
    series = frappe.get_value("Company" ,doc.company ,"nmb_series") or ""
    if not series:
        frappe.throw(_("Please set NMB User Series in Company {0}".format(doc.company)))
    data = {
    "reference" : str(series) + "-" + str(doc.name), 
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
                    doc_exist = frappe.db.exists("Fees",message["reference"][7:])
                    if doc_exist:
                        message["fees_token"] = frappe.get_value("Fees",message["reference"][7:],"callback_token")
                        message["doctype"] = "NMB Callback"
                        nmb_doc = frappe.get_doc(message)
                        enqueue(method=make_payment_entry, queue='short', timeout=10000, is_async=True , kwargs =nmb_doc)
        