# -*- coding: utf-8 -*-
# Copyright (c) 2021, Aakvatech Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils import nowdate, getdate
from erpnext.accounts.utils import get_outstanding_invoices, get_account_currency
from erpnext.setup.utils import get_exchange_rate
from erpnext.controllers.accounts_controller import get_supplier_block_status
from erpnext.accounts.doctype.payment_entry.payment_entry import get_orders_to_be_billed, get_negative_outstanding_invoices

from six import string_types


@frappe.whitelist()
def get_outstanding_reference_documents(args):

    if isinstance(args, string_types):
        args = json.loads(args)

    if args.get('party_type') == 'Member':
        return

    # confirm that Supplier is not blocked
    if args.get('party_type') == 'Supplier':
        supplier_status = get_supplier_block_status(args['party'])
        if supplier_status['on_hold']:
            if supplier_status['hold_type'] == 'All':
                return []
            elif supplier_status['hold_type'] == 'Payments':
                if not supplier_status['release_date'] or getdate(nowdate()) <= supplier_status['release_date']:
                    return []

    party_account_currency = get_account_currency(args.get("party_account"))
    company_currency = frappe.get_cached_value(
        'Company',  args.get("company"),  "default_currency")

    # Get negative outstanding sales /purchase invoices
    negative_outstanding_invoices = []
    if args.get("party_type") not in ["Student", "Employee"] and not args.get("voucher_no"):
        negative_outstanding_invoices = get_negative_outstanding_invoices(args.get("party_type"), args.get("party"),
            args.get("party_account"), args.get("company"), party_account_currency, company_currency)

    # Get positive outstanding sales /purchase invoices/ Fees
    condition = ""
    if args.get("voucher_type") and args.get("voucher_no"):
        condition = " and voucher_type={0} and voucher_no={1}"\
            .format(frappe.db.escape(args["voucher_type"]), frappe.db.escape(args["voucher_no"]))

    # Add cost center condition
    if args.get("cost_center"):
        condition += " and cost_center='%s'" % args.get("cost_center")

    date_fields_dict = {
        'posting_date': ['from_posting_date', 'to_posting_date'],
        'due_date': ['from_due_date', 'to_due_date']
    }

    for fieldname, date_fields in date_fields_dict.items():
        if args.get(date_fields[0]) and args.get(date_fields[1]):
            condition += " and {0} between '{1}' and '{2}'".format(fieldname,
                args.get(date_fields[0]), args.get(date_fields[1]))

    if args.get("company"):
        condition += " and company = {0}".format(
            frappe.db.escape(args.get("company")))

    outstanding_invoices = get_outstanding_invoices(args.get("party_type"), args.get("party"),
                                                args.get("party_account"), filters=args, condition=condition)

    for d in outstanding_invoices:
        d["exchange_rate"] = 1
        if party_account_currency != company_currency:
            if d.voucher_type in ("Sales Invoice", "Purchase Invoice", "Expense Claim"):
                d["exchange_rate"] = frappe.db.get_value(
                    d.voucher_type, d.voucher_no, "conversion_rate")
            elif d.voucher_type == "Journal Entry":
                d["exchange_rate"] = get_exchange_rate(
                    party_account_currency,	company_currency, d.posting_date
                )
        if d.voucher_type in ("Purchase Invoice"):
            d["bill_no"] = frappe.db.get_value(d.voucher_type, d.voucher_no, "bill_no")

    # Get all SO / PO which are not fully billed or aginst which full advance not paid
    orders_to_be_billed = []
    if (args.get("party_type") != "Student"):
        orders_to_be_billed = get_orders_to_be_billed(args.get("posting_date"), args.get("party_type"),
            args.get("party"), args.get("company"), party_account_currency, company_currency, filters=args)

    data = negative_outstanding_invoices + \
        outstanding_invoices + orders_to_be_billed

    if not data:
        frappe.msgprint(_("No outstanding invoices found for the {0} {1} which qualify the filters you have specified.")
                    .format(args.get("party_type").lower(), frappe.bold(args.get("party"))), alert=True)

    return data

