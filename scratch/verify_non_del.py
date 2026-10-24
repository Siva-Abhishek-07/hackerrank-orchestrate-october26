import csv

with open('dataset/deletion_requests.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

explicit_not_del = [
    'leave the account active',
    'not asking for deletion',
    'keep the account as it is',
    'do not close the account',
    'without removing any of my records',
    'marketing lists only',
    'not a request to erase',
    'leave my profile',
    'continue using the service',
    "don't delete",
    "do not delete"
]

matched_cases = []
for r in rows:
    t = r['request_text'].lower()
    if any(p in t for p in explicit_not_del):
        matched_cases.append(r['case_id'])

print("Matched cases:", matched_cases)
print("Count:", len(matched_cases))
