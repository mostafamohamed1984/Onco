# Copyright (c) 2026, ds and contributors
# For license information, please see license.txt

from frappe.model.document import Document


<<<<<<< HEAD:onco/onco/doctype/supplier_quotation/supplier_quotation.py
class SupplierQuotation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.pricing_rule_detail.pricing_rule_detail import PricingRuleDetail
		from erpnext.accounts.doctype.purchase_taxes_and_charges.purchase_taxes_and_charges import PurchaseTaxesandCharges
		from erpnext.buying.doctype.supplier_quotation_item.supplier_quotation_item import SupplierQuotationItem
		from frappe.types import DF

		additional_discount_percentage: DF.Float
		address_display: DF.SmallText | None
		amended_from: DF.Link | None
		apply_discount_on: DF.Literal["", "Grand Total", "Net Total"]
		auto_repeat: DF.Link | None
		base_discount_amount: DF.Currency
		base_grand_total: DF.Currency
		base_in_words: DF.Data | None
		base_net_total: DF.Currency
		base_rounded_total: DF.Currency
		base_rounding_adjustment: DF.Currency
		base_taxes_and_charges_added: DF.Currency
		base_taxes_and_charges_deducted: DF.Currency
		base_total: DF.Currency
		base_total_taxes_and_charges: DF.Currency
		billing_address: DF.Link | None
		billing_address_display: DF.SmallText | None
		buying_price_list: DF.Link | None
		company: DF.Link
		contact_display: DF.SmallText | None
		contact_email: DF.Data | None
		contact_mobile: DF.SmallText | None
		contact_person: DF.Link | None
		conversion_rate: DF.Float
		cost_center: DF.Link | None
		currency: DF.Link
		disable_rounded_total: DF.Check
		discount_amount: DF.Currency
		grand_total: DF.Currency
		group_same_items: DF.Check
		ignore_pricing_rule: DF.Check
		in_words: DF.Data | None
		incoterm: DF.Link | None
		is_subcontracted: DF.Check
		items: DF.Table[SupplierQuotationItem]
		language: DF.Data | None
		letter_head: DF.Link | None
		named_place: DF.Data | None
		naming_series: DF.Literal[None]
		net_total: DF.Currency
		opportunity: DF.Link | None
		other_charges_calculation: DF.TextEditor | None
		plc_conversion_rate: DF.Float
		price_list_currency: DF.Link | None
		pricing_rules: DF.Table[PricingRuleDetail]
		project: DF.Link | None
		quotation_number: DF.Data | None
		rounded_total: DF.Currency
		rounding_adjustment: DF.Currency
		select_print_heading: DF.Link | None
		shipping_address: DF.Link | None
		shipping_address_display: DF.SmallText | None
		shipping_rule: DF.Link | None
		status: DF.Literal["", "Draft", "Submitted", "Stopped", "Cancelled", "Expired"]
		supplier: DF.Link
		supplier_address: DF.Link | None
		supplier_name: DF.Data | None
		tax_category: DF.Link | None
		taxes: DF.Table[PurchaseTaxesandCharges]
		taxes_and_charges: DF.Link | None
		taxes_and_charges_added: DF.Currency
		taxes_and_charges_deducted: DF.Currency
		tc_name: DF.Link | None
		terms: DF.TextEditor | None
		title: DF.Data | None
		total: DF.Currency
		total_net_weight: DF.Float
		total_qty: DF.Float
		total_taxes_and_charges: DF.Currency
		transaction_date: DF.Date
		valid_till: DF.Date | None
	# end: auto-generated types
=======
class PriceListForTender(Document):
>>>>>>> f53d04c3ea85962bbc45f422aa53854d31fb0308:onco/onco/doctype/price_list_for_tender/price_list_for_tender.py
	pass
