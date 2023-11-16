import json
import pandas as pd
from database_utils import DatabaseConnector
import tabula
import requests
from dotenv import load_dotenv
import boto3
from io import StringIO

class DataExtractor:
    """
    Class for extracting data from different sources and creating a DataFrame out of the information.

    Methods:
    - read_rds_table: Read data from an RDS table.
    - retrieve_pdf_data: Retrieve data from a PDF file.
    - list_number_of_stores: Get the number of stores from an API endpoint.
    - retrieve_stores_data: Retrieve stores data from an API endpoint.
    - extract_from_s3: Extract data from an S3 bucket.
    - retrieve_data_from_url: Retrieve data from a JSON file hosted at a URL.


    Usage example:
    ```python
    de = DataExtractor()
    pdf_data = de.retrieve_pdf_data(pdf_url)
    ```
    """


    def __init__(self):
        self.dbc = DatabaseConnector()
        load_dotenv()

        # Reads data from an RDS table
    def read_rds_table(self, table_name: str):

        """
        Reads data from an RDS table.

        Parameters:
        - table_name (str): Name of the table to read.

        Returns:
        - DataFrame: DataFrame containing the data from the specified table.
        """

        data = pd.read_sql_table(table_name, self.dbc.engine)
        df = pd.DataFrame(data)
        return df
    

    # retrieves pdf data and converts it to dataframe
    def retrieve_pdf_data(self, url: str):

        """
        Retrieves data from a PDF file.

        Parameters:
        - url (str): URL of the PDF file.

        Returns:
        - DataFrame: DataFrame containing the data from the PDF.
        """

        dfs = tabula.read_pdf(url, pages='all')
        df = pd.concat(dfs)
        return df
    
    # returns the number of stores
    def list_number_of_stores(self, url: str, headers: dict):

        """
        Retrieves the number of stores from the API endpoint.

        Parameters:
        - url (str): URL of the API endpoint.
        - headers (dict): Headers to include in the API request.

        Returns:
        - int: Number of stores.
        """

        response = requests.get(url, headers=headers)
        return response.json()['number_stores']
    
    # retrieves all stores from the link and puts them into a dataframe
    def retrieve_stores_data(self, url: str, num_stores: int, headers: dict):

        """
        Retrieve stores data from an API endpoint.

        Parameters:
        - url (str): URL template for the API endpoint.
        - num_stores (int): Number of stores to retrieve/the number of stores available.
        - headers (dict): Headers to include in the API request.

        Returns:
        - DataFrame: DataFrame containing the stores data.
        """

        stores_data = []
        for store in range(num_stores):
            store_link = url.format(store)
            response = requests.get(store_link, headers=headers)
            stores_data.append(response.json())

        store_df = pd.DataFrame(stores_data)
        return store_df


    # extracts data from an s3 bucket
    def extract_from_s3(self, url: str):

        """
        Extract data from an S3 bucket.

        Parameters:
        - url (str): S3 URL of the file.

        Returns:
        - DataFrame: DataFrame containing the data from the S3 file.
        """

        s3 = boto3.client('s3')
        bucket_name, key = url.split("//")[1].split("/", 1)
        s3_object = s3.get_object(Bucket=bucket_name, Key=key)
        object_body = s3_object['Body']
        body_string = object_body.read().decode('utf-8')
        df = pd.read_csv(StringIO(body_string))
        return df
    
    def retrieve_data_from_url(self, url: str):

        """
        Retrieve data from a JSON file hosted at a URL.

        Parameters:
        - url (str): URL of the JSON file.

        Returns:
        - DataFrame: DataFrame containing the data from the JSON file.
        """

        df = pd.read_json(url)
        return df

    