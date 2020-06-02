// Copyright (c) 2020, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Repack Template', {
	onload: function(frm) {
		frm.set_query("item_code", function() {
			return {
				"filters": {
					"is_stock_item": 1
				}
			};
		
		});
		frm.set_query("item_code","repack_template_details", function() {
			return {
				"filters": {
					"is_stock_item": 1
				}
			};
		
		});
	},
	validate: function(frm) {
		const item_list = [];
		const items = frm.doc.repack_template_details;
		items.forEach(element => {
			if (!item_list.includes(element.item_code)) {
				item_list.push(element.item_code);
			} else {
				frappe.throw(__("The items cannot be duplicated! Please remove the duplicate item"));
			}
		});
	},
});
