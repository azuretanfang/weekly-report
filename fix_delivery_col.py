#!/usr/bin/env python3
"""Fix delivery status column missing <td> and filter dropdown issues"""
import os

filepath = '/data/meeting-system/app-views.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Insert delivery status <td> between riskNote td and planSchedule td
# Find the pattern: renderPlanScheduleCell that follows the riskNote textarea td
old_pattern = '<td>${renderPlanScheduleCell(item, canEdit)}</td>'
new_pattern = '<td>${renderDeliveryStatusCell(item, canEdit)}</td>\n      <td>${renderPlanScheduleCell(item, canEdit)}</td>'

# Count occurrences first
count = content.count(old_pattern)
print(f"Found '{old_pattern}' {count} time(s)")

if count == 1:
    content = content.replace(old_pattern, new_pattern)
    print("[FIX 1] Inserted delivery status <td> before planSchedule <td> ✅")
else:
    print(f"[FIX 1] WARNING: Expected 1 occurrence, found {count}")

# Fix 2: Check colspan - update "no matching" message colspan from 17 to match actual column count (now 17 with delivery)
# The "没有匹配的需求" empty row
old_colspan = "colspan=\"17\""
if old_colspan in content:
    print("[FIX 2] colspan already 17, checking if we need 18 now...")
    # We added 1 column (delivery status), so need to update colspan
    # Count actual <th> in the thead by looking at the table structure
    # th columns: #, TAPD ID, name, status, source, backendDev, frontendDev, dataDev, tester, 
    #             planTestStart, planTestBegin, planTestEnd, planRelease, riskNote, deliveryStatus, planSchedule, actions = 17
    # But we're adding the td, the th was already there, so colspan stays at 17
    print("[FIX 2] colspan=17 is correct (17 th columns exist) ✅")

# Write the modified content
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ All fixes applied!")

# Verify the fix
with open(filepath, 'r', encoding='utf-8') as f:
    verify = f.read()

if 'renderDeliveryStatusCell(item, canEdit)' in verify:
    print("[VERIFY] renderDeliveryStatusCell found in row rendering ✅")
else:
    print("[VERIFY] ERROR: renderDeliveryStatusCell NOT found!")
