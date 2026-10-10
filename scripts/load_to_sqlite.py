from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATABASE_PATH = PROJECT_ROOT / "olist.db"

CSV_TABLES = {
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_customers_dataset.csv": "customers",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_products_dataset.csv": "products",
    "product_category_name_translation.csv": "product_category_name_translation",
}


def main():
    missing_files = [
        filename
        for filename in CSV_TABLES
        if not (RAW_DATA_DIR / filename).is_file()
    ]
    if missing_files:
        missing_list = "\n".join(f"  - {filename}" for filename in missing_files)
        raise FileNotFoundError(
            f"Missing CSV files in {RAW_DATA_DIR}:\n{missing_list}\n"
            "Download the Olist dataset from Kaggle and place these files in data/raw."
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        for filename, table_name in CSV_TABLES.items():
            csv_path = RAW_DATA_DIR / filename
            dataframe = pd.read_csv(csv_path)
            dataframe.to_sql(table_name, connection, if_exists="replace", index=False)
            print(f"Loaded {table_name}: {len(dataframe):,} rows")

    print(f"\nDatabase created at: {DATABASE_PATH}")


if __name__ == "__main__":
    main()
