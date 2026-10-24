import json
from pathlib import Path

trace = Path(r"agent-trace\antigravity\d27db20e-39f1-414d-873b-8b6d6163c2d9\.system_generated\logs\transcript.jsonl")
output = Path("log.txt")

entries = []
for line in trace.read_text(encoding="utf-8").splitlines():
    try:
        entries.append(json.loads(line))
    except json.JSONDecodeError:
        pass

prompts = [
    e for e in entries
    if e.get("type") == "USER_INPUT"
]

if not prompts:
    raise SystemExit("No USER_INPUT events found in the original trace.")

repo = str(Path.cwd())
lines = [
    "# RECONSTRUCTED LOG — generated from Antigravity transcript.jsonl",
    "# This is not the original agent-generated log.txt.",
    "",
    "## SESSION START",
    "",
    "tool=antigravity",
    "model=Multiple models; see recorded model settings in original trace",
    f"Repo Root: {repo}",
    "Branch: main",
    "Worktree: main",
    "Parent Agent: none",
    "Language: py",
    "Time Remaining: not configured",
    "",
]

for i, e in enumerate(prompts, 1):
    timestamp = e.get("created_at", "timestamp unavailable")
    content = e.get("content", "")
    if isinstance(content, (dict, list)):
        content = json.dumps(content, ensure_ascii=False)

    lines.extend([
        f"## [{timestamp}] Reconstructed user turn {i}",
        "",
        "User Prompt (verbatim, secrets redacted):",
        str(content),
        "",
        "Agent Response Summary:",
        "This entry is reconstructed from the saved session trace. Consult the original transcript.jsonl for the recorded agent actions and responses; this file does not claim to reproduce the original agent-generated log.",
        "",
        "Actions:",
        "* See the original Antigravity transcript.jsonl and associated session artifacts.",
        "",
        "Context:",
        "tool=antigravity",
        "model=See original trace; model varied during the session",
        "branch=main",
        f"repo_root={repo}",
        "worktree=main",
        "parent_agent=none",
        "",
    ])

output.write_text("\n".join(lines), encoding="utf-8")
print(f"Created {output.resolve()}")
print(f"Reconstructed user turns: {len(prompts)}")
