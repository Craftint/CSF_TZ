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
               frm.clear_table("items");
               r.message.forEach(d => {
                    const child = frm.add_child("items");
                    frappe.model.set_value(child.doctype, child.name, "item_code", d.item_code)
                    frappe.model.set_value(child.doctype, child.name, "qty", d.qty)
                    frappe.model.set_value(child.doctype, child.name, "uom", d.item_uom)
                    if (d.s_warehouse) {
                        frappe.model.set_value(child.doctype, child.name, "s_warehouse", d.s_warehouse)
                    }
                    if (d.t_warehouse) {
                        frappe.model.set_value(child.doctype, child.name, "t_warehouse", d.t_warehouse)
                    }
                });
                
            }
        });
        frm.refresh_field("items");
    },
    stock_entry_type: function(frm) {
        if (frm.doc.stock_entry_type == "Repack from template") {
            frappe.meta.get_docfield("Stock Entry Detail", "item_code", frm.doc.name).read_only = 1;
            frappe.meta.get_docfield("Stock Entry Detail", "item_group", frm.doc.name).read_only = 1;
            $('.grid-add-multiple-rows').hide();
		    $('.grid-add-row').hide();
		    $('.grid-remove-rows').hide();
            $('.grid-download').hide();
            $('.grid-upload').hide();
            frm.toggle_reqd("qty", frm.doc.stock_entry_type == "Repack from template" ? 1:0);
        } else {
            frappe.meta.get_docfield("Stock Entry Detail", "item_code", frm.doc.name).read_only = 0;
            frappe.meta.get_docfield("Stock Entry Detail", "item_group", frm.doc.name).read_only = 0;
            $('.grid-add-multiple-rows').show();
		    $('.grid-add-row').show();
		    $('.grid-remove-rows').show();
            $('.grid-download').show();
            $('.grid-upload').show();
            frm.toggle_reqd("qty", frm.doc.stock_entry_type == "Repack from template" ? 1:0);
        }
        frm.refresh_field("items");
        frm.refresh();
    },
});
frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+q',
    action: () => { 
            const current_doc = $('.data-row.editable-row').parent().attr("data-name");
            const item_row = locals["Sales Invoice Item"][current_doc];
            frappe.call({
                method: 'csf_tz.custom_api.get_item_info',
                args: {item_code: item_row.item_code},
                callback: function(r) {
                    if (r.message.length > 0){
                        const d = new frappe.ui.Dialog({
                            title: __('Item Balance'),
                            width: 600
                        });
                        $(`<div class="modal-body ui-front">
                            <h2>${item_row.item_code} : ${item_row.qty}</h2>
                            <p>Choose Warehouse and click Select :</p>
                            <table class="table table-bordered">
                            <thead>
                            </thead>
                            <tbody>
                            </tbody>
                            </table>
                        </div>`).appendTo(d.body);
                        const thead = $(d.body).find('thead');
                        if (r.message[0].batch_no){
                            r.message.sort((a,b) => a.expiry_status-b.expiry_status);
                            $(`<tr>
                            <th>Check</th>
                            <th>Warehouse</th>
                            <th>Qty</th>
                            <th>UOM</th>
                            <th>Batch No</th>
                            <th>Expires On</th>
                            <th>Expires in Days</th>
                            </tr>`).appendTo(thead);
                        } else {
                            $(`<tr>
                            <th>Check</th>
                            <th>Warehouse</th>
                            <th>Qty</th>
                            <th>UOM</th>
                            </tr>`).appendTo(thead);
                        }
                        r.message.forEach(element => {
                            const tbody = $(d.body).find('tbody');
                            const tr = $(`
                            <tr>
                                <td><input type="checkbox" class="check-warehouse" data-warehouse="${element.warehouse}"></td>
                                <td>${element.warehouse}</td>
                                <td>${element.actual_qty}</td>
                                <td>${item_row.stock_uom }</td>
                            </tr>
                            `).appendTo(tbody);
                            if (element.batch_no) {
                                $(`
                                    <td>${element.batch_no}</td>
                                    <td>${element.expires_on}</td>
                                    <td>${element.expiry_status }</td>
                                `).appendTo(tr);
                                tr.find('.check-warehouse').attr('data-batch',element.batch_no);
                                tr.find('.check-warehouse').attr('data-batchQty',element.actual_qty);
                            }
                            tbody.find('.check-warehouse').on('change', function() {
                                $('input.check-warehouse').not(this).prop('checked', false);  
                            });
                        });
                        d.set_primary_action("Select", function() {
                            $(d.body).find('input:checked').each(function(i, input) {
                                frappe.model.set_value(item_row.doctype, item_row.name, 'warehouse', $(input).attr('data-warehouse'));
                                if ($(input).attr('data-batch')) {
                                    frappe.model.set_value(item_row.doctype, item_row.name, 'batch_no', $(input).attr('data-batch'));
                                }
                            });
                            cur_frm.rec_dialog.hide();
                            cur_frm.refresh_fields();
                        });
                        cur_frm.rec_dialog = d;
                        d.show();  
                    }
                }
            });     
    },
    page: this.page,
    description: __('Select Item Warehouse'),
    ignore_inputs: true,
});