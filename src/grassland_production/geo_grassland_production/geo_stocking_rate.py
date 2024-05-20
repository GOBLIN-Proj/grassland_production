"""
======================
Livestock Unit Module
======================

This module contains the GeoStockingRate class, which is dedicated to calculating and managing 
the livestock units and stocking rates for various farm types and scenarios. This class is 
part of the grassland_production package and utilizes other components within the package 
to analyze and compute essential data related to livestock management.

Classes:
    GeoStockingRate: Manages livestock units and stocking rates.
"""
from grassland_production.geo_grassland_production.geo_spared_area import GeoGrasslands
from grassland_production.stocking_rate import StockingRate


class GeoStockingRate:
    """
    A class to manage and compute livestock units and stocking rates for various farm types and scenarios.

    The StockingRate class calculates the number of livestock units for different farm types 
    (e.g., dairy, beef, sheep) and determines the stocking rate for each farm type based on the total 
    grassland area and respective livestock units.

    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.
        
    Attributes:
        stocking_rate_class (StockingRate): An instance of the StockingRate class

    Methods:
        get_livestock_units_past(): Calculates livestock units for past scenarios based on baseline data.
        get_livestock_units_future(): Calculates livestock units for future scenarios.
        get_livestock_units(): Aggregates livestock units for past and future scenarios.
        get_stocking_rate(): Computes stocking rates for different farm types and scenarios.
    """
    def __init__(self,ef_country, calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df):

        grassland_class = GeoGrasslands(ef_country, 
                                     calibration_year, 
                                     target_year, 
                                     scenario_data, 
                                     scenario_animals_df,
                                     baseline_animals_df)
        
        self.stocking_rate_class = StockingRate(ef_country, 
                                     calibration_year, 
                                     target_year, 
                                     scenario_data, 
                                     scenario_animals_df,
                                     baseline_animals_df,
                                     grassland_class=grassland_class)
        


    def get_livestock_units_past(self):
        """
        Calculates and returns the livestock units for the baseline scenario for each farm type.

        This method processes the baseline data to compute the livestock units present on dairy, beef, 
        and sheep farm types for the calibration year. It takes into account the different types of animals 
        within each cohort and their respective populations to calculate the total livestock units. The 
        livestock unit values for each animal type are obtained from the Loader class.

        For each animal cohort (dairy, beef, and sheep), the method iterates over the respective animal 
        types, applying the necessary filters to the baseline data and using the livestock unit values to 
        compute the total livestock units for each farm type.

        Returns:
            DataFrame: A DataFrame with the calibration year as the index and the farm types (dairy, beef, sheep) 
                    as columns. Each cell contains the total livestock units for that farm type in the calibration year.
        """
        return self.stocking_rate_class.get_livestock_units_past()
    
    
    def get_livestock_units_future(self):
        """
        Calculates and returns the livestock units for future scenarios for each farm type.

        This method processes scenario-specific data to compute the livestock units for dairy, beef, 
        and sheep farm types for the target year. It considers the animal populations in each farm type 
        within each scenario and calculates the total livestock units using the livestock unit values 
        for each animal type.

        The method iterates through each scenario and farm type, applying appropriate filters to the 
        scenario data. It accumulates the livestock units for each type of animal in the dairy, beef, 
        and sheep cohorts.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. Each DataFrame 
                has the target year as the index and farm types (dairy, beef, sheep) as columns. 
                Each cell contains the total livestock units for that farm type in the target year.
        """
        return self.stocking_rate_class.get_livestock_units_future()
    

    def get_livestock_units(self):
        """
        Aggregates and returns livestock unit data for both past (baseline) and future scenarios.

        This method combines the livestock unit data from past (baseline) scenarios calculated using
        the get_livestock_units_past method and future scenarios calculated using the 
        get_livestock_units_future method. It ensures that the livestock units for the calibration 
        year from the past data are included in the future scenarios data, providing a complete 
        picture of the livestock units across all scenarios and both time periods.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. Each DataFrame 
                has both the calibration year and the target year as the index and farm types (dairy, beef, sheep) 
                as columns. Each cell contains the total livestock units for that farm type in the respective year.
        """
        return self.stocking_rate_class.get_livestock_units()


    def get_stocking_rate(self):
        """
        Calculates and returns the stocking rates per ha for different farm types across various scenarios.

        This method computes the stocking rate for each farm type (dairy, beef, and sheep) in each scenario, 
        for both the calibration year and the target year. The stocking rate is determined by dividing 
        the number of livestock units by the total grassland area for each farm system. The livestock units 
        are obtained using the get_livestock_units method, and the grassland areas are derived from the 
        get_cohort_grassland_area method of the Grasslands class.

        The method iterates over each scenario and farm type, calculating the stocking rate for each combination. 
        The resulting stocking rates provide insights into the density of livestock per unit area of grassland.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. Each DataFrame 
                has years as the index and farm types (dairy, beef, sheep) as columns. Each cell contains 
                the stocking rate for that farm type in the respective year and scenario.
        """
        return self.stocking_rate_class.get_stocking_rate()