from pathlib import Path
import sqlite3

import pandas as pd


DATABASE_PATH = Path(__file__).resolve().parent.parent / "olist.db"


def scalar(connection, query):
    return connection.execute(query).fetchone()[0]


def main():
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(
            f"Database not found at {DATABASE_PATH}. Run scripts\\load_to_sqlite.py first."
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        tables = [
            "orders",
            "order_items",
            "customers",
            "order_reviews",
            "order_payments",
            "products",
            "product_category_name_translation",
        ]

        print("Row counts")
        for table in tables:
            print(f"  {table}: {scalar(connection, f'SELECT COUNT(*) FROM {table}'):,}")

        print("\nKey and grain checks")
        checks = {
            "duplicate order IDs": """
                SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM orders
            """,
            "duplicate customer IDs": """
                SELECT COUNT(*) - COUNT(DISTINCT customer_id) FROM customers
            """,
            "duplicate product IDs": """
                SELECT COUNT(*) - COUNT(DISTINCT product_id) FROM products
            """,
            "duplicate order/item ID pairs": """
                SELECT COUNT(*) - COUNT(DISTINCT order_id || ':' || order_item_id)
                FROM order_items
            """,
            "review rows beyond unique review IDs": """
                SELECT COUNT(*) - COUNT(DISTINCT review_id) FROM order_reviews
            """,
            "exact duplicate review rows": """
                SELECT COUNT(*) FROM (
                    SELECT review_id, order_id, review_score, review_comment_title,
                           review_comment_message, review_creation_date,
                           review_answer_timestamp
                    FROM order_reviews
                    GROUP BY review_id, order_id, review_score, review_comment_title,
                             review_comment_message, review_creation_date,
                             review_answer_timestamp
                    HAVING COUNT(*) > 1
                )
            """,
            "orders with multiple item rows": """
                SELECT COUNT(*) FROM (
                    SELECT order_id FROM order_items GROUP BY order_id HAVING COUNT(*) > 1
                )
            """,
            "orders with multiple payment rows": """
                SELECT COUNT(*) FROM (
                    SELECT order_id FROM order_payments GROUP BY order_id HAVING COUNT(*) > 1
                )
            """,
            "orders with multiple review rows": """
                SELECT COUNT(*) FROM (
                    SELECT order_id FROM order_reviews GROUP BY order_id HAVING COUNT(*) > 1
                )
            """,
        }
        for label, query in checks.items():
            print(f"  {label}: {scalar(connection, query):,}")

        print("\nOrder and delivery checks")
        statuses = pd.read_sql_query(
            "SELECT order_status, COUNT(*) AS rows FROM orders "
            "GROUP BY order_status ORDER BY rows DESC",
            connection,
        )
        for row in statuses.itertuples(index=False):
            print(f"  {row.order_status}: {row.rows:,}")
        delivered_missing_date = scalar(
            connection,
            "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' "
            "AND order_delivered_customer_date IS NULL",
        )
        non_delivered_with_date = scalar(
            connection,
            "SELECT COUNT(*) FROM orders WHERE order_status != 'delivered' "
            "AND order_delivered_customer_date IS NOT NULL",
        )
        print(f"  delivered orders missing delivery date: {delivered_missing_date:,}")
        print(f"  non-delivered orders with delivery date: {non_delivered_with_date:,}")

        print("\nCategory checks")
        print(
            "  products with no category: "
            f"{scalar(connection, 'SELECT COUNT(*) FROM products WHERE product_category_name IS NULL'):,}"
        )
        unmapped_categories = scalar(
            connection,
            "SELECT COUNT(*) FROM products p "
            "LEFT JOIN product_category_name_translation t "
            "ON p.product_category_name = t.product_category_name "
            "WHERE p.product_category_name IS NOT NULL "
            "AND t.product_category_name IS NULL",
        )
        print(f"  non-null categories missing an English translation: {unmapped_categories:,}")

        print("\nJoin checks (rows without a matching parent)")
        relationships = {
            "orders without customers": """
                SELECT COUNT(*) FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                WHERE c.customer_id IS NULL
            """,
            "items without orders": """
                SELECT COUNT(*) FROM order_items i
                LEFT JOIN orders o ON i.order_id = o.order_id
                WHERE o.order_id IS NULL
            """,
            "items without products": """
                SELECT COUNT(*) FROM order_items i
                LEFT JOIN products p ON i.product_id = p.product_id
                WHERE p.product_id IS NULL
            """,
            "payments without orders": """
                SELECT COUNT(*) FROM order_payments p
                LEFT JOIN orders o ON p.order_id = o.order_id
                WHERE o.order_id IS NULL
            """,
            "reviews without orders": """
                SELECT COUNT(*) FROM order_reviews r
                LEFT JOIN orders o ON r.order_id = o.order_id
                WHERE o.order_id IS NULL
            """,
        }
        for label, query in relationships.items():
            print(f"  {label}: {scalar(connection, query):,}")


if __name__ == "__main__":
    main()
