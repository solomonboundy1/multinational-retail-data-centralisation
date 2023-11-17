import os
from dotenv import load_dotenv
from data_cleaning import DataCleaning
from database_utils import DatabaseConnector
from data_extraction import DataExtractor
import requests

"""
    Main.py's function is to load, extract, clean, transform and upload data to the database.

    Steps:
    1. Initialise necessary classes and objects.
    2. Extract data from various sources.
    3. Clean and transform the data.
    4. Load the data into a centralised database.

    Usage:
    - Ensure the necessary environment variables are set, including API keys and database credentials.
    - Run this script to perform the data processing tasks.

    Usage Example
    ```python
    # Step 1: Initialize classes
    dc = DataCleaning()
    de = DataExtractor()

#     Step 2: Extract data
#     (Example: Retrieve data from a PDF)
    pdf_url = "https://example.com/sample.pdf"
    pdf_data = de.retrieve_pdf_data(pdf_url)

#     Step 3: Clean and transform data
    cleaned_data = dc.clean_data(pdf_data)

#     Step 4: Load data into the database
    dc.upload_to_db(cleaned_data, "cleaned_data_table")
    ```

"""



# Initialise instances of classes
dbc = DatabaseConnector()
dc = DataCleaning()
de = DataExtractor()


# Example Usage for each case

# Extract data from RDS table
user_data = de.read_rds_table('legacy_users')

# Clean  RDS table data
user_data_cleaned = dc.clean_user_data(user_data)

# Upload to database
dbc.upload_to_db(user_data_cleaned, "dim_users")


# Extract data from PDF
card_data = de.retrieve_pdf_data('https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf')

# Clean PDF data
card_data_cleaned = dc.clean_card_data(card_data)

# Upload to database
dbc.upload_to_db(card_data_cleaned, "dim_card_details")



# Load .env to access API Key
load_dotenv()

# Assign API key to a variable
api_key = os.getenv('API_KEY')

# Assign API link to variable
number_of_stores_url = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores"

# Assign variable 'headers' for API access, include API key in header
headers = {
    "Content-Type": "application/json",
     "X-API-Key": f"{api_key}"
    }

# Assign variable to retrieve the number of stores
url = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/{}"

# Retrieve number of stores
num_stores = de.list_number_of_stores(number_of_stores_url, headers)

# Extract data from API link
stores_data = de.retrieve_stores_data(url=url, num_stores=num_stores, headers=headers)

# Clean API link data
stores_data_cleaned = dc.clean_stores_data(stores_data)

# Upload to database
dbc.upload_to_db(stores_data_cleaned, "dim_store_details")



# Extract data from s3 link
s3data = de.extract_from_s3("s3://data-handling-public/products.csv")

# Convert the product weights column to kilogram
s3data_weight_corrected = dc.convert_product_weights(s3data)

# Clean s3 link data
s3data_cleaned = dc.clean_product_data(s3data_weight_corrected)

# Upload to database
dbc.upload_to_db(s3data_cleaned, "dim_products")


# List database tables
print(dbc.list_db_tables())


# Extract data from RDS
orders_table = de.read_rds_table('orders_table')

# Clean RDS data
orders_table_cleaned = dc.clean_orders_data(orders_table)

# Upload to database
dbc.upload_to_db(orders_table_cleaned, "orders_table")


# Extract data from URL
sales_data = de.retrieve_data_from_url('https://data-handling-public.s3.eu-west-1.amazonaws.com/date_details.json')

# Clean URL data
sales_data_cleaned = dc.clean_sales_data(sales_data)

# Upload to database
dbc.upload_to_db(sales_data_cleaned, 'dim_date_times')