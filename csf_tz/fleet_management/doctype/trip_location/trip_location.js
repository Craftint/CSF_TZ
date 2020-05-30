// Copyright (c) 2016, Bravo Logistics and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip Location', {
	refresh: function(frm) {

	},
	
	is_local_border: function(frm){
		if(frm.doc.is_local_border && frm.doc.is_local_border == 1)
		{
			frm.set_value('is_international_border', 0);
		}
	},
	
	is_international_border: function(frm){
		if(frm.doc.is_international_border && frm.doc.is_international_border == 1)
		{
			frm.set_value('is_local_border', 0);
		}
	}
});
