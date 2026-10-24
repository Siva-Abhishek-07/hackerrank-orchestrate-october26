import csv, json
import os, sys, re
import importlib.util

spec = importlib.util.spec_from_file_location("agent_main", os.path.join(os.getcwd(), "code", "main.py"))
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)

# Let's check how trace grouping can be implemented
def parse_log_with_traces(lines):
    # Parse lines into events
    events_by_trace = {} # trace_id -> list of event dicts
    standalone_events = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        event = {"raw": line}
        for m in re.finditer(r'(\w+)=([^\s"]+|"[^"]*")', line):
            k, v = m.group(1), m.group(2).strip('"')
            event[k] = v
        
        tid = event.get("trace_id")
        if tid:
            events_by_trace.setdefault(tid, []).append(event)
        else:
            standalone_events.append(event)
            
    # For each trace, consolidate attributes:
    # If any event in trace has subject_key, lookup_key, correlation_key, or email, propagate it
    consolidated_events = []
    for tid, trace_evs in events_by_trace.items():
        # Find all keys/identifiers in this trace
        keys = []
        for e in trace_evs:
            for k in ["subject_key", "lookup_key", "correlation_key", "user_id", "email", "phone"]:
                if e.get(k):
                    keys.append(e[k])
        
        # Also find all resource_ids and determine overall state
        # A trace might have a start event and a complete event
        # Group by resource_id within the trace
        by_res = {}
        for e in trace_evs:
            rid = e.get("resource_id")
            if rid:
                by_res.setdefault(rid, []).append(e)
                
        for rid, revs in by_res.items():
            # Merge fields into a summary event
            merged = {"raw": "\n".join(e["raw"] for e in revs), "resource_id": rid, "trace_id": tid}
            for e in trace_evs:
                for k, v in e.items():
                    if k not in merged and k != "raw":
                        merged[k] = v
            # Specific completed events override started
            for e in revs:
                if "completed" in e.get("event", "") or "evaluated" in e.get("event", "") or "heartbeat" in e.get("event", "") or "check" in e.get("event", ""):
                    for k, v in e.items():
                        if k != "raw": merged[k] = v
            # Include all keys found in trace in merged raw
            merged["_trace_keys"] = keys
            consolidated_events.append(merged)
            
    return consolidated_events

# Let's test against evidence_61, evidence_01, evidence_94
users = agent_module.load_csv('dataset/user_identities.csv')
audit_log = agent_module.load_csv('dataset/user_audit_log.csv')
email_to_uid, uid_to_user, uid_to_all_emails, uid_to_all_phones = agent_module.build_identity_index(users, audit_log)

# Also index email_hash from users and audit_log
uid_to_all_hashes = {}
for u in users:
    uid = u['user_id']
    uid_to_all_hashes.setdefault(uid, set())
    if u.get('email_hash'):
        uid_to_all_hashes[uid].add(u['email_hash'].lower())
for a in audit_log:
    uid = a['user_id']
    if a.get('field_name') == 'email_hash':
        uid_to_all_hashes.setdefault(uid, set())
        if a.get('old_value'): uid_to_all_hashes[uid].add(a['old_value'].lower())
        if a.get('new_value'): uid_to_all_hashes[uid].add(a['new_value'].lower())

for fid, path, target_uids in [
    ('evidence_61', 'dataset/evidence/logs/support_replica.log', ['user_10']),
    ('evidence_01', 'dataset/evidence/logs/service_events_ap_south_20260915.log', ['user_12', 'user_15', 'user_17']),
    ('evidence_94', 'dataset/evidence/logs/resource_lookup_trace_20260926_103856.log', ['user_43']),
]:
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    evs = parse_log_with_traces(lines)
    print(f"\n=== {fid}: {len(evs)} consolidated events ===")
    for uid in target_uids:
        emails = {e.lower() for e in uid_to_all_emails[uid]}
        phones = uid_to_all_phones[uid]
        hashes = uid_to_all_hashes[uid]
        print(f"Target {uid}: emails={emails}, hashes={hashes}")
        for e in evs:
            # check match
            raw_str = (e.get('raw', '') + ' ' + ' '.join(e.get('_trace_keys', []))).lower()
            matched = False
            if any(em in raw_str for em in emails): matched = True
            if any(h in raw_str for h in hashes): matched = True
            if re.search(r'\b' + re.escape(uid.lower()) + r'\b', raw_str): matched = True
            if matched:
                state = agent_module.EvidenceIndex._determine_log_state(None, e)
                print(f"  MATCH: res_id={e.get('resource_id')} svc={e.get('service')} event={e.get('event')} state={state}")

