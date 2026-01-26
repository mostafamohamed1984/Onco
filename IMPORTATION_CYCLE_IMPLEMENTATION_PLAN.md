# Importation Cycle Implementation Plan

## Executive Summary
The current importation cycle workflow is approximately 60% complete. This plan addresses the critical gaps and provides a roadmap to complete the implementation.

## Phase 1: Create Missing Core Doctypes (Week 1-2)

### 1. Create Importation Approval Request (EDA-IMAR) Doctype
**Purpose**: Replace the current Supplier Quotation workaround

**Required Fields**:
- `naming_series`: EDA-SPIMR-.YYYY.-.##### and EDA-APIMR-.YYYY.-.#####
- `request_type`: Special (SPIMR) | Annual (APIMR)
- `product_name`: Link to Item
- `supplier_name`: Link to Supplier (auto-fetched from Item)
- `requested_quantity`: Float
- `requested_to`: Link to Customer
- `date`: Date (manual entry)
- `year_plan`: Int (for APIMR only)
- `status`: Pending | Totally Approved | Partially Approved | Refused
- `approved_quantity`: Float (for partial approvals)
- `attachments`: Attach field

**Child Table**: Importation Approval Request Item
- `item_code`: Link to Item
- `supplier`: Link to Supplier
- `requested_qty`: Float
- `approved_qty`: Float
- `status`: Select

### 2. Create Importation Approvals (EDA-IMA) Doctype
**Purpose**: Separate approval tracking from requests

**Required Fields**:
- `naming_series`: EDA-SPIMA-.YYYY.-.##### and EDA-APIMA-.YYYY.-.#####
- `approval_type`: Special (SPIMA) | Annual (APIMA)
- `importation_approval_request`: Link to Importation Approval Request
- `spimr_no` / `apimr_no`: Data (auto-fetched)
- `quantity`: Float (auto-fetched from request)
- `valid_date`: Date
- `special_conditions`: Text
- `hard_copy_attachment`: Attach
- `status`: Draft | Submitted

