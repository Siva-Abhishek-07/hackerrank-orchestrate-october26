import csv

with open('dataset/deletion_requests.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
    for i in range(495, len(rows)):
        r = rows[i]
        print(f"Row {i+1} ({r['case_id']}): {r['request_text']}")
