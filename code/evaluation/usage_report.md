# Usage Report — Ghost Data Still Exists

**Run Date**: 2026-10-24  
**Run Mode**: Deterministic rule-based agent (no external LLM/API calls)

---

## Model and Provider Information

| Field | Value |
|---|---|
| Approach | Rule-based evidence matching; no LLM API used |
| External model providers | None |
| External model names | None |
| LLM API calls | 0 |

This agent processes all 518 cases using deterministic Python logic:
- Identity index built from `user_identities.csv` and `user_audit_log.csv`
- Evidence parsed from 94 files (JSON, SQL via SQLite, log files, PDF via pypdf, PNG via OCR cache, TXT)
- Records matched against user identifiers (email, phone, email hash — current + historical)
- Deletion status determined from evidence states following `deletion_rules.csv` semantics
- Steps generated following the contract in `AGENTS.md §6`

---

## Resource Usage

| Metric | Value |
|---|---|
| Total model API calls | 0 |
| Input tokens | 0 |
| Output tokens | 0 |
| Total tokens | 0 |
| Estimated total cost | $0.00 |
| Average tokens per case | 0 |

---

## Compute Time

| Metric | Value |
|---|---|
| Total wall-clock time | ~11 seconds |
| Cases processed | 518 |
| Average time per case | ~21 ms |

---

## Evidence Parsed

| File Type | Count | Notes |
|---|---|---|
| `.json` | 28 | service_resource_export, snapshot_bundle, and records formats |
| `.log` | 26 | Trace-grouped key=value log events |
| `.sql` | 24 | Loaded into in-memory SQLite |
| `.png` | 11 | Read from pre-generated OCR cache |
| `.pdf` | 4 | Extracted via pypdf |
| `.txt` | 1 | Pipe-delimited handover log |
| **Total** | **94** | All files in `dataset/evidence_files.csv` |

---

## Dependencies

| Package | Purpose |
|---|---|
| `pypdf` | PDF text extraction |
| Python stdlib: `csv`, `json`, `sqlite3`, `re`, `pathlib` | Core parsing |

No API keys or credentials required. No network calls made during execution.

---

## Notes

The agent is fully deterministic: given the same input files, it produces identical output. This satisfies the reproducibility requirement in `AGENTS.md §6.7`.
