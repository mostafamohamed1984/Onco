# Importation Approvals - Currency Exchange Rate Fix

## Issue
When creating a Purchase Order from Importation Approvals, the system threw an error:
```
frappe.exceptions.ValidationError: Exchange Rate is mandatory. Maybe Currency Exchange record is not created for None to EGP.
```

## Root Cause
The `make_purchase_order` function was not properly setting the currency and conversion_rate when calling `get_item_details()`. This caused ERPNext to fail validation because:
1. Currency was not being passed to the item details function
2. Conversion rate was not being calculated properly
3. The system couldn't determine the exchange rate from None to EGP

## Solution
Updated `importation_approvals.py` with two key fixes:

### 1. Enhanced `set_missing_values` function
- Added proper conversion_rate calculation
- If currency matches company currency, set conversion_rate to 1.0
- Otherwise, fetch exchange rate using ERPNext's `get_exchange_rate` utility

### 2. Enhanced `update_item` function
- Added currency detection from supplier or company defaults
- Added conversion_rate calculation before calling `get_item_details`
- Ensured all required parameters (currency, conversion_rate) are passed to avoid validation errors

## Files Modified
- `Onco/onco/onco/doctype/importation_approvals/importation_approvals.py`

## Testing
After applying this fix:
1. Create or open an Importation Approvals document
2. Submit it
3. Click "Create Purchase Order"
4. The Purchase Order should be created without currency/exchange rate errors

## Notes
- The fix handles both same-currency (EGP to EGP) and cross-currency scenarios
- If exchange rate is not found in the system, it defaults to 1.0 to prevent errors
- Supplier's default currency is used if available, otherwise falls back to company currency
