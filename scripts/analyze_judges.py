"""Pillar 3 reliability: judge vs O_prog and judge vs judge. Ordinal-appropriate."""
import json, numpy as np, krippendorff
from pathlib import Path
from itertools import combinations
from sklearn.metrics import cohen_kappa_score, confusion_matrix

ROOT = Path(__file__).resolve().parent.parent
rows = [json.loads(l) for l in open(ROOT / "results" / "judge_scores.jsonl")]
JUDGES = ["gpt-5.5", "opus-4.8", "gemini-3.5-flash"]

# keep only rows where all judges returned a value
rows = [r for r in rows if all(r["judges"].get(j) is not None for j in JUDGES)]
oracle = np.array([r["prog_severity"] for r in rows])
J = {j: np.array([r["judges"][j] for r in rows]) for j in JUDGES}
print(f"N = {len(rows)} episodes with complete judge sets\n")

def male(a, b):   return float(np.mean(np.abs(a - b)))
def bias(a, b):   return float(np.mean(a - b))   # judge - oracle

print("=== Judge vs O_prog (programmatic oracle) ===")
print(f"{'judge':18s} {'exact%':>7} {'MALE':>6} {'bias':>6} {'wkappa':>7}")
for j in JUDGES:
    ex = 100*np.mean(J[j] == oracle)
    wk = cohen_kappa_score(oracle, J[j], weights="quadratic", labels=list(range(7)))
    print(f"{j:18s} {ex:7.0f} {male(J[j],oracle):6.2f} {bias(J[j],oracle):+6.2f} {wk:7.3f}")

# Krippendorff alpha (ordinal) across the 3 judges + oracle as 4 raters
rel = np.vstack([oracle] + [J[j] for j in JUDGES]).astype(float)
alpha_all = krippendorff.alpha(reliability_data=rel, level_of_measurement="ordinal")
alpha_judges = krippendorff.alpha(
    reliability_data=np.vstack([J[j] for j in JUDGES]).astype(float),
    level_of_measurement="ordinal")
print(f"\nKrippendorff alpha (ordinal): judges+oracle = {alpha_all:.3f} | judges only = {alpha_judges:.3f}")

print("\n=== Judge-vs-judge weighted kappa (pairwise) ===")
for a, b in combinations(JUDGES, 2):
    wk = cohen_kappa_score(J[a], J[b], weights="quadratic", labels=list(range(7)))
    print(f"  {a:16s} vs {b:16s} {wk:.3f}")

print("\n=== Confusion matrix vs O_prog (rows=O_prog L0..L6, cols=judge) ===")
for j in JUDGES:
    cm = confusion_matrix(oracle, J[j], labels=list(range(7)))
    print(f"\n{j}:")
    print("       " + " ".join(f"L{c}" for c in range(7)))
    for i, r in enumerate(cm):
        print(f"  L{i} | " + " ".join(f"{v:2d}" for v in r))

# save a machine-readable summary for the figures
summary = {"n": len(rows),
           "per_judge": {j: {"exact": float(np.mean(J[j]==oracle)),
                             "male": male(J[j],oracle), "bias": bias(J[j],oracle),
                             "wkappa_vs_oracle": cohen_kappa_score(oracle,J[j],weights="quadratic",labels=list(range(7)))}
                         for j in JUDGES},
           "alpha_judges": alpha_judges, "alpha_all": alpha_all}
json.dump(summary, open(ROOT/"results"/"judge_reliability_summary.json","w"), indent=2)
print("\nWrote results/judge_reliability_summary.json")
