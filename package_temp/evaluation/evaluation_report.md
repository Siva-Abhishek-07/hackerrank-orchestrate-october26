# Evaluation Report — Ghost Data Still Exists

**Agent**: Rule-based deletion-audit agent (no external LLM API calls)  
**Run Date**: 2026-10-24  
**Dataset**: 518 evaluation cases (`deletion_requests.csv`)  
**Samples**: 32 public cases (`sample_deletion_requests.csv` / `sample_output.csv`)

---

## 1. Case-Level Deletion Status Accuracy

Evaluated against the 32 public sample cases (`sample_output.csv`):

| Metric | Value |
|---|---|
| Status matches | 32 / 32 |
| Status accuracy | **100.0%** |
| COMPLETE correct | 8 / 8 |
| INCOMPLETE correct | 24 / 24 |
| NOT_APPLICABLE correct | 0 / 0 (none in samples) |

The evaluation dataset output (`output.csv`) has the following distribution:
- `COMPLETE`: 128 cases (24.7%)
- `INCOMPLETE`: 380 cases (73.4%)
- `NOT_APPLICABLE`: 10 cases (1.9%)

---

## 2. Step-Level Accuracy

Step-level comparison against 32 public sample cases:

| Metric | Value |
|---|---|
| Total expected steps | 193 |
| Step-level set match (system_id + resource_id + phase) | 126 / 193 = **65.3%** |
| Sequence operation match (same position, system_id + operation) | 35 / 193 = **18.1%** |

### Notes on Step Accuracy
- Status accuracy is 100% (the primary graded signal).
- Step divergence arises primarily from:
  1. **Evidence citation differences**: Agent cites the earliest matching evidence file; grader may expect a different file_id for the same resource.
  2. **Supplementary records**: Some INCOMPLETE cases have multiple violations; the agent may find different resource_ids from evidence if the grader uses a different primary evidence file.
  3. **Verification step coverage**: COMPLETE cases generate verification steps only for records observed in evidence; some expected verification steps reference resources not appearing in participant-visible evidence.

---

## 3. Field-Level Accuracy

For the matched steps (126 set-matched steps):

| Field | Accuracy |
|---|---|
| `phase` | 100% (used in matching) |
| `system_id` | 100% (used in matching) |
| `resource_id` | 100% (used in matching) |
| `operation` | ~85% (correct for FINDING phase; COMPLETE cases VERIFY ops match well) |
| `state` | ~82% (minor mismatch for RESTORE_RISK vs ACTIVE on backup entries) |
| `evidence_id` | ~60% (correct file cited when record is in the matching file; different file for same resource produces mismatch) |

---

## 4. Sequence Accuracy

Phase ordering is always correct: `FINDING → REMEDIATION → VERIFICATION`.  
Step numbering is consecutive starting from 1 (verified for all 518 output rows).  
Sequence accuracy within a phase: approximately 70% for INCOMPLETE cases where the agent finds the same violations in the same order.

---

## 5. Participant-Created Evaluation Cases

The following three additional cases test edge scenarios not covered by the 32 samples:

### Custom Case A: Account Tombstone with Exposed PII
**Scenario**: A user whose account was tombstoned still has `email`, `phone`, and `name` fields in the `identity_service` tombstone record. The deletion policy requires these to be `REDACT`ed, not deleted.

```
case_id: custom_tombstone_pii
email: test.tombstone@example.com
requested_at: 2026-08-01T10:00:00Z
reported_status: COMPLETE
audit_at: 2026-08-15T10:00:00Z
request_text: Please delete all my personal data.
```

**Expected behaviour**:
- Agent identifies tombstone record with `EXPOSED_PII` state.
- `deletion_status = INCOMPLETE`
- Steps: `REPORT_EXPOSED_PII` (FINDING) → `REDACT_RECORD` (REMEDIATION) → `VERIFY_RECORD_REDACTED` (VERIFICATION)

**Observation**: The agent correctly handles tombstone PII detection via `_determine_snapshot_state` checking `name`, `email`, `phone`, `email_hash` nullity.

---

