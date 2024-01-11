"""
========================
Database Manager Module
========================

This module contains the DataManager class, which is responsible for managing database interactions
for the grassland production system. It uses SQLAlchemy for database connectivity and Pandas for 
data manipulation.

Classes:
    DataManager: Manages database interactions and data retrieval.
"""


import sqlalchemy as sqa
import pandas as pd
from grassland_production.database import get_local_dir
import os


class DataManager:
    """
    The DataManager class manages interactions with the grassland management database. 
    It creates a connection to the database and provides methods to retrieve data in the 
    form of pandas DataFrames.

    Attributes:
        database_dir (str): Directory where the database file is located.
        engine (sqa.engine.base.Engine): SQLAlchemy engine object for database connection.

    Methods:
        data_engine_creater():
            Creates and returns a SQLAlchemy engine for database connectivity.

        get_cso_grassland_data():
            Retrieves data on CSO (Central Statistics Office, Ireland) grassland areas.

        get_grassland_fertilization_by_system():
            Retrieves data on grassland fertilization by system.

        get_dairy_area_nfs():
            Retrieves data on dairy areas from NFS (National Farm Survey).

        get_beef_area_nfs():
            Retrieves data on beef areas from NFS (National Farm Survey).

        get_sheep_area_nfs():
            Retrieves data on sheep areas from NFS (National Farm Survey).

        get_nfs_farm_numbers():
            Retrieves data on NFS farm numbers (National Farm Survey).

        get_dairy_soil_group():
            Retrieves data on dairy soil groups from NFS (National Farm Survey).

        get_cattle_soil_group():
            Retrieves data on cattle soil groups from NFS (National Farm Survey).

        get_sheep_soil_group():
            Retrieves data on sheep soil groups from NFS (National Farm Survey).

        get_fao_fertiliser_data():
            Retrieves FAO (Food and Agricutlure Organisation) data on fertilization.

        get_nir_fertiliser_data():
            Retrieves NIR (National Inventory Report, Ireland) data on fertilization.

        get_dairy_nfs_animals():
            Retrieves data on dairy animal numbers from NFS (National Farm Survey).

        get_cattle_nfs_animals():
            Retrieves data on cattle animal numbers from NFS (National Farm Survey).

        get_sheep_nfs_animals():
            Retrieves data on sheep animal numbers from NFS (National Farm Survey).

        get_livestock_units():
            Retrieves data on livestock units (Teagasc).
    """
    def __init__(self):
        """
        Initializes the DataManager class by setting up the database directory and creating a database engine.
        """
        self.database_dir = get_local_dir()
        self.engine = self.data_engine_creater()

    def data_engine_creater(self):
        """
        Creates and returns a SQLAlchemy engine for the database.

        This method constructs the full path to the database file and then uses SQLAlchemy to create an engine 
        that facilitates database connectivity.

        Returns:
            sqa.engine.base.Engine: An SQLAlchemy engine for database operations.
        """
        database_path = os.path.abspath(
            os.path.join(self.database_dir, "grassland_management_database.db")
        )
        engine_url = f"sqlite:///{database_path}"

        return sqa.create_engine(engine_url)

    def get_cso_grassland_data(self):
        """
        Retrieves data on CSO (Central Statistics Office, Ireland) grassland areas.

        Returns:
            pandas.DataFrame: A DataFrame containing the CSO grassland areas.
        """
        table = "CSO_grassland_areas"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Year"],
        )

        # Scale the values by 1000
        dataframe *= 1000

        return dataframe

    def get_grassland_fertilization_by_system(self):
        """
        Retrieves data on grassland fertilization by system.

        Returns:
            pandas.DataFrame: A DataFrame containing the grassland fertilization by system.
        """
        table = "grassland_fertilization_by_system"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Grasslandtype", "Farmsystem"],
        )

        return dataframe

    def get_dairy_area_nfs(self):
        """
        Retrieves data on dairy areas from NFS (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the dairy areas from NFS (National Farm Survey).
        """
        table = "dairy_nfs_areas"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_beef_area_nfs(self):
        """
        Retrieves data on beef areas from NFS (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the beef areas from NFS (National Farm Survey).
        """
        table = "cattle_nfs_areas"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_sheep_area_nfs(self):
        """
        Retrieves data on sheep areas from NFS (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the sheep areas from NFS (National Farm Survey).
        """
        table = "sheep_nfs_areas"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_nfs_farm_numbers(self):
        """
        Retrieves data on NFS farm numbers (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the NFS farm numbers (National Farm Survey).
        """

        table = "national_farm_survey_system_numbers"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_dairy_soil_group(self):
        """
        Retrieves data on dairy soil groups from NFS (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the dairy soil groups from NFS (National Farm Survey).
        """ 
        table = "dairy_soil_group"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_cattle_soil_group(self):
        """
        Retrieves data on cattle soil groups from NFS (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the cattle soil groups from NFS (National Farm Survey).
        """
        table = "cattle_soil_group"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_sheep_soil_group(self):
        """
        Retrieves data on sheep soil groups from NFS (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the sheep soil groups from NFS (National Farm Survey).
        """
        table = "sheep_soil_group"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_fao_fertiliser_data(self):
        """
        Retrieves FAO (Food and Agricutlure Organisation) data on fertilization.

        Returns:
            pandas.DataFrame: A DataFrame containing the FAO (Food and Agricutlure Organisation) data on fertilization.
        """
        table = "FAO_fertilization"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Year"],
        )

        dataframe *= 1000

        return dataframe
    

    def get_nir_fertiliser_data(self):
        """
        Retrieves NIR (National Inventory Report, Ireland) data on fertilization.

        Returns:
            pandas.DataFrame: A DataFrame containing the NIR (National Inventory Report, Ireland) data on fertilization.
        """
        table = "NIR_fertilization"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        dataframe *= 1000

        return dataframe


    def get_dairy_nfs_animals(self):
        """
        Retrieves data on dairy animal numbers from NFS (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the dairy animal numbers from NFS (National Farm Survey).
        """
        table = "dairy_nfs_animals"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_cattle_nfs_animals(self):
        """
        Retrieves data on cattle animal numbers from NFS (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the cattle animal numbers from NFS (National Farm Survey).
        """
        table = "cattle_nfs_animals"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_sheep_nfs_animals(self):
        """
        Retrieves data on sheep animal numbers from NFS (National Farm Survey).

        Returns:
            pandas.DataFrame: A DataFrame containing the sheep animal numbers from NFS (National Farm Survey).
        """ 
        table = "sheep_nfs_animals"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe
    
    def get_livestock_units(self):
        """
        Retrieves data on livestock units (Teagasc).

        Returns:    
            pandas.DataFrame: A DataFrame containing the livestock units (Teagasc).
        """
        table = "livestock_units"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
        )

        return dataframe