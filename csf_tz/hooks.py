# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "csf_tz"
app_title = "CSF TZ"
app_publisher = "Aakvatech"
app_description = "Country Specific Functionality Tanzania"
app_icon = "octicon octicon-bookmark"
app_color = "green"
app_email = "info@aakvatech.com"
app_license = "GNU General Public License (v3)"

fixtures = [
	{"doctype":"Custom Field", "filters": [["name", "in", (
		"Supplier-vrn",
		"Customer-vrn",
		"Company-vrn",
		"Company-p_o_box",
		"Company-city",
		"Company-street",
		"Company-block_number",
		"Company-plot_number",
		"Company-company_bank_details",
		"Company-section_break_12",
		"Journal Entry-to_date",
		"Journal Entry-from_date",
		"Payment Entry Reference-section_break_9",
		"Payment Entry Reference-posting_date",
		"Payment Entry Reference-end_date",
		"Sales Invoice-witholding_tax_certificate_number",
		"Purchase Invoice Item-withholding_tax_rate",
		"Sales Invoice Item-withholding_tax_rate",
		"Payment Entry Reference-start_date",
		"Sales Invoice-column_break_29",
		"Sales Invoice-tra_control_number",
		"Sales Invoice-statutory_details",
		"Sales Order-cost_center",
		"Sales Order-posting_date",
		"Purchase Order-posting_date",
		"Sales Invoice-electronic_fiscal_device",
		"Sales Invoice-efd_z_report",
		"POS Profile-column_break_1",
		"POS Profile-electronic_fiscal_device",
		"Item-witholding_tax_rate_on_purchase",
		"Company-max_records_in_dialog",
		"Stock Entry-repack_template",
		"Stock Entry-qty",
		"Stock Entry-item_uom",
		"Account-item",
	)]]},
	{"doctype":"Property Setter", "filters": [["name", "in", (
		"Sales Invoice-default_print_format",
		"Sales Invoice-pos_profile-in_standard_filter",
		"Sales Invoice-posting_date-in_list_view",
		"Sales Invoice-is_pos-in_standard_filter",
		"Payment Reconciliation Payment-posting_date-in_list_view",
		"Payment Reconciliation Payment-posting_date-columns",
		"Payment Entry Reference-reference_doctype-in_list_view",
		"Payment Entry Reference-reference_name-columns",
		"Payment Entry Reference-reference_doctype-columns",
		"Payment Entry Reference-due_date-columns",
		"Payment Entry Reference-due_date-width",
		"Customer-tax_id-label",
		"Bank Reconciliation Detail-posting_date-in_list_view",
		"Bank Reconciliation Detail-posting_date-columns",
		"Bank Reconciliation Detail-payment_entry-columns",
		"Purchase Invoice-default_print_format",
		"Payment Entry-section_break_12-collapsible",
		"Payment Entry-payment_accounts_section-collapsible",
		"Special Closing Balance-naming_series-options",
		"Special Closing Balance-naming_series-default",
	)]]},
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/csf_tz/css/csf_tz.css"
# app_include_js = "/assets/csf_tz/js/csf_tz.js"
app_include_js = "/assets/js/select_dialog.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/csf_tz/css/csf_tz.css"
# web_include_js = "/assets/csf_tz/js/csf_tz.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Payment Entry" : "csf_tz/payment_entry.js",
	"Sales Invoice" : "csf_tz/sales_invoice.js",
	"Sales Order" : "csf_tz/sales_order.js",
	"Delivery Note" : "csf_tz/delivery_note.js",
	"Customer" : "csf_tz/customer.js",
	"Supplier" : "csf_tz/supplier.js",
	"Stock Entry" : "csf_tz/stock_entry.js",
	"Account" : "csf_tz/account.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "csf_tz.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "csf_tz.install.before_install"
# after_install = "csf_tz.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "csf_tz.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Open Invoice Exchange Rate Revaluation": {
		"validate": "csf_tz.custom_api.getInvoiceExchangeRate"
	},
	"Sales Invoice": {
		"on_submit":"csf_tz.custom_api.create_delivery_note"
	},
	"Account": {
		"validate":"csf_tz.custom_api.create_indirect_expense_item",
		"after_insert":"csf_tz.custom_api.create_indirect_expense_item",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"csf_tz.tasks.all"
#	],
#	"daily": [
#		"csf_tz.tasks.daily"
#	],
#	"hourly": [
#		"csf_tz.tasks.hourly"
#	],
#	"weekly": [
#		"csf_tz.tasks.weekly"
#	]
#	"monthly": [
#		"csf_tz.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "csf_tz.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "csf_tz.event.get_events"
# }

