"""
Figure 1 (headline): binary attack-success rate hides severity structure.
Both panels use PERCENTAGE OF EPISODES; every bar totals 100%. Thin severity
segments are labeled to the RIGHT of their bar (No-defense L3 into the inter-bar
gap, Tool-filter L4 into the right margin) so no label touches the y-axis, the
legend, or another label. Solid dark baseline; the 0% bar draws no ghost edge.
gpt-4o-mini, no-defense vs tool_filter (n=55 each).
"""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from figstyle import apply_style, SEVERITY_COLORS, SEVERITY_LABELS, BINARY_COLOR

apply_style()
ROOT = Path(__file__).resolve().parent.parent
S = json.load(open(ROOT / "results" / "paper_summary.json"))["tool_filter_casestudy"]

configs = [("No defense", "gpt-4o-mini-2024-07-18__none"),
           ("Tool filter", "gpt-4o-mini-2024-07-18__tool_filter")]
names = [c[0] for c in configs]
cells = [S[c[1]] for c in configs]
totals = [c["n"] for c in cells]

def solid_baseline(ax):
    ax.spines["bottom"].set_linewidth(1.3); ax.spines["bottom"].set_color("#333333")
    ax.spines["left"].set_linewidth(1.3);   ax.spines["left"].set_color("#333333")
    ax.tick_params(length=4, color="#333333")

fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.8, 5.0),
                               gridspec_kw={"width_ratios": [0.78, 1.22]})

asr = [c["binary_asr_pct"] for c in cells]
xb = np.arange(len(names))
for xi, v in zip(xb, asr):
    if v > 0:
        axL.bar(xi, v, width=0.5, color=BINARY_COLOR, edgecolor="white", linewidth=1.2, zorder=3)
    axL.text(xi, v + 2.5, f"{v:.0f}%", ha="center", va="bottom", fontweight="bold", fontsize=12)
axL.set_xticks(xb); axL.set_xticklabels(names)
axL.set_xlim(-0.6, 1.6)
axL.set_ylabel("Episodes (%)")
axL.set_ylim(0, 105)
axL.set_title("Binary metric\n(attack succeeded: yes / no)", pad=10)
axL.annotate("reads as fully\ndefended", xy=(1, 1.5), xytext=(1, 34),
             ha="center", fontsize=9.5, color="#5a5a5a",
             arrowprops=dict(arrowstyle="-|>", color="#8a8a8a", lw=1.3))
solid_baseline(axL)

xr = np.arange(len(names))
bar_w = 0.42
bottom = np.zeros(len(names))
seg = {}
handles_labels = []
for lvl in range(7):
    counts = np.array([c["severity_dist"][f"L{lvl}"] for c in cells], dtype=float)
    pct = 100.0 * counts / np.array(totals)
    if pct.sum() == 0:
        continue
    b = axR.bar(xr, pct, bottom=bottom, width=bar_w, color=SEVERITY_COLORS[lvl],
                edgecolor="white", linewidth=0.9, label=SEVERITY_LABELS[lvl], zorder=3)
    handles_labels.append((b, SEVERITY_LABELS[lvl]))
    for xi in range(len(names)):
        if pct[xi] > 0:
            seg[(xi, lvl)] = (bottom[xi] + pct[xi]/2, pct[xi], int(counts[xi]))
    bottom += pct

right_edge = {0: 0 + bar_w/2, 1: 1 + bar_w/2}
text_x     = {0: 0.30, 1: 1.34}
for (xi, lvl), (ymid, v, cnt) in seg.items():
    if v >= 8:
        axR.text(xi, ymid, f"{v:.0f}%\n(n={cnt})", ha="center", va="center",
                 color="white", fontsize=9.5, fontweight="bold", zorder=5)
    else:
        axR.annotate(f"L{lvl}: {v:.0f}% (n={cnt})",
                     xy=(right_edge[xi], ymid), xytext=(text_x[xi], ymid),
                     ha="left", va="center", fontsize=9, color=SEVERITY_COLORS[lvl],
                     fontweight="bold", zorder=6,
                     arrowprops=dict(arrowstyle="-", color=SEVERITY_COLORS[lvl], lw=1.1))

axR.set_xticks(xr); axR.set_xticklabels(names)
axR.set_xlim(-0.55, 2.15)
axR.set_ylabel("Episodes (%)")
axR.set_ylim(0, 108)
axR.set_title("Severity metric (this work)\n(peak level L0 to L6)", pad=10)
solid_baseline(axR)

handles = [h[0] for h in handles_labels]
labels = [h[1] for h in handles_labels]
fig.legend(handles, labels, loc="lower center", ncol=len(labels),
           bbox_to_anchor=(0.5, -0.02), title="Peak severity", title_fontsize=9.5,
           handlelength=1.1, handleheight=1.1, columnspacing=1.3)

fig.suptitle("A defense that looks flawless under binary scoring still leaks under severity scoring",
             fontsize=12.5, fontweight="bold", y=1.02)
fig.text(0.5, -0.11,
         "gpt-4o-mini on AgentDojo workspace, important-instructions attack, n = 55 episodes per condition. "
         "Each severity bar sums to 100%.",
         ha="center", fontsize=8.5, color="#707070")
fig.tight_layout(rect=[0, 0.06, 1, 1])
outdir = ROOT / "figures"; outdir.mkdir(exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(outdir / f"fig1_binary_vs_severity.{ext}", bbox_inches="tight")
print("wrote figures/fig1_binary_vs_severity.png / .pdf")
