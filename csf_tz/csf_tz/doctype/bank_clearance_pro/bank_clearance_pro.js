// Copyright (c) 2020, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bank Clearance Pro', {
	setup: function (frm) {
		frm.add_fetch("account", "account_currency", "account_currency");
	},

	onload: function (frm) {

		let default_bank_account = frappe.defaults.get_user_default("Company") ?
			locals[":Company"][frappe.defaults.get_user_default("Company")]["default_bank_account"] : "";
		frm.set_value("account", default_bank_account);

		frm.set_query("account", function () {
			return {
				"filters": {
					"account_type": ["in", ["Bank", "Cash"]],
					"is_group": 0,
					"disabled": 0
				}
			};
		});

		frm.set_query("bank_account", function () {
			return {
				"filters": {
					"is_company_account": true
				}
			};
		});

		frm.set_value("from_date", frappe.datetime.month_start());
		frm.set_value("to_date", frappe.datetime.month_end());
	},

	refresh: function (frm) {
		frm.disable_save();
	},

	update_clearance_date: function (frm) {
		return frappe.call({
			method: "update_clearance_date",
			doc: frm.doc,
			callback: function (r, rt) {
				frm.refresh_field("payment_entries");
				frm.refresh_fields();
			}
		});
	},
	@frappe.whitelist()
	get_payment_entries: function (frm) {
		if (!frm.doc.statement_opening_balance || !frm.doc.statement_closing_balance) {
			frappe.throw("Statement Opening balance and Statement Closing Balance is Mandatory")
			return
		}
		frappe.call({
			method: 'erpnext.accounts.utils.get_balance_on',
			args: {
				account: frm.doc.account,
				date: frappe.datetime.add_days(frm.doc.from_date, -1),
			},
			async: false,
			callback: function (r) {
				if (r.message) {
					frm.set_value("opening_balance", r.message || 0);
				}
				else {
					frm.set_value("opening_balance", 0);
				}
			}
		});
		return frappe.call({
			method: "get_payment_entries",
			doc: frm.doc,
			callback: function (r, rt) {
				frm.refresh_field("payment_entries");
				frm.refresh_fields();
				$(frm.fields_dict.payment_entries.wrapper).find("[data-fieldname=amount]").each(function (i, v) {
					if (i != 0) {
						$(v).addClass("text-right")
					}
				})
				frm.trigger('update_fields')
			}
		});
	},
	statement_opening_balance: function (frm) {
		frm.trigger('update_fields')
	},
	statement_closing_balance: function (frm) {
		frm.trigger('update_fields')
	},
	update_fields: function (frm) {
		frm.set_value("closing_balance", frm.doc.total_amount + frm.doc.opening_balance);
		frm.set_value("opening_difference", frm.doc.opening_balance - frm.doc.statement_opening_balance);
		frm.set_value("closing_difference", frm.doc.closing_balance - frm.doc.statement_closing_balance);
	},
});

frappe.ui.form.on('Bank Clearance Pro Detail', {
	clearance_date: function (frm) {
		let reconciled_amount = 0;
		frm.doc.payment_entries.forEach(element => {
			if (element.clearance_date) {
				reconciled_amount += element.flt_amount;
			}
		});
		frm.set_value("reconciled_amount", reconciled_amount);
	}
});