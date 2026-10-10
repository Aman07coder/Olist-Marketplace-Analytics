-- Question 3b: What are the top customer segments using simple RFM?
-- RFM means Recency (how recently), Frequency (how often), and Monetary
-- (how much in item revenue). Scores range from 1 (lower) to 5 (higher).
-- For recency, newer customers receive a higher score. Frequency uses clear
-- repeat-purchase bands because most customers have exactly one delivered order.
WITH order_item_revenue AS (
    SELECT
        order_id,
        SUM(price) AS revenue
    FROM order_items
    GROUP BY order_id
),
customer_orders AS (
    SELECT
        customer.customer_unique_id,
        order_header.order_id,
        order_header.order_purchase_timestamp,
        COALESCE(order_item_revenue.revenue, 0) AS revenue
    FROM orders AS order_header
    JOIN customers AS customer
        ON order_header.customer_id = customer.customer_id
    LEFT JOIN order_item_revenue
        ON order_header.order_id = order_item_revenue.order_id
    WHERE order_header.order_status = 'delivered'
),
customer_rfm AS (
    SELECT
        customer_unique_id,
        CAST(
            julianday(date((SELECT MAX(order_purchase_timestamp) FROM customer_orders)))
            - julianday(date(MAX(order_purchase_timestamp)))
            AS INTEGER
        ) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(revenue) AS monetary
    FROM customer_orders
    GROUP BY customer_unique_id
),
scored_customers AS (
    SELECT
        customer_unique_id,
        recency_days,
        frequency,
        monetary,
        6 - NTILE(5) OVER (ORDER BY recency_days ASC) AS recency_score,
        CASE
            WHEN frequency = 1 THEN 1
            WHEN frequency = 2 THEN 4
            ELSE 5
        END AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS monetary_score
    FROM customer_rfm
),
segmented_customers AS (
    SELECT
        customer_unique_id,
        recency_days,
        frequency,
        monetary,
        recency_score,
        frequency_score,
        monetary_score,
        CASE
            WHEN recency_score >= 4
                AND frequency_score >= 4
                AND monetary_score >= 4 THEN 'Champions'
            WHEN recency_score >= 3 AND frequency_score >= 3 THEN 'Loyal'
            WHEN recency_score = 5 AND frequency_score <= 2 THEN 'New customers'
            WHEN recency_score <= 2
                AND (frequency_score >= 4 OR monetary_score = 5) THEN 'At risk'
            ELSE 'Other customers'
        END AS customer_segment
    FROM scored_customers
)
SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_pct,
    ROUND(AVG(frequency), 2) AS avg_delivered_orders,
    ROUND(AVG(monetary), 2) AS avg_item_revenue
FROM segmented_customers
GROUP BY customer_segment
ORDER BY customer_count DESC;
