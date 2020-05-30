frappe.listview_settings['Job Card'] = {
	get_indicator: function(doc) {
		if(doc.status=="Open") {
			return [__("Open"), "orange", "status,=,Open"];
		} else if(doc.status=="Closed") {
			return [__("Closed"), "green", "status,=,Open"];
		}
	}
};
