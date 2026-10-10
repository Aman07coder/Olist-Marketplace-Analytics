from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "olist.db"
SQL_DIR = PROJECT_ROOT / "sql"
EXPORT_DIR = PROJECT_ROOT / "exports"

EXPORTS = {
    "monthly_revenue.csv": "question_1_monthly_revenue.sql",
    "category_pareto.csv": "question_2_category_pareto.sql",
    "repeat_customers.csv": "question_3_repeat_customers.sql",
    "rfm_segments.csv": "question_3_rfm_segments.sql",
    "late_delivery_reviews.csv": "question_4_late_delivery_reviews.sql",
}


def main():
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(
            f"Database not found at {DATABASE_PATH}. Run scripts\\load_to_sqlite.py first."
        )

    missing_queries = [
        filename for filename in EXPORTS.values() if not (SQL_DIR / filename).is_file()
    ]
    if missing_queries:
        missing_list = "\n".join(f"  - {filename}" for filename in missing_queries)
        raise FileNotFoundError(f"Required SQL query files are missing:\n{missing_list}")

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        for csv_filename, sql_filename in EXPORTS.items():
            query = (SQL_DIR / sql_filename).read_text(encoding="utf-8")
            result = pd.read_sql_query(query, connection)
            csv_path = EXPORT_DIR / csv_filename
            result.to_csv(csv_path, index=False)
            print(f"Exported {len(result):,} rows to {csv_path}")


if __name__ == "__main__":
    main()
