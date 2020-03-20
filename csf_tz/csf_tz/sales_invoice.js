frappe.ui.form.on("Sales Invoice", {
    setup: function(frm) {

        frm.trigger("update_stock");
    },
    refresh: function(frm) {

        frm.trigger("update_stock");
    },
    onload: function(frm) {
        if (frm.doc.document_status == "Draft") {
            if (frm.doc.is_return == "0") {
                frm.set_value("naming_series","ACC-SINV-.YYYY.-");
            }
            else if (frm.doc.is_return == "1") {
                frm.set_value("naming_series","ACC-CN-.YYYY.-");
            }
        }
        frm.trigger("update_stock");
    },  
    update_stock: (frm) => {
        const warehouse_field = frappe.meta.get_docfield("Sales Invoice Item", "warehouse", frm.doc.name);
        const item_field = frappe.meta.get_docfield("Sales Invoice Item", "item_code", frm.doc.name);
        const qty_field = frappe.meta.get_docfield("Sales Invoice Item", "qty", frm.doc.name);
        if (frm.doc.update_stock){
            warehouse_field.in_list_view = 1;
            warehouse_field.idx = 3;
            warehouse_field.columns = 2;
            item_field.columns =3;
            qty_field.columns =1;
            refresh_field("items");
        }else{
            warehouse_field.in_list_view = 0;
            warehouse_field.columns = 0;
            item_field.columns =4;
            qty_field.columns =2;
            refresh_field("items");
        }
    },
});


frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+q',
    action: () => { 
            let current_doc = $('.data-row.editable-row').parent().attr("data-name");
            let d = locals["Sales Invoice Item"][current_doc];
            frappe.call({
                method: 'erpnext.stock.dashboard.item_dashboard.get_data',
                args: {
                    item_code: d.item_code,
                },
                callback: function(r) {
                    if (r.message.length > 0){
                        console.log(r.message);
                        r.message.forEach(element => {
                            frappe.msgprint("In " + element.warehouse + " there is " + element.actual_qty + " " + d.stock_uom);
                        });
                    }
                }
            });
    },
    page: this.page,
    description: __('Get Item INFO'),
    ignore_inputs: true,
});