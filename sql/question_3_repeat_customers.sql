-- Question 3a: What percentage of customers are repeat customers?
-- A customer is identified by customer_unique_id and is "repeat" if they
-- have more than one delivered order in this dataset.
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
        COALESCE(order_item_revenue.revenue, 0) AS revenue
    FROM orders AS order_header
    JOIN customers AS customer
        ON order_header.customer_id = customer.customer_id
    LEFT JOIN order_item_revenue
        ON order_header.order_id = order_item_revenue.order_id
    WHERE order_header.order_status = 'delivered'
),
customer_frequency AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS delivered_order_count
    FROM customer_orders
    GROUP BY customer_unique_id
)
SELECT
    COUNT(*) AS delivered_customers,
    SUM(CASE WHEN delivered_order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        100.0 * SUM(CASE WHEN delivered_order_count > 1 THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS repeat_customer_pct
FROM customer_frequency;
