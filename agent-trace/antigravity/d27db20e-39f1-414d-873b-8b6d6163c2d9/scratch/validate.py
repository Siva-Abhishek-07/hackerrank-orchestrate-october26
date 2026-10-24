#!/usr/bin/env python3
"""Validate output.csv against sample_output.csv."""
import csv
import json
import sys
import os

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return {r['case_id']: r for r in csv.DictReader(f)}

sample_output = load_csv('dataset/sample_output.csv')
my_output = load_csv('output.csv')

# Check all sample cases
correct_status = 0
wrong_status = 0
total_steps_expected = 0
total_steps_got = 0

for case_id, expected in sorted(sample_output.items()):
    got = my_output.get(case_id, {})

    exp_status = expected['deletion_status']
    got_status = got.get('deletion_status', 'MISSING')

    exp_steps = json.loads(expected.get('steps_json', '[]'))
    got_steps = json.loads(got.get('steps_json', '[]'))

    status_match = exp_status == got_status

    if status_match:
        correct_status += 1
    else:
        wrong_status += 1

    mark = 'OK' if status_match else 'FAIL'
    print(f"{case_id}: expected={exp_status}, got={got_status} [{mark}]")

    total_steps_expected += len(exp_steps)
    total_steps_got += len(got_steps)

    if not status_match:
        print(f"  Expected steps ({len(exp_steps)}):")
        for s in exp_steps[:5]:
            print(f"    {s['step_no']:2d} [{s['phase'][:4]}] {s['system_id']:25s} {s['resource_id']:20s} {s['operation']}")
        print(f"  Got steps ({len(got_steps)}):")
        for s in got_steps[:5]:
            print(f"    {s['step_no']:2d} [{s['phase'][:4]}] {s['system_id']:25s} {s['resource_id']:20s} {s['operation']}")
        print()

print(f"\n=== SUMMARY ===")
print(f"Status accuracy: {correct_status}/{len(sample_output)} ({100*correct_status/len(sample_output):.1f}%)")
print(f"Expected total steps: {total_steps_expected}")
print(f"Got total steps: {total_steps_got}")
