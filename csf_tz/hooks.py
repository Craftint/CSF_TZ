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
		"Stock Entry-repack_qty",
		"Stock Entry-item_uom",
		"Account-item",
		"Purchase Invoice-expense_record",
		"Journal Entry-expense_record",
		"Sales Invoice Item-allow_over_sell",
		"Sales Invoice-delivery_status",
		"Sales Invoice Item-delivery_status",
		"Stock Entry-final_destination",
		"Stock Entry-transport_receipt_date",
		"Stock Entry-driver_name",
		"Stock Entry-transporter_name",
		"Stock Entry-column_break_69",
		"Stock Entry-vehicle_no",
		"Stock Entry-transport_receipt_no",
		"Stock Entry-driver",
		"Stock Entry-transporter",
		"Stock Entry-transporter_info",
		"Stock Entry-transporter_info",
		"Stock Entry-transporter_info",
		"Material Request Item-stock_reconciliation",
		"Stock Reconciliation Item-material_request",
		"Sales Invoice-price_reduction",
		"Delivery Note-form_sales_invoice",
		"Stock Entry-total_net_weight",
		"Stock Entry Detail-item_weight_details",
		"Stock Entry Detail-weight_per_unit",
		"Stock Entry Detail-total_weight",
		"Stock Entry Detail-column_break_32",
		"Stock Entry Detail-weight_uom",
		"Sales Invoice Item-allow_override_net_rate",
		"Company-default_withholding_payable_account",
		"Purchase Invoice Item-withholding_tax_entry",
		"Company-enabled_auto_create_delivery_notes",
		"Stock Reconciliation-sort_items",
		"Student-bank",
		"Fees-callback_token",
		"Company-nmb_series",
		"Company-nmb_password",
		"Company-nmb_username",
		"Company-withholding_section",
		"Company-auto_submit_for_purchase_withholding",
		"Company-column_break_55",
		"Company-default_withholding_receivable_account",
		"Company-auto_submit_for_sales_withholding",
		"Item-withholding_tax_rate_on_sales",
		"Sales Invoice Item-withholding_tax_entry",
		"Company-nmb_url",
		"Fees-bank_reference",
		"Fees-abbr",
		"Sales Invoice-enabled_auto_create_delivery_notes",
		"Payroll Entry-bank_payment_details",
		"Payroll Entry-cheque_number",
		"Payroll Entry-column_break_34",
		"Payroll Entry-cheque_date",
		"Employee-national_identity",
		"Employee-bank_code",
		"Employee-wcf_number",
		"Employee-column_break_50",
		"Employee-pension_fund_number",
		"Employee-pension_fund",
		"Employee-statutory_details",
		"Employee-employee_ot_component",
		"Employee-overtime_components",
		"Loan-total_nsf_repayments",
		"Repayment Schedule-changed_interest_amount",
		"Repayment Schedule-changed_principal_amount",
		"Repayment Schedule-change_amount",
		"Salary Component-column_break_16",
		"Salary Component-payware_specifics",
		"Additional Salary-column_break_19",
		"Additional Salary-last_transaction_amount",
		"Additional Salary-last_transaction_details",
		"Additional Salary-auto_created_based_on",
		"Additional Salary-last_transaction_date",
		"Additional Salary-section_break_17",
		"Additional Salary-column_break_15",
		"Additional Salary-auto_repeat_details",
		"Additional Salary-auto_repeat_end_date",
		"Additional Salary-auto_repeat_frequency",
		"Salary Component-create_cash_journal",
		"Loan-loan_repayments_not_from_salary",
		"Salary Component-hourly_rate",
		"Salary Component-based_on_hourly_rate",
		"Salary Slip-salary_slip_ot_component",
		"Salary Slip-overtime_components",
		"Employee-biometric_id",
		"Employee-biometric_code",
		"Employee-area",
		"Additional Salary-based_on_hourly_rate",
		"Additional Salary-no_of_hours",
		"Additional Salary-hourly_rate",
		"Loan-not_from_salary_loan_repayments",
		"Employee-enable_biometric",
		"Salary Component-sdl_emolument_category"
	)]]},
	{"doctype":"Property Setter", "filters": [["name", "in", (
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
		"Payment Entry-section_break_12-collapsible",
		"Payment Entry-payment_accounts_section-collapsible",
		"Stock Entry-from_warehouse-fetch_from",
		"Loan-posting_date-in_list_view",
		"Loan-status-in_standard_filter",
		"Loan-search_fields",
		"Loan-loan_amount-in_list_view",
		"Payroll Entry-posting_date-in_list_view",
		"Loan-loan_type-in_list_view",
		"Loan-loan_type-in_standard_filter",
		"Loan-applicant_name-in_list_view",
		"Loan-applicant_name-in_standard_filter",
		"Loan-repayment_method-options",
		"Payroll Entry-end_date-in_list_view",
		"Salary Structure Assignment-employee-in_list_view",
		"Salary Structure Assignment-base-in_list_view"
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
	"Asset" : "csf_tz/asset.js",
	"Warehouse" : "csf_tz/warehouse.js",
	"Company": "csf_tz/company.js",
	"Stock Reconciliation": "csf_tz/stock_reconciliation.js",
	"Fees": "csf_tz/fees.js",
	"Program Enrollment Tool": "csf_tz/program_enrollment_tool.js",
	"Purchase Invoice": "csf_tz/purchase_invoice.js",
	"Quotation": "csf_tz/quotation.js",
	"Purchase Receipt": "csf_tz/purchase_receipt.js",
	"Purchase Order": "csf_tz/purchase_order.js",
	"Loan" : "payware/loan.js",
	"Additional Salary" : "payware/additional_salary.js",
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
		"on_submit":[
			'csf_tz.custom_api.validate_net_rate',
			"csf_tz.custom_api.create_delivery_note",
			'csf_tz.custom_api.check_submit_delivery_note',
			'csf_tz.custom_api.make_withholding_tax_gl_entries_for_sales',
			],
		'validate': [
			'csf_tz.custom_api.check_validate_delivery_note',
			'csf_tz.custom_api.validate_items_remaining_qty',
			'csf_tz.custom_api.calculate_price_reduction',
			],
		'on_cancel': 'csf_tz.custom_api.check_cancel_delivery_note',
	},
	'Delivery Note': {
		'on_submit': 'csf_tz.custom_api.update_delivery_on_sales_invoice',
		'on_cancel': 'csf_tz.custom_api.update_delivery_on_sales_invoice',
  },
	"Account": {
		"on_update":"csf_tz.custom_api.create_indirect_expense_item",
		"after_insert":"csf_tz.custom_api.create_indirect_expense_item",
	},
	"Purchase Invoice": {
		"on_submit":"csf_tz.custom_api.make_withholding_tax_gl_entries_for_purchase",
	},
	"Fees": {
		"before_insert":"csf_tz.custom_api.set_fee_abbr",
		"after_insert":"csf_tz.bank_api.set_callback_token",
		"on_submit":"csf_tz.bank_api.invoice_submission",
		"on_cancel":"csf_tz.bank_api.cancel_invoice",
	},
	"Fees": {
		"onload":"csf_tz.csftz_hooks.program_enrollment.create_course_enrollments_override",
		"refresh":"csf_tz.csftz_hooks.program_enrollment.create_course_enrollments_override",
		"reload":"csf_tz.csftz_hooks.program_enrollment.create_course_enrollments_override",
	},
	"*": {
		"validate"                      :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"onload"                        :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"before_insert"                 :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"after_insert"                  :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"before_naming"                 :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"before_change"                 :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"before_update_after_submit"    :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"before_validate"               :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"before_save"                   :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"on_update"                     :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"before_submit"                 :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"autoname"                      :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"on_cancel"                     :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"on_trash"                      :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"on_submit"                     :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"on_update_after_submit"        :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
		"on_change"                     :  ["csf_tz.csf_tz.doctype.visibility.visibility.run_visibility"],
	},
	"Stock Entry": {
		"validate": "csf_tz.custom_api.calculate_total_net_weight"
	},
	"Loan": {
		"validate": "csf_tz.payware.utils.validate_loan"
	},
	"Salary Slip": {
		"on_submit": "csf_tz.payware.utils.set_loan_paid",
		"on_cancel": "csf_tz.payware.utils.set_loan_paid",
		"before_insert": "csf_tz.payware.salary_slip_hook.generate_component_in_salary_slip_insert",
		"before_save": "csf_tz.payware.salary_slip_hook.generate_component_in_salary_slip_update"
	},
	"Loan Repayment Not From Salary": {
		"on_submit": "csf_tz.payware.utils.create_loan_repayment_jv",
		"validate": "csf_tz.payware.utils.validate_loan_repayment_nfs",
		"on_cancel": "csf_tz.payware.utils.create_loan_repayment_jv"
	},
	"Additional Salary": {
		"on_submit": "csf_tz.payware.utils.create_additional_salary_journal",
		"on_cancel": "csf_tz.payware.utils.create_additional_salary_journal",
		"before_validate": "csf_tz.payware.utils.set_employee_base_salary_in_hours"
	},
	"Employee": {
		"validate": "csf_tz.payware.doctype.biometric_settings.biometric_settings.check_employee_bio_info"
	},

}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"csf_tz.tasks.all"
	# ],
	"daily": [
		"csf_tz.custom_api.create_delivery_note_for_all_pending_sales_invoice",
		"csf_tz.csf_tz.doctype.visibility.visibility.trigger_daily_alerts",
		"csf_tz.csf_tz.doctype.vehicle_fine_record.vehicle_fine_record.check_fine_all_vehicles",
		"csf_tz.bank_api.reconciliation",
	],
	# "hourly": [
	# 	"csf_tz.tasks.hourly"
	# ],
	"weekly": [
		"csf_tz.custom_api.make_stock_reconciliation_for_all_pending_material_request"
	]
	# "monthly": [
	# 	"csf_tz.tasks.monthly"
	# ]
}

# Testing
# -------

# before_tests = "csf_tz.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "csf_tz.event.get_events"
# }

