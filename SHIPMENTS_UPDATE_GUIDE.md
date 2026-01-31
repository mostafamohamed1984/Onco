# Shipments Module Update Guide

## Overview
This guide walks you through updating the Shipments module with the latest enhancements for status validation and multiple invoice items handling.

## Prerequisites
- Backup your database before proceeding
- Ensure you have bench access
- Stop any running processes

## Update Steps

### Step 1: Backup Database
```bash
# Create a backup
bench --site [your-site] backup

# Verify backup was created
ls -lh ~/frappe-bench/sites/[your-site]/private/backups/
```

### Step 2: Update Doctype Files

The following files have been updated:
- `onco/onco/doctype/shipments/shipments.json`
- `onco/onco/doctype/shipments/shipments.py`
- `onco/onco/doctype/shipments/shipments.js`
- `onco/onco/doctype/shipment_invoice/shipment_invoice.json` (renamed to Purchase Invoices)
- `onco/onco/client scripts/create_shipments_btn.js`

### Step 3: Migrate Doctype

```bash
# Navigate to bench directory
cd ~/frappe-bench

# Migrate the site
bench --site [your-site] migrate

# Clear cache
bench --site [your-site] clear-cache

# Rebuild assets
bench build --app onco
```

### Step 4: Run Migration Script (Optional)

If you have existing Shipment records, run the migration script to update them:

```bash
# Run migration
bench --site [your-site] execute onco.migrate_shipment_invoices.migrate_all

# Generate report to check for issues
bench --site [your-site] execute onco.migrate_shipment_invoices.generate_migration_report
```

### Step 5: Restart Services

```bash
# Restart bench
bench restart

# Or if using supervisor
sudo supervisorctl restart all
```

### Step 6: Verify Updates

1. **Test Status Field Protection:**
   - Open any Shipment document
   - Try to manually change the Status field
   - Should be read-only and cannot be changed

2. **Test Multiple Items:**
   - Create a Purchase Invoice with multiple items
   - Click "Create Shipments" button
   - Verify all items appear in the Purchase Invoices child table
   - Each item should have its own row with complete information

3. **Test Purchase Receipt Creation:**
   - Complete all milestones in a Shipment
   - Click "Create Purchase Receipt"
   - Verify all items from all invoices are included

## Troubleshooting

### Issue: Migration fails with "DocType not found"

**Solution:**
```bash
# Reload doctype
bench --site [your-site] reload-doctype Shipments
bench --site [your-site] reload-doctype "Purchase Invoices"
```

### Issue: Status field still editable

**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard reload the page (Ctrl+Shift+R)
3. Clear server cache:
```bash
bench --site [your-site] clear-cache
bench --site [your-site] clear-website-cache
```

### Issue: Items not appearing in child table

**Solution:**
1. Check if Purchase Invoice has items
2. Verify Purchase Invoice is submitted (docstatus = 1)
3. Check browser console for JavaScript errors
4. Verify the client script is loaded:
```bash
bench --site [your-site] execute frappe.clear_cache
bench build --app onco
```

### Issue: "Purchase Invoices" child table not found

**Solution:**
The child table was renamed from "Shipment Invoice" to "Purchase Invoices". You may need to:

```bash
# Option 1: Rename via bench console
bench --site [your-site] console

# In console:
frappe.rename_doc("DocType", "Shipment Invoice", "Purchase Invoices", force=True)
frappe.db.commit()
exit()

# Option 2: Manual migration
# Contact support for assistance
```

## Rollback Procedure

If you need to rollback the changes:

### Step 1: Restore Database
```bash
# List available backups
ls -lh ~/frappe-bench/sites/[your-site]/private/backups/

# Restore from backup
bench --site [your-site] restore [backup-file-path]
```

### Step 2: Revert Code Changes
```bash
cd ~/frappe-bench/apps/onco
git log --oneline  # Find the commit before changes
git revert [commit-hash]
```

### Step 3: Migrate and Restart
```bash
bench --site [your-site] migrate
bench restart
```

## Post-Update Checklist

- [ ] Database backup completed
- [ ] Doctype migration successful
- [ ] Cache cleared
- [ ] Assets rebuilt
- [ ] Services restarted
- [ ] Status field is read-only
- [ ] Multiple items appear in child table
- [ ] Purchase Receipt includes all items
- [ ] No console errors in browser
- [ ] Migration script executed (if needed)
- [ ] All users notified of changes

## Key Changes Summary

### 1. Status Field
- Now completely read-only
- Cannot be changed manually or via API
- Automatically updated based on milestones
- Enhanced validation in both client and server

### 2. Purchase Invoices Child Table
- Renamed from "Shipment Invoice"
- Added `item_code` field
- One row per item (not one row per invoice)
- Automatically populated from Purchase Invoice

### 3. Purchase Receipt Creation
- Now includes all items from all linked invoices
- Proper mapping of item details
- Correct warehouse assignments

## Support

For issues or questions:
1. Check `SHIPMENTS_ENHANCEMENTS.md` for technical details
2. Review `SHIPMENTS_FIXES_SUMMARY.md` for user guide
3. Contact development team with:
   - Error messages
   - Steps to reproduce
   - Browser console logs
   - Server logs from `~/frappe-bench/logs/`

## Additional Resources

- **Technical Documentation**: `SHIPMENTS_ENHANCEMENTS.md`
- **User Guide**: `SHIPMENTS_FIXES_SUMMARY.md`
- **Workflow Documentation**: `onco/onco/importation_cycle_workflow.md`
- **Migration Script**: `migrate_shipment_invoices.py`

## Version Information

- **Update Date**: January 31, 2026
- **Module**: Onco - Shipments
- **Changes**: Status validation + Multiple invoice items
- **Breaking Changes**: Child table renamed (migration required)
- **Backward Compatible**: Yes (with migration script)
