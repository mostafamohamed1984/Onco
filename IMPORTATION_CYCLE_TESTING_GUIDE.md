# Importation Cycle Workflow - Complete Testing Guide

## Prerequisites Setup

### 1. Master Data Setup (Required Before Testing)
```
1. Create Items:
   - Go to Stock > Item > New
   - Create at least 3 items with different suppliers
   - Ensure each item has a default supplier set

2. Create Suppliers:
   - Go to Buying > Supplier > New
   - Create at least 2 suppliers with email addresses
   - Note: Email addresses will be used for notification testing

3. Create Customers:
   - Go to Selling > Customer > New
   - Create at least 2 customers
   - These will be used for "Requested To" field
```

## Testing Workflow - Phase by Phase

### PHASE 1: Basic EDA-IMAR Creation (Special Importation)

#### Test Case 1.1: Create Special Importation Approval Request
```
Steps:
1. Go to Onco > Importation Approval Request > New
2. Select Request Type: "Special Importation (SPIMR)"
3. Verify naming series auto-sets to: EDA-SPIMR-.YYYY.-.#####
4. Set Date (should default to today)
5. Add Items:
   - Select Item Code (should auto-fetch Item Name and Supplier)
   - Set Requested To: [Select Customer] ⚠️ MANDATORY
   - Set Requested Quantity: 100
6. Save document
7. Verify Status = "Pending" ✅

Expected Results:
✅ Document saves successfully
✅ Status automatically set to "Pending"
✅ Total Requested Quantity calculated automatically
✅ Supplier auto-fetched from item
✅ REQUESTED TO field is mandatory and enforced
```

#### Test Case 1.2: Create Annual Importation Approval Request
```
Steps:
1. Go to Onco > Importation Approval Request > New
2. Select Request Type: "Annual Importation (APIMR)"
3. Verify naming series auto-sets to: EDA-APIMR-.YYYY.-.#####
4. Set Year Plan: 2024 ⚠️ MANDATORY for APIMR
5. Add Items and save
6. Verify all fields work as in Test 1.1

Expected Results:
✅ Year Plan field appears and is mandatory
✅ Document saves with APIMR naming series
```

### PHASE 2: Approval Process Testing

#### Test Case 2.1: Total Approval Scenario
```
Steps:
1. Open the SPIMR document from Test 1.1
2. Set Approval Status: "Totally Approved"
3. Verify quantities auto-populate:
   - Approved Quantity = Requested Quantity (automatic)
   - Item Status = "Totally Approved"
4. Submit the document
5. Verify Status = "Totally Approved"

Expected Results:
✅ Quantities transfer automatically
✅ Cannot manually edit approved quantities
✅ Document submits successfully
```

#### Test Case 2.2: Partial Approval Scenario
```
Steps:
1. Create new SPIMR with Requested Qty: 100
2. Set Approval Status: "Partially Approved"
3. Manually set Approved Quantity: 60
4. Verify you CAN edit quantities (only in partial approval)
5. Submit document

Expected Results:
✅ Can edit quantities in partial approval
✅ Item Status = "Partially Approved"
✅ Total Approved Qty = 60
```

#### Test Case 2.3: Refused Approval Scenario
```
Steps:
1. Create new SPIMR
2. Set Approval Status: "Refused"
3. Verify Approved Quantity auto-sets to 0
4. Verify cannot edit quantities
5. Submit document

Expected Results:
✅ Approved quantities auto-set to 0
✅ Cannot edit quantities
✅ Status = "Refused"
```

### PHASE 3: EDA-IMA Creation (Importation Approvals)

