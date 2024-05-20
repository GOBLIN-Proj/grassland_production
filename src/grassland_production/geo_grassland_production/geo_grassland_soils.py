"""
=========================
GeoGrassland Soils Module
=========================
This module contains the GeoSoilGroups class, which is responsible for managing and analyzing
soil group data related to various cohorts. It focuses on categorizing and 
distributing soil types among different livestock categories like dairy, beef, and sheep.
The module utilizes several components from the grassland_production package to 
compute and provide detailed insights into soil group distributions for grassland management.

Classes:
    GeoSoilGroups: Manages soil group data.

"""
from grassland_production.geo_grassland_production.geo_spared_area import GeoGrasslands
from grassland_production.grassland_soils import SoilGroups

class GeoSoilGroups:
    """
    A class to manage and analyze soil group data for different grassland cohorts.

    The GeoSoilGroups class integrates data from various sources to provide a comprehensive
    overview of soil group distribution across different types of livestock systems, such as
    dairy, beef, and sheep. It plays a crucial role in understanding and managing 
    soil-related aspects in grassland areas.
    
    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.

    Attributes:
        soil_groups (SoilGroups): An instance of the SoilGroups class.

    Methods:
        get_cohort_soil_groups(): Computes and returns the soil group distribution for spared (destocked) areas.
    """
    def __init__(self, 
                 ef_country, 
                 calibration_year, 
                 target_year, 
                 scenario_data, 
                 scenario_animals_df,
                 baseline_animals_df):

        grassland_class = GeoGrasslands(ef_country,
                                     calibration_year,
                                     target_year,
                                     scenario_data,
                                     scenario_animals_df, 
                                     baseline_animals_df)
        
        self.soil_groups = SoilGroups(ef_country,
                                     calibration_year,
                                     target_year,
                                     scenario_data,
                                     scenario_animals_df,
                                     baseline_animals_df,
                                     grassland_class=grassland_class)
        



    def get_cohort_soil_groups(self):
        """
        Computes and returns a detailed breakdown of soil groups across different livestock cohorts for spared areas.

        This method analyzes soil distribution among various cohorts (such as dairy, beef, 
        and sheep) and their respective spared (destocked) areas. It calculates the area for each soil group 
        within each cohort by applying area multipliers based on the calibration year data. 
        In cases where data for the specified calibration year is not available, it defaults to 
        using data from a predefined default calibration year.

        The method iterates over all combinations of scenarios, soil groups, and cohorts to 
        compile a comprehensive dataset representing the distribution of soil groups within destocked (spared) areas.

        Returns:
            DataFrame: A dataframe containing columns for scenario, year, cohort, soil group, 
                    and calculated area in hectares (ha). This dataframe provides a detailed 
                    view of how different soil groups are distributed within spared areas based on livstock cohorts.
        """
        return self.soil_groups.get_cohort_soil_groups()

