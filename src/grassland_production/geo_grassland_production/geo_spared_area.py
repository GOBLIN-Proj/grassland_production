"""
======================
Geo Spared Area Module
======================

This module contains the GeoGrasslands class, which is designed to manage and process 
data related to grassland areas, specifically focusing on calculating the total 
grassland area and spared area under various scenarios. It utilizes classes from 
the grassland_production package for detailed analysis and computations.

Classes:
    GeoGrasslands: Manages and computes grassland and spared area data.
"""

import pandas as pd
from grassland_production.geo_grassland_production.geo_grass_yield import GeoYield
from grassland_production.geo_grassland_production.geo_dry_matter import GeoDryMatter
from grassland_production.geo_grassland_production.geo_utilisation_rate import GeoUtilisationRate
from grassland_production.spared_area import Grasslands

class GeoGrasslands:
    """
    A class to manage and compute catchment grassland and spared area data under various scenarios.

    This class integrates data from various sources to assess the total area of grasslands 
    and the spared area (destocked grassland) for different scenarios.

    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.

    Attributes:
        sc_class (ScenarioDataFetcher): Fetches scenario data.
        scenario_list (list): List of scenarios.
        data_manager_class (DataManager): Manages and processes grassland data.
        calibration_year (int): Year of data calibration.
        target_year (int): Target year for data analysis.
        default_calibration_year (int): Default year used for calibration in case of data discrepancies.
        loader_class (Loader): Class for loading necessary data.
        yield_class (Yield): Class for managing grassland yield data.
        areas_class (Areas): Class for managing grassland area data.
        dm_class (DryMatter): Class for managing dry matter data.
        farm_based_UR (GeoUtilisationRate): Class for calculating utilisation rates.

    Methods:
        get_grass_total_area(): Computes and returns the total grassland area.
        get_non_grass_total_area(): Computes and returns the total non-grassland (spared) area.
        get_cohort_spared_area(): Computes spared area distributed across different cohorts.
        get_cohort_grassland_area(): Computes grassland area distributed across different cohorts.
    """
    def __init__(
        self,
        ef_country,
        calibration_year,
        target_year,
        scenario_data,
        scenario_animals_df,
        baseline_animals_df,
    ):
        
        yield_class = GeoYield(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )

        dm_class = GeoDryMatter(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )

        farm_based_UR = GeoUtilisationRate(ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,)
        
        self.grassland_class = Grasslands(ef_country,
                                          calibration_year,
                                          target_year,
                                          scenario_data,
                                          scenario_animals_df,
                                          baseline_animals_df,
                                          yield_class = yield_class,
                                          dry_matter_class = dm_class,
                                          utilisation_class = farm_based_UR)

    def get_grass_total_area(self):
        """
        Calculates and returns the total grassland area for each scenario and system over specified years.

        This method computes the total area of grasslands required to meet the dry matter requirements
        for dairy, beef and sheep. It uses a weighted average yield of different grassland types within each 
        system to determine the necessary area. The weights are based on the proportions of each 
        grassland type in the system.

        The total area is calculated by dividing the dry matter requirement for each system by the 
        weighted average yield and then by the system's utilization rate. The process is repeated 
        for each scenario and system for the given years, and the results are aggregated into a single 
        DataFrame.

        The calculation considers two specific years - the calibration year and the target year, and 
        operates across all defined scenarios.

        Returns:
            DataFrame: A DataFrame with rows representing the years and columns representing each scenario. 
                    Each cell contains the total grassland area required for that scenario and year.
        """
        return self.grassland_class.get_grass_total_area()


    def get_non_grass_total_area(self):
        """
        Calculates and returns a DataFrame representing the spared (destocked) area for various scenarios.

        The spared area is defined as the difference in grassland area between the calibration year 
        and the target year. For each scenario, if the year is not the target year, the spared area 
        is assumed to be zero. If the year is the target year, the spared area is calculated as the 
        difference between the grassland area in the calibration year and the grassland area in the 
        target year.

        This method first computes the total grassland area for each scenario and then uses this data
        to determine the spared area.

        Returns:
            DataFrame: A DataFrame with rows representing the years (calibration year and target year) 
                    and columns representing each scenario. Each cell contains the spared area for 
                    that scenario and year.
        """
        return self.grassland_class.get_non_grass_total_area()


    def get_cohort_spared_area(self):
        """
        Calculates and returns the spared area distributed across different cohorts for each scenario.

        This method determines the spared area (destocked grassland) for each cohort in each scenario.
        It utilizes the weighted dry matter (DM) reduction contributions calculated by the DryMatter class 
        (self.dm_class) to apportion the total spared area among different cohorts. The spared area for 
        each scenario is obtained using the get_non_grass_total_area method.

        The calculation multiplies the total spared area for each scenario by the weighted DM reduction 
        contribution for each cohort within that scenario. This approach provides a detailed view of how 
        spared area origins are distributed among different cohorts.

        Returns:
            dict: A dictionary where each key is a scenario and its value is another dictionary. 
                The nested dictionary has cohorts as keys and their respective spared areas as values.
        """
        return self.grassland_class.get_cohort_spared_area()
    

    def get_cohort_grassland_area(self):
        """
        Calculates and returns the grassland area for each cohort within each scenario.

        This method assesses the grassland area distribution among various cohorts for each scenario. 
        It uses the actual dry matter (DM) weights, as calculated by the DryMatter class, to determine 
        the proportion of grassland area allocated to each cohort. The total grassland area for each 
        scenario is obtained using the get_grass_total_area method.

        The calculation involves multiplying the total grassland area for each scenario by the 
        DM weights for each cohort. This provides a detailed breakdown of grassland area distribution, 
        which is essential for understanding the allocation of grassland resources among different 
        cohorts in various scenarios.

        Returns:
            dict: A nested dictionary where the outer keys are scenarios, the inner keys are cohorts, 
                and the values are dictionaries with years as keys and their respective grassland areas as values.
        """
        return self.grassland_class.get_cohort_grassland_area()
    
