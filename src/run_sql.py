"""
Run a .sql file against the SQLite database and print results as a table.

Usage:
  python src/run_sql.py sql/analysis/<query_name>.sql

This is a development utility. It reads the SQL file, executes it,
and prints the results in a readable column-aligned format.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("db/survey.db")


def run_query(sql_path: Path) -> None:
    if not sql_path.exists():
        print(f"ERROR: File not found: {sql_path}")
        sys.exit(1)

    sql = sql_path.read_text(encoding="utf-8")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    try:
        cur.execute(sql)
    except sqlite3.Error as e:
        print(f"SQL ERROR: {e}")
        conn.close()
        sys.exit(1)

    rows = cur.fetchall()
    headers = [d[0] for d in cur.description] if cur.description else []

    print_table(headers, rows)
    print(f"\n{len(rows)} row(s)")

    conn.close()


def print_table(headers: list, rows: list) -> None:
    if not headers:
        print("(no output columns)")
        return

    # Determine column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))

    # Print header
    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in rows:
        line = " | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row))
        print(line)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/run_sql.py <path_to_sql_file>")
        sys.exit(1)

    run_query(Path(sys.argv[1]))