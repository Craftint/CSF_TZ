# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe import _
from frappe.utils import flt, cint, getdate
from erpnext.stock.utils import add_additional_uom_columns
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition


from six import iteritems


def execute(filters=None):
    if not filters:
        filters = {}

    validate_filters(filters)

    if filters.get("company"):
        company_currency = erpnext.get_company_currency(filters.get("company"))
    else:
        company_currency = frappe.db.get_single_value(
            "Global Defaults", "default_currency")

    include_uom = filters.get("include_uom")
    columns = get_columns(filters)
    items = get_items(filters)
    sle = get_stock_ledger_entries(filters, items)

    # if no stock ledger entry found return
    if not sle:
        return columns, []

    iwb_map = get_item_warehouse_map(filters, sle)
    item_map = get_item_details(items, sle, filters)

    data = []
    conversion_factors = {}

    def _func(x): return x[1]

    for (company, item) in sorted(iwb_map):
        if item_map.get(item):
            qty_dict = iwb_map[(company, item)]

            report_data = {
                'currency': company_currency,
                'item_code': item,
                'company': company,
            }
            report_data.update(item_map[item])
            report_data.update(qty_dict)

            if include_uom:
                conversion_factors.setdefault(
                    item, item_map[item].conversion_factor)

            data.append(report_data)

    add_additional_uom_columns(columns, data, include_uom, conversion_factors)
    return columns, data


def get_columns(filters):
    """return columns"""
    columns = [
        {"label": _("Item"), "fieldname": "item_code",
        "fieldtype": "Link", "options": "Item", "width": 100},
        {"label": _("Item Name"), "fieldname": "item_name", "width": 150},
        {"label": _("Item Group"), "fieldname": "item_group",
        "fieldtype": "Link", "options": "Item Group", "width": 100},
        {"label": _("Stock UOM"), "fieldname": "stock_uom",
        "fieldtype": "Link", "options": "UOM", "width": 90},
        {"label": _("Opening Qty"), "fieldname": "opening_qty",
        "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("In Qty"), "fieldname": "in_qty",
        "fieldtype": "Float", "width": 80, "convertible": "qty"},
        {"label": _("Out Qty"), "fieldname": "out_qty",
        "fieldtype": "Float", "width": 80, "convertible": "qty"},
        {"label": _("Balance Qty"), "fieldname": "bal_qty",
        "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Excise Qty"), "fieldname": "excise_stock",
        "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Company"), "fieldname": "company",
        "fieldtype": "Link", "options": "Company", "width": 100}
    ]

    if filters.get('show_variant_attributes'):
        columns += [{'label': att_name, 'fieldname': att_name, 'width': 100}
                    for att_name in get_variants_attributes()]

    return columns


def get_conditions(filters):
    conditions = ""
    if not filters.get("from_date"):
        frappe.throw(_("'From Date' is required"))

    if filters.get("to_date"):
        conditions += " and sle.posting_date <= %s" % frappe.db.escape(
            filters.get("to_date"))
    else:
        frappe.throw(_("'To Date' is required"))

    if filters.get("company"):
        conditions += " and sle.company = %s" % frappe.db.escape(
            filters.get("company"))

    if filters.get("warehouse"):
        warehouse_details = frappe.db.get_value("Warehouse",
                                                filters.get("warehouse"), ["lft", "rgt"], as_dict=1)
        if warehouse_details:
            conditions += " and exists (select name from `tabWarehouse` wh \
                where wh.lft >= %s and wh.rgt <= %s and sle.warehouse = wh.name)" % (warehouse_details.lft,
                                                                        warehouse_details.rgt)

    if filters.get("warehouse_type") and not filters.get("warehouse"):
        conditions += " and exists (select name from `tabWarehouse` wh \
            where wh.warehouse_type = '%s' and sle.warehouse = wh.name)" % (filters.get("warehouse_type"))

    return conditions


