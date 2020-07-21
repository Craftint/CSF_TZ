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
# from werkzeug import url_fix


class ToObject(object):
    def __init__(self, data):
	    self.__dict__ = json.loads(data)


def set_callback_token(doc, method):
    if not doc.callback_token:
	    doc.callback_token = binascii.hexlify(os.urandom(14)).decode()


def get_nmb_token(username=None, password=None):
        if not username or not password:
            username = "182M200J1JSR5T"
            password = "H5Ba0Xcd1%7N*4&27JqG!eWguJq%tdm6j%H"
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


def send_nmb(method, data):
        data["token"] = get_nmb_token()
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


def invoice_submission(doc, method):
    data = {
    "reference" : "SAS666-" + str(doc.name), 
    "student_name" : doc.student_name, 
    "student_id" :  doc.student,
    "amount" : doc.grand_total,
    "type" : "Fees Invoice",
    "code" : doc.name,
    "allow_partial" :"TRUE",
    "callback_url" : "https://" + get_host_name() + "/api/method/csf_tz.bank_api.receive_callback?token=" + doc.callback_token,
    }
    print_out(data)
    message = send_nmb("invoice_submission", data)
    print_out(message)
    frappe.msgprint(str(message))



@frappe.whitelist(allow_guest=True)
def receive_callback(*args, **kwargs):
    r = frappe.request
    # uri = url_fix(r.url.replace("+"," "))
    http_method = r.method
    body = r.get_data()
    headers = r.headers

    print_out(headers)
    print_out(body)