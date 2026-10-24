import json, csv

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
sample_out = {r['case_id']: r for r in csv.DictReader(open('dataset/sample_output.csv', encoding='utf-8'))}
for s in samples[:10]:
    cid = s['case_id']
    steps = json.loads(sample_out[cid]['steps_json'])
    print(f'=== {cid} ({sample_out[cid]["deletion_status"]}) ===')
    for st in steps:
        print(f'  {st["phase"]} | {st["system_id"]} | {st["resource_id"]} | {st["operation"]} | {st["state"]} | {st["evidence_id"]}')
