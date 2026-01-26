# Importation Cycle Testing Checklist

## Pre-Testing Setup
- [ ] Run `python setup_test_data.py` to create test data
- [ ] Verify test items, suppliers, and customers are created
- [ ] Check SMTP settings for email testing (optional)

## Phase 1: Basic EDA-IMAR Creation
### Test Case 1.1: Special Importation (SPIMR)
- [ ] Create new Importation Approval Request
- [ ] Select "Special Importation (SPIMR)"
- [ ] Verify naming series: EDA-SPIMR-.YYYY.-.#####
- [ ] Add item with mandatory "Requested To" field
- [ ] Save document
- [ ] Verify status = "Pending"

### Test Case 1.2: Annual Importation (APIMR)  
- [ ] Create new Importation Approval Request
- [ ] Select "Annual Importation (APIMR)"
- [ ] Verify naming series: EDA-APIMR-.YYYY.-.#####
- [ ] Verify "Year Plan" field is mandatory
- [ ] Save document successfully

## Phase 2: Approval Process
### Test Case 2.1: Total Approval
- [ ] Set Approval Status: "Totally Approved"
- [ ] Verify approved quantities auto-populate
- [ ] Verify cannot manually edit quantities
- [ ] Submit document successfully

### Test Case 2.2: Partial Approval
- [ ] Set Approval Status: "Partially Approved"
- [ ] Manually edit approved quantities (should work)
- [ ] Verify can only edit in partial approval
- [ ] Submit document

### Test Case 2.3: Refused Approval
- [ ] Set Approval Status: "Refused"
- [ ] Verify approved quantities auto-set to 0
- [ ] Verify cannot edit quantities
- [ ] Submit document

## Phase 3: EDA-IMA Creation
### Test Case 3.1: From SPIMR
- [ ] Open submitted SPIMR
- [ ] Click "Create Importation Approval"
- [ ] Verify naming series: EDA-SPIMA-.YYYY.-.#####
- [ ] Verify SPIMR NO auto-populated
- [ ] Verify quantities auto-transferred
- [ ] Fill mandatory fields:
  - [ ] Valid Date (future date)
  - [ ] Special Condition (text)
  - [ ] Attach Hard Copy (file)
- [ ] Test email notification settings
- [ ] Save and submit

### Test Case 3.2: From APIMR
- [ ] Follow same process with APIMR
- [ ] Verify naming series: EDA-APIMA-.YYYY.-.#####
- [ ] Verify APIMR NO auto-populated

## Phase 4: Purchase Order Creation
### Test Case 4.1: With Email Notification
- [ ] Open submitted EDA-IMA
- [ ] Click "Create Purchase Order"
- [ ] Verify supplier auto-set
- [ ] Verify items and quantities transferred
- [ ] Check email notification sent (if enabled)

### Test Case 4.2: From Closed Document (Should Fail)
- [ ] Create modification to close original
- [ ] Try creating PO from closed document
- [ ] Verify error message appears
- [ ] Confirm PO creation blocked

## Phase 5: Modifications
### Test Case 5.1: SPIMR Modification
- [ ] Open submitted SPIMR
- [ ] Click "Create Modification"
- [ ] Fill modification reason and details
- [ ] Verify new document naming: EDA-SPIMR-MD-.YYYY.-.#####
- [ ] Verify original status: "Closed - Modified"
- [ ] Verify cannot create PO from original

### Test Case 5.2: EDA-IMA Modification
- [ ] Create modification of EDA-IMA
- [ ] Verify naming: EDA-SPIMA-MD-.YYYY.-.#####
- [ ] Verify original document cancelled

## Phase 6: Extensions
### Test Case 6.1: SPIMR Extension
- [ ] Open submitted SPIMR
- [ ] Click "Create Extension"
- [ ] Fill extension details and new date
- [ ] Verify naming: EDA-SPIMR-EX-.YYYY.-.###### (6 digits)
- [ ] Verify original status: "Closed - Extended"

### Test Case 6.2: EDA-IMA Extension
- [ ] Create extension of EDA-IMA
- [ ] Verify naming: EDA-SPIMA-EX-.YYYY.-.###### (6 digits)
- [ ] Test quantity changes if needed

## Phase 7: Validation Testing
### Test Case 7.1: Mandatory Fields
- [ ] Try saving without "Requested To" (should fail)
- [ ] Try APIMR without "Year Plan" (should fail)
- [ ] Try EDA-IMA without "Valid Date" (should fail)
- [ ] Try EDA-IMA without "Attach Hard Copy" (should fail)
- [ ] Try EDA-IMA without "Special Condition" (should fail)
- [ ] Try email notification without email (should fail)

### Test Case 7.2: Quantity Validation
- [ ] Try approved qty > requested qty (should fail)
- [ ] Try editing qty in "Totally Approved" (should fail)
- [ ] Try editing qty in "Refused" (should fail)
- [ ] Confirm editing only works in "Partially Approved"

### Test Case 7.3: Document Version Control
- [ ] Create modification of document
- [ ] Try submitting original after modification
- [ ] Verify version control error message

## Final Verification
- [ ] All naming series follow HTML patterns exactly
- [ ] All mandatory fields enforced
- [ ] Auto-fetch logic works correctly
- [ ] Email notifications functional
- [ ] Document closure prevents unauthorized actions
- [ ] Status transitions work properly
- [ ] Quantity editing restrictions enforced

## Test Results Summary
**Total Tests**: 25+ test cases
**Passed**: ___/25
**Failed**: ___/25
**Issues Found**: ________________

## Notes & Issues
_Use this space to document any issues found during testing:_

1. ________________________________
2. ________________________________
3. ________________________________
4. ________________________________
5. ________________________________

---
**Testing Date**: _______________
**Tested By**: _________________
**Environment**: _______________