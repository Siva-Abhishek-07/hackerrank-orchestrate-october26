import csv, re

print("=== CHECKING DELETION_REQUESTS.CSV FOR NON-DELETION INTENTS ===")
with open('dataset/deletion_requests.csv', newline='', encoding='utf-8') as f:
    for i, r in enumerate(csv.DictReader(f)):
        t = r['request_text']
        # Look for things that clearly do NOT want deletion
        # e.g., update, correct, access, export without delete
        # Let's inspect rows with update / phone / email / export / download / correct / invoice / surname / address
        lower = t.lower()
        if any(w in lower for w in ['update', 'correct', 'misspell', 'invoice', 'export', 'download', 'access', 'opt-out', 'opt out', 'keep', 'rectify']):
            # Print to inspect
            print(f"Row {i+1} ({r['case_id']}): {t}")
