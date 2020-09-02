frappe.ui.form.on("Purchase Invoice", {
    supplier: function(frm) {
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
    setup: function(frm) {
        frm.set_query("taxes_and_charges", function() {
			return {
				"filters": {
                    "company": frm.doc.company,
				}
			};
        });
        frappe.call({
            method: "erpnext.accounts.doctype.accounting_dimension.accounting_dimension.get_dimension_filters",
            callback: function(r) {
                if(!r.exc) {
                    const dimensions = [];
                    r.message[0].forEach(element => {
                        dimensions.push(element.fieldname);
                    });
                    frm.dimensions = dimensions;
                    console.log(frm.dimensions);
                }
            }
        });  
    },

});
frappe.ui.form.on("Purchase Invoice Item", {
    items_add: function(frm, cdt, cdn) {
        var row = frappe.get_doc(cdt, cdn);
        frm.dimensions.forEach(i => {
            row[i]=frm.doc[i]
        });
        frm.refresh_field("items");
	},
});