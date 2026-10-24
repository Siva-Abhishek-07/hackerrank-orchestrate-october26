import csv, json
from collections import Counter

with open('output.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f'Total rows: {len(rows)}')
print('First row case_id:', rows[0]['case_id'], 'status:', rows[0]['deletion_status'])
print('Last row case_id:', rows[-1]['case_id'], 'status:', rows[-1]['deletion_status'])

# Check all steps are valid JSON arrays
errors = 0
for r in rows:
    try:
        steps = json.loads(r['steps_json'])
        assert isinstance(steps, list)
    except Exception as e:
        print(f"ERROR in {r['case_id']}: {e}")
        errors += 1
print(f'JSON validation: {errors} errors')

# Check step field completeness  
for r in rows:
    steps = json.loads(r['steps_json'])
    for s in steps:
        for field in ['step_no', 'phase', 'system_id', 'resource_id', 'operation', 'state']:
            if field not in s:
                print(f"MISSING FIELD {field} in {r['case_id']}: {s}")

# Check NOT_APPLICABLE cases
na_cases = [r for r in rows if r['deletion_status'] == 'NOT_APPLICABLE']
for r in na_cases:
    assert r['steps_json'] == '[]', f"{r['case_id']} has non-empty steps"
print(f'NOT_APPLICABLE cases: {len(na_cases)} (all have empty steps OK)')

# Status distribution
status_counts = Counter(r['deletion_status'] for r in rows)
print('Status distribution:', dict(status_counts))
