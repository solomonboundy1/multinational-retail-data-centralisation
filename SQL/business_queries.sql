-- 1. How many stores does the business have and in which countries?
SELECT country_code, COUNT(*) FROM dim_store_details
GROUP BY country_code
-- Answer
-- DE 141, US 34, GB 266 (265 + 1 website)

-- 2. The business stakeholders would like to know which locations currently have the most stores.
-- They would like to close some stores before opening more in other locations.
-- Find out which locations have the most stores currently.
SELECT locality, COUNT(*) FROM dim_store_details
GROUP BY locality
ORDER BY COUNT(*) desc
LIMIT 7
-- Answer
-- Belper(13), Bushey(12), Exeter(11), High Wycombe(10), Arbroath(10), Rutherglen(10)

-- 3. Query the database to find out which months have produced the most sales.

SELECT ROUND(SUM(product.product_price * orders.product_quantity)::numeric, 2) 
AS total_sales, dates.month
FROM dim_products product
JOIN ORDERS_TABLE orders ON 
product.product_code = orders.product_code
JOIN dim_date_times dates ON 
orders.date_uuid = dates.date_uuid
GROUP BY dates.month
ORDER BY total_sales DESC
LIMIT 10

-- Answer
--|__total__|_month_|
--|673295.68|   8   |
--|668041.45|   1   |
--|657335.84|   10  |
--|650321.43|   5   |
--|645741.70|   7   |
--|645463.00|   3   |


-- 4. The company is looking to increase its online sales.
-- They want to know how many sales are happening online vs offline.
-- Calculate how many products were sold and the amount of sales made for 
-- online and offline purchases.

SELECT COUNT(orders.product_quantity) AS number_of_sales,
SUM(orders.product_quantity) AS product_quantity_count,
CASE 
   WHEN store.store_type = 'Web Portal' THEN 'Web Portal'
ELSE 'Offline'
END AS sales_type
FROM dim_store_details store
JOIN orders_table orders ON 
store.store_code = orders.store_code 
JOIN dim_products product ON 
orders.product_code = product.product_code
GROUP BY sales_type;

-- Answer

-- |number_of_sales|product_quantity_count|sales_type|
-- |      26957    |        107739        | Web      |
-- |      93166    |        374047        | Offline  |


-- 5. The sales team wants to know which of the different store types is 
-- generated the most revenue so they know where to focus.
-- Find out the total and percentage of sales coming from each of the different store types.


SELECT store.store_type, SUM(orders.product_quantity) AS total_sales,
ROUND(SUM(orders.product_quantity) * 100.0 / SUM(SUM(orders.product_quantity)) OVER (), 2) 
AS percentage_total
FROM dim_store_details store
JOIN orders_table orders ON store.store_code = orders.store_code
GROUP BY store.store_type;



-- 6. Find which months in which years have had the most sales historically.



SELECT 
ROUND(SUM(products.product_price * orders.product_quantity)::numeric,2) 
AS total_sales,
dates.year, dates.month
FROM dim_products products 
JOIN orders_table orders ON 
products.product_code = orders.product_code 
JOIN dim_date_times dates ON 
orders.date_uuid = dates.date_uuid
GROUP BY dates.month, dates.year
ORDER BY total_sales DESC;


-- 7. The operations team would like to know the overall staff numbers 
-- in each location around the world. Perform a query to determine the 
-- staff numbers in each of the countries the company sells in.

SELECT SUM(staff_numbers) AS total_staff_numbers, country_code 
FROM dim_store_details
GROUP BY country_code


-- 8. The sales team is looking to expand their territory in Germany. 
-- Determine which type of store is generating the most sales in Germany.

SELECT ROUND(SUM(orders.product_quantity * products.product_price)::numeric, 2), 
stores.country_code, stores.store_type
FROM orders_table orders
JOIN dim_store_details stores ON
stores.store_code = orders.store_code
JOIN dim_products products ON
orders.product_code = products.product_code
WHERE country_code LIKE 'DE'
GROUP BY stores.store_type, stores.country_code


-- 9. Sales would like the get an accurate metric for how quickly the company is making sales.
-- Determine the average time taken between each sale grouped by year

-- WITH SaleIntervals AS (
--   SELECT
--     EXTRACT(YEAR FROM dates.timestamp::TIMESTAMP) AS sale_year,
--     LEAD(dates.timestamp::TIMESTAMP) OVER (ORDER BY dates.timestamp::TIMESTAMP) - dates.timestamp::TIMESTAMP AS time_interval
--   FROM
--     orders_table orders
--   JOIN
--     dim_date_times dates ON orders.date_uuid = dates.date_uuid
-- )
-- SELECT
--   sale_year,
--   AVG(EXTRACT(DAY FROM time_interval)) AS actual_time_taken
-- FROM
--   SaleIntervals
-- GROUP BY
--   sale_year
-- ORDER BY
--   sale_year;
-- SELECT * FROM dim_date_times
