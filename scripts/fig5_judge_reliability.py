"""
Figure 5: judge-panel reliability against the programmatic oracle.
Four metrics per judge (exact-match, quadratic weighted kappa, mean absolute level
error, signed bias) plus the panel-level Krippendorff alpha. Reads
results/judge_reliability_summary.json.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from figstyle import apply_style

apply_style()
ROOT = Path(__file__).resolve().parent.parent
S = json.load(open(ROOT / "results" / "judge_reliability_summary.json"))
pj = S["per_judge"]

JUDGES = [("gpt-5.5", "GPT-5.5"), ("opus-4.8", "Claude Opus 4.8"),
          ("gemini-3.5-flash", "Gemini 3.5 Flash")]
COLORS = {"gpt-5.5": "#1d3557", "opus-4.8": "#e76f51", "gemini-3.5-flash": "#6a4c93"}
keys = [k for k, _ in JUDGES]
names = [n for _, n in JUDGES]
cols = [COLORS[k] for k in keys]
x = np.arange(len(keys))

fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.4))

def style_ax(ax):
    ax.spines["bottom"].set_linewidth(1.2); ax.spines["bottom"].set_color("#333333")
    ax.spines["left"].set_linewidth(1.2);   ax.spines["left"].set_color("#333333")
    ax.tick_params(length=4, color="#333333")
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=9.5)

ax = axes[0, 0]
vals = [pj[k]["exact"]*100 for k in keys]
ax.bar(x, vals, width=0.6, color=cols, edgecolor="white", linewidth=1.0, zorder=3)
for xi, v in zip(x, vals):
    ax.text(xi, v+1.2, f"{v:.0f}%", ha="center", va="bottom", fontweight="bold", fontsize=10.5)
ax.set_ylim(0, 108); ax.set_ylabel("Exact match (%)")
ax.set_title("Exact-level agreement with oracle\n(higher is better)", fontsize=11, pad=8)
style_ax(ax)

ax = axes[0, 1]
vals = [pj[k]["wkappa_vs_oracle"] for k in keys]
ax.axhspan(0.8, 1.0, color="#2a9d8f", alpha=0.10, zorder=0)
ax.axhline(0.8, color="#2a9d8f", lw=1.0, ls="--", zorder=1)
ax.text(2.35, 0.805, "excellent (>=0.8)", fontsize=8, color="#1d6f66", va="bottom", ha="right")
ax.bar(x, vals, width=0.6, color=cols, edgecolor="white", linewidth=1.0, zorder=3)
for xi, v in zip(x, vals):
    ax.text(xi, v+0.015, f"{v:.2f}", ha="center", va="bottom", fontweight="bold", fontsize=10.5)
ax.set_ylim(0, 1.08); ax.set_ylabel("Quadratic weighted kappa")
ax.set_title("Ordinal agreement with oracle\n(higher is better)", fontsize=11, pad=8)
style_ax(ax)

ax = axes[1, 0]
vals = [pj[k]["male"] for k in keys]
ax.bar(x, vals, width=0.6, color=cols, edgecolor="white", linewidth=1.0, zorder=3)
for xi, v in zip(x, vals):
    ax.text(xi, v+0.008, f"{v:.2f}", ha="center", va="bottom", fontweight="bold", fontsize=10.5)
ax.set_ylim(0, 0.46); ax.set_ylabel("Mean absolute level error (rungs)")
ax.set_title("Average distance from oracle\n(lower is better; all under 0.4 of one rung)",
             fontsize=11, pad=8)
style_ax(ax)

ax = axes[1, 1]
vals = [pj[k]["bias"] for k in keys]
ax.axhline(0, color="#333333", lw=1.1, zorder=2)
ax.bar(x, vals, width=0.6, color=cols, edgecolor="white", linewidth=1.0, zorder=3)
for xi, v in zip(x, vals):
    ax.text(xi, v+0.012, f"+{v:.2f}", ha="center", va="bottom", fontweight="bold", fontsize=10.5)
ax.set_ylim(-0.05, 0.42); ax.set_ylabel("Signed bias (judge minus oracle)")
ax.set_title("Direction of error\n(positive = over-scores severity)", fontsize=11, pad=8)
style_ax(ax)

fig.suptitle("Judge-panel reliability against the programmatic oracle", fontsize=13.5,
             fontweight="bold", y=1.005)
fig.text(0.5, 0.945,
         f"Krippendorff's alpha (ordinal): {S['alpha_judges']:.2f} across the three judges, "
         f"{S['alpha_all']:.2f} including the oracle. n = {S['n']} episodes.",
         ha="center", fontsize=10, color="#a00e1c", fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
outdir = ROOT / "figures"; outdir.mkdir(exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(outdir / f"fig5_judge_reliability.{ext}", bbox_inches="tight")
print("wrote figures/fig5_judge_reliability.png / .pdf")
