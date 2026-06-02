"""
Chart 3 — Cluster A (instrumental) vs Cluster B (capability) density
across four human-development chapters.

Data source: same SQL logic as 04_framing_comparison_social_chapters.sql

Output: outputs/charts/03_cluster_comparison.png
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DB_PATH = Path("db/survey.db")
OUT_PATH = Path("outputs/charts/03_cluster_comparison.png")

TARGET_CHAPTERS = (11.0, 12.0, 13.0, 15.0)

CHAPTER_LABELS = {
    11.0: "11\nEducation\n& Health",
    12.0: "12\nEmployment\n& Skill",
    13.0: "13\nRural\nDevelopment",
    15.0: "15\nUrbanisation",
}

CLUSTER_A_TERMS = [
    ("human capital", 13),
    ("workforce", 9),
    ("productivity", 12),
    ("skill", 5),
    ("outcome", 7),
]

CLUSTER_B_TERMS = [
    ("capabilit", 9),
    ("freedom", 7),
    ("agency", 6),
    ("well-being", 10),
    ("wellbeing", 9),
    ("dignity", 7),
]


def hit_expr(term: str, n: int) -> str:
    """Build the LENGTH/REPLACE expression used throughout the project."""
    return f"SUM((LENGTH(LOWER(p.text)) - LENGTH(REPLACE(LOWER(p.text), '{term}', ''))) / {n})"


def load_data() -> pd.DataFrame:
    cluster_a_sum = " + ".join(hit_expr(t, n) for t, n in CLUSTER_A_TERMS)
    cluster_b_sum = " + ".join(hit_expr(t, n) for t, n in CLUSTER_B_TERMS)

    placeholders = ",".join("?" for _ in TARGET_CHAPTERS)
    sql = f"""
        SELECT
            c.chapter_id,
            SUM(p.word_count) AS total_words,
            ({cluster_a_sum}) AS cluster_a_hits,
            ({cluster_b_sum}) AS cluster_b_hits
        FROM chapters c
        JOIN pages p ON p.chapter_id = c.chapter_id
        WHERE c.chapter_id IN ({placeholders})
        GROUP BY c.chapter_id
        ORDER BY c.chapter_id;
    """

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn, params=TARGET_CHAPTERS)
    conn.close()

    df["density_a"] = (1000.0 * df["cluster_a_hits"] / df["total_words"]).round(2)
    df["density_b"] = (1000.0 * df["cluster_b_hits"] / df["total_words"]).round(2)
    df["label"] = df["chapter_id"].map(CHAPTER_LABELS)
    return df


def plot(df: pd.DataFrame) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    x = np.arange(len(df))
    width = 0.38

    fig, ax = plt.subplots(figsize=(9, 6))

    bars_a = ax.bar(x - width/2, df["density_a"], width,
                    label="Cluster A — instrumental\n(human capital, workforce,\nproductivity, skill, outcome)",
                    color="#c25450")
    bars_b = ax.bar(x + width/2, df["density_b"], width,
                    label="Cluster B — capability / freedom\n(capabilit*, freedom, agency,\nwell-being, dignity)",
                    color="#4a6fa5")

    # Numeric labels on top of bars
    for bars in (bars_a, bars_b):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.15,
                    f"{h:.2f}", ha="center", va="bottom", fontsize=9, color="#333")

    ax.set_xticks(x)
    ax.set_xticklabels(df["label"], fontsize=10)
    ax.set_ylabel("Density per 1,000 words", fontsize=10)
    ax.set_title(
        "Instrumental vocabulary dominates capability vocabulary\n"
        "Four human-development chapters, Economic Survey 2025-26",
        fontsize=12, loc="left", pad=15
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)

    # Headroom for top labels
    ax.set_ylim(0, df["density_a"].max() * 1.18)

    ax.legend(loc="upper right", fontsize=9, frameon=False)

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    df = load_data()
    plot(df)