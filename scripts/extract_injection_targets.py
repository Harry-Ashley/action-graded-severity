"""
Extract attacker-target tokens per injection task, from the injection GOAL text.
The oracle marks an action attack-attributed ONLY if its arguments contain one
of these tokens. Self-contained: reads the attacker's stated goal, NOT AgentDojo's
security verdict. Portable to any suite by regenerating this map.
"""
import json, re, agentdojo
from pathlib import Path
from agentdojo.task_suite.load_suites import get_suites

ROOT = Path(__file__).resolve().parent.parent
suite = get_suites("v1.2")["workspace"]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
FILEID_RE = re.compile(r"file(?:\s+with\s+ID|\s*id)?\s*'?(\d+)'?", re.IGNORECASE)

targets = {}
for tid, t in suite.injection_tasks.items():
    goal = getattr(t, "GOAL", "") or ""
    emails = sorted(set(EMAIL_RE.findall(goal)))
    file_ids = sorted(set(FILEID_RE.findall(goal)))
    # 'delete the sent email' / exfil-then-delete => a delete step is part of goal
    mentions_delete = bool(re.search(r"\bdelete\b", goal, re.IGNORECASE))
    targets[tid] = {
        "goal": goal,
        "target_emails": emails,
        "target_file_ids": file_ids,
        "goal_includes_delete": mentions_delete,
    }

out = ROOT / "injection_targets.json"
json.dump(targets, open(out, "w"), indent=2)
for tid, d in targets.items():
    print(f"{tid:18s} emails={d['target_emails']} files={d['target_file_ids']} del={d['goal_includes_delete']}")
print("\nWrote", out)
