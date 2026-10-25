"""Shared chart style: thin marks, hairline grid, ink-coloured text, colour-blind-safe palette.

Palette (validated for colour-vision deficiency, adjacent pairs):
  slot 1 blue   #2a78d6
  slot 2 orange #eb6834
  slot 3 aqua   #1baf7a   (below 3:1 contrast on white, so always direct-labelled)
Ordinal blue ramp (light -> dark): #86b6ef, #3987e5, #184f95
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
RAMP3 = ["#86b6ef", "#3987e5", "#184f95"]
GRAY = "#b9b8b0"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
GRID, SURFACE = "#e1e0d9", "#fcfcfb"


def setup():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "font.family": "DejaVu Sans", "font.size": 10.5,
        "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "axes.edgecolor": GRID, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "grid.linestyle": "-",
        "axes.axisbelow": True, "legend.frameon": False, "legend.fontsize": 9.5,
        "axes.titlesize": 12.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.titlepad": 12,
    })


def title(ax, main, sub=None):
    ax.set_title(main, loc="left", fontsize=12.5, fontweight="bold", color=INK, pad=24 if sub else 12)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9.5, color=INK2, va="bottom")


def source(fig, text):
    fig.text(0.01, -0.035, text, fontsize=8, color=MUTED, ha="left", va="top")
