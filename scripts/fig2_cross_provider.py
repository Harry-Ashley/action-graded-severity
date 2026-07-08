"""
Figure 2: peak-severity distribution across four models (no defense).
Three of four models (Haiku 4.5, GPT-5.4, Sonnet 4.6) never reach a consequential
action (100% L0); the low-cost gpt-4o-mini spreads across L3, L4, L6. Binary
attack-success rate annotated above each bar.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from figstyle import apply_style, SEVERITY_COLORS, SEVERITY_LABELS

apply_style()
ROOT = Path(__file__).resolve().parent.parent
S = json.load(open(ROOT / "results" / "paper_summary.json"))["spotlighting_sweep"]

order = [
    ("GPT-4o mini",      "gpt-4o-mini-2024-07-18__none"),
    ("Claude Haiku 4.5", "claude-haiku-4-5__none"),
    ("GPT-5.4",          "gpt-5.4__none"),
    ("Claude Sonnet 4.6","claude-sonnet-4-6__none"),
]
labels_x = [o[0] for o in order]
cells = [S[o[1]] for o in order]
totals = [c["n"] for c in cells]
asr = [c["binary_asr_pct"] for c in cells]

fig, ax = plt.subplots(figsize=(9.8, 5.6))

x = np.arange(len(order))
bar_w = 0.46
bottom = np.zeros(len(order))
seg = {}
present_levels = []
for lvl in range(7):
    counts = np.array([c["severity_dist"][f"L{lvl}"] for c in cells], dtype=float)
    pct = 100.0 * counts / np.array(totals)
    if pct.sum() == 0:
        continue
    present_levels.append(lvl)
    ax.bar(x, pct, bottom=bottom, width=bar_w, color=SEVERITY_COLORS[lvl],
           edgecolor="white", linewidth=1.0, label=SEVERITY_LABELS[lvl], zorder=3)
    for xi in range(len(order)):
        if pct[xi] > 0:
            seg[(xi, lvl)] = (bottom[xi] + pct[xi]/2, pct[xi], int(counts[xi]))
    bottom += pct

for (xi, lvl), (ymid, v, cnt) in seg.items():
    if v >= 10:
        ax.text(xi, ymid, f"{v:.0f}%\n(n={cnt})", ha="center", va="center",
                color="white", fontsize=9.5, fontweight="bold", zorder=5)
    elif v >= 4:
        ax.text(xi, ymid, f"L{lvl}: {v:.0f}% (n={cnt})", ha="center", va="center",
                color="white", fontsize=8, fontweight="bold", zorder=5)
    else:
        ax.annotate(f"L{lvl}: {v:.0f}% (n={cnt})",
                    xy=(xi + bar_w/2, ymid), xytext=(xi + 0.36, ymid - 6),
                    ha="left", va="center", fontsize=9, color=SEVERITY_COLORS[lvl],
                    fontweight="bold", zorder=6,
                    arrowprops=dict(arrowstyle="-", color=SEVERITY_COLORS[lvl], lw=1.1,
                                    connectionstyle="arc3,rad=0.2"))

for xi, a in zip(x, asr):
    ax.text(xi, 103.5, f"binary ASR: {a:.0f}%", ha="center", va="bottom",
            fontsize=9.5, fontweight="bold",
            color=("#a00e1c" if a > 0 else "#2a9d8f"))

ax.annotate("", xy=(0.65, 112), xytext=(3.35, 112),
            arrowprops=dict(arrowstyle="-", color="#8a8a8a", lw=1.2))
ax.text(2.0, 114, "three of four models: no consequential action (100% L0)",
        ha="center", va="bottom", fontsize=9.5, color="#4a4a4a", style="italic")

ax.set_xticks(x); ax.set_xticklabels(labels_x)
ax.set_xlim(-0.55, 3.55)
ax.set_ylabel("Episodes (%)")
ax.set_ylim(0, 120)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.set_title("Peak-severity distribution across four models, no defense", pad=36, fontweight="bold")
ax.spines["bottom"].set_linewidth(1.3); ax.spines["bottom"].set_color("#333333")
ax.spines["left"].set_linewidth(1.3);   ax.spines["left"].set_color("#333333")
ax.tick_params(length=4, color="#333333")

ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=len(present_levels),
          title="Peak severity", title_fontsize=9.5, handlelength=1.1, handleheight=1.1,
          columnspacing=1.4)

fig.text(0.5, -0.02,
         "AgentDojo workspace, important-instructions attack. gpt-4o-mini/Haiku n=50; GPT-5.4/Sonnet n=25. "
         "Each bar sums to 100%.",
         ha="center", fontsize=8.5, color="#707070")
fig.tight_layout(rect=[0, 0.04, 1, 1])
outdir = ROOT / "figures"; outdir.mkdir(exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(outdir / f"fig2_cross_provider.{ext}", bbox_inches="tight")
print("wrote figures/fig2_cross_provider.png / .pdf")
