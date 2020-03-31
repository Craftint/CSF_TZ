from __future__ import unicode_literals
from frappe.utils import flt
from erpnext.setup.utils import get_exchange_rate
import frappe
import frappe.permissions
import frappe.share
import traceback

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
		error_log = app_error_log(frappe.session.user,str(e))


@frappe.whitelist()
def getInvoice(currency,name):
	try:
		sinv_details = frappe.get_all("Sales Invoice",filters = [["Sales Invoice","currency","=",str(currency)],["Sales Invoice","status","in",["Unpaid","Overdue"]]],fields = ["name","grand_total","conversion_rate","currency"])
		pinv_details = frappe.get_all("Purchase Invoice",filters = [["Purchase Invoice","currency","=",str(currency)],["Purchase Invoice","status","in",["Unpaid","Overdue"]]],fields = ["name","grand_total","conversion_rate","currency"])
		doc = frappe.get_doc("Open Invoice Exchange Rate Revaluation",name)
		doc.inv_err_detail = []
		doc.save()
		if sinv_details:
			count = 1
			for sinv in sinv_details:
				if not flt(sinv.conversion_rate) == flt(doc.exchange_rate_to_company_currency):
					addChildItem(name,sinv.name,'Sales Invoice',sinv.conversion_rate,sinv.currency,sinv.grand_total,doc.exchange_rate_to_company_currency,count)
					count += 1
		if pinv_details:
			for pinv in pinv_details:
				if not flt(pinv.conversion_rate) == flt(doc.exchange_rate_to_company_currency):
					addChildItem(name,pinv.name,'Purchase Invoice',pinv.conversion_rate,pinv.currency,pinv.grand_total,doc.exchange_rate_to_company_currency,count)
					count += 1
		return sinv_details

	except Exception as e:
		error_log = app_error_log(frappe.session.user,str(e))


def addChildItem(name,inv_no,invoice_type,invoice_exchange_rate,invoice_currency,invoice_amount,current_exchange,idx):
	gain_loss = (flt(invoice_amount) * flt(invoice_exchange_rate))-(flt(invoice_amount) * flt(current_exchange))
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
		invoice_amount = invoice_amount,
		idx = idx
	)).insert()




