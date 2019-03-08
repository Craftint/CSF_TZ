from __future__ import unicode_literals
from collections import defaultdict
from datetime import date
from datetime import datetime
from datetime import timedelta
from erpnext.accounts.utils import get_fiscal_year
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe import throw, msgprint, _
from frappe.client import delete
from frappe.desk.notifications import clear_notifications
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint,flt,format_datetime,get_datetime_str,now_datetime,add_days,today,formatdate,date_diff,getdate,add_months
from frappe.utils.password import update_password as _update_password
from frappe.utils.user import get_system_managers
from erpnext.setup.utils import get_exchange_rate
from dateutil import relativedelta
from calendar import monthrange
import collections
import calendar
import frappe
import frappe.permissions
import frappe.share
import json
import logging
import math
import random
import re
import string
import time
import traceback
import urllib

@frappe.whitelist()
def app_error_log(title,error):
	d = frappe.get_doc({
			"doctype": "Custom Error Log",
			"title":str("User:")+str(title),
			"error":traceback.format_exc()
		})
	d = d.insert(ignore_permissions=True)
	return d	

@frappe.whitelist()
def getInvoiceExchangeRate(date,currency):
	try:
		exchange_rate = get_exchange_rate(currency,frappe.defaults.get_global_default("currency"),str(date))
		return exchange_rate

	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


@frappe.whitelist()
def getInvoice(currency,name):
	try:
		sinv_details=frappe.get_all("Sales Invoice",filters = [["Sales Invoice","currency","=",str(currency)],["Sales Invoice","status","=","Unpaid"]],fields = ["name","grand_total","conversion_rate","currency"])
		doc=frappe.get_doc("Open Invoice Exchange Rate Revaluation",name)
		doc.inv_err_detail = []
		doc.save()
		if sinv_details:
			for sinv in sinv_details:
				addChildItem(name,sinv.name,'Sales Invoice',sinv.conversion_rate,sinv.currency,sinv.grand_total,doc.exchange_rate_to_company_currency)
		return sinv_details
	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


def addChildItem(name,inv_no,invoice_type,invoice_exchange_rate,invoice_currency,invoice_amount,current_exchange):
	gain_loss = flt(invoice_amount) * flt(invoice_exchange_rate)-flt(invoice_amount) * flt(current_exchange)
	child_doc = frappe.get_doc(dict(
		doctype = "Inv ERR Detail",
		parent = name,
		parenttype = "Open Invoice Exchange Rate Revaluation",
		parentfield = "inv_err_detail",
		invoice_number = inv_no,
		invoice_type = invoice_type,
		invoice_exchange_rate = invoice_exchange_rate,
		invoice_currency = invoice_currency,
		invoice_gain_or_loss = gain_loss,
		invoice_amount = invoice_amount
	)).insert()




