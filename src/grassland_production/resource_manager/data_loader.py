"""
===================
Data Loader Module
===================

The Data Loader module provides a set of classes and methods to facilitate the retrieval of various agricultural data.
The data is retrieved from a DataManager instance which manages the underlying database connections and queries.

Classes:
    Loader: Provides methods to retrieve data from a DataManager instance.
"""
from grassland_production.resource_manager.database_manager import DataManager


class Loader:
    """
    The Loader class is designed to facilitate the retrieval of various agricultural data
    related to grassland and livestock management from a DataManager instance. 
    This class primarily focuses on providing easy access to different sets of data 
    related to grassland fertilization, livestock areas, soil groups, and livestock numbers.

    Attributes:
        dataframes (DataManager): An instance of DataManager which manages the underlying
                                  database connections and queries.

    Methods:
        grassland_fertilization_by_system():
            Retrieves data on grassland fertilization by system.

        cso_grassland_areas():
            Retrieves data on CSO (Central Statistics Office, Ireland) grassland areas.

        cso_grassland_area_percent():
            Retrieves data on CSO (Central Statistics Office, Ireland) grassland areas as a percentage of total area (Hay, Silage, and Pasture).

        dairy_area_nfs():
            Retrieves data on dairy areas from NFS (National Farm Survey).

        beef_area_nfs():
            Retrieves data on beef areas from NFS (National Farm Survey).

        sheep_area_nfs():
            Retrieves data on sheep areas from NFS (National Farm Survey).

        nfs_farm_numbers():
            Retrieves data on NFS (National Farm Survey) farm numbers.

        dairy_soil_group():
            Retrieves data on dairy soil groups.

        cattle_soil_group():
            Retrieves data on cattle soil groups.

        sheep_soil_group():
            Retrieves data on sheep soil groups.

        fao_fertilization():
            Retrieves FAO (Food and Agriculture Organisation of the United Nations) data on fertilization.

        nir_fertilization():
            Retrieves NIR (Ireland's National Inventory Report) data on fertilization.

        dairy_nfs_animals():
            Retrieves data on dairy animals from NFS (National Farm Survey).

        cattle_nfs_animals():
            Retrieves data on cattle animals from NFS (National Farm Survey).

        sheep_nfs_animals():
            Retrieves data on sheep animals from NFS (National Farm Survey).

        livestock_units():
            Retrieves data on livestock units (Teagasc).
    """
    def __init__(self):
        self.dataframes = DataManager()


    def grassland_fertilization_by_system(self):
        """
        Retrieves data on grassland fertilization application rates segmented by various systems and 
        grassland types.

        This method accesses the DataManager's 'get_grassland_fertilization_by_system' 
        function to fetch data related to the application of fertilizers in different 
        grassland management systems.

        Returns:
            DataFrame: A pandas DataFrame containing detailed information about 
                    grassland fertilization rates segmented by system and grassland type.

        """
        return self.dataframes.get_grassland_fertilization_by_system()


    def cso_grassland_areas(self):
        """
        Retrieves data on grassland areas from the Central Statistics Office (CSO) in Ireland.

        This method provides access to detailed statistical information about grassland areas 
        reported by the CSO. The data is segmented by grassland type.

        Returns:
            DataFrame: A pandas DataFrame with CSO grassland areas by type and year.

        """
        return self.dataframes.get_cso_grassland_data()
    

    def cso_grassland_area_percent(self):
        """
        Retrieves data on grassland areas as a percentage of total area (Hay, Grass silage, Pasture) from the Central Statistics Office (CSO) in Ireland.

        This method provides access to detailed statistical information about grassland areas 
        reported by the CSO. The data is segmented by grassland type.

        Returns:
            DataFrame: A pandas DataFrame with CSO grassland areas as a percentage of total area by type and year.

        """
        return self.dataframes.get_cso_grassland_data_as_percent()

    def dairy_area_nfs(self):
        """
        Retrieves data on dairy farming areas from the National Farm Survey (NFS).

        This method accesses NFS data focusing on areas used for dairy farming. It provides insights into 
        the size of dairy farms. The data is segmented by grassland type.

        Returns:
            DataFrame: A pandas DataFrame containing NFS data on dairy farming areas by type and year.

        """
        return self.dataframes.get_dairy_area_nfs()


    def beef_area_nfs(self):
        """
        Retrieves data on beef farming areas from the National Farm Survey (NFS).

        This method accesses NFS data focusing on areas used for beef farming. It provides insights into 
        the size of beef farms. The data is segmented by grassland type.

        Returns:
            DataFrame: A pandas DataFrame containing NFS data on beef farming areas by type and year.

        """
        return self.dataframes.get_beef_area_nfs()


    def sheep_area_nfs(self):
        """
        Retrieves data on sheep farming areas from the National Farm Survey (NFS).

        This method accesses NFS data focusing on areas used for sheep farming. It provides insights into 
        the size of sheep farms. The data is segmented by grassland type.

        Returns:
            DataFrame: A pandas DataFrame containing NFS data on sheep farming areas by type and year.

        """
        return self.dataframes.get_sheep_area_nfs()


    def nfs_farm_numbers(self):
        """
        Retrieves data on the number of farms reported in the National Farm Survey (NFS).

        This method provides aggregate data on the number of farms surveyed by the NFS and is 
        segmented by system (dairy, beef, sheep) and year.

        Returns:
            DataFrame: A pandas DataFrame containing data on the number of farms per system by year.

        """
        return self.dataframes.get_nfs_farm_numbers()


    def dairy_soil_group(self):
        """
        Retrieves data on dairy farming soil group areas from the National Farm Survey (NFS).

        This method accesses NFS data focusing on areas used for dairy farming. It provides insights into 
        the size of dairy farms. The data is segmented by soil group and year.

        Returns:
            DataFrame: A pandas DataFrame containing NFS data on dairy farming areas by type and year.

        """
        return self.dataframes.get_dairy_soil_group()


    def cattle_soil_group(self):
        """
        Retrieves data on beef farming soil group areas from the National Farm Survey (NFS).

        This method accesses NFS data focusing on areas used for beef farming. It provides insights into 
        the size of beef farms. The data is segmented by soil group and year.

        Returns:
            DataFrame: A pandas DataFrame containing NFS data on beef farming areas by type and year.

        """
        return self.dataframes.get_cattle_soil_group()


    def sheep_soil_group(self):
        """
        Retrieves data on sheep farming soil group areas from the National Farm Survey (NFS).

        This method accesses NFS data focusing on areas used for sheep farming. It provides insights into 
        the size of sheep farms. The data is segmented by soil group and year.

        Returns:
            DataFrame: A pandas DataFrame containing NFS data on sheep farming areas by type and year.

        """
        return self.dataframes.get_sheep_soil_group()


    def fao_fertilization(self):
        """
        Retrieves FAO (Food and Agriculture Organisation of the United Nations) data on fertilization.

        This method provides access to FAO data on fertilization rates segmented by type (phosphorus, potassium) and year.

        Returns:
            DataFrame: A pandas DataFrame containing FAO data on fertilization by type and year.
        """
        return self.dataframes.get_fao_fertiliser_data()
    

    def nir_fertilization(self):
        """
        Retrieves NIR (Ireland's National Inventory Report) data on fertilization.

        This method provides access to NIR data on fertilization rates segmented by type (ammonium nitrate and urea) and year.

        Returns:
            DataFrame: A pandas DataFrame containing NIR data on fertilization by type and year.
        """
        return self.dataframes.get_nir_fertiliser_data()


    def dairy_nfs_animals(self):
        """
        Retrieves data on dairy animals numbers from NFS (National Farm Survey).

        This method provides access to NFS data on dairy animals numbers segmented by cohort and year.

        Returns:
            DataFrame: A pandas DataFrame containing NFS data on dairy animals numbers by cohort and year.
        """
        return self.dataframes.get_dairy_nfs_animals()


    def cattle_nfs_animals(self):
        """
        Retrieves data on cattle animals numbers from NFS (National Farm Survey).

        This method provides access to NFS data on cattle animals numbers segmented by cohort and year.

        Returns:
            DataFrame: A pandas DataFrame containing NFS data on cattle animals numbers by cohort and year.
        """
        return self.dataframes.get_cattle_nfs_animals()


    def sheep_nfs_animals(self):
        """
        Retrieves data on sheep animals numbers from NFS (National Farm Survey).

        This method provides access to NFS data on sheep animals numbers segmented by cohort and year.

        Returns:
            DataFrame: A pandas DataFrame containing NFS data on sheep animals numbers by cohort and year.
        """
        return self.dataframes.get_sheep_nfs_animals()
    

    def livestock_units(self):
        """
        Retrieves data on livestock units (Teagasc).

        This method provides access to Teagasc data on livestock units coefs segmented by cohort and year.

        Returns:
            DataFrame: A pandas DataFrame containing Teagasc data on livestock units coefs by cohort and year.
        """
        return self.dataframes.get_livestock_units()
    
    
    def lime_fertiliser_proportion_by_system(self):
        """
        Retrieves data on lime fertilization use segmented by proportion of various systems
        applying lime.

        Returns:
            DataFrame: A pandas DataFrame containing detailed information about 
                    lime fertilization segmented by system and grassland type.

        """
        return self.dataframes.get_lime_fertilisation_by_system()