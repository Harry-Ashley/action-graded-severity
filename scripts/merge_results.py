"""Merge all sweep result files into one master dataset with clean, unambiguous fields.

Adds:
  pipeline_name : AgentDojo's raw name (model + defense suffix), preserved for provenance
  model         : CLEAN model id (no defense suffix) -- use for grouping/figures
  defense       : none | spotlighting_with_delimiting | tool_filter
  provenance    : spotlighting_sweep | tool_filter_casestudy
Rule: filter by ONE provenance per figure (each has its own 'none' baseline).
"""
import json, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

SOURCES = {
    "sweep_cheap_results.jsonl":    "spotlighting_sweep",
    "sweep_frontier_results.jsonl": "spotlighting_sweep",
    "sweep_A_gpt_rescored.jsonl":   "tool_filter_casestudy",
}
DEFENSE_SUFFIXES = ["-spotlighting_with_delimiting", "-tool_filter", "-repeat_user_prompt"]

def clean_model(row):
    # prefer the runner-provided clean id; else strip a known defense suffix
    m = row.get("model_enum")
    if m:
        return m
    m = row.get("model", "")
    for suf in DEFENSE_SUFFIXES:
        if m.endswith(suf):
            return m[: -len(suf)]
    return m

master, seen = [], set()
for fname, provenance in SOURCES.items():
    p = RES / fname
    if not p.exists():
        print(f"  (skip, not found: {fname})")
        continue
    for line in open(p):
        r = json.loads(line)
        r["provenance"] = provenance
        r["pipeline_name"] = r.get("model")      # preserve raw
        r["model"] = clean_model(r)              # overwrite with clean id
        if not r.get("defense"):
            r["defense"] = "none"
        key = (r["model"], r["defense"], r["user_task"], r["injection_task"], provenance)
        if key in seen:
            continue
        seen.add(key)
        master.append(r)

out = RES / "master_results.jsonl"
with open(out, "w") as fh:
    for r in master:
        fh.write(json.dumps(r) + "\n")

print(f"Merged {len(master)} episodes -> {out}\n")
# clean census by (model, defense) within each provenance
cen = collections.Counter((r["provenance"], r["model"], r["defense"]) for r in master)
for (prov, m, d), n in sorted(cen.items()):
    print(f"  [{prov:22s}] {m:24s} {d:26s} {n}")
