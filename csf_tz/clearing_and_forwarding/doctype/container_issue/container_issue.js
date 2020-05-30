// Copyright (c) 2019, Bravo Logisitcs and contributors
// For license information, please see license.txt

frappe.ui.form.on('Container Issue', {
    onload: function (frm) {
        frm.set_query("container_no", "container_detail", function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [


                    //Add filter ,got booking_no but no export reference 
			         //['Container', 'booking_number', '=', doc.booking_number], 
                     ['Container', 'export_reference', '=', ''], 
                     ['Container', 'shipping_line', '=', doc.shipping_line]
		]
            }
        });

        frm.set_query("seal_number", "container_detail", function (doc, cdt, cdn) {
            var d = locals[cdt][cdn];
            return {
                filters: [


                    //Add filter for Container Seals 
			        //['Container Seals', 'booking_number', '=', doc.booking_number],
                    ['Container Seals', 'export_reference', '=', ''], 
                    ['Container Seals', 'shipping_line', '=', doc.shipping_line]
		]
            }
        });
        //filter export based on shipping line
        frm.fields_dict['export_reference'].get_query = function (doc) {
            return {
                filters: [
                    ['shipping_line', '=', frm.doc.shipping_line]
                ]
            }
        }

    },
    refresh: function (frm) {
        //frappe.msgprint(cstr(frm.doc.container_detail.length));
        console.log(frm);
    }
});
