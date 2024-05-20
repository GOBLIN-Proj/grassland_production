"""
========================
Utilisation Rate Module
========================
This module contains the UtilisationRate class, which is focused on calculating and 
managing the utilisation rates of grassland for different farm types across various scenarios. 
This class is a crucial part of the grassland_production package, integrating components 
like grassland yield, fertilisation, and dry matter production for comprehensive analysis.

Classes:
    UtilisationRate: Manages and computes utilisation rates of grassland.
"""
import pandas as pd
import copy
from grassland_production.resource_manager.data_loader import Loader
from grassland_production.resource_manager.grassland_data_manager import DataManager
from grassland_production.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from grassland_production.grass_yield import Yield
from grassland_production.fertilisation import Fertilisation
from grassland_production.grassland_area import Areas
from grassland_production.dry_matter import DryMatter
import cattle_lca.lca as cattle_lca
import sheep_lca.lca as sheep_lca

class UtilisationRate:
    """
    A class to manage and compute the utilisation rates of grassland for different farm types and scenarios.

    The UtilisationRate class calculates the utilisation rate, defined as the ratio of dry matter required 
    by livestock to the dry matter produced on grasslands. It integrates data from various sources, including 
    grass yield, fertilisation, and livestock needs, to compute the utilisation rates for dairy, beef, 
    and sheep farms under various scenarios. This information is vital for sustainable grassland and livestock management.
    
    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.
        yield_class (Yield, optional): An instance of the Yield class. If not provided, a new instance is created with default parameters.
        fertilisation_class (Fertilisation, optional): An instance of the Fertilisation class. If not provided, a new instance is created with default parameters.
        dry_matter_class (DryMatter, optional): An instance of the DryMatter class. If not provided, a new instance is created with default parameters.

    Attributes:
        sc_class (ScenarioDataFetcher): Fetches scenario data.
        scenario_list (list): List of scenarios.
        data_manager_class (DataManager): Manages and processes grassland and livestock data.
        calibration_year (int): Year of data calibration.
        target_year (int): Target year for data analysis.
        default_calibration_year (int): Default year used for calibration in case of data discrepancies.
        yield_class (Yield): Class for managing grassland yield data.
        areas_class (Areas): Class for managing grassland area data.
        fertiliser_class (Fertilisation): Class for managing fertilisation data.
        dm_class (DryMatter): Class for managing dry matter data.
        loader_class (Loader): Class for loading necessary data.
        cattle_grass_feed_class (cattle_lca.GrassFeed): Class for calculating grass feed for cattle.
        sheep_grass_feed_class (sheep_lca.GrassFeed): Class for calculating grass feed for sheep.
        concentrate_feed_class (cattle_lca.Energy): Class for calculating energy requirements for cattle.
        sheep_concentrate_feed_class (sheep_lca.Energy): Class for calculating energy requirements for sheep.

    Methods:
        get_farm_type_dry_matter_produced(): Calculates dry matter produced by each farm type (uses NFS areas).
        get_farm_type_dry_matter_required(): Calculates dry matter required by each farm type (uses NFS areas).
        get_farm_based_utilisation_rate(): Computes utilisation rate based on farm type and scenario.
        get_dynamic_utilisation_rate(): Calculates dynamic utilisation rate considering scenario-specific parameters.
    """

    def __init__(
        self,
        ef_country,
        calibration_year,
        target_year,
        scenario_data,
        scenario_animals_df,
        baseline_animals_df,
        yield_class=None,
        fertilisation_class=None,
        dry_matter_class=None,
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
            target_year, calibration_year, self.default_calibration_year
        )

        if fertilisation_class is None:
            self.fertiliser_class = Fertilisation(
                ef_country,
                calibration_year,
                target_year,
                scenario_data,
                scenario_animals_df,
                baseline_animals_df,
            )
        else:
            self.fertiliser_class = fertilisation_class

        if dry_matter_class is None:
            self.dm_class = DryMatter(
                ef_country,
                calibration_year,
                target_year,
                scenario_data,
                scenario_animals_df,
                baseline_animals_df,
            )
        else:
            self.dm_class = dry_matter_class

        self.loader_class = Loader()
        self.cattle_grass_feed_class = cattle_lca.GrassFeed(ef_country)
        self.sheep_grass_feed_class = sheep_lca.GrassFeed(ef_country)
        self.concentrate_feed_class = cattle_lca.Energy(ef_country)
        self.sheep_concentrate_feed_class = sheep_lca.Energy(ef_country)


    def get_farm_type_dry_matter_produced(self):
        """
        Calculates and returns the dry matter produced by different farm types across various scenarios.

        This method utilizes the grass yield per hectare, obtained from the Yield class, combined with 
        area data from the National Farm Survey (NFS) to compute the total dry matter produced on dairy, 
        beef, and sheep farms. The calculations are performed for both the calibration year and the target year.

        The method iterates over each scenario and farm type, summing the product of yield per hectare and 
        the corresponding area for each type of grassland.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. Each DataFrame 
                has years as the index and farm types (dairy, beef, sheep) as columns. Each cell contains 
                the total dry matter produced for that farm type in the respective year.
        """
        yield_per_ha = self.yield_class.get_yield()

        # Getting area data
        area_data = {
            "dairy": self.loader_class.dairy_area_nfs(),
            "beef": self.loader_class.beef_area_nfs(),
            "sheep": self.loader_class.sheep_area_nfs()
        }

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.scenario_list


        farm_dm_production = {}
        keys = ["dairy", "beef", "sheep"]

        for sc in scenario_list:
            farm_dm_production_df = pd.DataFrame(0.0, index=year_list, columns=keys)

            for key in keys:
                for year in year_list:
                    total = 0
                    for grassland in self.data_manager_class.get_grassland_types():
                        total += yield_per_ha[sc][key].loc[year, grassland] * area_data[key].loc[self.calibration_year, grassland]
                    farm_dm_production_df.loc[year, key] = total

            farm_dm_production[sc] = farm_dm_production_df.copy(deep=True)

        return farm_dm_production


    def get_farm_type_dry_matter_required(self):
        """
        Calculates and returns the dry matter required by the National Farm Survey (NFS) average livestock population on each of 
        the three farm types (dairy, beef, sheep).

        This method determines the amount of dry matter required by dairy, beef, and sheep farms based on 
        the average livestock populations from NFS data. It involves converting the NFS data into dry matter 
        requirements from grass. The calculation is performed for both the calibration year and the target year across various scenarios.

        The method iterates through each scenario, farm type, and animal cohort, using the grass feed class 
        to calculate the dry matter required from grass for each animal type. This provides essential insights 
        into the feed requirements of different farm types.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. Each DataFrame has years 
                as the index and farm types (dairy, beef, sheep) as columns. Each cell contains the total dry matter 
                required for that farm type in the respective year.
        """
        kg_to_t = 1e-3
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.scenario_list

        NFS_data = {
            "NFS_dairy":{"dairy": self.loader_class.dairy_nfs_animals()},
            "NFS_beef":{"beef":self.loader_class.cattle_nfs_animals()},
            "NFS_sheep":{"sheep":self.loader_class.sheep_nfs_animals()}
        }

        COHORTS = {
            "dairy": self.data_manager_class.get_dairy_beef_cohorts()["Dairy"],
            "beef": self.data_manager_class.get_dairy_beef_cohorts()["Beef"],
            "sheep": self.data_manager_class.get_cohorts()["Sheep"],
        }

        grass_feed_class = {"dairy": self.cattle_grass_feed_class,
                            "beef": self.cattle_grass_feed_class,
                            "sheep": self.sheep_grass_feed_class}

        keys = ["dairy", "beef", "sheep"]

        animal_list = list(self.data_manager_class.get_cohorts()["Cattle"]) + list(
            self.data_manager_class.get_cohorts()["Sheep"]
        )

        dry_matter_req = {}

        for sc in scenario_list:
            NFS_farm_dm_df = pd.DataFrame(0.0, index=year_list, columns=keys)

            for animal_name in animal_list:

                animal_past = getattr(self.data_manager_class.get_baseline_animals_dict()[self.calibration_year]["animals"],
                                  animal_name,)

                for key in keys:
                    if animal_name in COHORTS[key]:
                        NFS_farm_dm_df.loc[year_list, key] += (
                            grass_feed_class[key].dry_matter_from_grass(animal_past,)
                            * kg_to_t
                            * 365
                            * NFS_data[f"NFS_{key}"][key].loc[self.calibration_year, animal_name]
                        )

            dry_matter_req[sc] = NFS_farm_dm_df

        return dry_matter_req


    def get_farm_based_utilisation_rate(self):
        """
        Calculates and returns the utilisation rate of grassland for different farm types across various scenarios.

        This method computes the grassland utilisation rate, defined as the ratio of dry matter demand to dry matter 
        availability, for dairy, beef, and sheep farms. The calculations consider both the calibration year and the 
        target year, and they incorporate scenario-specific adjustments for dairy and beef Grass Use Efficiency (GUE) increases.

        This method incorporates NFS data related to dry matter demand and dry matter availability.

        The utilisation rate is calculated separately for each scenario and farm type. For years other than the target 
        year, it is the ratio of the dry matter demand in the calibration year to the dry matter availability in the 
        calibration year. For the target year, the utilisation rate includes additional adjustments based on the 
        scenario-specific GUE increases for dairy and beef farms.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. The DataFrame has years 
                as the index and farm types (dairy, beef, sheep) as columns. Each cell contains the utilisation 
                rate for that farm type in the respective year and scenario.
        """
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.scenario_list
        scenario_df = self.sc_class.get_scenario_dataframe()

        dry_matter_demand = self.get_farm_type_dry_matter_required()
        dry_matter_available = self.get_farm_type_dry_matter_produced()

        cols = ["dairy", "beef", "sheep"]
        utilisation_rate = {}

        for sc in scenario_list:
            utilisation_rate_df = pd.DataFrame(0.0, index=year_list, columns=cols)

            dairy_mask = (scenario_df["Scenarios"] == sc) & (scenario_df["Cattle systems"] == "Dairy") & (scenario_df["Manure management"] == "tank liquid")
            beef_mask = (scenario_df["Scenarios"] == sc) & (scenario_df["Cattle systems"] == "Beef") & (scenario_df["Manure management"] == "tank liquid")
            dairy_GUE_scenario_increase = scenario_df.loc[dairy_mask, "Dairy GUE"].unique()
            beef_GUE_scenario_increase = scenario_df.loc[beef_mask, "Beef GUE"].unique()

            for year in year_list:
                for col in cols:
                    if year != self.target_year:
                        utilisation_rate_df.loc[year, col] = dry_matter_demand[sc].loc[self.calibration_year, col] / dry_matter_available[sc].loc[self.calibration_year, col]
                    else:
                        if col == "dairy":
                            utilisation_rate_df.loc[self.target_year, col] = dry_matter_demand[sc].loc[self.calibration_year, col] / dry_matter_available[sc].loc[self.calibration_year, col] + dairy_GUE_scenario_increase
                        elif col == "beef":
                            utilisation_rate_df.loc[self.target_year, col] = dry_matter_demand[sc].loc[self.calibration_year, col] / dry_matter_available[sc].loc[self.calibration_year, col] + beef_GUE_scenario_increase
                        else:  # Assuming sheep has no GUE increase
                            utilisation_rate_df.loc[self.target_year, col] = dry_matter_demand[sc].loc[self.calibration_year, col] / dry_matter_available[sc].loc[self.calibration_year, col]

            utilisation_rate[sc] = utilisation_rate_df.copy(deep=True)

        return utilisation_rate


    def get_dynamic_utilisation_rate(self):
        """
        Calculates and returns a dynamic utilisation rate for each livestock system and scenario.

        This method computes the utilisation rate, which is the ratio of dry matter required to dry matter produced, 
        for dairy, beef, and sheep farms. For years prior to the target year, the utilisation rate is calculated by 
        aggregating the dry matter produced for each livestock system and grassland type, then dividing the dry matter 
        requirement by this aggregated amount. For the target year, the utilisation rate is determined by adding the 
        utilisation rate increase specified in the scenario parameters to the utilisation rate of the calibration year.

        The method considers various scenarios and adjusts the utilisation rates based on scenario-specific parameters 
        for dairy and beef Grass Use Efficiency (GUE) increases.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. The DataFrame has years 
                as the index and farm types (dairy, beef, sheep) as columns. Each cell contains the dynamic 
                utilisation rate for that farm type in the respective year and scenario.
        """
        grasslands = self.data_manager_class.get_grassland_types()
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.scenario_list
        cols = ["dairy", "beef", "sheep"]

        utilisation_rate = {}

        scenario_df = self.sc_class.get_scenario_dataframe()
        dry_matter_produced = self.dm_class.get_actual_dry_matter_produced()
        dry_matter_req = self.dm_class.actual_dry_matter_required()

        for sc in scenario_list:
            scenario_mask = scenario_df["Scenarios"] == sc
            dairy_mask =(scenario_df["Scenarios"] == sc) & (scenario_df["Cattle systems"] == "Dairy") \
                        & (scenario_df["Manure management"] == "tank liquid")
            beef_mask = (scenario_df["Scenarios"] == sc) & (scenario_df["Cattle systems"] == "Beef") \
                        & (scenario_df["Manure management"] == "tank liquid")
            
            dairy_GUE_scenario_increase = scenario_df.loc[dairy_mask, "Dairy GUE"].unique()
            beef_GUE_scenario_increase = scenario_df.loc[beef_mask, "Beef GUE"].unique()

            utilisation_rate_df = pd.DataFrame(0.0, index=year_list, columns=cols)

            for farm_type in cols:
                for year in year_list:
                    if year == self.target_year:
                        if farm_type == "dairy":
                            utilisation_rate_df.loc[year, "dairy"] = \
                                (utilisation_rate_df.loc[self.calibration_year, farm_type]) \
                                + dairy_GUE_scenario_increase

                        elif farm_type == "beef":
                            utilisation_rate_df.loc[year, "beef"] = \
                                (utilisation_rate_df.loc[self.calibration_year, farm_type]) \
                                + beef_GUE_scenario_increase

                        else:
                            utilisation_rate_df.loc[year, farm_type] = \
                                (utilisation_rate_df.loc[self.calibration_year, farm_type])

                    else:
                        for grassland_type in grasslands:
                            utilisation_rate_df.loc[year, farm_type] += \
                                dry_matter_produced[sc][farm_type].loc[year, grassland_type]
                        utilisation_rate_df.loc[year, farm_type] = (dry_matter_req[sc].loc[year, farm_type]/ \
                                                                    utilisation_rate_df.loc[year, farm_type])

            utilisation_rate[sc] = copy.deepcopy(utilisation_rate_df)

        return utilisation_rate