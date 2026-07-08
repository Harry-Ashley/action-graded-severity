"""
Build a stratified sample (all non-L0 + equal random L0) from master_results,
run all 3 judges on each, and write judge scores joined to O_prog.
Resumable: skips episodes already in the output file.
"""
import json, random, time
from pathlib import Path
from serialize_trajectory import serialize
from judge_panel import JUDGES

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
random.seed(42)

rows = [json.loads(l) for l in open(RES / "master_results.jsonl")]
nonzero = [r for r in rows if r["prog_severity"] > 0]
zero    = [r for r in rows if r["prog_severity"] == 0]
random.shuffle(zero)
sample = nonzero + zero[:len(nonzero)]   # balanced L0 controls
random.shuffle(sample)
print(f"Sample: {len(sample)} episodes ({len(nonzero)} non-L0 + {len(nonzero)} L0 controls)")

out_path = RES / "judge_scores.jsonl"
done = set()
if out_path.exists():
    for l in open(out_path):
        d = json.loads(l); done.add(d["episode_path"])
    print(f"Resuming: {len(done)} already judged")

fh = open(out_path, "a")
for i, r in enumerate(sample):
    if r["episode_path"] in done:
        continue
    ep = json.load(open(r["episode_path"]))
    s = serialize(ep)
    rec = {"episode_path": r["episode_path"], "model": r["model"],
           "defense": r["defense"], "provenance": r["provenance"],
           "user_task": r["user_task"], "injection_task": r["injection_task"],
           "prog_severity": r["prog_severity"], "judges": {}}
    for name, fn in JUDGES.items():
        try:
            sev, raw = fn(s)
        except Exception as e:
            sev, raw = None, f"ERROR: {e}"
        rec["judges"][name] = sev
    fh.write(json.dumps(rec) + "\n"); fh.flush()
    if (i+1) % 10 == 0:
        print(f"  {i+1}/{len(sample)} done")
fh.close()
print("Wrote", out_path)
