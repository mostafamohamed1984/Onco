import frappe
from frappe import _

def validate_sales_invoice_tender_price(doc, method):
    """
    Block Sales Invoice submission if item prices deviate from Tender prices
    without explicit manager approval and detailed reasoning.
    """
    if doc.get("custom_tender_ref"):
        tender = frappe.get_doc("Tenders", doc.custom_tender_ref)
        
        # Build map of tender prices
        tender_prices = {}
        for row in tender.item_tender or []:
            if row.item_code:
                tender_prices[row.item_code] = row.tender_price
            
        for item in doc.items:
            if item.item_code in tender_prices:
                t_price = tender_prices[item.item_code]
                if item.rate < t_price:
                    # Check for detailed approval
                    if not doc.get("custom_price_deviation_approved"):
                        frappe.throw(_(
                            "Row #{0}: Item {1} price ({2}) is less than Tender price ({3}). "
                            "Please check 'Price Deviation Approved' and ensure management approval is documented."
                        ).format(item.idx, item.item_code, item.rate, t_price))
                    
                    if not doc.get("custom_cause_of_deviation"):
                        frappe.throw(_("Please provide the 'Cause of Deviation' for the price deviation approval."))
                    
                    if not doc.get("custom_approved_by"):
                        frappe.throw(_("Please specify which manager approved this price deviation in 'Approved By'."))

                    # Log deviation to Tender (for the price deviation details table)
                    tender.update_deviation_details(doc.name, [item])
                    tender.save(ignore_permissions=True)
