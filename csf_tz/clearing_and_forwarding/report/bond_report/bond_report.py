# Copyright (c) 2013, Bravo Logisitcs and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	
	columns = [
		{
			"fieldname": "bond_reference",
			"label": _("Bond Reference"),
			"fieldtype": "Data",
			"width": 150
		},
		{
            "fieldname":"sub_t1",
            "label": _("Sub T1"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname":"bond_date",
            "label": _("Bond Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname":"bond_value",
            "label": _("Bond Value"),
            "fieldtype": "Float",
            "width": 150
        },
        {
            "fieldname":"cargo",
            "label": _("Cargo"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname":"bond_cancellation_date",
            "label": _("Bond Cancelled"),
            "fieldtype": "Date",
            "width": 150
        },
        {
            "fieldname":"reference_type",
            "label": _("Reference Type"),
            "fieldtype": "Link",
            "options": "Doctype",
            "width": 100
        },
        {
            "fieldname":"reference_doc",
            "label": _("Reference"),
            "fieldtype": "Dynamic Link",
            "options": "reference_type",
            "width": 100
        }
	]
	
	where = ""
	where_filter = {}
	
	if filters:
		where += ' WHERE '
		if filters.from_date > filters.to_date:
			frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
			
		if filters.from_date and filters.to_date:
			if filters.filter_by == 'Bond Date':
				where += " bond_date >= %(from_date)s AND bond_date <= %(to_date)s "
				where_filter.update({'from_date': filters.from_date, "to_date": filters.to_date})
			elif filters.filter_by == 'Bond Cancelation Date':
				where += " bond_cancellation_date >= %(from_date)s AND bond_cancellation_date <= %(to_date)s "
				where_filter.update({'from_date': filters.from_date, "to_date": filters.to_date})
			
		if filters.bt:
			where += " AND bond_reference LIKE %(bond_reference)s "
			where_filter.update({"bond_reference": filters.bt})
			
		if filters.status == 'Not Cancelled':
			where += " AND bond_cancellation_date IS NULL "
		elif filters.status == 'Cancelled':
			where += " AND bond_cancellation_date IS NOT NULL "
	
	data = frappe.db.sql('''SELECT * FROM 
							(
								SELECT 
									`tabImport`.bt_number AS bond_reference,
									cargo1.bond_ref_no AS sub_t1,
									`tabImport`.t1_approved AS bond_date,
									cargo1.bond_value,
									`tabImport`.cargo,
									`tabBorder Clearance`.bond_canceled_date AS bond_cancellation_date,
									'Import' AS reference_type,
									`tabImport`.name AS reference_doc
								FROM
									`tabCargo Details` AS cargo1
								LEFT JOIN
									`tabImport` ON `tabImport`.name = cargo1.parent
								LEFT JOIN
									`tabBorder Clearance` ON `tabBorder Clearance`.name = (SELECT cargo2.parent FROM `tabCargo Details` AS cargo2 \
										WHERE cargo2.parenttype = 'Border Clearance' AND cargo2.bond_ref_no = cargo1.bond_ref_no LIMIT 1)
								WHERE
									cargo1.parenttype = 'Import' AND `tabImport`.bt_number IS NOT NULL AND `tabImport`.bt_number != ''
							UNION ALL
								SELECT
									`tabExport`.bt_ref_no AS bond_reference,
									`tabBond Reference Table`.customs_ref_number AS sub_t1,
									`tabExport`.bt_approval_date AS bond_date,
									`tabBond Reference Table`.bond_value,
									`tabExport`.material AS cargo,
									`tabExport`.bond_validated AS bond_cancellation_date,
									'Export' AS reference_type,
									`tabExport`.name AS reference_doc
								FROM
									`tabBond Reference Table`
								LEFT JOIN
									`tabExport` ON `tabExport`.name = `tabBond Reference Table`.parent
								WHERE
									`tabBond Reference Table`.parenttype = 'Export' AND `tabExport`.bt_ref_no IS NOT NULL AND `tabExport`.bt_ref_no != ''
							UNION ALL
								SELECT
									`tabBorder Clearance`.bond_ref_no AS bond_reference,
									`tabCargo Details`.bond_ref_no AS sub_t1,
									`tabBorder Clearance`.bt_approval_date AS bond_date,
									`tabCargo Details`.bond_value,
									`tabBorder Clearance`.cargo_description AS cargo,
									`tabBorder Clearance`.bond_canceled_date AS bond_cancellation_date,
									'Border Clearance' AS reference_type,
									`tabBorder Clearance`.name AS reference_doc
								FROM
									`tabCargo Details`
								LEFT JOIN
									`tabBorder Clearance` ON `tabBorder Clearance`.name = `tabCargo Details`.parent
								WHERE
									`tabCargo Details`.parenttype = 'Border Clearance' AND `tabBorder Clearance`.bond_ref_no IS NOT NULL \
									AND `tabBorder Clearance`.bond_ref_no != '' AND `tabBorder Clearance`.cargo_type = 'Container' \
									AND `tabBorder Clearance`.clearance_type IN ('Entry', 'Pass Through')
							UNION ALL
								SELECT
									`tabBorder Clearance`.bond_ref_no AS bond_reference,
									`tabBorder Clearance`.loose_sub_t1_ref AS sub_t1,
									`tabBorder Clearance`.bt_approval_date AS bond_date,
									`tabBorder Clearance`.loose_bond_value AS bond_value,
									`tabBorder Clearance`.cargo_description AS cargo,
									`tabBorder Clearance`.bond_canceled_date AS bond_cancellation_date,
									'Border Clearance' AS reference_type,
									`tabBorder Clearance`.name AS reference_doc
								FROM
									`tabBorder Clearance`
								WHERE
									`tabBorder Clearance`.bond_ref_no IS NOT NULL \
									AND `tabBorder Clearance`.bond_ref_no != '' AND `tabBorder Clearance`.cargo_type = 'Loose Cargo' \
									AND `tabBorder Clearance`.clearance_type IN ('Entry', 'Pass Through')
							) AS a'''
							+ where +
							'''ORDER BY bond_date ASC''', where_filter, as_dict=1)
	return columns, data
