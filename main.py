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




dbc = DatabaseConnector()
dc = DataCleaning()
de= DataExtractor()




# user_data = de.read_rds_table('legacy_users')

# user_data_cleaned = dc.clean_user_data(user_data)
# dbc.upload_to_db(user_data_cleaned, "dim_users")

# card_data = de.retrieve_pdf_data('https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf')
# card_data_cleaned = dc.clean_card_data(card_data)
# dbc.upload_to_db(card_data_cleaned, "dim_card_details")
#card_data_cleaned.to_csv('cleaned_card_data.csv', index=False)



load_dotenv()
api_key = os.getenv('API_KEY')
number_of_stores_url = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores"
headers = {
    "Content-Type": "application/json",
     "X-API-Key": f"{api_key}"
    }

url = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/{}"

num_stores = de.list_number_of_stores(number_of_stores_url, headers)

stores_data = de.retrieve_stores_data(url=url, num_stores=num_stores, headers=headers)
stores_data_cleaned = dc.clean_stores_data(stores_data)

dbc.upload_to_db(stores_data_cleaned, "dim_store_details")



# de.extract_from_s3("s3://data-handling-public/products.csv")
# s3data = de.extract_from_s3("s3://data-handling-public/products.csv")
# s3data_weight_corrected = dc.convert_product_weights(s3data)

# s3data_cleaned = dc.clean_product_data(s3data_weight_corrected)
# dbc.upload_to_db(s3data_cleaned, "dim_products")

# print(dbc.list_db_tables())


# orders_table = de.read_rds_table('orders_table')
# orders_table_cleaned = dc.clean_orders_data(orders_table)
#print(orders_table_cleaned)
#dbc.upload_to_db(orders_table_cleaned, "orders_table")

# sales_data = de.retrieve_data_from_url('https://data-handling-public.s3.eu-west-1.amazonaws.com/date_details.json')
# sales_data_cleaned = dc.clean_sales_data(sales_data)
# dbc.upload_to_db(sales_data_cleaned, 'dim_date_times')