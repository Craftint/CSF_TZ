# -*- coding: utf-8 -*-
# Copyright (c) 2017, Bravo Logisitcs and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.utils import get_fetch_values
from frappe.utils import cstr, flt, getdate, comma_and, cint
from frappe import msgprint


class Files(Document):
	from csf_tz.after_sales_services.doctype.reference_payment_table.reference_payment_table import update_child_table
	def onload(self):
		expenses_html = self.load_expenses()
		invoices_html = self.load_invoices()
		purchase_invoices_html = self.load_purchase_invoices()
		payments_html = self.load_payments()
		self.set_onload("expenses_html", {"display": expenses_html})
		self.set_onload("invoices_html", {"display": invoices_html})
		self.set_onload("purchase_invoices_html", {"display": purchase_invoices_html})
		self.set_onload("payments_html", {"display": payments_html})
		#check_import_status(self)
		#Set default company
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")

		
	
	def load_expenses(self):
		expenses_list = []
		expenses_import = frappe.db.sql("""SELECT * FROM `tabExpenses` WHERE parenttype = 'Import' AND parent IN (SELECT name FROM `tabImport` WHERE reference_file_number = %s)""", self.name, as_dict=True)
		expenses_export = frappe.db.sql("""SELECT * FROM `tabExpenses` WHERE parenttype = 'Export' AND parent IN (SELECT name FROM `tabExport` WHERE file_number = %s)""", self.name, as_dict=True)
		expenses_trip_main = frappe.db.sql("""SELECT * FROM `tabExpenses` WHERE parenttype = 'Vehicle Trip' AND parentfield = 'main_expenses' AND parent IN (SELECT name FROM `tabVehicle Trip` WHERE main_file_number = %s)""", self.name, as_dict=True)
		expenses_trip_return = frappe.db.sql("""SELECT * FROM `tabExpenses` WHERE parenttype = 'Vehicle Trip' AND parentfield = 'return_expenses' AND parent IN (SELECT name FROM `tabVehicle Trip` WHERE return_file_number = %s)""", self.name, as_dict=True)
		expenses_border = frappe.db.sql("""SELECT * FROM `tabExpenses` WHERE parenttype = 'Border Clearance' AND parent IN (SELECT name FROM `tabBorder Clearance` WHERE file_number = %s)""", self.name, as_dict=True)
		expenses_list = expenses_import + expenses_export + expenses_trip_main + expenses_trip_return + expenses_border
		
		self.set_onload("expenses_list", expenses_list)
		return frappe.render_template("templates/file_expenses.html", {"expenses_list": expenses_list})
		
	def load_invoices(self):
		invoices_list = []
		invoices_list = frappe.db.sql("""SELECT * FROM `tabSales Invoice` where files = %s""", self.name,as_dict=True)
		self.set_onload("invoices_list", invoices_list)
		return frappe.render_template("templates/file_invoices.html", {"invoices_list": invoices_list})
		
	def load_purchase_invoices(self):
		purchase_invoices_list = []
		purchase_invoices_list = frappe.db.sql("""SELECT * FROM `tabPurchase Invoice` where reference_doctype = 'Files' AND reference_docname = %s""", self.name,as_dict=True)
		self.set_onload("purchase_invoices_list", purchase_invoices_list)
		return frappe.render_template("templates/file_purchase_invoices.html", {"purchase_invoices_list": purchase_invoices_list})
		
	def load_payments(self):
		payments_list = []
		payments_list = frappe.db.sql("""SELECT * FROM `tabGL Entry` WHERE credit_in_account_currency > 0 AND against_voucher_type = 'Sales Invoice' AND against_voucher IN (SELECT name 
			FROM `tabSales Invoice` where files = %s)""", self.name, as_dict=True)
		self.set_onload("payments_list", payments_list)
		return frappe.render_template("templates/file_payments.html", {"payments_list": payments_list})
		
		

@frappe.whitelist()
def make_sales_invoice(source_name):
	#get SO reference
	docs = frappe.get_doc("Files", source_name)
	ref = docs.sales_order_reference

	#get data for referenced SO
	source_name = frappe.get_doc("Sales Order", ref)

	#create invoice
	new_invoice = frappe.new_doc("Sales Invoice")
	new_invoice.update({
		"customer": source_name.customer,
		"taxes_and_charges": source_name.taxes_and_charges
	})
	stock = source_name.items
	for value in stock:
		value.update({
			"docstatus": 0,
			"doctype": "Sales Invoice Item",
			"__islocal": 1,
			"__unsaved": 1,
			"parent": None,
			"parenttype": None,
			"sales_order": source_name.name,
			"so_detail": value.name,
			"qty": 1
		})
		new_invoice.append('items', value)
		'''new_invoice.append('items',
							{
								"item_code": value.item_code,
								"item_name": value.item_name,
								"description": value.description,
								"qty": value.qty,
								"stock_uom": value.stock_uom,
								"uom": value.uom,
								"conversion_factor": value.conversion_factor,
								"margin_type": value.margin_type,
								"margin_rate_or_amount": value.margin_rate_or_amount,
								"rate_with_margin": value.rate_with_margin,
								"discount_percentage": value.discount_percentage,
								"discount_amount": value.discount_amount,
								"base_rate_with_margin": value.base_rate_with_margin,
								"rate": value.rate,
								"amount": value.amount
							})
	new_invoice.update({
		"items": stock
	})'''
	charges=source_name.taxes
	for taxes in charges:
		new_invoice.append('taxes',
				{
						"charge_type": taxes.charge_type,
						"account_head": taxes.account_head,
						"description": taxes.description,
						"rate": taxes.rate,
						"tax_amount": taxes.tax_amount


				})
	#new_invoice.save()
	#new_invoice.insert()
	return new_invoice


@frappe.whitelist(allow_guest=True)
def check_import_status(doc):
	# update booking no value in container doctype selected

	docs = doc.name
	#for d in docs:
	frappe.msgprint(docs)

	# get Container doctype ambayo ina jina la d.container_no
	#update_container = frappe.get_doc("Container", d.container_no)
	#update_container.booking_number = ""
	#update_container.save()


@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		set_missing_values(source, target)
		#Get the advance paid Journal Entries in Sales Invoice Advance
		target.set_advances()

	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.status = "Draft"
		target.reference_doctype = source.doctype
		target.reference_docname = source.name
		'''target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

		# set company address
		target.update(get_company_address(target.company))
		if target.company_address:
			target.update(get_fetch_values("Purchase Invoice", 'company_address', target.company_address))'''

	def update_item(source, target, source_parent):
		target.amount = flt(source.amount) - flt(source.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = target.amount / flt(source.rate) if (source.rate and source.billed_amt) else source.qty

		item = frappe.db.get_value("Item", target.item_code, ["item_group", "selling_cost_center"], as_dict=1)
		target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center") \
			or item.selling_cost_center \
			or frappe.db.get_value("Item Group", item.item_group, "default_cost_center")

	doclist = get_mapped_doc("Files", source_name, {
		"Files": {
			"doctype": "Purchase Invoice",
		}
	}, target_doc, postprocess)

	return doclist
