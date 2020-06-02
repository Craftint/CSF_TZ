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
			]
		},
		{
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"name": "Withholding Tax Summary on Sales",
					"is_query_report": True,
					"doctype": "Sales Invoice",
					"label": _("Withholding Tax Summary on Sales"),
					"description": _("Reports of Withholding Tax Paid on behalf of the customer"),
				},
			]
		},
	]