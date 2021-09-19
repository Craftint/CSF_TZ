frappe.ui.form.on("Sales Order", {
    customer: function(frm) {
        if (!frm.doc.customer) {
            return
        }
        setTimeout(function() {
            if (!frm.doc.tax_category){
                frappe.call({
                    method: "csf_tz.custom_api.get_tax_category",
                    args: {
                        doc_type: frm.doc.doctype,
                        company: frm.doc.company,
                    },
                    callback: function(r) {
                        if(!r.exc) {
                            frm.set_value("tax_category", r.message);
                            frm.trigger("tax_category");
                        }
                    }
                });           
        }
          }, 1000);   
    },
    default_item_discount: function (frm) {
        frm.doc.items.forEach(item => {
            frappe.model.set_value(item.doctype, item.name, 'discount_percentage', frm.doc.default_item_discount);
        });
    },});

frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+q',
    action: () => { 
            const current_doc = $('.data-row.editable-row').parent().attr("data-name");
            const item_row = locals["Sales Order Item"][current_doc];
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
                    else {
                        frappe.show_alert({message:__('There are no records'), indicator:'red'}, 5);
                    }
                }
            });     
    },
    page: this.page,
    description: __('Select Item Warehouse'),
    ignore_inputs: true,
});


frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+i',
    action: () => { 
            const current_doc = $('.data-row.editable-row').parent().attr("data-name");
            const item_row = locals["Sales Order Item"][current_doc];
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
                        const c = new frappe.ui.Dialog({
                            title: __('Item Prices'),
                            width: 600
                        });
                        $(`<div class="modal-body ui-front">
                        <h2>${item_row.item_code} : ${item_row.qty}</h2>
                            <p>Choose Price and click Select :</p>
                            <table class="table table-bordered">
                            <thead>
                            </thead>
                            <tbody>
                            </tbody>
                            </table>
                        </div>`).appendTo(c.body);
                        const thead = $(c.body).find('thead');
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
                            const tbody = $(c.body).find('tbody');
                            const tr = $(`
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
                    else {
                        frappe.show_alert({message:__('There are no records'), indicator:'red'}, 5);
                    }
                }
            });     
    },
    page: this.page,
    description: __('Select Customer Item Price'),
    ignore_inputs: true,
});

frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+u',
    action: () => { 
            const current_doc = $('.data-row.editable-row').parent().attr("data-name");
            const item_row = locals["Sales Order Item"][current_doc];
            frappe.call({
                method: 'csf_tz.custom_api.get_item_prices',
                args: {
                    item_code: item_row.item_code,
                    currency: cur_frm.doc.currency,
                    company: cur_frm.doc.company
                },
                callback: function(r) {
                    if (r.message.length > 0){
                        const e = new frappe.ui.Dialog({
                            title: __('Item Prices'),
                            width: 600
                        });
                        $(`<div class="modal-body ui-front">
                            <h2>${item_row.item_code} : ${item_row.qty}</h2>
                            <p>Choose Price and click Select :</p>
                            <table class="table table-bordered">
                            <thead>
                            </thead>
                            <tbody>
                            </tbody>
                            </table>
                        </div>`).appendTo(e.body);
                        const thead = $(e.body).find('thead');
                        $(`<tr>
                            <th>Check</th>
                            <th>Rate</th>
                            <th>Qty</th>
                            <th>Date</th>
                            <th>Invoice</th>
                            <th>Customer</th>
                        </tr>`).appendTo(thead);
                        r.message.forEach(element => {
                            const tbody = $(e.body).find('tbody');
                            const tr = $(`
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
                    else {
                        frappe.show_alert({message:__('There are no records'), indicator:'red'}, 5);
                    }
                }
            });     
    },
    page: this.page,
    description: __('Select Item Price'),
    ignore_inputs: true,
});
