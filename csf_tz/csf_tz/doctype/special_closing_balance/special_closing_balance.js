// Copyright (c) 2020, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Special Closing Balance', {
	onload: function(frm) {

		frm.set_query("item_code", "closing_balance_details", function(doc, cdt, cdn) {
			return {
				query: "erpnext.controllers.queries.item_query",
				filters:{
					"is_stock_item": 1
				}
			}
		});

		if (frm.doc.company) {
			erpnext.queries.setup_queries(frm, "Warehouse", function() {
				return erpnext.queries.warehouse(frm.doc);
			});
		}
	},
	refresh: function(frm) {
		if(frm.doc.docstatus < 1) {
			frm.add_custom_button(__("Fetch Items from Warehouse"), function() {
				frm.events.get_items(frm);
			});
		}
	},
	get_items: function(frm) {
		if (!frm.doc.warehouse) {
			frappe.prompt({label:"Warehouse", fieldname: "warehouse", fieldtype:"Link", options:"Warehouse", reqd: 1,
			"get_query": function() {
				return {
					"filters": {
						"company": frm.doc.company,
					}
				}
			}},
			function(data) {
				frm.set_value('warehouse',data.warehouse);
				frm.trigger("_get_items");
			}
		);
		}
		else {frm.trigger("_get_items");}
	},
	_get_items: function(frm) {
		if (!frm.doc.warehouse) {return}
		frappe.call({
			method:"csf_tz.csf_tz.doctype.special_closing_balance.special_closing_balance.get_items",
			args: {
				warehouse: frm.doc.warehouse,
				posting_date: frm.doc.posting_date,
				posting_time: frm.doc.posting_time,
				company:frm.doc.company
			},
			callback: function(r) {
				var items = [];
				frm.clear_table("closing_balance_details");
				for(var i=0; i< r.message.length; i++) {
					var d = frm.add_child("closing_balance_details");
					$.extend(d, r.message[i]);
					if(!d.quantity) d.quantity = 0;
				}
				frm.refresh_field("closing_balance_details");
			}
		});
	}
});
