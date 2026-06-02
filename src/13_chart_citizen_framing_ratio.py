"""
Chart 5 — Citizen framing: input-to-end ratio per chapter (strict version).

Uses the same SQL logic as 06_citizen_framing_strict.sql.

Each chapter's bar length = input_to_end_ratio.
Reference line at ratio = 1.0 separates input-dominant from end-dominant.

Output: outputs/charts/05_citizen_framing_ratio.png
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = Path("db/survey.db")
OUT_PATH = Path("outputs/charts/05_citizen_framing_ratio.png")

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

INPUT_TERMS = [
    ("worker", 6),
    ("workforce", 9),
    ("labour", 6),
    ("human capital", 13),
    ("human resource", 14),
    ("beneficiar", 10),
    ("consumer", 8),
    ("taxpayer", 8),
    ("manpower", 8),
]

END_TERMS = [
    ("citizen", 7),
    ("individual", 10),
    ("person", 6),
]


def hit_expr(term: str, n: int) -> str:
    return f"((LENGTH(combined_text) - LENGTH(REPLACE(combined_text, '{term}', ''))) / {n})"


def load_data() -> pd.DataFrame:
    input_sum = " + ".join(hit_expr(t, n) for t, n in INPUT_TERMS)
    end_sum = " + ".join(hit_expr(t, n) for t, n in END_TERMS)

    sql = f"""
        WITH chapter_text AS (
            SELECT
                c.chapter_id,
                SUM(p.word_count) AS total_words,
                LOWER(GROUP_CONCAT(p.text, ' ')) AS combined_text
            FROM chapters c
            JOIN pages p ON p.chapter_id = c.chapter_id
            GROUP BY c.chapter_id
        )
        SELECT
            chapter_id,
            ({input_sum}) AS input_hits,
            ({end_sum})   AS end_hits
        FROM chapter_text
        ORDER BY chapter_id;
    """

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()

    # Avoid divide-by-zero; mark as NaN
    df["ratio"] = df.apply(
        lambda r: r["input_hits"] / r["end_hits"] if r["end_hits"] > 0 else float("nan"),
        axis=1,
    )
    df["label"] = df["chapter_id"].map(CHAPTER_LABELS)
    return df


def plot(df: pd.DataFrame) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Sort so highest ratio at top
    df = df.sort_values("ratio", ascending=True)

    colors = ["#c25450" if r >= 1 else "#4a6fa5" for r in df["ratio"]]

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(df["label"], df["ratio"], color=colors, edgecolor="none")

    # Numeric labels at bar ends
    for bar, ratio in zip(bars, df["ratio"]):
        ax.text(ratio + 0.15, bar.get_y() + bar.get_height() / 2,
                f"{ratio:.2f}", va="center", fontsize=9, color="#333")

    # Reference line at ratio = 1
    ax.axvline(x=1.0, color="#666", linestyle="--", linewidth=1)
    ax.text(1.02, -0.7, "ratio = 1\n(balanced)", fontsize=8, color="#666")

    ax.set_xlabel("Input-to-end ratio (instrumental nouns / agentive nouns)", fontsize=10)
    ax.set_title(
        "How the Survey refers to citizens, by chapter\n"
        "Red bars: input-framing dominates. Blue bars: end-framing dominates.",
        fontsize=12, loc="left", pad=15
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    ax.set_xlim(0, df["ratio"].max() * 1.10)

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    df = load_data()
    plot(df)