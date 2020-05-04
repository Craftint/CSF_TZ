# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "CSF TZ",
			"category": "Modules",
			"label": _("Country Specific"),
			"color": "green",
			"icon": "octicon octicon-bookmark",
			"type": "module",
			"description": "Country specific customizations for compliance, taxation and statutory reports.",
		},
	]
