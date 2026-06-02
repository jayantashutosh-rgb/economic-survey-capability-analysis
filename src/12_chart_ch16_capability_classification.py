"""
Chart 4 — Chapter 16 capability classification.

Visualises the 66 occurrences of "capability/capabilities" in Chapter 16
(Strategic Resilience Parts I and II), split into the four manual
classification categories.

The data here comes from the manual classification recorded in
docs/findings.md (Finding 2). The counts are hard-coded because the
classification itself was a manual coding step, not a query.

Output: outputs/charts/04_ch16_capability_classification.png
"""

from pathlib import Path

import matplotlib.pyplot as plt

OUT_PATH = Path("outputs/charts/04_ch16_capability_classification.png")

CATEGORIES = [
    ("A — State capability\n(Mazzucato sense)",       23, "#4a6fa5"),
    ("B — Industrial / productive\ncapability",       41, "#7a9fd1"),
    ("C — Human capability\n(Sen sense)",              0, "#c25450"),
    ("D — Ambiguous",                                  2, "#999999"),
]


def plot() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    labels = [c[0] for c in CATEGORIES]
    counts = [c[1] for c in CATEGORIES]
    colors = [c[2] for c in CATEGORIES]

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.barh(labels, counts, color=colors, edgecolor="none")

    # Reverse so first category is at top
    ax.invert_yaxis()

    # Label each bar with its count
    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(count + 0.6, bar.get_y() + bar.get_height() / 2,
                    str(count), va="center", fontsize=11, color="#333")
        else:
            # For the zero bar, place label just to the right of axis
            ax.text(0.4, bar.get_y() + bar.get_height() / 2,
                    "0", va="center", fontsize=11, color="#c25450", fontweight="bold")

    ax.set_xlabel("Number of occurrences", fontsize=10)
    ax.set_title(
        "How the Survey uses \"capability\" in Chapter 16\n"
        "Manual classification of 66 occurrences (Strategic Resilience, Parts I & II)",
        fontsize=12, loc="left", pad=15
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    ax.set_xlim(0, max(counts) * 1.12)

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    plot()