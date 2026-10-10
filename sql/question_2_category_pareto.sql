-- Question 2: Which product categories bring the most revenue?
-- Revenue is delivered-order item price, excluding freight, as in Question 1.
-- Product rows map each item to one category before categories are ranked.
WITH category_revenue AS (
    SELECT
        COALESCE(
            translation.product_category_name_english,
            product.product_category_name,
            'Unknown / missing'
        ) AS category_name,
        SUM(item.price) AS revenue
    FROM order_items AS item
    JOIN orders AS order_header
        ON item.order_id = order_header.order_id
    JOIN products AS product
        ON item.product_id = product.product_id
    LEFT JOIN product_category_name_translation AS translation
        ON product.product_category_name = translation.product_category_name
    WHERE order_header.order_status = 'delivered'
    GROUP BY category_name
),
ranked_categories AS (
    SELECT
        category_name,
        revenue,
        ROW_NUMBER() OVER (ORDER BY revenue DESC, category_name) AS category_rank,
        COUNT(*) OVER () AS category_count,
        SUM(revenue) OVER () AS total_revenue,
        SUM(revenue) OVER (
            ORDER BY revenue DESC, category_name
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue
    FROM category_revenue
)
SELECT
    category_rank,
    category_name,
    ROUND(revenue, 2) AS category_revenue,
    ROUND(100.0 * revenue / total_revenue, 2) AS revenue_share_pct,
    ROUND(100.0 * cumulative_revenue / total_revenue, 2) AS cumulative_revenue_share_pct,
    CASE
        WHEN category_rank <= (category_count + 4) / 5 THEN 'Top 20% of categories'
        ELSE 'Remaining categories'
    END AS pareto_group
FROM ranked_categories
ORDER BY category_rank;
