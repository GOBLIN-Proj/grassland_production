"""
====================
Grass Yield Module
====================

This module includes the Yield class, which calculates grass yield per hectare for various farm systems 
and scenarios. The class uses models and data to estimate yields based on different fertilization strategies 
and soil conditions.

Classes:
    Yield: Manages the computation of grass yield for different farm systems and scenarios.
"""

import pandas as pd
from itertools import product
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.fertilisation import Fertilisation


class Yield:
    """
        The Yield class is dedicated to calculating grass yield per hectare for different farm systems (dairy, beef, 
        sheep) under various scenarios. It considers the impact of fertilization (both inorganic and organic), 
        clover proportion, soil types, and other factors on grass yield.

        Args:
            ef_country (str): The country for which the analysis is performed.
            calibration_year (int): The calibration year.
            target_year (int): The target year for future scenario projections.
            scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
            scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
            baseline_animals_df (DataFrame): DataFrame containing baseline animal data.

        Attributes:
            data_manager_class (DataManager): Instance of DataManager for managing data related to yield.
            fertiliser_class (Fertilisation): Instance of Fertilisation for handling fertilization-related data.
            loader_class (Loader): Instance of Loader to load various datasets.
            calibration_year (int): The base year for data calibration.
            target_year (int): The target year for future scenario projections.
            soil_class_yield_gap (dict): A dictionary mapping soil types to yield gaps.
            soil_class_prop (DataFrame): A DataFrame indicating the proportion of different soil types.

        Methods:
            get_clover_parameters():
                Defines clover proportion and rate for different scenarios to differentiate between conventional 
                yield response curves and clover-grass systems.

            get_yield():
                Calculates the yield per hectare for each grassland type, farm system, and scenario.

            _yield_response_function_to_fertilizer():
                Internal method to model the yield response to fertilizer application.
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
        self.fertiliser_class = Fertilisation(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.loader_class = Loader()
        self.calibration_year = self.data_manager_class.calibration_year
        self.target_year = self.data_manager_class.target_year

        self.soil_class_yield_gap = self.data_manager_class.soil_class_yield_gap

        self.soil_class_prop = self.data_manager_class.soil_class_prop


    def get_clover_parameters(self):
        """
        Defines clover proportion and rate for each scenario, differentiating between conventional
        yield response curves and clover-grass systems. This method considers scenarios for dairy,
        beef, and sheep farm systems with specific manure management practices.

        The method retrieves these parameters from the scenario data and organizes them in a dictionary
        structure for later use in yield calculations.

        Returns:
            dict: A dictionary containing clover parameters for different scenarios and farm systems.

        The clover parameters include:
            - Clover proportion: The proportion of clover in the pasture.
            - Clover fertilisation rate: The rate of clover fertilisation.

        """
        scenario_df = self.data_manager_class.scenario_inputs_df

        keys = ["dairy", "beef", "sheep"]
        inner_keys = ["proportion", "fertilisation"]

        clover_dict = {key: {inner_key: {} for inner_key in inner_keys} for key in keys}

        conditions = {
            "dairy": (
                    (scenario_df["Cattle systems"] == "Dairy")
                    & (scenario_df["Manure management"] == "tank liquid")
            ),
            "beef": (
                    (scenario_df["Cattle systems"] == "Beef")
                    & (scenario_df["Manure management"] == "tank liquid")
            ),
            "sheep": (
                    (scenario_df["Cattle systems"] == "Lowland sheep")
                    & (scenario_df["Manure management"] == "tank solid")
            )
        }

        for key in keys:
            for sc in scenario_df["Scenarios"]:
                mask = (scenario_df["Scenarios"] == sc) & conditions[key]
                clover_proportion = scenario_df.loc[mask, "Clover proportion"].item()
                clover_fertilisation = scenario_df.loc[mask, "Clover fertilisation"].item()
                clover_dict[key]["proportion"][sc] = clover_proportion
                clover_dict[key]["fertilisation"][sc] = clover_fertilisation


        return clover_dict
       

    def get_yield(self):
        """
        Calculates the yield per hectare for different scenarios and farm systems based on fertilization and other factors.
        The method computes yield values for dairy, beef, and sheep farm systems under various scenarios.

        The method utilizes information on fertilization rates, organic manure spread, soil properties, and clover parameters
        to calculate yields for each scenario and farm system. It iterates through different combinations of scenarios,
        farm systems, grassland types, and soil groups to compute yields.

        Returns:
            dict: A dictionary containing yield data for different scenarios and farm systems. The dictionary is structured as follows:
            - Keys: Farm system types ("dairy," "beef," "sheep").
            - Values: Nested dictionaries, where each inner dictionary represents a scenario with the following structure:
                - Keys: Scenario names.
                - Values: Pandas DataFrames containing yield values for different grassland types (e.g., "Pasture," "Grass silage").
                    - The DataFrame's rows correspond to grassland types.
                    - The DataFrame's columns correspond to calibration and target years.
        """
        fertilization_by_system_data_frame = (
            self.loader_class.grassland_fertilization_by_system()
        )
        fert_rate = self.fertiliser_class.compute_inorganic_fertilization_rate()
        organic_manure = self.fertiliser_class.organic_fertilisation_per_ha()

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        clover_parameters_dict = self.get_clover_parameters()

        keys = ["dairy", "beef", "sheep"]

        yield_per_ha = {
            farm_type: {
                sc: pd.DataFrame(
                    0,
                    index=fertilization_by_system_data_frame.index.levels[0],
                    columns=year_list,
                )
                for sc in scenario_list
            }
            for farm_type in keys
        }

        for sc, farm_type, grassland_type, soil_group in product(
            scenario_list,
            keys,
            fertilization_by_system_data_frame.index.levels[0],
            self.soil_class_yield_gap.keys(),
        ):
            yield_per_ha_df = yield_per_ha[farm_type][sc]
            soil_class_prop = self.soil_class_prop[farm_type].loc[
                int(self.calibration_year), soil_group
            ]

            yield_per_ha_df.loc[grassland_type, int(self.calibration_year)] += (
                self._yield_response_function_to_fertilizer(
                    fert_rate[farm_type][sc].loc[
                        grassland_type, str(self.calibration_year)
                    ],
                    grassland_type,
                    manure_spread=organic_manure[sc].loc[int(self.calibration_year), farm_type],
                )
                * self.soil_class_yield_gap[soil_group]
            ) * soil_class_prop

            clover_prop = clover_parameters_dict[farm_type]["proportion"][sc]
            clover_fert = clover_parameters_dict[farm_type]["fertilisation"][sc]

            yield_per_ha_df.loc[grassland_type, int(self.target_year)] += (
                self._yield_response_function_to_fertilizer(
                    fert_rate[farm_type][sc].loc[grassland_type, str(self.target_year)],
                    grassland_type,
                    clover_prop=clover_prop,
                    clover_fert=clover_fert,
                    manure_spread=organic_manure[sc].loc[int(self.target_year), farm_type],
                )
                * self.soil_class_yield_gap[soil_group]
            ) * soil_class_prop

        transposed_yield_per_ha = {
            sc: {farm_type: yield_per_ha[farm_type][sc].T for farm_type in keys}
            for sc in scenario_list
        }

        return transposed_yield_per_ha


    def _yield_response_function_to_fertilizer(
        self, fertilizer, grassland, clover_prop=0, clover_fert=0, manure_spread=0
    ):
        """
        Calculate the yield response to fertilizer application based on the specified parameters.

        This method calculates the yield response to fertilizer application based on a yield response function taken from Finneran et al. (2011).
        The function takes into account the type of grassland, clover proportion, clover fertilization, and organic manure spread.

        If the grassland is "Grass silage" or "Pasture," the method calculates the yield response by considering both
        the default yield response function and the contribution of clover. If the grassland is different, only the default
        yield response function is applied.

        Parameters:
            fertilizer (float): The amount of fertilizer applied (in kilograms per hectare).
            grassland (str): The type of grassland ("Grass silage" or "Pasture").
            clover_prop (float, optional): The proportion of clover in the grassland (0 to 1). Default is 0.
            clover_fert (float, optional): The rate of clover fertilization (in kilograms per hectare). Default is 0.
            manure_spread (float, optional): The amount of organic manure spread (in kilograms per hectare). Default is 0.

        Returns:
            float: The estimated yield response to the specified fertilizer application (in metric tons per hectare).


        Note: The result is converted to metric tons per hectare using the factor 1e-3.

        """

        kg_to_t = 1e-3
        if grassland == "Grass silage" or grassland == "Pasture":
         
            yield_response_default = ((-0.0444 * ((fertilizer + manure_spread) ** 2)
                + 38.419 * (fertilizer + manure_spread)
                + 6257) * (1 - clover_prop)) 
            
            yield_response_clover = (0.7056 * (clover_fert + manure_spread) + 12829) * clover_prop

            yield_response = yield_response_default + yield_response_clover

        else:
            yield_response = -0.0444 * (fertilizer**2) + 38.419 * fertilizer + 6257

        yield_response = yield_response * kg_to_t

        return yield_response