def get_stock_ledger_entries(filters, items):
    item_conditions_sql = ''
    if items:
        item_conditions_sql = ' and sle.item_code in ({})'\
            .format(', '.join([frappe.db.escape(i, percent=False) for i in items]))

    conditions = get_conditions(filters)

    return frappe.db.sql("""
        select
            sle.item_code, sle.warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
            sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
            sle.item_code as name, sle.voucher_no, sle.stock_value, 0 as excise_stock
        from
            `tabStock Ledger Entry` sle force index (posting_sort_index)
        inner join `tabStock Entry` se on sle.voucher_type = "Stock Entry" and se.name = sle.voucher_no
        inner join `tabItem` i on sle.item_code = i.name
        where sle.is_cancelled = 0
            and (se.purpose != "Material Transfer")
            and i.excisable_item = 1
            and sle.docstatus < 2 %s %s
        UNION ALL
        select
            sle.item_code, sle.warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
            sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
            sle.item_code as name, sle.voucher_no, sle.stock_value, sle.actual_qty * si.excise_duty_applicable as excise_stock
        from
            `tabStock Ledger Entry` sle force index (posting_sort_index)
        inner join `tabSales Invoice` si on sle.voucher_type = "Sales Invoice" and si.name = sle.voucher_no
        inner join `tabItem` i on sle.item_code = i.name
        where sle.is_cancelled = 0
            and i.excisable_item = 1
            and sle.docstatus < 2 %s %s
        UNION ALL
        select
            sle.item_code, sle.warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
            sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
            sle.item_code as name, sle.voucher_no, sle.stock_value, 0 as excise_stock
        from
            `tabStock Ledger Entry` sle force index (posting_sort_index)
        inner join `tabItem` i on sle.item_code = i.name
        where sle.is_cancelled = 0
            and sle.voucher_type NOT IN ("Stock Entry", "Sales Invoice")
            and i.excisable_item = 1
            and sle.docstatus < 2 %s %s
        order by 3""" %  # nosec
                        (item_conditions_sql, conditions, item_conditions_sql, conditions, item_conditions_sql, conditions), as_dict=1)


def get_item_warehouse_map(filters, sle):
    iwb_map = {}
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))

    float_precision = cint(frappe.db.get_default("float_precision")) or 3

    for d in sle:
        key = (d.company, d.item_code)
        if key not in iwb_map:
            iwb_map[key] = frappe._dict({
                "opening_qty": 0.0,
                "in_qty": 0.0,
                "out_qty": 0.0,
                "excise_stock": 0.0,
                "bal_qty": 0.0
            })

        qty_dict = iwb_map[(d.company, d.item_code)]

        if d.voucher_type == "Stock Reconciliation":
            qty_diff = flt(d.qty_after_transaction) - flt(qty_dict.bal_qty)
        else:
            qty_diff = flt(d.actual_qty)

        if d.posting_date < from_date:
            qty_dict.opening_qty += qty_diff

        elif d.posting_date >= from_date and d.posting_date <= to_date:
            if flt(qty_diff, float_precision) >= 0:
                qty_dict.in_qty += qty_diff
            else:
                qty_dict.out_qty += abs(qty_diff)
            qty_dict.excise_stock += abs(d.excise_stock) or 0

        qty_dict.bal_qty += qty_diff

    iwb_map = filter_items_with_no_transactions(iwb_map, float_precision)

    return iwb_map


def filter_items_with_no_transactions(iwb_map, float_precision):
    for (company, item) in sorted(iwb_map):
        qty_dict = iwb_map[(company, item)]

        no_transactions = True
        for key, val in iteritems(qty_dict):
            val = flt(val, float_precision)
            qty_dict[key] = val
            if key != "val_rate" and val:
                no_transactions = False

        if no_transactions:
            iwb_map.pop((company, item))

    return iwb_map


def get_items(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append("item.name=%(item_code)s")
    else:
        if filters.get("item_group"):
            conditions.append(get_item_group_condition(
                filters.get("item_group")))

    items = []
    if conditions:
        items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
                                .format(" and ".join(conditions)), filters)
    return items


def get_item_details(items, sle, filters):
    item_details = {}
    if not items:
        items = list(set([d.item_code for d in sle]))

    if not items:
        return item_details

    cf_field = cf_join = ""
    if filters.get("include_uom"):
        cf_field = ", ucd.conversion_factor"
        cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom=%s" \
            % frappe.db.escape(filters.get("include_uom"))

    res = frappe.db.sql("""
        select
            item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom %s
        from
            `tabItem` item
            %s
        where
            item.name in (%s)
    """ % (cf_field, cf_join, ','.join(['%s'] * len(items))), items, as_dict=1)

    for item in res:
        item_details.setdefault(item.name, item)

    if filters.get('show_variant_attributes', 0) == 1:
        variant_values = get_variant_values_for(list(item_details))
        item_details = {k: v.update(variant_values.get(k, {}))
                        for k, v in iteritems(item_details)}

    return item_details


def validate_filters(filters):
    if not (filters.get("item_code") or filters.get("warehouse")):
        sle_count = flt(frappe.db.sql(
            """select count(name) from `tabStock Ledger Entry`""")[0][0])
        if sle_count > 500000:
            frappe.throw(
                _("Please set filter based on Item or Warehouse due to a large amount of entries."))


def get_variants_attributes():
    '''Return all item variant attributes.'''
    return [i.name for i in frappe.get_all('Item Attribute')]


def get_variant_values_for(items):
    '''Returns variant values for items.'''
    attribute_map = {}
    for attr in frappe.db.sql('''select parent, attribute, attribute_value
        from `tabItem Variant Attribute` where parent in (%s)
        ''' % ", ".join(["%s"] * len(items)), tuple(items), as_dict=1):
        attribute_map.setdefault(attr['parent'], {})
        attribute_map[attr['parent']].update(
            {attr['attribute']: attr['attribute_value']})

    return attribute_map
