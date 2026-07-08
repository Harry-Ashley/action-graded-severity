"""
Figure 3: the spotlighting paradox. Under spotlighting_with_delimiting, gpt-4o-mini's
binary attack-success rate falls (48% to 40%), yet its worst-case severity tail
grows: L5 privilege-expansion appears (0 to 1) and L6 chains double (1 to 2), so
combined L5+L6 episodes rise from 1 to 3. The binary metric reports an improvement
the severity metric contradicts.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from figstyle import apply_style, SEVERITY_COLORS, SEVERITY_LABELS

apply_style()
ROOT = Path(__file__).resolve().parent.parent
S = json.load(open(ROOT / "results" / "paper_summary.json"))["spotlighting_sweep"]

order = [("No defense", "gpt-4o-mini-2024-07-18__none"),
         ("Spotlighting", "gpt-4o-mini-2024-07-18__spotlighting_with_delimiting")]
names = [o[0] for o in order]
cells = [S[o[1]] for o in order]
totals = [c["n"] for c in cells]
asr = [c["binary_asr_pct"] for c in cells]

fig, ax = plt.subplots(figsize=(8.8, 5.9))

x = np.arange(len(order))
bar_w = 0.44
bottom = np.zeros(len(order))
seg = {}
present = []
for lvl in range(7):
    counts = np.array([c["severity_dist"][f"L{lvl}"] for c in cells], dtype=float)
    pct = 100.0 * counts / np.array(totals)
    if pct.sum() == 0:
        continue
    present.append(lvl)
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
    elif 6 <= v < 10:
        ax.text(xi, ymid, f"L{lvl}: {v:.0f}% (n={cnt})", ha="center", va="center",
                color="white", fontsize=8, fontweight="bold", zorder=5)

def tail_label(xi, lvl, tx, ty):
    ymid, v, cnt = seg[(xi, lvl)]
    ax.annotate(f"L{lvl}: {v:.0f}% (n={cnt})",
                xy=(xi + bar_w/2, ymid), xytext=(tx, ty),
                ha="left", va="center", fontsize=9, color=SEVERITY_COLORS[lvl],
                fontweight="bold", zorder=6,
                arrowprops=dict(arrowstyle="-", color=SEVERITY_COLORS[lvl], lw=1.1,
                                connectionstyle="arc3,rad=0.15"))
if (0, 6) in seg: tail_label(0, 6, 0.30, 93)
if (1, 6) in seg: tail_label(1, 6, 1.30, 102)
if (1, 5) in seg: tail_label(1, 5, 1.30, 88)

for xi, a in zip(x, asr):
    ax.text(xi, 106, f"binary ASR: {a:.0f}%", ha="center", va="bottom",
            fontsize=10, fontweight="bold", color="#264653")

ax.annotate("", xy=(1, 114), xytext=(0, 114),
            arrowprops=dict(arrowstyle="-|>", color="#2a9d8f", lw=1.6))
ax.text(0.5, 116, "binary: 48%  down to  40%  (reads as safer)",
        ha="center", va="bottom", fontsize=9.5, color="#2a9d8f", fontweight="bold")
ax.text(0.5, 127, "severity: worst-case L5+L6 tail  1  up to  3 episodes  (actually worse)",
        ha="center", va="bottom", fontsize=9.5, color="#a00e1c", fontweight="bold")

ax.set_xticks(x); ax.set_xticklabels(names)
ax.set_xlim(-0.5, 1.9)
ax.set_ylabel("Episodes (%)")
ax.set_ylim(0, 135)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.set_title("A defense can lower binary attack-success while raising worst-case severity",
             pad=54, fontweight="bold", fontsize=12.5)
ax.spines["bottom"].set_linewidth(1.3); ax.spines["bottom"].set_color("#333333")
ax.spines["left"].set_linewidth(1.3);   ax.spines["left"].set_color("#333333")
ax.tick_params(length=4, color="#333333")

ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=len(present),
          title="Peak severity", title_fontsize=9.5, handlelength=1.1, handleheight=1.1,
          columnspacing=1.2)

fig.text(0.5, -0.02,
         "gpt-4o-mini on AgentDojo workspace, important-instructions attack, n = 50 episodes per condition. "
         "Each bar sums to 100%.",
         ha="center", fontsize=8.5, color="#707070")
fig.tight_layout(rect=[0, 0.04, 1, 1])
outdir = ROOT / "figures"; outdir.mkdir(exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(outdir / f"fig3_spotlighting_paradox.{ext}", bbox_inches="tight")
print("wrote figures/fig3_spotlighting_paradox.png / .pdf")
