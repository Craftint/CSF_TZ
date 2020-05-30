from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _


def execute(filters=None):
	columns, data = [], []
	columns = [
         {
			"fieldname": "description",
			"label": _("Document"),
			"fieldtype": "Link",
			"options": "Vehicle Documents Type",
            "width":250
		},
        
        {
			"fieldname":"expiration_date",
			"label": _("Expire Date"),
			"fieldtype": "Date",
		},
        {
			"fieldname": "type",
			"label": _("Vehicle/Trailer"),
			"fieldtype": "Data",
			"width": 150
		},
     
       
        {
			"fieldname": "reference_no",
			"label": _("Reference  Number"),
			"fieldtype": "Data",
			"width": 150
		}
	]

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date {}").format(filters.to_date))
   

	where_filter = {"from_date": filters.from_date,"to_date": filters.to_date,}
	where = ""

	data = frappe.db.sql('''SELECT 
                                tvd.description AS description,
								tvd.expire_date AS expiration_date,
								CASE 
									WHEN tvd.parenttype = 'Vehicle' THEN CONCAT('<a href="/desk#Form/Vehicle/', tvh.name, '">', tvh.number_plate, '</a>') 
									WHEN tvd.parenttype = 'Trailer' THEN CONCAT('<a href="/desk#Form/Trailer/', tt.name, '">', tt.number_plate, '</a>')
								END AS type,
                                tvd.reference_no AS reference_no
								FROM 
									(`tabVehicle Documents` tvd)
								LEFT JOIN tabVehicle tvh
									ON (tvd.parent=tvh.name)
								LEFT JOIN tabTrailer tt
									ON (tvd.parent=tt.name)
								WHERE
							 		tvd.expire_date BETWEEN %(from_date)s AND %(to_date)s '''+ where +'''
						''',
						where_filter, as_dict=1,as_list=1
							);
   
	return columns, data

