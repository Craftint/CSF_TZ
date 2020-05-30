// Copyright (c) 2016, Bravo Logistics and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip Route', {
    refresh: function (frm) {
        //console.log(frm);
    },




    validate: function (frm) {
        //Check not more than two local borders
        var local_border = 0;
        for (var key in locals['Trip Steps Table']) {
            if (1 == locals['Trip Steps Table'][key].is_local_border) {
                local_border++;
            }
        }
        if (local_border > 2) {
            msgprint('You cannot have more than two local borders in a route.', 'Error');
            validated = false;
        }
    },

    calculate_total_expenses: function (frm) {
        var totals = {
            "USD": 0,
            "TZS": 0
        };
        frm.doc.fixed_expenses.forEach(function (row) {
            if (row.currency && row.amount) {
                totals[row.currency] += row.amount;
            }
        });

        frm.set_value('total_usd', totals['USD']);
        frm.set_value('total_tzs', totals['TZS']);
    }
});


frappe.ui.form.on('Trip Steps Table', {
    location: function (frm, cdt, cdn) {
        if (locals[cdt][cdn].location != "") {
            frappe.model.with_doc('Trip Location', locals[cdt][cdn].location, function () {
                reference_doc = frappe.model.get_doc('Trip Location', locals[cdt][cdn].location);
                if (1 == reference_doc.is_local_border) {
                    frappe.model.set_value(cdt, cdn, 'is_local_border', 1);
                    frappe.model.set_value(cdt, cdn, 'is_international_border', 0);
                } else if (1 == reference_doc.is_international_border) {
                    frappe.model.set_value(cdt, cdn, 'is_international_border', 1);
                    frappe.model.set_value(cdt, cdn, 'is_local_border', 0);
                } else {
                    frappe.model.set_value(cdt, cdn, 'is_local_border', 0);
                    frappe.model.set_value(cdt, cdn, 'is_international_border', 0);
                }
            });
        }
    },
});




frappe.ui.form.on('Fixed Expense Table', {
    expense: function (frm, cdt, cdn) {
        if (locals[cdt][cdn].expense && locals[cdt][cdn].expense != '') {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Fixed Expense",
                    fieldname: ["currency", "fixed_value"],
                    filters: {
                        name: ["=", locals[cdt][cdn].expense]
                    }
                },
                callback: function (data) {
                    frappe.model.set_value(cdt, cdn, 'currency', data.message.currency);
                    frappe.model.set_value(cdt, cdn, 'amount', data.message.fixed_value);
                }
            });
        }
    },

    currency: function (frm, cdt, cdn) {
        frm.events.calculate_total_expenses(frm);
    },

    amount: function (frm, cdt, cdn) {
        frm.events.calculate_total_expenses(frm);
    }
});