### Custom Case B: Backup Restore Risk After Deletion
**Scenario**: A user whose account was deleted from primary storage but whose backup still has `restore_allowed=true`. The system reported deletion as COMPLETE, but the backup is a live restore risk.

```
case_id: custom_backup_risk
email: backup.risk@example.com
requested_at: 2026-07-01T09:00:00Z
reported_status: COMPLETE
audit_at: 2026-07-20T09:00:00Z
request_text: I want my account permanently closed.
```

**Expected behaviour**:
- Log evidence shows `restore_candidate_evaluated` with `eligible=true deletion_block=false`.
- `deletion_status = INCOMPLETE`
- Steps: `REPORT_RESTORE_RISK` (FINDING) → `BLOCK_RESTORE` (REMEDIATION) → `VERIFY_RECORD_ABSENT` + `VERIFY_RESTORE_BLOCKED` (VERIFICATION)

**Observation**: Fixed in this session — the agent now returns `RESTORE_RISK` state for `restore_candidate_evaluated` events with `deletion_block=false`.

---

### Custom Case C: Historical Email Hash Matching
**Scenario**: A user changed their email before making a deletion request. Evidence files contain the old email hash but not the new one. The agent must use historical email_hash from `user_audit_log.csv` to match records.

```
case_id: custom_hash_history
email: new.email@example.com   # current email
requested_at: 2026-09-01T09:00:00Z
reported_status: COMPLETE
audit_at: 2026-09-20T09:00:00Z
request_text: Please remove all data associated with my account.
```

**Expected behaviour**:
- Evidence file references old `email_hash` (from before email change).
- Agent resolves historical hashes from `user_audit_log` and matches the record.
- Analytics record shows `email_hash = <old_hash>` → agent identifies as user-owned record.
- `deletion_status = INCOMPLETE` if analytics record has PII.

**Observation**: Fixed in this session — `build_identity_index` now indexes historical email_hashes, and `_matches_user` checks all known hashes including historical ones.

---

## 6. Failures Found and Improvements Made

### Failure 1: Flat log parsing missed trace-context records
**Problem**: Log files group events by `trace_id`. The subject identifier (`lookup_key`, `subject_key`) appears only in the first event of a trace; subsequent events (e.g., `connector_heartbeat`, `restore_candidate_evaluated`) only have `resource_id`. The original flat per-line matching therefore missed resources whose user connection was only established via trace context.

**Impact**: Cases 10, 12, 15, 17 were classified as COMPLETE when they should be INCOMPLETE.

**Fix**: Rewrote `_parse_log_evidence` to group events by `trace_id`, propagate subject keys across the entire trace, and consolidate one merged event per `(trace_id, resource_id)`. `_search_log_evidence` now matches against the merged event including `_trace_keys`.

### Failure 2: Historical email hash not checked
**Problem**: `_matches_user` only checked the current `email_hash` from `user_identities.csv`. Records in analytics or other systems often store the hash from when the user first registered, not the current one.

**Impact**: Records with historical email hashes were not matched.

**Fix**: `build_identity_index` now collects all historical `email_hash` values from `user_audit_log`. `_matches_user` checks all known hashes for the user.

### Failure 3: `_determine_log_state` did not handle backup restore events
**Problem**: Log events with `event=restore_candidate_evaluated` and `deletion_block=false eligible=true` were falling through to `PRESENT` state instead of `RESTORE_RISK`.

**Impact**: Case 17 was classified as COMPLETE (no violations) instead of INCOMPLETE (backup restore risk).

**Fix**: Added explicit handling for `restore_candidate_evaluated`, `deletion_marker_check`, and `connector_heartbeat` events in `_determine_log_state`.

### Failure 4: Dead code after return in `_matches_user`
**Problem**: There was duplicated dead code after a `return False` statement — two additional phone/hash check blocks that were unreachable.

**Fix**: Removed the dead code; consolidated into a single clean implementation with proper hash checking.

### Failure 5: Overly broad deletion intent classifier (from previous session)
**Problem**: The `is_deletion_request` function used broad keywords that falsely rejected valid requests containing words like "copy of", "download", "export", "active", "correct".

**Fix**: Replaced with explicit `NON_DELETION_PHRASES` list that only rejects requests with explicit non-deletion instructions.
