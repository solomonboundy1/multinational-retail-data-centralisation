-- CASTING CORRECT DATA TYPES

-- orders_table

ALTER TABLE orders_table
ALTER COLUMN date_uuid TYPE UUID USING date_uuid::UUID;

ALTER TABLE orders_table
ALTER COLUMN user_uuid TYPE UUID USING user_uuid::UUID;


DO $$
BEGIN
    EXECUTE format('ALTER TABLE orders_table ALTER COLUMN card_number TYPE VARCHAR(%s)', (
        SELECT MAX(LENGTH(card_number)) FROM orders_table
    ));
END $$;

DO $$
BEGIN
	EXECUTE format('ALTER TABLE orders_table ALTER COLUMN store_code TYPE VARCHAR(%s)', (
		SELECT MAX(LENGTH(store_code)) FROM orders_table
	));
END $$;

DO $$
BEGIN
	EXECUTE format('ALTER TABLE orders_table ALTER COLUMN product_code TYPE VARCHAR(%s)', (
		SELECT MAX(LENGTH(product_code)) FROM orders_table
	));
END $$;

ALTER TABLE orders_table
ALTER COLUMN product_quantity TYPE SMALLINT;


--Users table

ALTER TABLE dim_users
ALTER COLUMN first_name TYPE VARCHAR(255);

ALTER TABLE dim_users
ALTER COLUMN last_name TYPE VARCHAR(255);

ALTER TABLE dim_users
ALTER COLUMN date_of_birth TYPE DATE USING date_of_birth::DATE;

DO $$
BEGIN
	EXECUTE format('ALTER TABLE dim_users ALTER COLUMN country_code TYPE VARCHAR(%s)', (
		SELECT MAX(LENGTH(country_code)) FROM dim_users
	));
END $$;

ALTER TABLE dim_users
ALTER COLUMN user_uuid TYPE UUID USING user_uuid::UUID;

ALTER TABLE dim_users
ALTER COLUMN join_date TYPE DATE USING join_date::DATE;


-- store details

UPDATE dim_store_details
SET latitude = COALESCE(latitude, lat);

ALTER TABLE dim_store_details
DROP COLUMN lat
-- error message ERROR:  cached plan must not change result type 

--SQL state: 0A000
-- when running select statements after this query^^
-- Resolve: restart pgAdmin

--Setting N/A results to null so I can cast column to correct data type
UPDATE dim_store_details
SET longitude = NULL
WHERE longitude = 'N/A'

UPDATE dim_store_details
SET latitude = NULL
WHERE latitude = 'N/A'

ALTER TABLE dim_store_details
ALTER COLUMN longitude TYPE real USING longitude::real;

ALTER TABLE dim_store_details
ALTER COLUMN locality TYPE VARCHAR(255);

DO $$
BEGIN
	EXECUTE format('ALTER TABLE dim_store_details ALTER COLUMN store_code TYPE VARCHAR(%s)', 
		(SELECT MAX(LENGTH(store_code)) FROM dim_store_details
		));
END $$;

ALTER TABLE dim_store_details
ALTER COLUMN staff_numbers TYPE SMALLINT USING staff_numbers::smallint;

ALTER TABLE dim_store_details
ALTER COLUMN opening_date TYPE DATE USING opening_date::DATE;

ALTER TABLE dim_store_details
ALTER COLUMN store_type TYPE VARCHAR(255) USING store_type::VARCHAR(255);

ALTER TABLE dim_store_details
ALTER COLUMN latitude TYPE real USING latitude::real;

DO $$
BEGIN
	EXECUTE format('ALTER TABLE dim_store_details ALTER COLUMN country_code TYPE VARCHAR(%s)', 
		(SELECT MAX(LENGTH(country_code)) FROM dim_store_details
		));
END $$;

ALTER TABLE dim_store_details
ALTER COLUMN continent TYPE VARCHAR(255)


-- products table

UPDATE dim_products
SET product_price = REPLACE(product_price, '£', '')
WHERE product_price LIKE '£%';

ALTER TABLE dim_products
ADD COLUMN weight_class VARCHAR(14);

UPDATE dim_products
SET weight_class = 
    CASE
        WHEN weight::numeric < 2 THEN 'Light'
        WHEN weight::numeric >= 2 AND weight::numeric < 40 THEN 'Mid_Sized'
        WHEN weight::numeric >= 40 AND weight::numeric < 140 THEN 'Heavy'
        ELSE 'Truck_Required'
    END;
SELECT * FROM dim_products 

ALTER TABLE dim_products
RENAME COLUMN removed TO still_available

ALTER TABLE dim_products
ALTER COLUMN product_price TYPE REAL USING product_price::real

