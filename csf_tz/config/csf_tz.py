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
	]