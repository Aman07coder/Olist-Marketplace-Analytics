-- Question 4: Do late deliveries lead to lower review scores? By how much?
-- Compare delivered orders with a known actual and estimated delivery date.
-- Aggregate reviews to one average score per order to give each order equal weight.
WITH order_review_score AS (
    SELECT
        order_id,
        AVG(review_score) AS average_review_score
    FROM order_reviews
    GROUP BY order_id
),
delivery_outcomes AS (
    SELECT
        order_header.order_id,
        CASE
            WHEN julianday(order_header.order_delivered_customer_date)
                 > julianday(order_header.order_estimated_delivery_date)
                THEN 'Late'
            ELSE 'On time or early'
        END AS delivery_status,
        order_review_score.average_review_score
    FROM orders AS order_header
    JOIN order_review_score
        ON order_header.order_id = order_review_score.order_id
    WHERE order_header.order_status = 'delivered'
      AND order_header.order_delivered_customer_date IS NOT NULL
      AND order_header.order_estimated_delivery_date IS NOT NULL
),
score_summary AS (
    SELECT
        delivery_status,
        COUNT(*) AS reviewed_orders,
        ROUND(AVG(average_review_score), 2) AS average_review_score
    FROM delivery_outcomes
    GROUP BY delivery_status
),
score_gap AS (
    SELECT
        MAX(CASE WHEN delivery_status = 'On time or early'
                 THEN average_review_score END) AS on_time_score,
        MAX(CASE WHEN delivery_status = 'Late'
                 THEN average_review_score END) AS late_score
    FROM score_summary
)
SELECT
    score_summary.delivery_status,
    score_summary.reviewed_orders,
    score_summary.average_review_score,
    ROUND(score_gap.on_time_score - score_gap.late_score, 2)
        AS late_delivery_score_drop
FROM score_summary
CROSS JOIN score_gap
ORDER BY CASE score_summary.delivery_status
    WHEN 'On time or early' THEN 1
    ELSE 2
END;
