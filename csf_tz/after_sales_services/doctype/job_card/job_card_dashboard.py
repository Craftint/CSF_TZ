from frappe import _

def get_data():
	return {
		'fieldname': 'job_card',
		'internal_links': {
			'Maintenance Request': ['items', 'maintenance_request']
		},
		'transactions': [
			{
				'label': _('Related'),
				'items': ['Maintenance Request', 'Sales Invoice']
			},
		]
	}
