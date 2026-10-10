-- Question 1: How do monthly revenue and average order value trend over time?
-- Revenue is the sum of item prices for delivered orders, excluding freight.
-- First aggregate item rows to one row per order so later joins cannot multiply revenue.
WITH order_item_revenue AS (
    SELECT
        order_id,
        SUM(price) AS revenue
    FROM order_items
    GROUP BY order_id
),
delivered_orders AS (
    SELECT
        o.order_id,
        strftime('%Y-%m', o.order_purchase_timestamp) AS purchase_month,
        COALESCE(r.revenue, 0) AS revenue
    FROM orders AS o
    LEFT JOIN order_item_revenue AS r
        ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
)
SELECT
    purchase_month,
    COUNT(*) AS delivered_orders,
    ROUND(SUM(revenue), 2) AS monthly_revenue,
    ROUND(AVG(revenue), 2) AS average_order_value
FROM delivered_orders
GROUP BY purchase_month
ORDER BY purchase_month;
