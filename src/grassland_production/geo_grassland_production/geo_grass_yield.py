"""
====================
Grass Yield Module
====================

This module includes the Yield class, which calculates grass yield per hectare for various farm systems 
and scenarios for the selected catchment. 
The class uses models and data to estimate yields based on different fertilization strategies 
and soil conditions.

Classes:
    Yield: Manages the computation of grass yield for different farm systems and scenarios.
"""

import pandas as pd
from itertools import product
from grassland_production.resource_manager.data_loader import Loader
from grassland_production.resource_manager.grassland_data_manager import DataManager
from grassland_production.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from grassland_production.geo_grassland_production.geo_fertilisation import Fertilisation
from grassland_production.grass_yield import Yield as GrasslandYield

class Yield:
    """
    The Yield class is responsible for calculating grass yield per hectare for various farm systems (dairy, beef, sheep)
    under different scenarios for the specified catchment. This calculation takes into account factors such as fertilization (both inorganic and organic),
    clover proportion, soil types, and other variables, to estimate the impact on grass yield.

    This class integrates data from multiple sources, including fertilization rates and soil characteristics, to provide 
    a comprehensive analysis of grassland production potential under varying agricultural practices and environmental conditions.

    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year for historical data reference.
        target_year (int): The target year for projecting future scenarios.
        scenario_inputs_df (DataFrame): DataFrame containing input variables for different scenarios.
        scenario_animals_df (DataFrame): DataFrame containing data on animals involved in different scenarios.
        baseline_animals_df (DataFrame): DataFrame containing baseline data on animal populations.

    Attributes:
        sc_class (ScenarioDataFetcher): Instance of ScenarioDataFetcher for fetching scenario data.
        scenario_list (list): List of scenarios for which the analysis is performed.
        data_manager_class (DataManager): Instance of DataManager for managing data related to grass yield.
        geo_fertiliser_class (Fertilisation): Instance of Fertilisation for handling geo-specific fertilization data.
        grass_yield_class (GrasslandYield): Instance of Yield class from the grassland_production lib.
        loader_class (Loader): Instance of Loader to load various necessary datasets.
        calibration_year (int): The base year for data calibration and historical reference.
        target_year (int): The target year for future scenario projections.
        soil_class_yield_gap (dict): A dictionary mapping soil types to their respective yield gaps.
        soil_class_prop (DataFrame): A DataFrame indicating the proportion of different soil types across scenarios.

    Methods:
        get_clover_parameters():
            Retrieves clover parameters, such as proportion and fertilization rate, for each scenario, differentiating between 
            conventional yield response curves and clover-grass systems.

        get_yield():
            Calculates the grass yield per hectare for each grassland type, farm system, and scenario. This method takes into 
            account various factors including fertilization rates, soil properties, and clover parameters.

        _yield_response_function_to_fertilizer(fertilizer, grassland, clover_prop=0, clover_fert=0, manure_spread=0):
            An internal method that models the yield response to various factors including fertilizer application, clover proportion,
            and organic manure spread. This function is critical in determining the yield per hectare under different scenarios.

    Note:
        This class is part of a broader framework aimed at understanding and optimizing grassland production. It should be used 
        in conjunction with other related classes to gain a holistic view of the agricultural systems under study.
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
        self.sc_class = ScenarioDataFetcher(scenario_data)
        self.scenario_list = self.sc_class.get_scenario_list()

        self.data_manager_class = DataManager(
            calibration_year,
            target_year,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.geo_fertiliser_class = Fertilisation(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )

        #Classes from Main Model    
        self.grass_yield_class = GrasslandYield(ef_country,
                        calibration_year,
                        target_year,
                        scenario_data,
                        scenario_animals_df,
                        baseline_animals_df)
        
        self.loader_class = Loader()
        self.calibration_year = self.data_manager_class.get_calibration_year()
        self.target_year = self.data_manager_class.get_target_year()

        self.soil_class_yield_gap = self.data_manager_class.get_yield_gap()

        self.soil_class_prop = self.data_manager_class.get_soil_properties()


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
        clover_dict = self.grass_yield_class.get_clover_parameters()

        return clover_dict
       

    def get_yield(self):
        """
        Calculates the yield per hectare for different scenarios and farm systems for the catchment based on fertilization and other factors.
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
        fert_rate = self.geo_fertiliser_class.compute_inorganic_fertilization_rate()

        #Catchment specific
        organic_manure = self.geo_fertiliser_class.organic_fertilisation_per_ha()

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.scenario_list

        clover_parameters_dict = self.get_clover_parameters()

        keys = ["dairy", "beef", "sheep"]

        yield_per_ha = {
            farm_type: {
                sc: pd.DataFrame(
                    0.0,
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
        yield_response = self.grass_yield_class._yield_response_function_to_fertilizer(
            fertilizer, grassland, clover_prop, clover_fert, manure_spread
        )

        return yield_response
