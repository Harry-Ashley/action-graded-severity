"""
Figure 4: judge-vs-oracle confusion matrices (three frontier judges).
Rows = programmatic oracle severity (O_prog), columns = LLM judge severity.
The strong diagonal shows agreement; off-diagonal cells reveal systematic judge
errors (for example true L6 chains scored as L4, and benign L0 episodes flagged
as L4). Built from results/judge_scores.jsonl.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from figstyle import apply_style

apply_style()
ROOT = Path(__file__).resolve().parent.parent
rows = [json.loads(l) for l in open(ROOT / "results" / "judge_scores.jsonl")]
JUDGES = [("gpt-5.5", "GPT-5.5"), ("opus-4.8", "Claude Opus 4.8"),
          ("gemini-3.5-flash", "Gemini 3.5 Flash")]
LEVELS = list(range(7))

def confusion(jkey):
    M = np.zeros((7, 7), dtype=int)
    for r in rows:
        jv = r["judges"].get(jkey)
        if jv is None:
            continue
        M[r["prog_severity"], jv] += 1
    return M

def wkappa(M):
    n = M.sum()
    if n == 0:
        return float("nan")
    r = M.sum(1); c = M.sum(0)
    W = np.array([[(i-j)**2 for j in LEVELS] for i in LEVELS], dtype=float)
    E = np.outer(r, c) / n
    num = (W*M).sum(); den = (W*E).sum()
    return 1 - num/den if den else float("nan")

teal = LinearSegmentedColormap.from_list("teal_seq", ["#ffffff", "#a8dadc", "#2a9d8f", "#1d6f66"])

fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.7))
for ax, (jkey, jname) in zip(axes, JUDGES):
    M = confusion(jkey)
    n = M.sum()
    exact = np.trace(M) / n * 100
    wk = wkappa(M)
    im = ax.imshow(np.sqrt(M), cmap=teal, vmin=0, vmax=np.sqrt(M.max()))
    ax.set_xticks(LEVELS); ax.set_yticks(LEVELS)
    ax.set_xticklabels([f"L{l}" for l in LEVELS], fontsize=9)
    ax.set_yticklabels([f"L{l}" for l in LEVELS], fontsize=9)
    ax.set_xlabel("Judge severity", fontsize=10)
    if ax is axes[0]:
        ax.set_ylabel("Oracle severity (O_prog)", fontsize=10)
    ax.set_title(f"{jname}\nexact {exact:.0f}%   weighted kappa {wk:.2f}",
                 fontsize=11, fontweight="bold", pad=8)
    for i in LEVELS:
        for j in LEVELS:
            v = M[i, j]
            if v == 0:
                continue
            txt_color = "white" if np.sqrt(v) > 0.55*np.sqrt(M.max()) else "#333333"
            ax.text(j, i, str(v), ha="center", va="center", fontsize=9,
                    fontweight="bold", color=txt_color)
    for k in LEVELS:
        ax.add_patch(plt.Rectangle((k-0.5, k-0.5), 1, 1, fill=False,
                                   edgecolor="#e76f51", lw=1.6))
    ax.set_xticks(np.arange(-.5, 7, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 7, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)
    for s in ax.spines.values():
        s.set_visible(False)

fig.suptitle("Judge-vs-oracle severity confusion (orange outline = perfect agreement)",
             fontsize=12.5, fontweight="bold", y=1.02)
fig.text(0.5, -0.03,
         "n = 188 stratified episodes (94 harmful + 94 L0 controls). Rows sum to the oracle count per level; "
         "L1, L2 unoccupied in this sample.",
         ha="center", fontsize=8.5, color="#707070")
fig.tight_layout(rect=[0, 0.02, 1, 1])
outdir = ROOT / "figures"; outdir.mkdir(exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(outdir / f"fig4_judge_confusion.{ext}", bbox_inches="tight")
print("wrote figures/fig4_judge_confusion.png / .pdf")
