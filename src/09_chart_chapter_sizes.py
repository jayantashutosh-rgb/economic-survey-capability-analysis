"""
Chart 1 — Chapter-level size overview.

Horizontal bar chart of total word count per chapter.
Establishes editorial weight before the analytical charts that follow.

Output: outputs/charts/01_chapter_sizes.png
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = Path("db/survey.db")
OUT_PATH = Path("outputs/charts/01_chapter_sizes.png")

# Short, human-readable chapter labels for display
CHAPTER_LABELS = {
    1.0:  "01 State of Economy",
    2.0:  "02 Fiscal",
    3.0:  "03 Monetary",
    4.0:  "04 External Sector",
    5.0:  "05 Inflation",
    6.0:  "06 Agriculture",
    7.0:  "07 Services",
    8.0:  "08 Industry",
    9.0:  "09 Investment & Infra",
    10.0: "10 Environment",
    11.0: "11 Education & Health",
    12.0: "12 Employment & Skill",
    13.0: "13 Rural Development",
    14.0: "14 AI Ecosystem",
    15.0: "15 Urbanisation",
    16.1: "16.1 Strategic Resilience I",
    16.2: "16.2 Strategic Resilience II",
}


def load_data() -> pd.DataFrame:
    """Pull chapter-level word totals from the database."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT c.chapter_id, SUM(p.word_count) AS total_words
        FROM chapters c
        JOIN pages p ON p.chapter_id = c.chapter_id
        GROUP BY c.chapter_id
        ORDER BY total_words ASC;   -- ascending so largest ends at top
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["label"] = df["chapter_id"].map(CHAPTER_LABELS)
    return df


def plot(df: pd.DataFrame) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 7))

    bars = ax.barh(df["label"], df["total_words"], color="#4a6fa5", edgecolor="none")

    # Numeric labels at bar end
    for bar, value in zip(bars, df["total_words"]):
        ax.text(value + 200, bar.get_y() + bar.get_height() / 2,
                f"{value:,}", va="center", fontsize=9, color="#333")

    # Styling
    ax.set_xlabel("Total words", fontsize=10)
    ax.set_title(
        "Editorial weight by chapter\nEconomic Survey 2025-26, Government of India",
        fontsize=12, loc="left", pad=15
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", length=0)        # remove tick marks on y-axis
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)

    # Some headroom on x-axis so labels do not get clipped
    ax.set_xlim(0, df["total_words"].max() * 1.10)

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    df = load_data()
    plot(df)