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


@frappe.whitelist()
def print_out(message, alert= False, add_traceback=False, to_error_log=False ):
	if not message:
		return	
	
	def out(mssg):
		if message:
			frappe.errprint(str(mssg))
			if to_error_log:
				frappe.log_error(str(mssg))
			if add_traceback:
				if len(frappe.utils.get_traceback()) > 20:
					frappe.errprint(frappe.utils.get_traceback())
			if alert:
				frappe.msgprint(str(mssg))

	def check_msg(msg):
		if isinstance(msg, str):
			msg = str(msg)

		elif isinstance(msg, int):
			msg = str(msg)

		elif isinstance(msg, float):
			msg = str(msg)

		elif isinstance(msg, dict):
			msg = frappe._dict(msg)
			
		elif isinstance(msg, list):
			for item in msg:
				check_msg(item)
			msg = ""

		elif isinstance(msg, object):
			msg = str(msg.__dict__)
		
		else:
			msg = str(msg)
		out(msg)


	check_msg(message)



def get_stock_ledger_entries(item_code):
	conditions = " and item_code = '%s'" % item_code
	return frappe.db.sql("""
		select item_code, batch_no, warehouse, sum(actual_qty) as actual_qty
		from `tabStock Ledger Entry`
		where docstatus < 2  %s
		group by voucher_no, batch_no, item_code, warehouse
		order by item_code, warehouse""" %
		conditions, as_dict=1)


@frappe.whitelist()
def get_item_info(item_code):

	sle = get_stock_ledger_entries(item_code)
	iwb_map = {}
	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	for d in sle:
		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {})\
			.setdefault(d.batch_no, frappe._dict({
				 "bal_qty": 0.0
			}))
		qty_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]

		expiry_date_unicode = frappe.db.get_value('Batch', d.batch_no, 'expiry_date')
		
		if expiry_date_unicode:	
			qty_dict.expires_on = expiry_date_unicode
			exp_date = frappe.utils.data.getdate(expiry_date_unicode)
			qty_dict.expires_on = exp_date
			expires_in_days = (exp_date - frappe.utils.datetime.date.today()).days
			if expires_in_days > 0:
				qty_dict.expiry_status = expires_in_days
			else:
				qty_dict.expiry_status = 0

		qty_dict.actual_qty = flt(qty_dict.actual_qty, float_precision) + flt(d.actual_qty, float_precision)

	iwd_list = []
	for key1,value1 in iwb_map.items():
		for key2,value2 in value1.items():
			for key3,value3 in value2.items():
				lin_dict = {
					"item_code"	: key1,
					"warehouse"	: key2,
					"batch_no"	: key3
				}
				lin_dict.update(value3)
				iwd_list.append(lin_dict)

	return iwd_list
