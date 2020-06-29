from __future__ import unicode_literals
from frappe import _


def get_data():
	return [
		
		{
			"label": _("Compliance"),
			"items": [
				{
					"type": "doctype",
					"name": "EFD Z Report",
					"description": _("Accounting journal entries with Multi-Currency."),
				},
			"items": [
				{
					"type": "doctype",
					"name": "Visibility",
					"description": _("Setup Visibity of records."),
				},
				{
					"type": "doctype",
					"name": "Repack Template",
					"description": _("Quick BOM feature for repacking. Making many items of one item"),
				},
				{
					"type": "doctype",
					"name": "Expense Record",
					"description": _("Petty expenses for Section. Intelligent expense transactions."),
				},
				{
					"type": "doctype",
					"name": "Section",
					"description": _("Sections for petty expense recording."),
				},
				{
					"type": "doctype",
					"name": "Expense Type",
					"description": _("Expense type to make petty expenses and linking to expense accounts."),
				},
				{
					"type": "doctype",
					"name": "CSF TZ Settings",
					"description": _("Settings for CSF TZ."),
				},
				{
					"type": "doctype",
					"name": "Electronic Fiscal Device",
					"description": _("Electronic Fiscal Device setup."),
				},
				{
					"type": "doctype",
					"name": "Special Closing Balance",
					"description": _("Special Closing Balance recording and generating Material Receipts for reverse calculated productions."),
				},
				{
					"type": "doctype",
					"name": "Open Invoice Exchange Rate Revaluation",
					"description": _("Open Invoice Exchange Rate Revaluation for period end P & L visibility."),
				},
				{
					"type": "doctype",
					"name": "EFD Z Report",
					"description": _("Accounting journal entries with Multi-Currency."),
				},
				{
					"type": "doctype",
					"name": "EFD Z Report",
					"description": _("Accounting journal entries with Multi-Currency."),
				},
			]
		},
		{
			"label": _("Analytics"),
			"items": [
				{
					"type": "report",
					"name": "Withholding Tax Summary on Sales",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Employment History",
					"doctype": "Employee",
					"is_query_report": True
				},
			]
		},
	]