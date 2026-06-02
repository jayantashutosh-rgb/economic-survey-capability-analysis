"""
Chart 6 — Chapter 16.2 citizen-end framing breakdown.

Stacked horizontal bar chart showing how the 44 occurrences of
citizen / individual in Chapter 16.2 split across four framing categories:
  S — Sen-adjacent (rights / agency / expectations)
  D — Duty-oriented (norms, compliance, responsibility)
  P — Partnership / co-production
  N — Neutral / structural

Counts come from the manual classification recorded in
docs/findings.md (Finding 6) and are hard-coded.

Output: outputs/charts/06_ch16_2_citizen_framing.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT_PATH = Path("outputs/charts/06_ch16_2_citizen_framing.png")

# Rows in the chart
TERMS = ["citizen(s)\n(31 occurrences)", "individual(s)\n(13 occurrences)"]

# Categories in stacking order, with their counts per term
CATEGORIES = [
    ("S — Sen-adjacent",     [13, 0],  "#4a6fa5"),
    ("D — Duty-oriented",    [11, 4],  "#c25450"),
    ("P — Partnership",      [2, 0],   "#5b9b6f"),
    ("N — Neutral/structural",[5, 9],  "#999999"),
]


def plot() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 4.5))

    y = np.arange(len(TERMS))
    left = np.zeros(len(TERMS))

    for label, counts, color in CATEGORIES:
        counts_arr = np.array(counts)
        bars = ax.barh(y, counts_arr, left=left, color=color, label=label, edgecolor="white")

        # Label each segment with its count (skip zeros — they have no visible width)
        for i, c in enumerate(counts_arr):
            if c > 0:
                ax.text(left[i] + c / 2, y[i], str(c),
                        ha="center", va="center", fontsize=10, color="white", fontweight="bold")

        left += counts_arr

    ax.set_yticks(y)
    ax.set_yticklabels(TERMS, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Number of occurrences", fontsize=10)

    ax.set_title(
        "Chapter 16.2 — how citizen-end words are actually used\n"
        "Most occurrences are duty-oriented or structural, not Sen-adjacent",
        fontsize=12, loc="left", pad=15
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18),
              ncol=4, fontsize=9, frameon=False)

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    plot()