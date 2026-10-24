import csv, json
from pathlib import Path

txt_path = Path("dataset/evidence/records/customer_account_handover_20261001.txt")
lines = txt_path.read_text(encoding='utf-8').splitlines()

# Handover parser
def parse_handover(lines, emails, uid):
    records = []
    for line in lines:
        line = line.strip()
        if not line.startswith("- "):
            continue
        parts = [p.strip() for p in line[2:].split("|")]
        if len(parts) >= 6:
            ts, system_id, resource_id, cat, status, target = parts[:6]
            
            # Check match
            target_lower = target.lower()
            is_match = False
            if target_lower in emails: is_match = True
            if uid and uid.lower() == target_lower: is_match = True
            
            if is_match:
                # Determine state
                if status == "NOT_FOUND": state = "ABSENT"
                elif status == "FOUND": state = "PRESENT"
                elif status == "IDENTIFIABLE": state = "EXPOSED_PII"
                elif status == "ANONYMIZED": state = "ANONYMIZED"
                elif status == "REDACTED": state = "REDACTED"
                elif status == "ACTIVE":
                    state = "ACTIVE" if system_id == "integration_service" else "RESTORE_RISK"
                elif status == "DISABLED": state = "DISABLED"
                elif status == "BLOCKED": state = "BLOCKED"
                else: state = "PRESENT"
                
                records.append({
                    "system_id": system_id,
                    "resource_id": resource_id,
                    "state": state,
                    "category": cat
                })
    return records

print("case_11 (novak.tomasz@icloud.com, user_32):")
r11 = parse_handover(lines, {"novak.tomasz@icloud.com"}, "user_32")
for r in r11: print(" ", r)

print("\ncase_13 (noor-khalil@proton.me, user_33):")
r13 = parse_handover(lines, {"noor-khalil@proton.me"}, "user_33")
for r in r13: print(" ", r)

print("\ncase_14 (y.tanaka32@gmail.com, user_37):")
r14 = parse_handover(lines, {"y.tanaka32@gmail.com"}, "user_37")
for r in r14: print(" ", r)
