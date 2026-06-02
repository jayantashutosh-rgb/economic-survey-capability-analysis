"""
Chart 2 — Keyword density heatmap across all chapters.

Reuses the same SQL logic as 02_keyword_density_by_chapter.sql but
pulls the result into pandas and plots a heatmap.

Rows: chapters (ordered by chapter_id)
Cols: five vocabulary clusters
Cell: density per 1,000 words

Output: outputs/charts/02_density_heatmap.png
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DB_PATH = Path("db/survey.db")
OUT_PATH = Path("outputs/charts/02_density_heatmap.png")

# Same chapter labels as Chart 1
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

# Each cluster lists (label_to_display, substring_to_search, length)
CLUSTERS = {
    "Growth": [
        ("growth", "growth", 6),
    ],
    "Capability": [
        ("capabilit", "capabilit", 9),
    ],
    "State": [
        ("state capacity", "state capacity", 14),
        ("entrepreneurial", "entrepreneurial", 15),
    ],
    "Welfare": [
        ("welfare", "welfare", 7),
        ("poverty", "poverty", 7),
    ],
    "Market": [
        ("market", "market", 6),
    ],
}


def load_data() -> pd.DataFrame:
    """Compute density per cluster per chapter using the same SQLite trick
    (LENGTH - LENGTH(REPLACE)) / N as our prior SQL queries."""

    # Build dynamic SQL: one SUM(...) expression per substring across all clusters
    expressions = []
    aliases = []
    for cluster_name, terms in CLUSTERS.items():
        for (display, substring, n_chars) in terms:
            alias = f"hits__{cluster_name}__{display}".replace(" ", "_")
            expr = (
                f"SUM((LENGTH(LOWER(p.text)) "
                f"- LENGTH(REPLACE(LOWER(p.text), '{substring}', ''))) / {n_chars}) "
                f"AS {alias}"
            )
            expressions.append(expr)
            aliases.append(alias)

    sql = f"""
        SELECT
            c.chapter_id,
            SUM(p.word_count) AS total_words,
            {', '.join(expressions)}
        FROM chapters c
        JOIN pages p ON p.chapter_id = c.chapter_id
        GROUP BY c.chapter_id
        ORDER BY c.chapter_id;
    """

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()

    # Sum hits per cluster, then convert to density per 1,000 words
    out = pd.DataFrame({"chapter_id": df["chapter_id"]})
    for cluster_name in CLUSTERS:
        cluster_cols = [a for a in aliases if a.startswith(f"hits__{cluster_name}__")]
        cluster_hits = df[cluster_cols].sum(axis=1)
        out[cluster_name] = (1000.0 * cluster_hits / df["total_words"]).round(2)

    out["label"] = out["chapter_id"].map(CHAPTER_LABELS)
    out = out.set_index("label")[list(CLUSTERS.keys())]
    return out


def plot(df: pd.DataFrame) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 8))
    sns.heatmap(
        df,
        annot=True, fmt=".1f",
        cmap="Blues",
        linewidths=0.5, linecolor="white",
        cbar_kws={"label": "Density per 1,000 words"},
        ax=ax,
    )

    ax.set_title(
        "Vocabulary density by chapter\nEconomic Survey 2025-26 — hits per 1,000 words",
        fontsize=12, loc="left", pad=15
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.setp(ax.get_xticklabels(), rotation=0)
    plt.setp(ax.get_yticklabels(), rotation=0)

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    df = load_data()
    plot(df)