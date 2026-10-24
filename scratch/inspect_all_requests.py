import csv

print("=== SAMPLE REQUESTS ===")
with open('dataset/sample_deletion_requests.csv', newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        print(f"{r['case_id']}: {r['request_text']}")
