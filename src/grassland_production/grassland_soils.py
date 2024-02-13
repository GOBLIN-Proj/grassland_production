"""
========================
Grassland Soils Module
========================
This module contains the SoilGroups class, which is responsible for managing and analyzing
soil group data related to various cohorts. It focuses on categorizing and 
distributing soil types among different livestock categories like dairy, beef, and sheep.
The module utilizes several components from the grassland_production package to 
compute and provide detailed insights into soil group distributions for grassland management.

Classes:
    SoilGroups: Manages soil group data.

"""

import pandas as pd
from resource_manager.data_loader import Loader
from resource_manager.grassland_data_manager import DataManager
from grassland_production.spared_area import Grasslands
import itertools

class SoilGroups:
    """
    A class to manage and analyze soil group data for different grassland cohorts.

    The SoilGroups class integrates data from various sources to provide a comprehensive
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
        data_manager_class (DataManager): Manages and processes grassland data.
        calibration_year (int): Year of data calibration.
        target_year (int): Target year for data analysis.
        default_calibration_year (int): Default year used for calibration in case of data discrepancies.
        loader_class (Loader): Class for loading necessary data.
        scenario_animals_df (DataFrame): Dataframe containing animal data for different scenarios.
        baseline_animals_df (DataFrame): Dataframe containing baseline animal data.
        dairy_soil_distribution (DataFrame): Soil distribution data for dairy grasslands.
        beef_soil_distribution (DataFrame): Soil distribution data for beef grasslands.
        sheep_soil_distribution (DataFrame): Soil distribution data for sheep grasslands.
        grassland_class (Grasslands): Class for managing grassland data.

    Methods:
        get_cohort_soil_groups(): Computes and returns the soil group distribution for spared (destocked) areas.
    """
    def __init__(self, ef_country, calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df):

        self.data_manager_class = DataManager(calibration_year, target_year, scenario_animals_df,baseline_animals_df)
        self.calibration_year = self.data_manager_class.calibration_year
        self.target_year = self.data_manager_class.target_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.loader_class = Loader()
        self.scenario_animals_df = scenario_animals_df
        self.baseline_animals_df = baseline_animals_df
        self.dairy_soil_distribution = self.loader_class.dairy_soil_group()
        self.beef_soil_distribution = self.loader_class.cattle_soil_group()
        self.sheep_soil_distribution = self.loader_class.sheep_soil_group()
        self.grassland_class = Grasslands(ef_country, self.calibration_year, target_year, scenario_data, scenario_animals_df, baseline_animals_df)



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
        spared_area_cohorts = self.grassland_class.get_cohort_spared_area()

        soil_distribution = {
            "dairy": self.dairy_soil_distribution,
            "beef": self.beef_soil_distribution,
            "sheep": self.sheep_soil_distribution,
        }

        groups = ("1", "2", "3")
        cohorts = soil_distribution.keys()
        scenarios = spared_area_cohorts.keys()


        data = []

        for sc, sg, cohort in itertools.product(scenarios, groups, cohorts):
            try:
                area_multiplier = soil_distribution[cohort].loc[self.calibration_year, sg].item()
            except KeyError:
                print(f"KeyError encountered for {cohort} in year {self.calibration_year}. Using default calibration year {self.default_calibration_year} instead.")
                area_multiplier = soil_distribution[cohort].loc[self.default_calibration_year, sg].item()

            row_data = {
                "Scenario": sc,
                "year": self.target_year,
                "cohort": cohort,
                "soil_group": sg,
                "area_ha": spared_area_cohorts[sc][cohort] * area_multiplier,
            }
            data.append(row_data)
        
        cohort_soil_groups = pd.DataFrame(data)

        return cohort_soil_groups

