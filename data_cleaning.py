import pandas as pd
from data_extraction import DataExtractor
import re

class DataCleaning:
    """
    A class for cleaning DataFrame data.

    Methods:
    - clean_user_data: Cleans user data.
    - clean_card_data: Cleans card data.
    - clean_stores_data: Cleans store data.
    - convert_product_weights: Converts product weights to kilograms.
    - clean_product_data: Cleans product data.
    - clean_orders_data: Cleans order data.
    - clean_sales_data: Cleans sales data.

    Usage Example:

    ```python
    dc = DataCleaning()

    cleaned_user_data = dc.clean_user_data(dataframe)
    ```
    
    """

    def __init__(self):
        pass
        

    
    def clean_user_data(self, user_data):
        """
        Cleans user data.

        Drops null values from dataframe
        Changes all mixed date formats to YYYY-MM-DD
        Drops duplicate entries in dataframe
        Reformats address to make it readable
        Replaces typos in country code

        Parameters:
        - user_data (DataFrame): The DataFrame containing user data.

        Returns:
        DataFrame: The cleaned user data DataFrame.
        """     

        # drops null values from dataframe
        user_data.dropna()

        # changes all mixed date formats to YYYY-MM-DD
        dates = ['date_of_birth', 'join_date']
        for date in dates: 
            user_data[date] = pd.to_datetime(user_data[date], format='mixed', errors='coerce')

        # drops duplicate entries in dataframe
        user_data = user_data.drop_duplicates()

        # reformats address to replace '\n' to ', '
        user_data['address'] = user_data['address'].str.replace('\n', ', ')

        # replaces typo in country code
        user_data['country_code'] = user_data['country_code'].str.replace('GGB', 'GB')

        return user_data
    
    def clean_card_data(self, card_data):

        """
        Cleans card data.

        Drops rows with null values
        Drops any row where card_number contains alphabet characters
        Drops rows with null entries in date_payment_confirmed column and formats all dates to YYYY-MM-DD
        Drops duplicate entries in dataframe

        Parameters:
        - card_data (DataFrame): The DataFrame containing card data.

        Returns:
        DataFrame: The cleaned user data DataFrame.
        """

        # drops rows with null values
        card_data.dropna()

        # drops any row where card_number contains alphabet characters
        card_data = card_data[card_data['card_number'].str.match('^\d+$', na=False)]

        # drops rows with null entries in date_payment_confirmed column, formats all dates to YYYY-MM-DD
        card_data['date_payment_confirmed'] = pd.to_datetime(card_data['date_payment_confirmed'], errors='coerce', format='mixed')
        card_data = card_data.dropna(subset=['date_payment_confirmed'])
        card_data['date_payment_confirmed'] = card_data['date_payment_confirmed'].dt.date

        # drops duplicate entries in dataframe
        card_data = card_data.drop_duplicates()

        return card_data

    def clean_stores_data(self, store_data):

        """
        Cleans store data.

        Drops rows with null values
        Drops any row where longitude or latitude contain alphabet characters
        Reformats address to make it readable
        Removes 'ee' from the beginning of some of the entries in the continent column
        Formats all dates in opening_date column to YYYY-MM-DD
        Drops duplicate entries in dataframe

        Parameters:
        - store_data (DataFrame): The DataFrame containing store data.

        Returns:
        DataFrame: The cleaned store data DataFrame.
        """

        # drops rows with null values
        store_data.dropna()
        
        # drops any row where longitude or latitude contain alphabet characters
        store_data = store_data[store_data['longitude'].str.match('^-?\d+(\.\d+)?$', na=False)]
        store_data = store_data[store_data['latitude'].str.match('^-?\d+(\.\d+)?$', na=False)]
        
        # reformats address to replace '\n' with ', '
        store_data['address'] = store_data['address'].str.replace('\n', ', ')
        
        # removes 'ee' from the beginning of some of the entries in the continent column
        store_data['continent'] = store_data['continent'].str.replace('^ee', '', regex=True)
        
        # formats all dates in opening_date column to YYYY-MM-DD
        store_data['opening_date'] = pd.to_datetime(store_data['opening_date'], format='mixed', errors='coerce')
        store_data['opening_date'] = store_data['opening_date'].dt.strftime('%Y-%m-%d')

        # drops duplicate entries in dataframe
        store_data = store_data.drop_duplicates()

        return store_data
    
    # converts entries in weight column to kilograms
    def convert_product_weights(self, s3_data):

        """
        Converts product weights to kilograms.

        Parameters:
        - s3_data (DataFrame): The DataFrame containing product data.

        Returns:
        DataFrame: The DataFrame with product weights converted to kilograms.
        """
        
        def convert(weight):

            non_numeric_re = "[^\d.]"
            if pd.isna(weight):
                # If weight is NaN, return it as is
                return weight
            elif ' x ' in weight:
                # if 'x' is in the weight column e.g '4 x 12g' it will multiply the two numbers
                # and return the weight in kg
                nums_to_multiply = weight.split(" x ")
                num_1 = float(nums_to_multiply[0])
                num_2 = float(re.sub(non_numeric_re, "", nums_to_multiply[1]))
                total = num_1 * num_2
                return f"{total/1000}kg"
            elif 'ml' in weight:
                # converts ml to g with 1:1 ratio and returns weight in kg
                return f'{float(re.sub(non_numeric_re, "", weight)) / 1000} kg'
            else:
                # returns weight as it is if weight ends in 'kg' or else it converts the weight to kg
                return weight if weight.endswith('kg') else f"{float(re.sub(non_numeric_re, '', weight)) / 1000} kg"
        # applies the nested method to the database and returns the converted data
        s3_data['weight'] = s3_data['weight'].apply(convert)
        return s3_data
    
    def clean_product_data(self, product_data):

        """
        Cleans product data.

        Drops rows with null values
        Formats all dates in date_added column to YYYY-MM-DD
        Drops any row where entry in EAN column contains alphabet characters
        Drops duplicate entries in dataframe

        Parameters:
        - product_data (DataFrame): The DataFrame containing card data.

        Returns:
        DataFrame: The cleaned product data DataFrame.
        """

        # drops rows with null values
        product_data.dropna()

        # formats all dates in date_added column to YYYY-MM-DD
        product_data['date_added'] = pd.to_datetime(product_data['date_added'], format='mixed', errors='coerce')
        product_data['date_added'] = product_data['date_added'].dt.strftime('%Y-%m-%d')

        # drops any row where EAN contains alphabet characters
        product_data = product_data[product_data['EAN'].str.match('^\d+$', na=False)]

        # drops unnamed column
        product_data.drop('Unnamed: 0', axis=1, inplace=True)

        # drops duplicate entries in dataframe
        product_data = product_data.drop_duplicates()

        return product_data


    def clean_orders_data(self, orders_data):

        """
        Cleans orders data.

        Drops rows with null values
        Removes columns first_name, last_name and 1
        Drops duplicate entries in dataframe

        Parameters:
        - orders_data (DataFrame): The DataFrame containing orders data.

        Returns:
        DataFrame: The cleaned card data DataFrame.
        """
        

        # remove columns first_name, last_name, 1
        orders_data.drop(['first_name', 'last_name', '1', 'level_0'], axis=1, inplace=True)

        # drops rows with null values
        orders_data.dropna()

        # drops duplicate entries in dataframe
        orders_data = orders_data.drop_duplicates()
        return orders_data
    
    def clean_sales_data(self, sales_data):

        """
        Cleans sales data.

        Drops rows with null values
        Drops any row where entry in 'year' column contains alphabet characters

        Parameters:
        - sales_data (DataFrame): The DataFrame containing sales data.

        Returns:
        DataFrame: The cleaned sales data DataFrame.
        """

        # drops rows with null values
        sales_data.dropna()

        # drops any row where year contains alphabet characters
        sales_data = sales_data[sales_data['year'].str.match('^\d+$', na=False)]

        return sales_data



if __name__ == '__main__':

    dc = DataCleaning()
    dc.clean_user_data
    #dc.user_data.to_csv('data.csv', index=False)
    # print(dc.user_data['date_of_birth'])
    #print(dc.user_data["join_date"])
    #print(dc.user_data['join_date'])
    #dc.user_data.info()
   # dc.clean_stores_data
    #dc.store_data.to_csv('cleaned_store_data.csv', index=False)
    #print(dc.store_data['continent'])