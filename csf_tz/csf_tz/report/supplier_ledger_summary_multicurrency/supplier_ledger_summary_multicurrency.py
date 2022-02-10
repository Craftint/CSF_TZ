# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from csf_tz.csf_tz.report.customer_ledger_summary_multicurrency.customer_ledger_summary_multicurrency import (
	PartyLedgerSummaryReport,
)


def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return PartyLedgerSummaryReport(filters).run(args)