**Actions Available After Submit**:
- Create Purchase Order
- Create Modification (EDA-IMAPR-MD-YYYY-#####)
- Create Extension (EDA-SPIMR-EX-YYYY-##### / EDA-APIMR-EX-YYYY-#####)

## Phase 2: Complete Authority Good Release Implementation (Week 2-3)

### Fix Authority Good Release Doctype
**Missing Fields to Add**:
- `requested_qty`: Float
- `released_qty`: Float  
- `actual_qty`: Float
- `net_released_qty`: Float (calculated: released_qty - shortage_control_qty)
- `shortage_control_qty`: Float
- `sample_qty`: Float (for analysis batch)
- `warehouse_from`: Link to Warehouse (default: "Under Release")
- `warehouse_to`: Link to Warehouse (default: "Sales Warehouse")

**Child Table: Authority Good Release Item**:
- `item_code`: Link to Item
- `batch_no`: Data
- `manufacturing_date`: Date
- `expiry_date`: Date
- `requested_qty`: Float
- `released_qty`: Float
- `actual_qty`: Float
- `net_released_qty`: Float (calculated)
- `shortage_control_qty`: Float
- `sample_qty`: Float

**Business Logic to Implement**:
- Lot Release: Net Released = Released Qty - Shortage Control Qty
- Analysis Batch: Handle partial/total release with sample withdrawal
- Auto-create Stock Entry on submit to transfer goods from "Under Release" to "Sales Warehouse"

## Phase 3: Complete Workflow Integration (Week 3-4)

### 3.1 Fix Shipments Doctype
**Issues to Fix**:
- Remove duplicate `restricted_release_status` field
- Complete Shipment Invoice child table configuration
- Add automatic data fetching from Purchase Invoice

**Missing Child Table: Shipment Invoice**:
- `purchase_invoice`: Link to Purchase Invoice
- `invoice_no`: Data
- `invoice_date`: Date
- `invoice_amount`: Currency
- `supplier`: Link to Supplier

### 3.2 Complete Purchase Receipt Report
**Missing Fields**:
- `batch_no`: Data
- `manufacturing_date`: Date
- `expiry_date`: Date
- `shortage_control_calculation`: Section Break
- `total_received_qty`: Float
- `damaged_qty`: Float
- `shortage_qty`: Float
- `net_accepted_qty`: Float (calculated)

**Auto-fetch Logic**:
- Fetch shipment data automatically from linked Purchase Receipt
- Auto-populate vehicle and document information

### 3.3 Complete Printing Order Implementation
**Missing Fields**:
- `awb_no`: Data (fetched from Purchase Invoice)
- `invoice_info`: Section Break
- `printing_quantities`: Float
- `rest_quantities`: Float
- `batch_details`: Text

**Child Table: Printing Order Item**:
- `item_code`: Link to Item
- `item_name`: Data
- `batch_no`: Data
- `printing_qty`: Float
- `rest_qty`: Float
- `status`: Pending | Completed

## Phase 4: Implement Workflow Automations (Week 4-5)

### 4.1 Automatic Data Fetching
1. **Purchase Invoice → Shipment**: Auto-fetch invoice data
2. **Shipment → Purchase Receipt**: Auto-link and fetch shipment data
3. **Purchase Receipt → Purchase Receipt Report**: Auto-fetch receipt data
4. **Purchase Receipt Report → Printing Order**: Auto-create with item data
5. **Printing Order → Authority Good Release**: Auto-link for final release

### 4.2 Workflow State Machine
- Implement approval workflow for EDA-IMAR → EDA-IMA
- Add quantity validation through the entire workflow
- Implement status tracking and blocking logic

### 4.3 Stock Transfer Automation
- Authority Good Release → Auto-create Stock Entry
- Transfer from "Under Release" warehouse to "Sales Warehouse"
- Handle sample quantities to "Sample Warehouse"

## Phase 5: Fix Standard Doctype Customizations (Week 5-6)

### 5.1 Purchase Order Enhancements
**Add Missing Fields**:
- `importation_approval`: Link to Importation Approvals
- `eda_reference`: Data (EDA-SPIMA/APIMA number)
- Email notification option for suppliers

### 5.2 Tenders Doctype Fixes
**Missing Fields in Item Tender Child Table**:
- `tender_price`: Currency
- `item_cost`: Currency (for price deviation calculation)

**Missing Fields in Distributor Offers**:
- `discount_percent`: Percent
- `credit_limit`: Currency

### 5.3 Sales Invoice Integration
- Complete price deviation blocking logic
- Implement "Losses Approval" workflow for items where Tender Price < Item Cost

## Implementation Priority Matrix

| Component | Priority | Effort | Impact |
|-----------|----------|--------|--------|
| Create EDA-IMAR Doctype | CRITICAL | High | High |
| Create EDA-IMA Doctype | CRITICAL | High | High |
| Complete Authority Good Release | CRITICAL | Medium | High |
| Fix Shipments Configuration | HIGH | Medium | Medium |
| Implement Stock Transfer | HIGH | Medium | High |
| Complete Purchase Receipt Report | MEDIUM | Low | Medium |
| Complete Printing Order | MEDIUM | Low | Medium |
| Fix Tenders Fields | LOW | Low | Low |

## Success Criteria

### Phase 1 Complete:
- [ ] EDA-IMAR doctype created and functional
- [ ] EDA-IMA doctype created and functional
- [ ] Proper naming series configured
- [ ] Basic workflow: Request → Approval → Purchase Order works

### Phase 2 Complete:
- [ ] Authority Good Release calculates quantities correctly
- [ ] Stock transfer automation works
- [ ] Sample withdrawal logic implemented

### Phase 3 Complete:
- [ ] All workflow steps are connected
- [ ] Data flows automatically between steps
- [ ] No manual data re-entry required

### Phase 4 Complete:
- [ ] Full workflow validation
- [ ] Status tracking works correctly
- [ ] Email notifications functional

### Phase 5 Complete:
- [ ] All standard doctypes properly customized
- [ ] Price deviation blocking works
- [ ] System ready for production

## Risk Mitigation

### High Risk Items:
1. **Data Migration**: Moving from Supplier Quotation to new doctypes
   - **Mitigation**: Create migration script to transfer existing data
   
2. **Naming Series Conflicts**: EDA series might conflict with existing data
   - **Mitigation**: Start new series from current max + 1
   
3. **Stock Entry Automation**: Complex business logic for different release types
   - **Mitigation**: Implement with extensive testing and rollback capability

### Medium Risk Items:
1. **Workflow Integration**: Complex dependencies between doctypes
   - **Mitigation**: Implement step-by-step with thorough testing
   
2. **User Training**: New workflow requires user adaptation
   - **Mitigation**: Create user guides and training sessions

## Next Steps

1. **Immediate (This Week)**:
   - Create EDA-IMAR doctype JSON file
   - Create EDA-IMA doctype JSON file
   - Configure naming series in hooks.py

2. **Week 1-2**:
   - Implement basic workflow: Request → Approval → Purchase Order
   - Test with sample data

3. **Week 2-3**:
   - Complete Authority Good Release implementation
   - Test stock transfer automation

4. **Week 3-4**:
   - Implement remaining workflow automations
   - End-to-end testing

5. **Week 4-5**:
   - User acceptance testing
   - Documentation and training materials

6. **Week 5-6**:
   - Production deployment
   - Data migration
   - Go-live support

## Conclusion

The importation cycle workflow has a solid foundation but requires focused effort to complete. The most critical need is creating proper doctypes for EDA-IMAR and EDA-IMA to replace the current Supplier Quotation workaround. Once these core components are in place, the remaining workflow integration should proceed smoothly.

Estimated total effort: 5-6 weeks with 1-2 developers working full-time.