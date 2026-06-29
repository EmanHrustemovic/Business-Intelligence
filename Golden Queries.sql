# 1. Golden Query 1
#Question : What is the total revenue?

SELECT SUM(payment_value) AS total_revenue
FROM fact_order_items;

/*2. Golden Query 2 
Question : How many orders have been placed?  */

SELECT COUNT(DISTINCT order_id) AS total_orders
FROM fact_order_items;

/*3. Goolden Query 3 
Question : How many unique customers do we have?
*/

SELECT COUNT(DISTINCT customer_id) AS total_customers
FROM fact_order_items;

/*Golden Query 4
Question : What is the average review score?
*/
SELECT AVG(review_score) AS average_review_score
FROM fact_order_items;

/*Golden Query 5 
Question : Show monthly revenue.
*/
SELECT
DATE_TRUNC('month', shipping_date_limit) AS month,
SUM(payment_value) AS revenue
FROM fact_order_items
GROUP BY month
ORDER BY month;

/*Golden Query 6 
Question : Show top 10 product categories by revenue.
*/

SELECT
dp.product_category_name,
SUM(f.payment_value) AS revenue
FROM fact_order_items f
JOIN dim_products dp
ON f.product_id = dp.product_id
GROUP BY dp.product_category_name
ORDER BY revenue DESC
LIMIT 10;


/*Golden Query 7 
Question : Show top 10 sellers by revenue.
*/

SELECT
seller_id,
SUM(payment_value) AS revenue
FROM fact_order_items
GROUP BY seller_id
ORDER BY revenue DESC
LIMIT 10;


/*Golden Query 8
Question : Show order distribution by payment type.
*/

SELECT
payment_type,
COUNT(*) AS number_of_orders
FROM fact_order_items
GROUP BY payment_type;

/*Golden Query 9
Question : Show average order value by review score.
*/

SELECT
review_score,
AVG(payment_value) AS average_order_value
FROM fact_order_items
GROUP BY review_score
ORDER BY review_score;

/*Golden Query 10
Question : Show average freight cost by number of installments. */

SELECT
payment_installments,
AVG(freight_value) AS average_freight
FROM fact_order_items
GROUP BY payment_installment
ORDER BY payment_installment;

/* Golden Query 11
Question: Show revenue by customer state.
*/

SELECT
c.customer_state,
SUM(f.payment_value) AS revenue
FROM fact_order_items f
JOIN dim_customers c
ON f.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY revenue DESC;