import csv, json

with open('output.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Check evidence_id presence in finding steps
ev_cited = 0
total_finding = 0
for r in rows:
    steps = json.loads(r['steps_json'])
    for s in steps:
        if s['phase'] == 'FINDING':
            total_finding += 1
            if s.get('evidence_id'):
                ev_cited += 1
print(f'Findings with evidence_id: {ev_cited}/{total_finding}')

# Verify step numbering
bad_numbering = 0
for r in rows:
    steps = json.loads(r['steps_json'])
    for i, s in enumerate(steps, 1):
        if s['step_no'] != i:
            print(f"Step numbering error in {r['case_id']}: expected {i}, got {s['step_no']}")
            bad_numbering += 1
            break
if bad_numbering == 0:
    print('Step numbering: all correct')

# Phase ordering check
bad_order = 0
for r in rows:
    steps = json.loads(r['steps_json'])
    phases = [s['phase'] for s in steps]
    valid = ['FINDING', 'REMEDIATION', 'VERIFICATION']
    phase_order = [phases.index(p) for p in set(phases) if p in valid]
    last = -1
    ok = True
    for p in phases:
        idx = valid.index(p)
        if idx < last:
            ok = False
            break
        last = idx
    if not ok:
        print(f"Phase order wrong in {r['case_id']}: {phases}")
        bad_order += 1
if bad_order == 0:
    print('Phase ordering: all correct')

print('Total rows:', len(rows))
