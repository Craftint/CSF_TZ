// Copyright (c) 2020, Aakvatech and contributors
// For license information, please see license.txt

frappe.notification = {
	setup_fieldname_select: function(frm) {
		// get the doctype to update fields
		if(!frm.doc.document_type) {
			return;
		}

		frappe.model.with_doctype(frm.doc.document_type, function() {
			let get_select_options = function(df) {
				return {value: df.fieldname, label: df.fieldname + " (" + __(df.label) + ")"};
			}

			let get_date_change_options = function() {
				let date_options = $.map(fields, function(d) {
					return (d.fieldtype=="Date" || d.fieldtype=="Datetime")?
						get_select_options(d) : null;
				});
				// append creation and modified date to Date Change field
				return date_options.concat([
					{ value: "creation", label: `creation (${__('Created On')})` },
					{ value: "modified", label: `modified (${__('Last Modified Date')})` }
				]);
			}

			let fields = frappe.get_doc("DocType", frm.doc.document_type).fields;
			let options = $.map(fields,
				function(d) { return in_list(frappe.model.no_value_type, d.fieldtype) ?
					null : get_select_options(d); });

			// set value changed options
			frm.set_df_property("value_changed", "options", [""].concat(options));
			frm.set_df_property("set_property_after_alert", "options", [""].concat(options));

			// set date changed options
			frm.set_df_property("date_changed", "options", get_date_change_options());

		});
	}
}


frappe.ui.form.on('Visibility', {
	onload: function(frm) {
		frm.set_query("document_type", function() {
			return {
				"filters": {
					"istable": 0
				}
			}
		});
		frm.set_query("print_format", function() {
			return {
				"filters": {
					"doc_type": frm.doc.document_type
				}
			}
		});
	},
	refresh: function(frm) {
		frappe.notification.setup_fieldname_select(frm);
		frm.get_field("is_standard").toggle(frappe.boot.developer_mode);
	},

	document_type: function(frm) {
		frappe.notification.setup_fieldname_select(frm);
	},
	view_properties: function(frm) {
		frappe.route_options = {doc_type:frm.doc.document_type};
		frappe.set_route("Form", "Customize Form");
	},
	
});
