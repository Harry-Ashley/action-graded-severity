"""Shared figure style for all paper figures. No em dashes anywhere in output text."""
import matplotlib as mpl

SEVERITY_COLORS = {
    0: "#2a9d8f", 1: "#8ab17d", 2: "#e9c46a", 3: "#f4a261",
    4: "#e76f51", 5: "#c1121f", 6: "#6a040f",
}
SEVERITY_LABELS = {
    0: "L0 none", 1: "L1 blocked", 2: "L2 rev-local", 3: "L3 irrev-local",
    4: "L4 cross-scope", 5: "L5 privilege", 6: "L6 chain",
}
BINARY_COLOR = "#264653"
ACCENT = "#e76f51"

def apply_style():
    mpl.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 300,
        "font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"], "font.size": 11,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.labelsize": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6, "axes.axisbelow": True,
        "legend.frameon": False, "legend.fontsize": 9,
        "xtick.labelsize": 10, "ytick.labelsize": 10,
    })
