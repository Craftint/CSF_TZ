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
        if (!frm.doc.parent_account || !frm.doc.parent_account.includes("Indirect Expenses") || frm.doc.item){
            frm.remove_custom_button("Create Expenses Item");
        }
        else{
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
        }
    },
    parent_account: function(frm) {
        frm.trigger("create_expenses_item_btn");
        if (!frm.doc.parent_account || !frm.doc.parent_account.includes("Indirect Expenses")){
            frm.set_df_property("item", "hidden", true);
        }
        else {
            frm.set_df_property("item", "hidden", false);
        }
        frm.refresh_field("item");
    },
    item: function(frm) {
        frm.trigger("create_expenses_item_btn");
    },
});