ALTER TABLE dim_products
ALTER COLUMN weight TYPE REAL USING weight::real

SELECT * FROM dim_products

-- The below query about the EAN column did not work and I had to
-- input the correct data type manually.
-- I kept on getting the error 'column "EAN does not exist"'
-- even when I did SELECT EAN FROM dim_products, however
-- the EAN column is there when I SELECT * FROM dim_products
-- Resolved: pgAdmin right click on EAN column, adjust properties
DO $$
BEGIN
	EXECUTE format('ALTER TABLE dim_products ALTER COLUMN EAN TYPE VARCHAR(%s)', 
		(SELECT MAX(LENGTH(EAN)) FROM dim_products
		));
END $$;

DO $$
BEGIN
	EXECUTE format('ALTER TABLE dim_products ALTER COLUMN product_code TYPE VARCHAR(%s)', 
		(SELECT MAX(LENGTH(product_code)) FROM dim_products
		));
END $$;

ALTER TABLE dim_products
ALTER COLUMN date_added TYPE DATE USING date_added::DATE

ALTER TABLE dim_products
ALTER COLUMN uuid  TYPE UUID USING uuid::uuid

ALTER TABLE dim_products
ALTER COLUMN still_available TYPE BOOLEAN USING 
    CASE 
        WHEN still_available = 'Still_avaliable' THEN TRUE 
        ELSE FALSE 
    END;

DO $$
BEGIN
	EXECUTE format('ALTER TABLE dim_products ALTER COLUMN weight_class TYPE VARCHAR(%s)', 
		(SELECT MAX(LENGTH(weight_class)) FROM dim_products
		));
END $$;

-- dim_date_times

SELECT * FROM dim_date_times

ALTER TABLE dim_date_times
ALTER COLUMN month TYPE VARCHAR(2)

ALTER TABLE dim_date_times
ALTER COLUMN year TYPE VARCHAR(4)

ALTER TABLE dim_date_times
ALTER COLUMN day TYPE VARCHAR(2)

DO $$
BEGIN
	EXECUTE format('ALTER TABLE dim_date_times ALTER COLUMN time_period TYPE VARCHAR(%s)',
				  (SELECT MAX(LENGTH(time_period)) FROM dim_date_times
				  ));
END $$;

ALTER TABLE dim_date_times
ALTER COLUMN date_uuid TYPE UUID USING date_uuid::uuid


-- dim_card_details

SELECT * FROM dim_card_details

DO $$
BEGIN
	EXECUTE format('ALTER TABLE dim_card_details ALTER COLUMN card_number TYPE VARCHAR(%s)', 
		(SELECT MAX(LENGTH(card_number)) FROM dim_card_details
		));
END $$;

DO $$
BEGIN
	EXECUTE format('ALTER TABLE dim_card_details ALTER COLUMN expiry_date TYPE VARCHAR(%s)', 
		(SELECT MAX(LENGTH(expiry_date)) FROM dim_card_details
		));
END $$;

ALTER TABLE dim_card_details
ALTER COLUMN date_payment_confirmed TYPE DATE
USING date_payment_confirmed::date

-- Adding Primary Keys to all 'dim' tables

-- dim_card_details
ALTER TABLE dim_card_details
ADD PRIMARY KEY (card_number);

-- dim_date_times
ALTER TABLE dim_date_times
ADD PRIMARY KEY (date_uuid);

-- dim_products
ALTER TABLE dim_products
ADD PRIMARY KEY (product_code);

-- dim_store_details
ALTER TABLE dim_store_details
ADD PRIMARY KEY (store_code);

-- dim_users
ALTER TABLE dim_users
ADD PRIMARY KEY (user_uuid);


-- Adding foreign keys to orders_table

-- dim_card_details
ALTER TABLE orders_table
ADD CONSTRAINT orders_card_fk FOREIGN KEY (card_number) REFERENCES dim_card_details(card_number);

-- dim_date_times
ALTER TABLE orders_table
ADD CONSTRAINT orders_date_fk FOREIGN KEY (date_uuid) REFERENCES dim_date_times(date_uuid);

-- dim_products
ALTER TABLE orders_table
ADD CONSTRAINT orders_products_fk FOREIGN KEY (product_code) REFERENCES dim_products(product_code);

-- dim_store_details
ALTER TABLE orders_table
ADD CONSTRAINT orders_store_fk FOREIGN KEY (store_code) REFERENCES dim_store_details(store_code);

-- dim_users
ALTER TABLE orders_table
ADD CONSTRAINT orders_users_fk FOREIGN KEY (user_uuid) REFERENCES dim_users(user_uuid);