#### Test Case 3.1: Create Importation Approval from SPIMR
```
Steps:
1. Open submitted SPIMR document
2. Click "Create" > "Create Importation Approval"
3. Verify new EDA-IMA document opens with:
   - Naming series: EDA-SPIMA-.YYYY.-.#####
   - Approval Type: "Special Importation (SPIMA)"
   - Reference No: Auto-populated with SPIMR number ✅
   - Items: Auto-populated from SPIMR ✅
   - Quantities: Auto-transferred ✅

4. Fill mandatory fields:
   - Valid Date: [Future date] ⚠️ MANDATORY
   - Special Condition: "Test conditions" ⚠️ MANDATORY
   - Attach Hard Copy: [Upload file] ⚠️ MANDATORY

5. Email Notification Settings:
   - Check "Mail Notification for suppliers"
   - Enter custom email or leave blank to use supplier default

6. Save and Submit

Expected Results:
✅ All data auto-fetches from SPIMR
✅ SPIMR NO field shows original request number
✅ All mandatory fields enforced
✅ Document submits successfully
```

#### Test Case 3.2: Create Importation Approval from APIMR
```
Steps:
1. Follow same process as 3.1 but with APIMR document
2. Verify naming series: EDA-APIMA-.YYYY.-.#####
3. Verify APIMR NO field populated correctly

Expected Results:
✅ APIMR workflow works identically to SPIMR
✅ Correct naming series and reference numbers
```

### PHASE 4: Purchase Order Creation & Email Testing

#### Test Case 4.1: Purchase Order Creation with Email
```
Steps:
1. Open submitted EDA-IMA document
2. Verify "Create Purchase Order" button available
3. Click "Create" > "Create Purchase Order"
4. Verify new Purchase Order opens with:
   - Supplier: Auto-set from items
   - Items: Auto-populated with approved quantities
   - Reference: Links back to EDA-IMA

5. Check email notification:
   - If email notification was enabled, verify email sent
   - Check supplier email or custom email address

Expected Results:
✅ Purchase Order created successfully
✅ All data transfers correctly
✅ Email notification sent (if enabled)
✅ Supplier receives notification
```

#### Test Case 4.2: Purchase Order Creation from Closed Document (Should Fail)
```
Steps:
1. Create and submit EDA-IMA
2. Create modification (this closes original)
3. Try to create Purchase Order from original (closed) document
4. Verify error message appears

Expected Results:
❌ Purchase Order creation blocked
✅ Error message: "Cannot create Purchase Order from closed document"
```

### PHASE 5: Modification Testing

#### Test Case 5.1: Create Modification of SPIMR
```
Steps:
1. Open submitted SPIMR document
2. Click "Create" > "Create Modification"
3. Fill modification dialog:
   - Modification Reason: "Error"
   - Requested Modification: "Change quantities"
4. Verify new document created with:
   - Naming series: EDA-SPIMR-MD-.YYYY.-.#####
   - Is Modification: Checked
   - Original Document: Links to original
   - Status: "Pending"

5. Verify original document:
   - Status changed to "Closed - Modified"
   - Cannot create Purchase Orders from original

Expected Results:
✅ Modification document created with MD naming series
✅ Original document closed properly
✅ Cannot create PO from closed original
```

#### Test Case 5.2: Create Modification of EDA-IMA
```
Steps:
1. Open submitted EDA-IMA document
2. Create modification with new conditions
3. Verify naming series: EDA-SPIMA-MD-.YYYY.-.#####
4. Verify original document cancelled (docstatus = 2)

Expected Results:
✅ IMA modification works correctly
✅ Original document properly cancelled
```

### PHASE 6: Extension Testing

#### Test Case 6.1: Create Extension of SPIMR
```
Steps:
1. Open submitted SPIMR document
2. Click "Create" > "Create Extension"
3. Fill extension dialog:
   - Extension Reason: "Validation"
   - Extension Details: "Need more time"
   - New Validation Date: [Future date]
4. Verify new document:
   - Naming series: EDA-SPIMR-EX-.YYYY.-.######
   - Is Extension: Checked
   - Original Document: Links to original

Expected Results:
✅ Extension created with EX naming series (6 digits)
✅ Original document closed properly
```

