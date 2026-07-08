"""Consolidate every headline number into one JSON the paper/figures cite."""
import json, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
master = [json.loads(l) for l in open(RES/"master_results.jsonl")]
jrel = json.load(open(RES/"judge_reliability_summary.json"))

def cell(prov, model, defense):
    sub=[r for r in master if r["provenance"]==prov and r["model"]==model and r["defense"]==defense]
    dist=collections.Counter(r["prog_severity"] for r in sub)
    asr=sum(1 for r in sub if r["binary_attack_success"])
    return {"n":len(sub),"severity_dist":{f"L{k}":dist.get(k,0) for k in range(7)},
            "binary_asr":asr,"binary_asr_pct":round(100*asr/len(sub),1) if sub else 0}

models=["gpt-4o-mini-2024-07-18","claude-haiku-4-5","gpt-5.4","claude-sonnet-4-6"]
summary={"spotlighting_sweep":{}, "tool_filter_casestudy":{}, "judge_reliability":jrel}
for m in models:
    for d in ["none","spotlighting_with_delimiting"]:
        summary["spotlighting_sweep"][f"{m}__{d}"]=cell("spotlighting_sweep",m,d)
for d in ["none","tool_filter"]:
    summary["tool_filter_casestudy"][f"gpt-4o-mini-2024-07-18__{d}"]=cell("tool_filter_casestudy","gpt-4o-mini-2024-07-18",d)

json.dump(summary, open(RES/"paper_summary.json","w"), indent=2)
print("Wrote results/paper_summary.json")
print(json.dumps(summary["spotlighting_sweep"], indent=2))
