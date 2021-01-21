# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.controllers.taxes_and_totals import get_itemised_taxable_amount
import json
from frappe.utils import flt
from csf_tz import console


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "fieldname": "type",
            "label": _("Type"),
            "fieldtype": "Data",
            "options": "",
            "width": 100
        },
        {
            "fieldname": "line",
            "label": _("Line"),
            "fieldtype": "Data",
            "options": "",
            "width": 100
        },
        {
            "fieldname": "excl",
            "label": _("Excl Amount"),
            "fieldtype": "Float",
            "options": "",
            "width": 100
        },
        {
            "fieldname": "vat",
            "label": _("VAT Amount"),
            "fieldtype": "Float",
            "options": "",
            "width": 100
        },
        {
            "fieldname": "category",
            "label": _("Category"),
            "fieldtype": "Data",
            "options": "",
            "width": 300
        },
    ]
    return columns


def get_data(filters):
    default_currency = frappe.get_value(
        "Company", filters.company, "default_currency")
    data = [
        {
            "type": "Purchase",
            "line": "Line 1",
            "excl": 500,
            "vat": 5,
            "category": "Some Text"
        }
    ]
    imported = {
        "type": "Purchase",
        "line": "Line 3",
        "excl": 0,
        "vat": 0,
        "category": "Value of imported services"
    }
    non_creditable_purchases = {
        "type": "Purchase",
        "line": "Line 2",
        "excl": 0,
        "vat": 0,
        "category": "Non-creditable purchases"
    }
    taxable_purchases = {
        "type": "Purchase",
        "line": "Line 1",
        "excl": 0,
        "vat": 0,
        "category": "Taxable purchases"
    }

    purchase_list = frappe.get_all("Purchase Invoice", filters={
        "docstatus": 1,
        "is_return": 0,
        "company": filters.company,
        "posting_date": ["between", [
            filters.from_date,
            filters.to_date
        ]
        ]
    },
        fields={"*"}
    )

    for element in purchase_list:
        currency = frappe.get_value(
            "Supplier", element.supplier, "default_currency")
        if currency and currency != default_currency:
            imported["excl"] += element.base_net_total
        elif not element.base_total_taxes_and_charges:
            non_creditable_purchases["excl"] += element.base_net_total
        else:
            console(element)
            vat = 0
            amount = 0
            taxable_purchases["vat"] += element.base_total_taxes_and_charges
            taxes = frappe.get_all("Purchase Taxes and Charges", filters={
                "parent": element.name,
                "parentfield": "taxes",
            },
                fields={"*"}
            )
            itemised_tax = get_itemised_tax(taxes)
            console(itemised_tax)
            items = frappe.get_all("Purchase Invoice Item", filters={
                "parent": element.name,
                "parentfield": "items",
            },
                fields={"*"}
            )

            itemised_taxable_amount = get_itemised_taxable_amount(items)
            console(itemised_taxable_amount)

    return [taxable_purchases, non_creditable_purchases, imported]


def get_itemised_tax(taxes, with_tax_account=False):
    itemised_tax = {}
    for tax in taxes:
        if getattr(tax, "category", None) and tax.category == "Valuation":
            continue

        item_tax_map = json.loads(
            tax.item_wise_tax_detail) if tax.item_wise_tax_detail else {}
        if item_tax_map:
            for item_code, tax_data in item_tax_map.items():
                itemised_tax.setdefault(item_code, frappe._dict())

                tax_rate = 0.0
                tax_amount = 0.0

                if isinstance(tax_data, list):
                    tax_rate = flt(tax_data[0])
                    tax_amount = flt(tax_data[1])
                else:
                    tax_rate = flt(tax_data)

                itemised_tax[item_code][tax.description] = frappe._dict(dict(
                    tax_rate=tax_rate,
                    tax_amount=tax_amount
                ))

                if with_tax_account:
                    itemised_tax[item_code][tax.description].tax_account = tax.account_head

    return itemised_tax


def get_rounded_tax_amount(itemised_tax, precision):
    # Rounding based on tax_amount precision
    for taxes in itemised_tax.values():
        for tax_account in taxes:
            taxes[tax_account]["tax_amount"] = flt(
                taxes[tax_account]["tax_amount"], precision)
