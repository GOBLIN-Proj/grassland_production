"""
====================
Spared Area Module
====================

This module contains the Grasslands class, which is designed to manage and process 
data related to grassland areas, specifically focusing on calculating the total 
grassland area and spared area under various scenarios. It utilizes classes from 
the grassland_production package for detailed analysis and computations.

Classes:
    Grasslands: Manages and computes grassland and spared area data.
"""
import pandas as pd
from grassland_production.resource_manager.data_loader import Loader
from grassland_production.resource_manager.grassland_data_manager import DataManager
from grassland_production.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from grassland_production.grass_yield import Yield
from grassland_production.dry_matter import DryMatter
from grassland_production.grassland_area import Areas
from grassland_production.utilisation_rate import UtilisationRate

class Grasslands:
    """
    A class to manage and compute grassland and spared area data under various scenarios.

    This class integrates data from various sources to assess the total area of grasslands 
    and the spared area (destocked grassland) for different scenarios.

    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.
        yield_class (Yield, optional): An instance of the Yield class. If not provided, a new instance is created with default parameters.
        dry_matter_class (DryMatter, optional): An instance of the DryMatter class. If not provided, a new instance is created with default parameters.
        utilisation_class (UtilisationRate, optional): An instance of the UtilisationRate class. If not provided, a new instance is created with default parameters.

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
        farm_based_UR (UtilisationRate): Class for calculating utilisation rates.

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
        yield_class = None,
        dry_matter_class = None,
        utilisation_class = None
    ):
        self.sc_class = ScenarioDataFetcher(scenario_data)
        self.scenario_list = self.sc_class.get_scenario_list()

        self.data_manager_class = DataManager(
            calibration_year,
            target_year,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.calibration_year = self.data_manager_class.get_calibration_year()
        self.target_year = self.data_manager_class.get_target_year()
        self.default_calibration_year = self.data_manager_class.get_default_calibration_year()  
        self.loader_class = Loader()

        if yield_class is None:
            self.yield_class = Yield(
                ef_country,
                calibration_year,
                target_year,
                scenario_data,
                scenario_animals_df,
                baseline_animals_df,
            )
        else:
            self.yield_class = yield_class 

        self.areas_class = Areas(
            self.target_year, self.calibration_year, self.default_calibration_year
        )

        if dry_matter_class is None:
            self.dm_class = DryMatter(
                ef_country,
                self.calibration_year,
                target_year,
                scenario_data,
                scenario_animals_df,
                baseline_animals_df,
            )
        else:
            self.dm_class = dry_matter_class

        if utilisation_class is None:
            self.farm_based_UR = UtilisationRate(ef_country,
                self.calibration_year,
                target_year,
                scenario_data,
                scenario_animals_df,
                baseline_animals_df,)
        else:
            self.farm_based_UR = utilisation_class

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

        # grass drymatter requirement for cattle and sheep, is dictionary
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.scenario_list

        keys = self.data_manager_class.get_farming_systems()

        transposed_yield_per_ha = self.yield_class.get_yield()


        dry_matter_req = self.dm_class.actual_dry_matter_required()

        farm_based_UR = self.farm_based_UR.get_farm_based_utilisation_rate()

        nfs_within_grassland_proportions = (
            self.areas_class.get_nfs_within_system_grassland_distribution()
        )

        grass_total_area = pd.DataFrame(0.0, index=year_list, columns=scenario_list)

        average_yield = 0

        for sc in scenario_list:
            for sys in keys:
                for year in year_list:
                    for grassland_type in transposed_yield_per_ha[sc][sys].columns:
                        if year != self.target_year:
                            average_yield += (
                                transposed_yield_per_ha[sc][sys].loc[
                                    year, grassland_type
                                ]
                                * nfs_within_grassland_proportions[sys].loc[
                                    year, grassland_type
                                ]
                            )
                        else:
                            average_yield += (
                                transposed_yield_per_ha[sc][sys].loc[
                                    self.target_year,
                                    grassland_type,
                                ]
                                * nfs_within_grassland_proportions[sys].loc[
                                    self.calibration_year,
                                    grassland_type,
                                ]
                            )

                    grass_total_area.loc[year, sc] += (
                        dry_matter_req[sc][sys].loc[year]
                        / average_yield
                        / farm_based_UR[sc][sys].loc[year]
                    )

                    average_yield = 0

        return grass_total_area


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
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.scenario_list

        spared_area = pd.DataFrame(0.0, index=year_list, columns=scenario_list)

        grass_total_area = self.get_grass_total_area()

        for sc in scenario_list:
            spared_area.loc[self.target_year, sc] = (
                grass_total_area.loc[self.calibration_year, sc]
                - grass_total_area.loc[self.target_year, sc]
            )

        return spared_area


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
        cohort_weights = self.dm_class.weighted_dm_reduction_contribution()

        spared_area = self.get_non_grass_total_area()

        cohort_spared_area = {}

        for sc in cohort_weights.keys():
            cohort_spared_area[sc] = {}
            for cohort in cohort_weights[sc].keys():
                if cohort != "total":
                    
                    cohort_spared_area[sc][cohort] = spared_area.loc[self.target_year, sc].item() * cohort_weights[sc][cohort]

        return cohort_spared_area
    

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
        cohort_weights = self.dm_class.get_actual_dm_weights()

        grass_area = self.get_grass_total_area()

        cohort_spared_area = {}

        for sc in cohort_weights.keys():
            cohort_spared_area[sc] = {}
            for cohort in cohort_weights[sc].keys():
                cohort_spared_area[sc][cohort] = {}
                for year in cohort_weights[sc][cohort].keys():
                    cohort_spared_area[sc][cohort][year] = grass_area.loc[year, sc].item() * cohort_weights[sc][cohort][year]

        return cohort_spared_area
    
