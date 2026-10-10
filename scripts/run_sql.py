from pathlib import Path
import sqlite3
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "olist.db"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts\\run_sql.py sql\\query_file.sql")

    query_path = (PROJECT_ROOT / sys.argv[1]).resolve()
    if not query_path.is_relative_to(PROJECT_ROOT.resolve()):
        raise ValueError("Query file must be inside the project folder.")
    if not query_path.is_file():
        raise FileNotFoundError(f"SQL file not found: {query_path}")
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(
            f"Database not found at {DATABASE_PATH}. Run scripts\\load_to_sqlite.py first."
        )

    query = query_path.read_text(encoding="utf-8")
    with sqlite3.connect(DATABASE_PATH) as connection:
        results = pd.read_sql_query(query, connection)

    if results.empty:
        print("Query returned no rows.")
    else:
        print(results.to_string(index=False))


if __name__ == "__main__":
    main()
