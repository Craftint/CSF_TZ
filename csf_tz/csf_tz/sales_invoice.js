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
				frm.set_value("select_print_heading","CREDIT NOTE");
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
            let item_row = locals["Sales Invoice Item"][current_doc];
            frappe.call({
                method: 'csf_tz.custom_api.get_item_info',
                args: {item_code: item_row.item_code},
                callback: function(r) {
                    if (r.message.length > 0){
                        var d = new frappe.ui.Dialog({
                            title: __('Item Balance'),
                            width: 600
                        });
                        $(`<div class="modal-body ui-front">
                            <h2>${item_row.item_code}</h2>
                            <p>Choose Warehouse and click Select :</p>
                            <table class="table table-bordered">
                            <thead>
                            </thead>
                            <tbody>
                            </tbody>
                            </table>
                        </div>`).appendTo(d.body);
                        let thead = $(d.body).find('thead');
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
                            let tbody = $(d.body).find('tbody');
                            let tr = $(`
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
    description: __('Get Item INFO'),
    ignore_inputs: true,
    
});


frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+i',
    action: () => { 
            let current_doc = $('.data-row.editable-row').parent().attr("data-name");
            let item_row = locals["Sales Invoice Item"][current_doc];
            frappe.call({
                method: 'csf_tz.custom_api.get_item_prices',
                args: {
                    item_code: item_row.item_code,
                    customer: cur_frm.doc.customer,
                    currency: cur_frm.doc.currency,
                    company: cur_frm.doc.company
                },
                callback: function(r) {
                    if (r.message.length > 0){
                        var c = new frappe.ui.Dialog({
                            title: __('Item Prices'),
                            width: 600
                        });
                        $(`<div class="modal-body ui-front">
                            <h2>${item_row.item_code}</h2>
                            <p>Choose Price and click Select :</p>
                            <table class="table table-bordered">
                            <thead>
                            </thead>
                            <tbody>
                            </tbody>
                            </table>
                        </div>`).appendTo(c.body);
                        let thead = $(c.body).find('thead');
                        // if (r.message[0].rate){
                            // r.message.sort((a,b) => a.expiry_status-b.expiry_status);
                            $(`<tr>
                            <th>Check</th>
                            <th>Rate</th>
                            <th>Qty</th>
                            <th>Date</th>
                            <th>Invoice</th>
                            <th>Customer</th>
                            </tr>`).appendTo(thead);
                        // }
                        r.message.forEach(element => {
                            let tbody = $(c.body).find('tbody');
                            let tr = $(`
                            <tr>
                                <td><input type="checkbox" class="check-rate" data-rate="${element.price}"></td>
                                <td>${element.price}</td>
                                <td>${element.qty}</td>
                                <td>${element.date }</td>
                                <td>${element.invoice }</td>
                                <td>${element.customer }</td>
                            </tr>
                            `).appendTo(tbody);
                         
                            tbody.find('.check-rate').on('change', function() {
                                $('input.check-rate').not(this).prop('checked', false);  
                            });
                        });
                        c.set_primary_action("Select", function() {
                            $(c.body).find('input:checked').each(function(i, input) {
                                frappe.model.set_value(item_row.doctype, item_row.name, 'rate', $(input).attr('data-rate'));
                            });
                            cur_frm.rec_dialog.hide();
                            cur_frm.refresh_fields();
                        });
                        cur_frm.rec_dialog = c;
                        c.show();  
                    }
                }
            });     
    },
    page: this.page,
    description: __('Get Item Prices'),
    ignore_inputs: true,
    
});

frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+u',
    action: () => { 
            let current_doc = $('.data-row.editable-row').parent().attr("data-name");
            let item_row = locals["Sales Invoice Item"][current_doc];
            frappe.call({
                method: 'csf_tz.custom_api.get_item_prices',
                args: {
                    item_code: item_row.item_code,
                    currency: cur_frm.doc.currency,
                    company: cur_frm.doc.company
                },
                callback: function(r) {
                    if (r.message.length > 0){
                        var e = new frappe.ui.Dialog({
                            title: __('Item Prices'),
                            width: 600
                        });
                        $(`<div class="modal-body ui-front">
                            <h2>${item_row.item_code}</h2>
                            <p>Choose Price and click Select :</p>
                            <table class="table table-bordered">
                            <thead>
                            </thead>
                            <tbody>
                            </tbody>
                            </table>
                        </div>`).appendTo(e.body);
                        let thead = $(e.body).find('thead');
                        $(`<tr>
                            <th>Check</th>
                            <th>Rate</th>
                            <th>Qty</th>
                            <th>Date</th>
                            <th>Invoice</th>
                            <th>Customer</th>
                        </tr>`).appendTo(thead);
                        r.message.forEach(element => {
                            let tbody = $(e.body).find('tbody');
                            let tr = $(`
                            <tr>
                                <td><input type="checkbox" class="check-rate" data-rate="${element.price}"></td>
                                <td>${element.price}</td>
                                <td>${element.qty}</td>
                                <td>${element.date }</td>
                                <td>${element.invoice }</td>
                                <td>${element.customer }</td>
                            </tr>
                            `).appendTo(tbody);
                         
                            tbody.find('.check-rate').on('change', function() {
                                $('input.check-rate').not(this).prop('checked', false);  
                            });
                        });
                        e.set_primary_action("Select", function() {
                            $(e.body).find('input:checked').each(function(i, input) {
                                frappe.model.set_value(item_row.doctype, item_row.name, 'rate', $(input).attr('data-rate'));
                            });
                            cur_frm.rec_dialog.hide();
                            cur_frm.refresh_fields();
                        });
                        cur_frm.rec_dialog = e;
                        e.show();  
                    }
                }
            });     
    },
    page: this.page,
    description: __('Get Item Prices'),
    ignore_inputs: true,
    
});