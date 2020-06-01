frappe.ui.form.on("Stock Entry", {
    onload: function(frm) {
        frm.trigger("stock_entry_type");
        frm.set_query("repack_template", function() {
			return {
				"filters": {
					"docstatus": 1
				}
			};
		
		});
    },
    repack_template: function(frm) {
        frm.trigger("get_repack_template");
    },
    qty: function(frm) {
        frm.trigger("get_repack_template");
    },
    get_repack_template: function(frm) {
        if (!frm.doc.repack_template || !frm.doc.qty){return}
        frappe.call({
            method: 'csf_tz.custom_api.get_repack_template',
            args: {
                template_name: frm.doc.repack_template,
                qty: frm.doc.qty,
            },
            callback: function(r) {
            //    console.log(r.message);
               frm.clear_table("items");
               r.message.forEach(d => {
                    const child = frm.add_child("items");
                    frappe.model.set_value(child.doctype, child.name, "item_code", d.item_code)
                    frappe.model.set_value(child.doctype, child.name, "qty", d.qty)
                    frappe.model.set_value(child.doctype, child.name, "uom", d.item_uom)
                });
                
            }
        });
        frm.refresh_field("items");
    },
    stock_entry_type: function(frm) {
        if (frm.doc.stock_entry_type == "Repack from template") {
            frappe.meta.get_docfield("Stock Entry Detail", "item_code", frm.doc.name).read_only = 1;
            frappe.meta.get_docfield("Stock Entry Detail", "qty", frm.doc.name).read_only = 1;
            frappe.meta.get_docfield("Stock Entry Detail", "item_group", frm.doc.name).read_only = 1;
            $('.grid-add-multiple-rows').hide();
		    $('.grid-add-row').hide();
		    $('.grid-remove-rows').hide();
            $('.grid-download').hide();
            $('.grid-upload').hide();
            frm.toggle_reqd("qty", frm.doc.stock_entry_type == "Repack from template" ? 1:0);
        } else {
            frappe.meta.get_docfield("Stock Entry Detail", "item_code", frm.doc.name).read_only = 0;
            frappe.meta.get_docfield("Stock Entry Detail", "qty", frm.doc.name).read_only = 0;
            frappe.meta.get_docfield("Stock Entry Detail", "item_group", frm.doc.name).read_only = 0;
            $('.grid-add-multiple-rows').show();
		    $('.grid-add-row').show();
		    $('.grid-remove-rows').show();
            $('.grid-download').show();
            $('.grid-upload').show();
            frm.toggle_reqd("qty", frm.doc.stock_entry_type == "Repack from template" ? 1:0);
        }
        frm.refresh_field("items");
    },
});