#### Test Case 6.2: Create Extension of EDA-IMA
```
Steps:
1. Follow same process for EDA-IMA
2. Verify naming series: EDA-SPIMA-EX-.YYYY.-.######
3. Test with quantity changes if needed

Expected Results:
✅ IMA extension works correctly
✅ Proper naming series with 6 digits
```

### PHASE 7: Edge Cases & Validation Testing

#### Test Case 7.1: Mandatory Field Validation
```
Test each mandatory field by leaving it blank:
1. REQUESTED TO in item table
2. YEAR PLAN for APIMR type
3. VALID DATE in EDA-IMA
4. ATTACH HARD COPY in EDA-IMA
5. SPECIAL CONDITION in EDA-IMA
6. Supplier email when notification enabled

Expected Results:
❌ Document should not save/submit without mandatory fields
✅ Clear error messages displayed
```

#### Test Case 7.2: Quantity Validation
```
Steps:
1. Try to set Approved Qty > Requested Qty
2. Try to edit quantities in "Totally Approved" status
3. Try to edit quantities in "Refused" status
4. Verify only "Partially Approved" allows editing

Expected Results:
❌ Cannot exceed requested quantity
❌ Cannot edit in total approval (auto-set)
❌ Cannot edit in refused (auto-set to 0)
✅ Can only edit in partial approval
```

#### Test Case 7.3: Document Version Control
```
Steps:
1. Create modification of a document
2. Try to submit the original document after modification created
3. Verify version control prevents outdated submissions

Expected Results:
❌ Cannot submit outdated versions
✅ Clear error message about newer version
```

## Testing Checklist Summary

### ✅ Basic Functionality
- [ ] SPIMR creation with correct naming series
- [ ] APIMR creation with Year Plan mandatory
- [ ] Status auto-sets to "Pending" on save
- [ ] All mandatory fields enforced

### ✅ Approval Process
- [ ] Total approval auto-sets quantities
- [ ] Partial approval allows manual editing
- [ ] Refused approval auto-sets to zero
- [ ] Quantity editing restrictions work

### ✅ EDA-IMA Creation
- [ ] Auto-fetch from SPIMR/APIMR works
- [ ] SPIMR NO/APIMR NO populates correctly
- [ ] All mandatory fields enforced
- [ ] Email notification settings work

### ✅ Purchase Order Creation
- [ ] PO creates with correct data
- [ ] Email notifications sent
- [ ] Cannot create from closed documents
- [ ] Supplier data transfers correctly

### ✅ Modifications
- [ ] MD naming series correct
- [ ] Original documents close properly
- [ ] Cannot create PO from closed originals
- [ ] Modification data preserved

### ✅ Extensions
- [ ] EX naming series correct (6 digits)
- [ ] Extension logic works properly
- [ ] Document closure prevents further actions
- [ ] New validation dates accepted

### ✅ Validation & Security
- [ ] All mandatory fields enforced
- [ ] Quantity validation works
- [ ] Document version control works
- [ ] Status-based editing restrictions work

## Troubleshooting Common Issues

### Issue: Email not sending
**Solution**: Check supplier email addresses and SMTP settings

### Issue: Naming series not auto-setting
**Solution**: Verify request_type/approval_type is selected first

### Issue: Quantities not auto-populating
**Solution**: Ensure original document is submitted before creating approval

### Issue: Cannot create Purchase Order
**Solution**: Verify document is submitted and not closed

## Test Data Recommendations

Create test data with these patterns:
- **Items**: TEST-ITEM-001, TEST-ITEM-002, TEST-ITEM-003
- **Suppliers**: Test Supplier A, Test Supplier B (with valid emails)
- **Customers**: Test Customer 1, Test Customer 2
- **Quantities**: Use round numbers (100, 200, 500) for easy validation

This comprehensive testing approach will validate every aspect of the importation cycle workflow and ensure all requirements from the HTML documentation are working correctly.