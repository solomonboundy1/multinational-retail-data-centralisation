import yaml
from sqlalchemy import create_engine, inspect
import pandas as pd



class DatabaseConnector:

    """
    A class for connecting to and interacting with the database.

    Methods:
    - read_db_creds: Read database credentials from the YAML file.
    - init_db_engine: Initialize the database engine using credentials.
    - list_db_tables: List the tables present in the connected database.
    - upload_to_db: Upload a DataFrame to a specified table in the database.

    Usage Example:
    ```python
    dbc = DatabaseConnector()

    dbc.list_db_tables()
    ```

    """


    def __init__(self):
        self.engine = self.init_db_engine()

    def read_db_creds(self):
        """
        Reads database credentials from the YAML file (db_creds.yaml).

        Returns:
        dict: A dictionary containing database credentials.
        """

        with open("./db_creds.yaml", 'r') as file:
            result = yaml.safe_load(file)
            return result
    

    def init_db_engine(self):
        """
        Initialises the database engine using credentials.

        Returns:
        engine: The database engine.
        """

        engine = create_engine(f"postgresql://{self.read_db_creds()['RDS_USER']}:{self.read_db_creds()['RDS_PASSWORD']}@{self.read_db_creds()['RDS_HOST']}:{self.read_db_creds()['RDS_PORT']}/{self.read_db_creds()['RDS_DATABASE']}")
        engine.execution_options(isolation_level='AUTOCOMMIT').connect()
        return engine
    
    
    def list_db_tables(self):
        """
        Lists the tables present in the connected database.

        Returns:
        list: A list of table names in the connected database.
        """

        inspector = inspect(self.engine)
        result = inspector.get_table_names()
        return result
    
    def upload_to_db(self, df: pd.DataFrame, table_name: str):
        """
        Creates and uploads a table to the database with the contents of the DataFrame.

        Parameters:
        - df: The pandas DataFrame to be uploaded.
        - table_name (str): The name of the table in the database.
        """

        engine = create_engine(f"postgresql://{self.read_db_creds()['POSTGRES_USER']}:{self.read_db_creds()['POSTGRES_PASSWORD']}@{self.read_db_creds()['POSTGRES_HOST']}:{self.read_db_creds()['POSTGRES_PORT']}/{self.read_db_creds()['POSTGRES_DATABASE']}")
        df.to_sql(table_name, engine, index=False)


