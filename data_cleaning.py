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
        

    
    def clean_user_data(self, user_data: pd.DataFrame):
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
        user_data.dropna(inplace=True)

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

        # drops any row where email_address does not contain @ character also drops null values
        user_data = user_data[user_data['email_address'].str.contains('@')]
     

        return user_data
    
    def clean_card_data(self, card_data: pd.DataFrame):

        """
        Cleans card data.

        Drops rows with null values
        Drops rows with errors and null entries in date_payment_confirmed column and formats all dates to YYYY-MM-DD
        Drops duplicate entries in dataframe
        Replaces question marks that are at the beginning of some 'card_number' entries with an empty string

        Parameters:
        - card_data (DataFrame): The DataFrame containing card data.

        Returns:
        DataFrame: The cleaned user data DataFrame.
        """

        # drops rows with null values
        card_data.dropna(inplace=True)

        # drops rows with errors and null entries in date_payment_confirmed column, formats all dates to YYYY-MM-DD
        card_data['date_payment_confirmed'] = pd.to_datetime(card_data['date_payment_confirmed'], format='mixed', errors='coerce' )
        card_data = card_data.dropna(subset=['date_payment_confirmed'])
        card_data['date_payment_confirmed'] = card_data['date_payment_confirmed'].dt.date

        # replace question marks that are at the beginning of some 'card_number' entries with an empty string
        def remove_question_marks(card_number):
            while str(card_number).startswith('?'):
                card_number = str(card_number[1:])
            return card_number
        
        # applies method to remove question marks
        card_data['card_number'] = card_data['card_number'].apply(remove_question_marks)

        # drops duplicate entries in dataframe
        card_data = card_data.drop_duplicates()

        return card_data

    def clean_stores_data(self, store_data: pd.DataFrame):

        """
        Cleans store data.

        Drops rows with null values
        Reformats address to make it readable
        Removes 'ee' from the beginning of some of the entries in the continent column
        Formats all dates in opening_date column to YYYY-MM-DD
        Drops duplicate entries in dataframe
        Cleans entries of staff_numbers where staff_numbers have alphabet characters in

        Parameters:
        - store_data (DataFrame): The DataFrame containing store data.

        Returns:
        DataFrame: The cleaned store data DataFrame.
        """

        # drops rows with null values
        store_data = store_data.dropna(subset=['store_code', 'staff_numbers', 'opening_date', 'store_type', 'country_code', 'continent'])
        
        # reformats address to replace '\n' with ', '
        store_data['address'] = store_data['address'].str.replace('\n', ', ')
        
        # removes 'ee' from the beginning of some of the entries in the continent column
        store_data['continent'] = store_data['continent'].str.replace('^ee', '', regex=True)
        
        # formats all dates in opening_date column to YYYY-MM-DD
        store_data['opening_date'] = pd.to_datetime(store_data['opening_date'], format='mixed', errors='coerce')
        store_data['opening_date'] = store_data['opening_date'].dt.strftime('%Y-%m-%d')

        # drops duplicate entries in dataframe
        store_data = store_data.drop_duplicates()

        # cleans entries of staff_numbers where staff_numbers have alphabet characters in
        store_data['staff_numbers'] = pd.to_numeric(store_data['staff_numbers'].str.replace(r'[^0-9]', '', regex=True), errors='coerce')

        # removes rows where staff_numbers are null after conversion
        store_data = store_data.dropna(subset=['staff_numbers'])

        # removes entries where the length of country_code is greater than 2
        store_data = store_data[store_data['country_code'].str.len() <= 2]

        return store_data
    
    # converts entries in weight column to kilograms
    def convert_product_weights(self, s3_data: pd.DataFrame):

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
                return total/1000
            elif 'ml' in weight:
                # converts ml to g with 1:1 ratio and returns weight in kg
                return float(re.sub(non_numeric_re, "", weight)) / 1000
            else:
                # returns weight as it is if weight ends in 'kg' or else it converts the weight to kg
                return float(re.sub(non_numeric_re, "",weight)) if weight.endswith('kg') else float(re.sub(non_numeric_re, '', weight)) / 1000
        # applies the nested method to the database and returns the converted data
        s3_data['weight'] = s3_data['weight'].apply(convert)
        return s3_data
    
    def clean_product_data(self, product_data: pd.DataFrame):

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


    def clean_orders_data(self, orders_data: pd.DataFrame):

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
    
    def clean_sales_data(self, sales_data: pd.DataFrame):

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
    
    