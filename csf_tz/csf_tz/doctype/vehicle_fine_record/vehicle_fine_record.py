# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe import _
import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
from csf_tz.custom_api import print_out


class VehicleFineRecord(Document):
    pass


def check_fine_all_vehicles():
    plate_list = frappe.get_all("Vehicle")
    for vehicle in plate_list:
        get_fine(vehicle["name"])
        reference_list = frappe.get_all(
            "Vehicle Fine Record", filters={"status": ["!=", "PAID"]})
    for reference in reference_list:
        update_fine(reference["name"])


def get_fine(number_plate=None):
    field_list = ["reference", "issued_date", "officer", "vehicle", "licence",
                  "location", "offence", "charge", "penalty", "total", "status", "qr_code"]
    formSig = "plcwb4um7FCh8BxsRRTBZ%2FXzw84N5SUnMv6ctKWPaiM%3D"
    url = "https://tms.tpf.go.tz/"

    try:
        response = requests.post(url=url, timeout=5)
    except Timeout:
        frappe.msgprint(_("Error"))
    else:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            formSig = soup.find(attrs={"type": "hidden"})['value']
            payload = {
                'service': 'VEHICLE',
                'vehicle': number_plate,
                'formSig': formSig
            }
            response2 = requests.post(url=url, data=payload, timeout=5)
            soup = BeautifulSoup(response2.text, 'html.parser')
            trs = soup.find_all('tr')
            for tr in trs:
                fields_dict = {'doctype': 'Vehicle Fine Record'}
                soup_tr = BeautifulSoup(str(tr), 'html.parser')
                tds = soup_tr.find_all('td')
                if len(tds) > 1:
                    i = 0
                    for td in tds:
                        soup_td = BeautifulSoup(str(td), 'html.parser')
                        td = soup_td.find('td').getText()
                        fields_dict[field_list[i]] = td
                        i += 1
                if len(tds) > 1:
                    if frappe.db.exists("Vehicle Fine Record", fields_dict["reference"]):
                        doc = frappe.get_doc(
                            "Vehicle Fine Record", fields_dict["reference"])
                        for key, value in fields_dict.items():
                            if key != "qr_code":
                                doc[key] = value
                        doc.save()
                    else:
                        fine_doc = frappe.get_doc(fields_dict)
                        fine_doc.insert()

        else:
            # res = json.loads(response.text)
            print_out(response)


def update_fine(reference=None):
    field_list = ["reference", "issued_date", "officer", "vehicle", "licence",
                  "location", "offence", "charge", "penalty", "total", "status", "qr_code"]
    formSig = "plcwb4um7FCh8BxsRRTBZ%2FXzw84N5SUnMv6ctKWPaiM%3D"
    url = "https://tms.tpf.go.tz/"

    try:
        response = requests.post(url=url, timeout=5)
    except Timeout:
        frappe.msgprint(_("Error"))
    else:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            formSig = soup.find(attrs={"type": "hidden"})['value']
            payload = {
                'service': 'REFERENCE',
                'vehicle': reference,
                'formSig': formSig
            }
            response2 = requests.post(url=url, data=payload, timeout=5)
            soup = BeautifulSoup(response2.text, 'html.parser')
            trs = soup.find_all('tr')
            for tr in trs:
                fields_dict = {'doctype': 'Vehicle Fine Record'}
                soup_tr = BeautifulSoup(str(tr), 'html.parser')
                tds = soup_tr.find_all('td')
                if len(tds) > 1:
                    i = 0
                    for td in tds:
                        soup_td = BeautifulSoup(str(td), 'html.parser')
                        td = soup_td.find('td').getText()
                        fields_dict[field_list[i]] = td
                        i += 1
                if len(tds) > 1:
                    if frappe.db.exists("Vehicle Fine Record", fields_dict["reference"]):
                        doc = frappe.get_doc(
                            "Vehicle Fine Record", fields_dict["reference"])
                        doc.update(fields_dict)
                        print(fields_dict)
                        doc.save()
                        frappe.db.commit()

        else:
            print_out(response)
