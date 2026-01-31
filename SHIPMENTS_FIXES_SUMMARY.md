# Shipments Module - Customer Requirements Implementation

## تم تنفيذ المتطلبات التالية / Following Requirements Implemented

### 1. حماية حقل الحالة (Status Field Protection)

**المشكلة / Problem:**
- المستخدم كان يستطيع تغيير حقل Status يدوياً وتجاوز التسلسل الصحيح
- Users could manually edit the status field and bypass the correct sequence

**الحل / Solution:**
- تم جعل حقل Status للقراءة فقط بشكل كامل
- Status field is now completely read-only
- لا يمكن تغييره يدوياً أو عبر API
- Cannot be changed manually or via API
- يتم تحديثه تلقائياً بناءً على إكمال المراحل
- Automatically updated based on milestone completion

**التسلسل الصحيح / Correct Sequence:**
```
Planned → In Progress → Completed
```

---

### 2. جلب جميع العناصر من الفاتورة (Fetch All Invoice Items)

**المشكلة / Problem:**
- عند إنشاء Shipment من Purchase Invoice تحتوي على عدة عناصر (من عدة Purchase Orders)
- When creating Shipment from Purchase Invoice with multiple items (from multiple POs)
- كان يتم جلب أول عنصر فقط
- Only the first item was being fetched

**الحل / Solution:**
- تم تحديث جدول "Purchase Invoices" ليحتوي على صف لكل عنصر
- Updated "Purchase Invoices" child table to have one row per item
- يتم جلب جميع العناصر من الفاتورة تلقائياً
- All items from the invoice are automatically fetched
- كل عنصر له معلوماته الكاملة (الكود، الكمية، السعر، إلخ)
- Each item has complete information (code, qty, rate, etc.)

**مثال / Example:**
```
Purchase Invoice has 5 items from 3 different POs
↓
Click "Create Shipments"
↓
Shipment created with 5 rows in Purchase Invoices table
(one row for each item)
```

---

## التغييرات التقنية / Technical Changes

### Files Modified:

1. **shipments.json**
   - Enhanced status field protection
   - Updated child table reference to "Purchase Invoices"

2. **shipments.py**
   - Added `before_save()` validation for status
   - Enhanced `make_purchase_receipt()` to handle all items
   - Improved item mapping from child table

3. **shipment_invoice.json** (renamed to Purchase Invoices)
   - Added `item_code` field
   - Renamed doctype for clarity

4. **create_shipments_btn.js**
   - Updated to fetch ALL items from Purchase Invoice
   - Creates one row per item in child table
   - Populates complete item information

5. **shipments.js**
   - Updated child table reference
   - Added item_code field handling

---

## سير العمل الكامل / Complete Workflow

```
Importation Approval Request
  ↓
Importation Approvals
  ↓
Purchase Order(s) - يمكن إنشاء عدة أوامر / Multiple POs possible
  ↓
Purchase Invoice - يمكن دمج عدة أوامر / Can consolidate multiple POs
  ↓ [Create Shipments Button]
Shipments - جميع العناصر تظهر / All items appear
  ↓ [Purchase Invoices child table - صف لكل عنصر / one row per item]
  ↓ [Create Purchase Receipt Button]
Purchase Receipt - جميع العناصر مضمنة / All items included
  ↓
Purchase Receipt Report
  ↓
Authority Good Release
  ↓
Stock Entry
```

---

## الحقول في جدول Purchase Invoices / Fields in Purchase Invoices Table

| Field | Type | Description (EN) | الوصف (AR) |
|-------|------|------------------|------------|
| purchase_invoice | Link | Purchase Invoice reference | مرجع الفاتورة |
| invoice_no | Data | Invoice number | رقم الفاتورة |
| invoice_date | Date | Invoice date | تاريخ الفاتورة |
| **item_code** | Link | Item code (NEW) | كود الصنف (جديد) |
| item_name | Data | Item name | اسم الصنف |
| qty | Float | Quantity | الكمية |
| uom | Data | Unit of measure | وحدة القياس |
| rate | Currency | Rate per unit | السعر للوحدة |
| amount | Currency | Total amount | المبلغ الإجمالي |
| batch_no | Data | Batch number | رقم الدفعة |
| expiry_date | Date | Expiry date | تاريخ الانتهاء |

---

## اختبار التحديثات / Testing the Updates

### Test 1: Status Protection
1. Create new Shipment
2. Try to change Status field manually → Should be prevented ✓
3. Complete a milestone → Status auto-updates ✓

### Test 2: Multiple Items
1. Create Purchase Invoice with 5 items from 3 POs
2. Click "Create Shipments" button
3. Verify 5 rows appear in Purchase Invoices table ✓
4. Verify each row has correct item_code, qty, rate ✓
5. Create Purchase Receipt
6. Verify all 5 items are in Purchase Receipt ✓

---

## ملاحظات مهمة / Important Notes

### للمستخدمين / For Users:
- ✅ لا تحاول تغيير حقل Status يدوياً - سيتم رفضه
- ✅ Don't try to change Status field manually - it will be rejected
- ✅ جميع العناصر من الفاتورة ستظهر تلقائياً
- ✅ All items from invoice will appear automatically
- ✅ تأكد من مراجعة جميع العناصر قبل الحفظ
- ✅ Review all items before saving

### للمطورين / For Developers:
- Child table renamed: "Shipment Invoice" → "Purchase Invoices"
- New field added: `item_code` in child table
- Status field has enhanced validation in both client and server
- `make_purchase_receipt()` now handles multiple items correctly

---

## الدعم / Support

For detailed technical documentation, see:
- `SHIPMENTS_ENHANCEMENTS.md` - Full technical details
- `importation_cycle_workflow.md` - Complete workflow documentation

للحصول على الوثائق التقنية الكاملة، راجع:
- `SHIPMENTS_ENHANCEMENTS.md` - التفاصيل التقنية الكاملة
- `importation_cycle_workflow.md` - وثائق سير العمل الكامل
