"""
======================
Livestock Unit Module
======================

This module contains the StockingRate class, which is dedicated to calculating and managing 
the livestock units and stocking rates for various farm types and scenarios. This class is 
part of the grassland_production package and utilizes other components within the package 
to analyze and compute essential data related to livestock management.

Classes:
    StockingRate: Manages livestock units and stocking rates.
"""

import pandas as pd
import itertools
from resource_manager.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.spared_area import Grasslands


class StockingRate:
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
        data_manager_class (DataManager): Manages and processes grassland and livestock data.
        calibration_year (int): Year of data calibration.
        target_year (int): Target year for data analysis.
        default_calibration_year (int): Default year used for calibration in case of data discrepancies.
        loader_class (Loader): Class for loading necessary data.
        livestock_unit_values (DataFrame): Dataframe containing livestock unit values for different animal types.
        grassland_class (Grasslands): Class for managing grassland data.

    Methods:
        get_livestock_units_past(): Calculates livestock units for past scenarios based on baseline data.
        get_livestock_units_future(): Calculates livestock units for future scenarios.
        get_livestock_units(): Aggregates livestock units for past and future scenarios.
        get_stocking_rate(): Computes stocking rates for different farm types and scenarios.
    """
    def __init__(self,ef_country, calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df):
        self.data_manager_class = DataManager(calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df)
        self.calibration_year = self.data_manager_class.calibration_year
        self.target_year = self.data_manager_class.target_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.loader_class = Loader()
        self.livestock_unit_values = self.loader_class.livestock_units()
        self.grassland_class = Grasslands(ef_country, calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df)


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
        baseline_animals_df = self.data_manager_class.baseline_animals_df

        keys = self.data_manager_class.systems
        COHORTS = self.data_manager_class.COHORTS_GROUPS

        animal_list = self.data_manager_class.baseline_animals_dict[self.calibration_year]["animals"]

        past_livestock_units = pd.DataFrame(0.0, index=[self.calibration_year], columns=keys)

        # Process dairy and beef
        for cohort in ["dairy", "beef"]:
            for animal_name in COHORTS[cohort]:
                if animal_name in animal_list.__dict__.keys():

                    mask_validation = (baseline_animals_df["year"] == self.calibration_year) & (
                        baseline_animals_df["cohort"] == animal_name) & (baseline_animals_df["mm_storage"] == "tank liquid") & (baseline_animals_df["pop"] > 0)
                    
                    if mask_validation.any():
                        past_livestock_units.loc[self.calibration_year, cohort] += (baseline_animals_df.loc[mask_validation, "pop"].item() * self.livestock_unit_values.loc[:,animal_name].item())
        
        for landtype in COHORTS["sheep"].keys():
            for animal_name in COHORTS["sheep"][landtype]:
                if animal_name in animal_list.__dict__.keys():
                    sheep_mask_validation = (
                        (baseline_animals_df["year"] == self.calibration_year)
                        & (baseline_animals_df["cohort"] == animal_name)
                        & (baseline_animals_df["grazing"] == landtype)
                        & (baseline_animals_df["mm_storage"] == "solid")
                        & (baseline_animals_df["pop"] > 0)
                    )
                    if sheep_mask_validation.any():
                        past_livestock_units.loc[self.calibration_year, "sheep"] += (baseline_animals_df.loc[sheep_mask_validation, "pop"].item() * self.livestock_unit_values.loc[:,animal_name].item())

        return past_livestock_units
    
    
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
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        scenario_animals_df = self.data_manager_class.scenario_animals_df

        keys = self.data_manager_class.systems
        COHORTS = self.data_manager_class.COHORTS_GROUPS

        animal_list = self.data_manager_class.scenario_animals_dict

        livestock_units = {}

        for sc in scenario_list:
            total_livestock_units = pd.DataFrame(0.0, index=[self.target_year], columns=keys)
            livestock_units[sc] = total_livestock_units

            farm_mask = self.data_manager_class.scenario_aggregation["Scenarios"] == sc
            farm_ids = self.data_manager_class.scenario_aggregation.loc[farm_mask, "farm_id"].unique()

            for farm_id in farm_ids:
                # Process dairy and beef
                for cohort in ["dairy", "beef"]:
                    for animal_name in COHORTS[cohort]:
                        if animal_name in animal_list[farm_id]["animals"].__dict__.keys():
                            mask = (scenario_animals_df["farm_id"] == farm_id) & (scenario_animals_df["cohort"] == animal_name) & (scenario_animals_df["mm_storage"] == "tank liquid") & (scenario_animals_df["pop"] > 0)
                            if mask.any():
                                livestock_units[sc].loc[self.target_year, cohort] += (scenario_animals_df.loc[mask, "pop"].item() * self.livestock_unit_values.loc[:, animal_name].item())

                # Process sheep
                for landtype in COHORTS["sheep"].keys():
                    for animal_name in COHORTS["sheep"][landtype]:
                        if animal_name in animal_list[farm_id]["animals"].__dict__.keys():

                            sheep_mask = (
                                (scenario_animals_df["farm_id"] == farm_id)
                                & (scenario_animals_df["cohort"] == animal_name)
                                & (scenario_animals_df["grazing"] == landtype)
                                & (scenario_animals_df["mm_storage"] == "solid")
                                & (scenario_animals_df["pop"] > 0)
                            )
                            if sheep_mask.any():                               
                                livestock_units[sc].loc[self.target_year, "sheep"] += (scenario_animals_df.loc[sheep_mask, "pop"].item() * self.livestock_unit_values.loc[:,animal_name].item())

        return livestock_units
    

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
        past_stock = self.get_livestock_units_past()
        future_stock = self.get_livestock_units_future()

        for sc in future_stock.keys():
            future_stock[sc].loc[self.calibration_year] = past_stock.loc[self.calibration_year]

        return future_stock


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
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        keys = self.data_manager_class.systems

        livestock_units = self.get_livestock_units()

        areas = self.grassland_class.get_cohort_grassland_area()

        stocking_rate = {}

        for sc in scenario_list:
            stocking_rate_df = pd.DataFrame(0.0, index=year_list, columns=keys)
            for sys, year in itertools.product(keys, year_list):
                try:
                    area = areas[sc][sys][year]
                    livestock_units_item = livestock_units[sc].loc[year, sys].item()
                    
                    # Check if area is zero or NaN
                    if area == 0 or pd.isna(area) or pd.isna(livestock_units_item):
                        stocking_rate_df.loc[year, sys] = 0.0
                    else:
                        stocking_rate_df.loc[year, sys] = livestock_units_item / area
                except Exception as e:  # Catching a more general exception
                    print(f"Error encountered: {e}")
                    stocking_rate_df.loc[year, sys] = 0.0

            
            stocking_rate[sc]=stocking_rate_df

        return stocking_rate