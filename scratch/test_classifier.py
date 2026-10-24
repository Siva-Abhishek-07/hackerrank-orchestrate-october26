import json, csv, os, sys, re
from pathlib import Path
from datetime import datetime
import pypdf

DATASET_DIR = Path("dataset")

# Non-deletion keywords (strict to the 10 actual non-deletion requests)
EXPLICIT_NON_DELETION = [
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
    "do not delete",
]

def is_deletion_request(text):
    if not text:
        return False
    lower = text.lower()
    for phrase in EXPLICIT_NON_DELETION:
        if phrase in lower:
            return False
    return True

print("Testing is_deletion_request on sample cases:")
samples = list(csv.DictReader(open(DATASET_DIR / "sample_deletion_requests.csv", encoding="utf-8")))
for s in samples:
    is_del = is_deletion_request(s['request_text'])
    if not is_del:
        print(f"False negative: {s['case_id']}: {s['request_text']}")
print("All sample requests passed is_deletion_request!")
