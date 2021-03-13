// Copyright (c) 2021, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Order Consignment', {
    onload: function (frm) {
        frm.set_query("default_source_warehouse", function () {
            return { filters: [["name", "like", "%Parts Store%"]] };
        });
    },
    parent_item: function (frm) {
        if (frm.doc.parent_item) {
            frappe.call({
                method: "csf_tz.csf_tz.doctype.work_order_consignment.work_order_consignment.get_boms",
                args: {
                    "item": frm.doc.parent_item,
                },
                callback: function (data) {
                    frm.clear_table("work_order_consignment_detail");
                    if (data.message) {
                        data.message.forEach(element => {
                            var child = frm.add_child("work_order_consignment_detail");
                            frappe.model.set_value(child.doctype, child.name, "bom", element.name);

                        });
                    }
                    frm.refresh_field("work_order_consignment_detail");
                }
            });
        }
    }
});