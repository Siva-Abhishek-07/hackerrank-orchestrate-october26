import sys
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/deletion_requests.csv')

def is_deletion_request(text: str) -> bool:
    t = text.lower()
    # Explicit non-deletion indicators
    non_del_phrases = [
        "not asking for deletion", "not a request to erase",
        "leave the account", "keep the account", "without removing",
        "leave my profile", "continue using the service",
        "do not close the account", "don't delete", "do not delete",
        "marketing lists only", "promotional emails",
        "is misspelled", "need help resetting"
    ]
    for p in non_del_phrases:
        if p in t:
            return False
    return True

non_del_cases = []
for idx, r in df_req.iterrows():
    if not is_deletion_request(r['request_text']):
        non_del_cases.append((r['case_id'], r['request_text']))

print(f"Total NOT_APPLICABLE cases identified: {len(non_del_cases)}")
for c, t in non_del_cases:
    print(f"[{c}] {t}")
