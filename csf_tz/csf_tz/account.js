frappe.ui.form.on("Account", {
    onload_post_render: function(frm) {
        frm.trigger("parent_account");
        frm.trigger("create_expenses_item_btn");
        frm.set_query("item", function() {
			return {
				"filters": {
					"item_group": "Indirect Expenses"
				}
			};
        });
    },
    refresh:function(frm) {
        frm.trigger("onload_post_render");
    },
    create_expenses_item_btn: function (frm) {
        frm.add_custom_button(__("Create Expenses Item"), function() {
            frappe.call({
                method: 'csf_tz.custom_api.add_indirect_expense_item',
                args: {
                    account_name: frm.doc.name,
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("item",r.message);
                        frm.refresh_field("item");
                        frm.save();
                    }
                }
            });
        });
    },
    parent_account: function(frm) {
        frm.trigger("create_expenses_item_btn");
        frm.refresh_field("item");
    },
    item: function(frm) {
        frm.trigger("create_expenses_item_btn");
    },
});
