"""
===================
Dry Matter Module
===================

This module contains the DryMatter class, which is responsible for calculating dry matter requirements 
and production in various agricultural scenarios, focusing on livestock systems. It integrates data 
from multiple sources and uses lifecycle assessment methods from the cattle and sheep lca modules.

Classes:
    DryMatter: Manages the calculation of dry matter requirements and production for livestock systems.
"""

import pandas as pd
from itertools import product
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.grass_yield import Yield
from grassland_production.fertilisation import Fertilisation
from grassland_production.grassland_area import Areas
import cattle_lca.lca as cattle_lca
import sheep_lca.lca as sheep_lca
from cattle_lca.animal_data import AnimalData as cattle_data
from sheep_lca.animal_data import AnimalData as sheep_data

class DryMatter:
    """
    The DryMatter class calculates the dry matter requirements and production for different livestock systems.
    It utilizes various classes and modules to integrate data from the National Farm Survey, CSO, and other sources,
    and applies lifecycle assessment methods from the cattle and sheep lca modules to evaluate agricultural scenarios.

    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.


    Attributes:
        data_manager_class (DataManager): Manages the data retrieval for various scenarios.
        calibration_year (int): The year used for calibrating data.
        target_year (int): The year for which the scenario is targeted.
        default_calibration_year (int): Default year (2015) used if calibration year data is unavailable.
        yield_class (Yield): Manages the yield calculations.
        areas_class (Areas): Manages the area-related calculations.
        fertiliser_class (Fertilisation): Manages the fertilization-related calculations.
        loader_class (Loader): Loads data from various sources.
        grass_feed_class (cattle_lca.GrassFeed): Manages the grass feed calculations for cattle.
        sheep_grass_feed_class (sheep_lca.GrassFeed): Manages the grass feed calculations for sheep.

    Methods:
        get_actual_dry_matter_produced():
            Calculates the actual dry matter produced in each livestock system.

        actual_dry_matter_required_past():
            Calculates the dry matter requirement for past livestock systems.

        actual_dry_matter_required_future():
            Calculates the dry matter requirement for future livestock systems based on scenarios.

        actual_dry_matter_required():
            Integrates past and future dry matter requirements for livestock systems.

        get_actual_dm_weights():
            Calculates the proportion of dry matter required for each livestock system.

        get_dm_proportional_reduction():
            Determines the proportional reduction in dry matter requirement for each system.

        weighted_dm_reduction_contribution():
            Calculates the weighted contribution of each livestock system to the total dry matter reduction.

        get_total_concentrate_feed_past():
            Computes the total amount of concentrate feed required by livestock in the past.

        get_total_concentrate_feed_future():
            Computes the total amount of concentrate feed required by livestock in the future based on scenarios.

        get_total_concentrate_feed():
            Integrates past and future concentrate feed requirements for livestock systems.
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
        self.data_manager_class = DataManager(
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.calibration_year = self.data_manager_class.calibration_year
        self.target_year = self.data_manager_class.target_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.yield_class = Yield(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.areas_class = Areas(
            target_year, calibration_year, self.default_calibration_year
        )
        self.fertiliser_class = Fertilisation(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.loader_class = Loader()
        self.grass_feed_class = cattle_lca.GrassFeed(ef_country)
        self.sheep_grass_feed_class = sheep_lca.GrassFeed(ef_country)



    def get_actual_dry_matter_produced(self):
        """
        Calculates the actual dry matter produced in each livestock system. This calculation is based on the yield per 
        hectare of grassland specific to each system, taking into account the type of grassland and the fertilization 
        practices used. The method integrates data from various sources to estimate dry matter production for different 
        farm types and scenarios.

        The method uses historical data for grassland areas and fertilization practices, and it interpolates for years 
        earlier than 2005, acknowledging that these interpolations may not be very accurate. However, data for years 
        prior to 2005 is generally not critical for the analysis.

        Returns:
            dict: A dictionary structured by scenario, then by farm type (dairy, beef, sheep), containing pandas 
                DataFrames. Each DataFrame represents the dry matter produced, indexed by grassland type and 
                segmented by year (calibration year and target year). A 'total' column is added to summarize 
                the dry matter produced across all grassland types.

        Notes:
            - If data for the calibration year is not present, a default year is used as a fallback.
            - The method assumes that the required data is available through the loader_class and yield_class 
            attributes, which are instances of the Loader and Yield classes, respectively.
        """
        fertilization_by_system_data_frame = (
            self.loader_class.grassland_fertilization_by_system()
        )
        yield_per_ha = self.yield_class.get_yield()

        grassland_areas = self.loader_class.cso_grassland_areas()
        nfs_system_proportions = self.areas_class.get_nfs_system_proportions()

        dairy_nfs_system_proportions = nfs_system_proportions[0]
        beef_nfs_system_proportions = nfs_system_proportions[1]
        sheep_nfs_system_proportions = nfs_system_proportions[2]

        nfs_system_proportions = {
            "dairy": dairy_nfs_system_proportions,
            "beef": beef_nfs_system_proportions,
            "sheep": sheep_nfs_system_proportions,
        }

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        keys = ["dairy", "beef", "sheep"]

        dry_matter_produced = {
            sc: {
                farm_type: pd.DataFrame(
                    0,
                    index=fertilization_by_system_data_frame.index.levels[0],
                    columns=year_list,
                )
                for farm_type in keys
            }
            for sc in scenario_list
        }

        default_year_flag = True
        for sc, year, farm_type, grassland_type in product(
            scenario_list,
            year_list,
            keys,
            fertilization_by_system_data_frame.index.levels[0],
        ):
            total_dm = dry_matter_produced[sc][farm_type]

            calibration_year_value = self.calibration_year

            try:
                proportion = nfs_system_proportions[farm_type].loc[
                    calibration_year_value, grassland_type
                ]

                total_dm.loc[grassland_type, year] += yield_per_ha[sc][farm_type].loc[
                    year, grassland_type
                ] * (
                    grassland_areas.loc[calibration_year_value, grassland_type]
                    * proportion
                )

            except KeyError:
                calibration_year_value = int(self.default_calibration_year)

                if default_year_flag == True:
                    print(
                        f"... calibration year not present, {calibration_year_value} default year used for total Dry Matter..."
                    )
                    default_year_flag = False

                proportion = nfs_system_proportions[farm_type].loc[
                    calibration_year_value, grassland_type
                ]

                total_dm.loc[grassland_type, year] += yield_per_ha[sc][farm_type].loc[
                    year, grassland_type
                ] * (
                    grassland_areas.loc[calibration_year_value, grassland_type]
                    * proportion
                )

        transposed_dry_matter_produced = {
            sc: {farm_type: dry_matter_produced[sc][farm_type].T for farm_type in keys}
            for sc in scenario_list
        }

        for sc, farm_type in product(scenario_list, keys):
            transposed_dry_matter_produced[sc][farm_type][
                "total"
            ] = transposed_dry_matter_produced[sc][farm_type].sum(axis=1)

        return transposed_dry_matter_produced
    


    def actual_dry_matter_required_past(self):
        """
        Calculates the dry matter requirement for each livestock system (dairy, beef, and sheep) for the calibration year. 
        The calculation is based on the livestock data available for the calibration year, using the lifecycle assessment 
        method 'dry_matter_from_grass' to estimate the dry matter required by each animal cohort.

        The method processes data for dairy, beef, and sheep livestock systems, summing up the dry matter requirements 
        for each type of livestock based on their population and specific dry matter intake rates.

        Returns:
            DataFrame: A pandas DataFrame indexed by the calibration year, with columns for dairy, beef, sheep, 
                    and a total column summing these values. Each cell in the DataFrame represents the total 
                    dry matter required in tonnes per year for that livestock type.

        Notes:
            - The method assumes that baseline animal data for the calibration year is available and structured 
            appropriately for the calculation.
            - The dry matter requirement is calculated per animal and then scaled to the total population of that 
            animal type.
            - The method differentiates between different types of animal management systems (e.g., tank liquid 
            vs. solid manure management) and different grazing types for sheep.
        """

        kg_to_t = 1e-3

        baseline_animals_df = self.data_manager_class.baseline_animals_df

        cols = ["dairy", "beef", "sheep", "total"]

        COHORTS = self.data_manager_class.COHORTS_GROUPS

        animal_list = self.data_manager_class.baseline_animals_dict[self.calibration_year]["animals"]

        past_total_dm_df = pd.DataFrame(0.0, index=[self.calibration_year], columns=cols)

        # Process dairy and beef
        for cohort in ["dairy", "beef"]:
            for animal_name in COHORTS[cohort]:
                if animal_name in animal_list.__dict__.keys():
                    animal_past = getattr(
                        animal_list,
                        animal_name,
                    )

                    mask_validation = (baseline_animals_df["year"] == self.calibration_year) & (
                        baseline_animals_df["cohort"] == animal_name) & (baseline_animals_df["mm_storage"] == "tank liquid") & (baseline_animals_df["pop"] > 0)

   
                    past_total_dm_df.loc[self.calibration_year, cohort] += (
                        self.grass_feed_class.dry_matter_from_grass(
                            animal_past,
                        )
                        * kg_to_t
                        * 365
                        * baseline_animals_df.loc[mask_validation, "pop"].values.item()
                    )
        # Process sheep
        for landtype in COHORTS["sheep"].keys():
            for animal_name in COHORTS["sheep"][landtype]:
                if animal_name in animal_list.__dict__.keys():
                    animal_past = getattr(
                        animal_list,
                        animal_name,
                    )
                    sheep_mask_validation = (
                        (baseline_animals_df["year"] == self.calibration_year)
                        & (baseline_animals_df["cohort"] == animal_name)
                        & (baseline_animals_df["grazing"] == landtype)
                        & (baseline_animals_df["mm_storage"] == "solid")
                        & (baseline_animals_df["pop"] > 0)
                    )
                    if sheep_mask_validation.any():
                        past_total_dm_df.loc[self.calibration_year, "sheep"] += (
                            self.sheep_grass_feed_class.dry_matter_from_grass(animal_past) * kg_to_t * 365
                            * baseline_animals_df.loc[sheep_mask_validation, "pop"].item()
                        )

        past_total_dm_df["total"] = past_total_dm_df[["dairy","beef","sheep"]].sum(axis=1)

        return past_total_dm_df
    

    def actual_dry_matter_required_future(self):
        """
        Calculates the future dry matter requirements for each livestock system (dairy, beef, and sheep) for 
        each scenario in the target year. This method considers various future scenarios based on different 
        animal population, management practices and farm types.

        The calculation is based on the data for each scenario's livestock, using the lifecycle assessment 
        method 'dry_matter_from_grass' to estimate the dry matter required by each animal type. The method 
        processes data for dairy, beef, and sheep livestock systems, summing up the dry matter requirements 
        for each type of livestock based on their population and specific dry matter intake rates.

        Returns:
            dict: A dictionary with scenario keys, each containing a pandas DataFrame indexed by the target 
                year. The DataFrame has columns for dairy, beef, sheep, and a total column summing these 
                values. Each cell represents the total dry matter required in tonnes per year for that 
                livestock type under each scenario.

        Notes:
            - The method assumes that scenario-specific animal data is available and structured appropriately 
            for the calculation.
            - The dry matter requirement is calculated per animal and then scaled to the total population of 
            that animal type in the scenario.
            - Different scenarios may represent varying farm management practices, livestock types, and animal 
            populations, reflecting possible future states of the livestock systems.
        """
        kg_to_t = 1e-3
        cols = ["dairy", "beef", "sheep", "total"]

        COHORTS = self.data_manager_class.COHORTS_GROUPS

        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()
        scenario_animals_df = self.data_manager_class.scenario_animals_df
        dry_matter_req = {}
        
        animal_list = self.data_manager_class.scenario_animals_dict
 
        for sc in scenario_list:
            dry_matter_req[sc] = pd.DataFrame(0.0, index=[self.target_year], columns=cols)
            farm_mask = self.data_manager_class.scenario_aggregation["Scenarios"] == sc
            farm_ids = self.data_manager_class.scenario_aggregation.loc[farm_mask, "farm_id"].unique()

            for farm_id in farm_ids:
                # Process dairy and beef
                for cohort in ["dairy", "beef"]:
                    for animal_name in COHORTS[cohort]:
                        if animal_name in animal_list[farm_id]["animals"].__dict__.keys():
                            animal_scenario = getattr(
                                animal_list[farm_id]["animals"],
                                animal_name
                            )
                            mask = (scenario_animals_df["farm_id"] == farm_id) & (scenario_animals_df["cohort"] == animal_name) & (scenario_animals_df["mm_storage"] == "tank liquid") & (scenario_animals_df["pop"] > 0)
                            if mask.any():
                                dry_matter_req[sc].loc[self.target_year, cohort] += (
                                    self.grass_feed_class.dry_matter_from_grass(animal_scenario) * kg_to_t * 365
                                    * scenario_animals_df.loc[mask, "pop"].item()
                                )

                # Process sheep
                for landtype in COHORTS["sheep"].keys():
                    for animal_name in COHORTS["sheep"][landtype]:
                        if animal_name in animal_list[farm_id]["animals"].__dict__.keys():
                            animal_scenario = getattr(
                                animal_list[farm_id]["animals"],
                                animal_name
                            )
                            sheep_mask = (
                                (scenario_animals_df["farm_id"] == farm_id)
                                & (scenario_animals_df["cohort"] == animal_name)
                                & (scenario_animals_df["grazing"] == landtype)
                                & (scenario_animals_df["mm_storage"] == "solid")
                                & (scenario_animals_df["pop"] > 0)
                            )
                            if sheep_mask.any():
                                dry_matter_req[sc].loc[self.target_year, "sheep"] += (
                                    self.sheep_grass_feed_class.dry_matter_from_grass(animal_scenario) * kg_to_t * 365
                                    * scenario_animals_df.loc[sheep_mask, "pop"].item()
                                )

            dry_matter_req[sc]["total"] = dry_matter_req[sc][["dairy", "beef", "sheep"]].sum(axis=1)

        return dry_matter_req
    

    def actual_dry_matter_required(self):
        """
        Integrates and calculates the total dry matter requirements for livestock systems, combining both past (historic) 
        and future scenarios. This method utilizes lifecycle assessment methods from cattle and sheep modules to determine the dry matter 
        requirements from grass for each livestock cohort, across various scenarios and timeframes.

        The method first computes the dry matter requirements for the calibration year (representing the past) 
        and then for the target year (representing future scenarios). It then integrates these requirements 
        into a comprehensive view, providing a complete picture of dry matter needs across different time periods 
        and scenarios.

        Returns:
            dict: A dictionary with scenario keys, each containing a pandas DataFrame that includes the dry matter 
                requirements for both the calibration year and the target year. Each DataFrame is indexed by year 
                and has columns for dairy, beef, sheep, and a total column summing these values.

        Notes:
            - The method relies on two key internal methods: 'actual_dry_matter_required_past' for calculating past 
            requirements and 'actual_dry_matter_required_future' for future scenario-based requirements.
            - This approach provides am integration of historical and projected data, facilitating analysis 
            and comparison across different time periods and scenarios.
        """
        past_dm = self.actual_dry_matter_required_past()
        future_dm = self.actual_dry_matter_required_future()

        for sc in future_dm.keys():
            future_dm[sc].loc[self.calibration_year] = past_dm.loc[self.calibration_year]

        return future_dm
    

    def get_actual_dm_weights(self):
        """
        Calculates the proportional weights of dry matter requirements for each livestock cohort (dairy, beef, sheep) 
        relative to the total dry matter requirements across different scenarios. This method helps in understanding 
        the contribution of each livestock type to the overall dry matter requirements in each scenario.

        The method first retrieves the total dry matter requirements for each scenario using the 
        'actual_dry_matter_required' method. It then computes the weight (as a proportion) of each cohort's 
        requirement relative to the total requirement for that scenario.

        Returns:
            dict: A dictionary with scenario keys, each containing a nested dictionary. The nested dictionary 
                maps each livestock cohort (dairy, beef, sheep) to its proportional weight of the total dry 
                matter requirement. The 'total' column is excluded from this calculation.

        Notes:
            - This method provides a percentage-like view of how much each livestock type contributes to the 
            total dry matter requirements within each scenario.
            - These weights can be used for analyses that require understanding the distribution of dry matter 
            needs among different livestock types under various future scenarios.
        """
        dm_required = self.actual_dry_matter_required()

        weights = {}

        for sc in dm_required.keys():
            weights[sc] = {}
            for cohort in dm_required[sc].columns:
                if cohort != "total":
                    weights[sc][cohort] = dm_required[sc][cohort]/dm_required[sc]["total"]

        return weights


    def get_dm_proportional_reduction(self):
        """
        Calculates the proportional reduction in dry matter requirements for each livestock cohort (dairy, beef, sheep)
        from the calibration year to the target year under various scenarios. This method assesses the impact of 
        different future scenarios on the dry matter requirements compared to past requirements.

        The method computes the dry matter requirements for both past (calibration year) and future (target year) 
        scenarios. It then determines the proportional reduction in dry matter requirements for each cohort in each 
        scenario by comparing the future requirements with the past.

        Returns:
            dict: A dictionary with scenario keys, each containing a nested dictionary. The nested dictionary maps 
                each livestock cohort to its proportional reduction in dry matter requirement relative to the past. 
                A 'total' entry is also included, representing the sum of the proportional reductions for all cohorts.

        Notes:
            - The proportional reduction is calculated as 1 minus the ratio of future to past dry matter requirements.
            - If the calculated proportion is negative (indicating an increase rather than a decrease), it is set to 0 
            to reflect no reduction.
        """
        past_dm = self.actual_dry_matter_required_past()
        future_dm = self.actual_dry_matter_required_future()

        proportion_reduction = {}

        for sc in future_dm.keys():
            proportion_reduction[sc] = {}
            for cohort in past_dm.columns:
                if cohort != "total":

                    proportion = 1-(future_dm[sc].loc[self.target_year,cohort]/past_dm.loc[self.calibration_year, cohort])

                    if proportion < 0:
                        proportion = 0
                
                    proportion_reduction[sc][cohort] = proportion
            
            proportion_reduction[sc]["total"] = sum(proportion_reduction[sc].values())
            
        return proportion_reduction


    def weighted_dm_reduction_contribution(self):
        """
        Calculates the weighted contribution of each livestock cohort (dairy, beef, sheep) to the total proportional 
        reduction in dry matter requirements across different scenarios. This method evaluates how each cohort 
        contributes to the overall reduction in dry matter needs when transitioning from the calibration year to 
        the target year under various scenarios.

        The method first determines the proportional reduction in dry matter requirements for each cohort in each 
        scenario using the 'get_dm_proportional_reduction' method. It then computes the weighted contribution of 
        each cohort's reduction relative to the total reduction in that scenario.

        Returns:
            dict: A dictionary with scenario keys, each containing a nested dictionary. The nested dictionary maps 
                each livestock cohort to its weighted contribution to the total proportional reduction. The 'total' 
                entry is not included in the calculation of weights.

        Notes:
            - The weighted contribution is calculated as the proportion of each cohort's reduction relative to the 
            total reduction in that scenario.
            - This method provides insight into which livestock cohort is contributing the most to the reduction in 
            dry matter requirements in each scenario, allowing for targeted analysis and planning.
        """
        proprotion_reduction = self.get_dm_proportional_reduction()

        weights = {} 

        for sc in proprotion_reduction.keys():
            weights[sc] = {}
            for cohort in proprotion_reduction[sc].keys():
                if cohort != "total":
                    weights[sc][cohort] = proprotion_reduction[sc][cohort]/proprotion_reduction[sc]["total"]

        return weights


    def get_total_concentrate_feed_past(self):
        """
        Calculates the total amount of concentrate feed required by all livestock within each farm system (dairy, beef, sheep) 
        in tonnes for the calibration year. This method estimates the concentrate feed needs based on the population and 
        specific feed requirements of different types of livestock in the calibration year.

        The calculation involves determining the amount of concentrate feed each animal requires and then aggregating these 
        amounts across all animals within each livestock cohort.

        Returns:
            DataFrame: A pandas DataFrame indexed by the calibration year, with columns for dairy, beef, sheep, 
                    and a total column summing these values. Each cell in the DataFrame represents the total 
                    concentrate feed required in tonnes per year for that livestock type.

        Notes:
            - The concentrate feed requirement is calculated per animal and then scaled to the total population of that 
            animal type.
            - The method differentiates between different types of animal management systems (e.g., tank liquid vs. 
            solid manure management) and different grazing types for sheep.
        """
        kg_to_t = 1e-3

        baseline_animals_df = self.data_manager_class.baseline_animals_df

        cols = ["dairy", "beef", "sheep", "total"]

        COHORTS = self.data_manager_class.COHORTS_GROUPS

        animal_list = self.data_manager_class.baseline_animals_dict[self.calibration_year]["animals"]

        past_total_conc_df = pd.DataFrame(0.0, index=[self.calibration_year], columns=cols)

        for cohort in ["dairy", "beef"]:
            for animal_name in COHORTS[cohort]:
                if animal_name in animal_list.__dict__.keys():

                    animal_past = getattr(animal_list, animal_name)

                    mask_validation = (baseline_animals_df["year"]== self.calibration_year) & (baseline_animals_df["cohort"] == animal_name) & (baseline_animals_df["mm_storage"] == "tank liquid") & (baseline_animals_df["pop"] > 0)
                    
                    if mask_validation.any():
                        past_total_conc_df.loc[self.calibration_year, cohort] += (cattle_data.get_animal_concentrate_amount(animal_past,) * kg_to_t * 365 * baseline_animals_df.loc[mask_validation, "pop"].item())

        for landtype in COHORTS["sheep"].keys():
            for animal_name in COHORTS["sheep"][landtype]:
                if animal_name in animal_list.__dict__.keys():
                    animal_past = getattr(animal_list, animal_name)
                    sheep_mask_validation = ((baseline_animals_df["year"]== self.calibration_year)& (baseline_animals_df["cohort"] == animal_name)& (baseline_animals_df["grazing"] == landtype)& (baseline_animals_df["mm_storage"] == "solid") & (baseline_animals_df["pop"] > 0))
                    if sheep_mask_validation.any():
                        past_total_conc_df.loc[self.calibration_year, "sheep"] += (sheep_data.get_animal_concentrate_amount(animal_past,) * kg_to_t * 365 * baseline_animals_df.loc[sheep_mask_validation, "pop"].item())

        past_total_conc_df["total"] = past_total_conc_df[["dairy", "beef", "sheep"]].sum(axis=1)

        return past_total_conc_df


    def get_total_concentrate_feed_future(self):
        """
        Calculates the total amount of concentrate feed required by all livestock within each farm system 
        (dairy, beef, sheep) in tonnes for the target year under various scenarios. This method provides 
        an estimation of future concentrate feed needs based on projected changes in livestock populations 
        and management practices across different scenarios.

        The calculation involves determining the amount of concentrate feed each animal requires in each 
        scenario and then aggregating these amounts across all animals within each livestock cohort.

        Returns:
            dict: A dictionary with scenario keys, each containing a pandas DataFrame indexed by the target year, 
                with columns for dairy, beef, sheep, and a total column summing these values. Each cell represents 
                the total concentrate feed required in tonnes per year for that livestock type under each scenario.

        Notes:
            - The concentrate feed requirement is calculated per animal and then scaled to the total population of 
            that animal type in each scenario.
            - The method accounts for different livestock management systems and grazing types for each animal 
            cohort, reflecting the varied nature of future livestock farming scenarios.
        """
        kg_to_t = 1e-3
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()
        scenario_animals_df = self.data_manager_class.scenario_animals_df

        cols = ["dairy", "beef", "sheep", "total"]

        COHORTS = self.data_manager_class.COHORTS_GROUPS

        animal_list = self.data_manager_class.scenario_animals_dict

        total_concentrate_feed = {}
        
        for sc in scenario_list:
            total_conc_df = pd.DataFrame(0.0, index=[self.target_year], columns=cols)
            total_concentrate_feed[sc] = total_conc_df

            farm_mask = self.data_manager_class.scenario_aggregation["Scenarios"] == sc
            farm_ids = self.data_manager_class.scenario_aggregation.loc[farm_mask, "farm_id"].unique()

            for farm_id in farm_ids:
                # Process dairy and beef
                for cohort in ["dairy", "beef"]:
                    for animal_name in COHORTS[cohort]:
                        if animal_name in animal_list[farm_id]["animals"].__dict__.keys():
                            animal_scenario = getattr(
                                animal_list[farm_id]["animals"],
                                animal_name
                            )
                            mask = (scenario_animals_df["farm_id"] == farm_id) & (scenario_animals_df["cohort"] == animal_name) & (scenario_animals_df["mm_storage"] == "tank liquid") & (scenario_animals_df["pop"] > 0)
                            if mask.any():
                                total_concentrate_feed[sc].loc[self.target_year, cohort] += (cattle_data.get_animal_concentrate_amount(animal_scenario) * kg_to_t * 365 * scenario_animals_df.loc[mask, "pop"].item())

                # Process sheep
                for landtype in COHORTS["sheep"].keys():
                    for animal_name in COHORTS["sheep"][landtype]:
                        if animal_name in animal_list[farm_id]["animals"].__dict__.keys():
                            animal_scenario = getattr(
                                animal_list[farm_id]["animals"],
                                animal_name
                            )
                            sheep_mask = (
                                (scenario_animals_df["farm_id"] == farm_id)
                                & (scenario_animals_df["cohort"] == animal_name)
                                & (scenario_animals_df["grazing"] == landtype)
                                & (scenario_animals_df["mm_storage"] == "solid")
                                & (scenario_animals_df["pop"] > 0)
                            )
                            if sheep_mask.any():                                    
                                total_concentrate_feed[sc].loc[self.target_year, "sheep"] += (sheep_data.get_animal_concentrate_amount(animal_scenario) * kg_to_t * 365 * scenario_animals_df.loc[sheep_mask, "pop"].item())

            total_concentrate_feed[sc]["total"] = total_concentrate_feed[sc][["dairy", "beef", "sheep"]].sum(axis=1)

        return total_concentrate_feed
    

    def get_total_concentrate_feed(self):
        """
        Integrates and calculates the total concentrate feed requirements for livestock systems, combining both past 
        (calibration year) and future (target year under various scenarios) data. This method provides a comprehensive 
        view of the concentrate feed needs for different livestock cohorts across time and scenarios.

        The method first calculates the concentrate feed requirements for the past (calibration year) and then for the 
        future (target year) under various scenarios. It then integrates these requirements, offering a complete 
        picture of concentrate feed needs across different time periods and scenarios.

        Returns:
            dict: A dictionary with scenario keys, each containing a pandas DataFrame that includes the concentrate 
                feed requirements for both the calibration year and the target year. Each DataFrame is indexed by 
                year and has columns for dairy, beef, sheep, and a total column summing these values.

        Notes:
            - The method relies on two key internal methods: 'get_total_concentrate_feed_past' for calculating past 
            requirements and 'get_total_concentrate_feed_future' for future scenario-based requirements.
        """
        past_con = self.get_total_concentrate_feed_past()
        future_con = self.get_total_concentrate_feed_future()

        for sc in future_con.keys():
            future_con[sc].loc[self.calibration_year] = past_con.loc[self.calibration_year]

        return future_con