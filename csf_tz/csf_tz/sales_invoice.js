frappe.ui.form.SelectDialog = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		var me = this;
		this.make();
	},
	make: function() {
		let me = this;

		this.page_length = 20;
		this.start = 0;

		let fields = [];
		let count = 0;
		if(!this.date_field) {
			this.date_field = "transaction_date";
		}


        if($.isArray(this.query_fields)) {
			for (let df of this.query_fields) {
				fields.push(df, {fieldtype: "Column Break"});
			}
		} else {
			this.query_fields.forEach(function(setter) {
				fields.push(setter);
				if (count++ < Object.keys(me.query_fields).length) {
					fields.push({fieldtype: "Column Break"});
				}
			});
        }
        
		fields = fields.concat([
			{
				"fieldname":"date_range",
				"label": __("Date Range"),
				"fieldtype": "DateRange",
			},
			{ fieldtype: "Section Break" },
			{ fieldtype: "HTML", fieldname: "results_area" },
			{ fieldtype: "Button", fieldname: "more_btn", label: __("More"),
				click: function(){
					me.start += 20;
					frappe.flags.auto_scroll = true;
					me.get_results();
				}
			}
		]);

		this.dialog = new frappe.ui.Dialog({
			title: __(this.title),
			fields: fields,
			primary_action_label: __("Get Items"),
			primary_action: function() {
				me.action(me.get_checked_values(), me.args);
			},
		});

		this.$parent = $(this.dialog.body);
		this.$wrapper = this.dialog.fields_dict.results_area.$wrapper.append(`<div class="results"
			style="border: 1px solid #d1d8dd; border-radius: 3px; height: 300px; overflow: auto;"></div>`);

		this.$results = this.$wrapper.find('.results');
		this.$results.append(this.make_list_row());

		this.args = {};

		this.bind_events();
		this.get_results();
		this.dialog.show();
	},

	bind_events: function() {
		let me = this;

		this.$results.on('click', '.list-item-container', function (e) {
			if (!$(e.target).is(':checkbox') && !$(e.target).is('a')) {
                $(this).find(':checkbox').trigger('click');
                
			}
		});
		this.$results.on('click', '.list-item--head :checkbox', (e) => {
			this.$results.find('.list-item-container .list-row-check')
				.prop("checked", ($(e.target).is(':checked')));
		});

		this.$parent.find('.input-with-feedback').on('change', (e) => {
			frappe.flags.auto_scroll = false;
            this.get_results();
            
        });
        

		this.$parent.find('[data-fieldname="date_range"]').on('blur', (e) => {
			frappe.flags.auto_scroll = false;
			this.get_results();
		});

        
	},

	get_checked_values: function() {
        var me = this;
		return this.$results.find('.list-item-container').map(function() {
			if ($(this).find('.list-row-check:checkbox:checked').length > 0 ) {
                console.log(this);
                console.log(`[data-item-${me.return_field}]`);
				return $(this).find(`[data-item-${me.return_field}]`).attr(`data-item-${me.return_field}`);
			}
		}).get();
	},

	make_list_row: function(result={}) {
		var me = this;
		// Make a head row by default (if result not passed)
		let head = Object.keys(result).length === 0;

		let contents = ``;
		let columns = [];

		if($.isArray(this.query_fields)) {
			for (let df of this.query_fields) {
				columns.push(df.fieldname);
			}
        } 
		columns.push("Date");

		columns.forEach(function(column) {
			contents += `<div class="list-item__content ellipsis">
				${
					head ? `<span class="ellipsis">${__(frappe.model.unscrub(column))}</span>`

					: `<span class="ellipsis" data-item-${column}="${result[column]}">${__(result[column])}</span>`
				}
			</div>`;
        })

		let $row = $(`<div class="list-item">
			<div class="list-item__content" style="flex: 0 0 10px;">
				<input type="checkbox" class="list-row-check" data-item-name="${result.name}" ${result.checked ? 'checked' : ''}>
			</div>
			${contents}
		</div>`);


		head ? $row.addClass('list-item--head')
            : $row = $(`<div class="list-item-container" data-item-name="${result.name}"></div>`).append($row);
        if (!me.multi_select) {
            $(".results").find('.list-row-check').on('change', function() {
                $('input.list-row-check').not(this).prop('checked', false);
            });
        }
        
		return $row;
	},

	render_result_list: function(results, more = 0) {
		var me = this;
		var more_btn = me.dialog.fields_dict.more_btn.$wrapper;

		// Make empty result set if filter is set
		if (!frappe.flags.auto_scroll) {
			this.empty_list();
		}
		more_btn.hide();

		if (results.length === 0) return;
		if (more) more_btn.show();
        $(".results").find(".list-item-container").remove()
		results.forEach((result) => {
			me.$results.append(me.make_list_row(result));
		});

		if (frappe.flags.auto_scroll) {
			this.$results.animate({scrollTop: me.$results.prop('scrollHeight')}, 500);
		}
	},

	empty_list: function() {
		this.$results.find('.list-item-container').remove();
	},

	get_results: function() {
		let me = this;

		let filters = this.get_query ? this.get_query().filters : {};
		let filter_fields = [me.date_field];
		if($.isArray(this.query_fields)) {
			for (let df of this.query_fields) {
				filters[df.fieldname] = me.dialog.fields_dict[df.fieldname].get_value() || undefined;
				me.args[df.fieldname] = filters[df.fieldname];
				filter_fields.push(df.fieldname);
			}
        } 

		let date_val = this.dialog.fields_dict["date_range"].get_value();
		if(date_val) {
			filters[this.date_field] = ['between', date_val];
		}

		let args = {
            doctype:"",
            txt: "",
			filters: filters,
			filter_fields: filter_fields,
			start: this.start,
			page_length: this.page_length + 1,
			query: this.get_query ? this.get_query().query : '',
			as_dict: 1
        }
		frappe.call({
			type: "GET",
            method:'frappe.desk.search.search_widget',
			no_spinner: true,
            args: args,
			callback: function(r) {
                if (r.message) {r.values = r.message}
				let results = [], more = 0;
				if (r.values.length) {
					if (r.values.length > me.page_length) {
						r.values.pop();
						more = 1;
					}
					r.values.forEach(function(result) {
						if(me.date_field in result) {
							result["Date"] = result[me.date_field]
						}
						result.checked = 0;
						result.parsed_date = Date.parse(result["Date"]);
						results.push(result);
					});
					results.map( (result) => {
						result["Date"] = frappe.format(result["Date"], {"fieldtype":"Date"});
					})

					results.sort((a, b) => {
						return a.parsed_date - b.parsed_date;
					});

					// Preselect oldest entry
					if (me.start < 1 && r.values.length === 1) {
						results[0].checked = 1;
					}
				}
				me.render_result_list(results, more);
			}
        });
        
    },
    

});


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


frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+i',
    action: () => { 
            const current_doc = $('.data-row.editable-row').parent().attr("data-name");
            const item_row = locals["Sales Invoice Item"][current_doc];
            new frappe.ui.form.SelectDialog({
                target: cur_frm,
                title: "Get Item",
                multi_select: 1,
                date_field: "posting_date",
                query_fields:[
                    {
                        fieldname: "rate",
                        fieldtype: "Currency",
                        label: "Rate",
                        options: "currency",
                        precision: "2",
                    },
                    {
                        fieldname: "qty",
                        fieldtype: "Float",
                        label: "Qty",
                    },
                    {
                        fieldname: "invoice",
                        fieldtype: "Link",
                        label: "Invoice",
                        options: "Sales Invoice"
                    },
                    {
                        default: cur_frm.doc.customer,
                        fieldname: "customer",
                        fieldtype: "Link",
                        label: "Customer",
                        options: "Customer"
                    },
                
                ],
                get_query() {
                    return {
                        filters: {
                            item_code: item_row.item_code,
                            customer: "",
                            currency: cur_frm.doc.currency,
                            company: cur_frm.doc.company
                        },
                        query:"csf_tz.custom_api.get_item_prices_custom",
                    }
                },
                return_field: "rate",
                action(selections) {
                    console.log(selections);
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
            const item_row = locals["Sales Invoice Item"][current_doc];
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
                }
            });     
    },
    page: this.page,
    description: __('Select Item Price'),
    ignore_inputs: true,
});