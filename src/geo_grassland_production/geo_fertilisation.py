"""
======================
Fertilisation Module
======================

This module encompasses the Fertilisation classes (both geo_fertilisation and fertilisation), which is focused on computing various fertilisation 
rates and their distribution across different farm systems and scenarios. This class is used in the calculation of 
grassland production for catchments.

Classes:
    Fertilisation: Manages the computation of fertilization-related data for different farm systems and scenarios.
"""

from itertools import product
import pandas as pd
from resource_manager.data_loader import Loader
from resource_manager.grassland_data_manager import DataManager
from resource_manager.scenario_data_fetcher import ScenarioDataFetcher

from grassland_production.grassland_area import Areas
from grassland_production.fertilisation import Fertilisation as Fert
from cattle_lca.lca import DailySpread
from geo_grassland_production.catchment_grassland import CatchmentGrass


class Fertilisation:
    """
    The Fertilisation class is responsible for calculating both inorganic and organic fertilization rates 
    and their application across various farm systems and scenarios. This class plays a crucial role in 
    the calculation of grassland production, providing insights into the environmental impact of fertilization 
    practices and aiding in the development of sustainable agricultural strategies.

    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year for historical data.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.

    Attributes:
        sc_class (ScenarioDataFetcher): Instance of ScenarioDataFetcher for fetching scenario data.
        catchment (str): The name of the catchment area.
        data_manager_class (DataManager): Instance of DataManager for managing data related to fertilization.
        loader_class (Loader): Instance of Loader to load various datasets.
        areas_class (Areas): Instance of Areas for calculating area-related data.
        cattle_spread_class (DailySpread): Instance for handling daily spread rates of fertilizers.
        calibration_year (int): The base year for data calibration.
        target_year (int): The target year for future scenario projections.
        catchment_grass (CatchmentGrass): Instance of CatchmentGrass for managing grassland data in the specified catchment.
        fert_class (Fert): Instance of Fertilisation class from the grassland production lib.
        default_calibration_year (int): The default year used for calibration if the specified year is not present in the data.
        default_grassland_year (int): The default grassland year used in calculations.

    Methods:
        compute_inorganic_fertilization_rate():
            Calculates the inorganic fertilization rate for various farm systems (dairy, beef, sheep) across 
            different scenarios, considering both historical data and future scenario projections.

        compute_organic_fertilization_rate():
            Computes the rate of organic fertilizer application (primarily cattle slurry) for different farm 
            systems, excluding sheep systems, and calculates the total organic nitrogen spread.

        organic_fertilisation_per_ha():
            Calculates the rate of organic fertilization per hectare for dairy and beef farm systems, adjusting 
            the total organic nitrogen spread to a per hectare basis and considering the area of different types 
            of grasslands within each farm system.
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
            scenario_animals_df,
            baseline_animals_df,
        )

        self.sc_class = ScenarioDataFetcher(scenario_data)

        self.catchment = self.sc_class.get_catchment_name()

        self.catchment_grass = CatchmentGrass(self.catchment,
            calibration_year,
            target_year,
            scenario_animals_df,
            baseline_animals_df,
        )


        self.calibration_year = self.data_manager_class.calibration_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.default_grassland_year = self.data_manager_class.default_grassland_year
        self.target_year = self.data_manager_class.target_year

        self.loader_class = Loader()
        self.areas_class = Areas(
            self.target_year, calibration_year, self.default_calibration_year
        )
        self.fert_class = Fert(ef_country,
                                calibration_year,
                                target_year,
                                scenario_data,
                                scenario_animals_df,
                                baseline_animals_df)

        self.cattle_spread_class = DailySpread(ef_country)



    def compute_inorganic_fertilization_rate(self):
        """
        Calculates the inorganic fertilization rate for various farm systems (dairy, beef, sheep) across 
        different scenarios. This method determines the average fertilization rate per grassland type 
        (Pasture, Silage, Hay) within each farm system, considering both historical data and future scenario 
        projections.

        The computation uses fertilization data by system and farm numbers to estimate the average fertilization 
        rate. For the target year, scenario-specific values are used for dairy and beef systems, while sheep 
        systems use an average value based on historical data.

        Returns:
            dict: A dictionary with keys for each farm system ('dairy', 'beef', 'sheep'), containing DataFrames 
                with fertilization rates for each grassland type. Each DataFrame is indexed by grassland type 
                and contains columns for the calibration year and the target year.

        Notes:
            - The method uses scenario-specific fertilization values for 'Pasture' and 'Grass silage' types in dairy 
            and beef systems. For sheep and other grassland types, average historical values are used.
        """

        inorganic_fertilization_rate = self.fert_class.compute_inorganic_fertilization_rate()

        return inorganic_fertilization_rate

    def compute_organic_fertilization_rate(self):
        """
        Computes the rate of organic fertilizer application (primarily cattle slurry) for different farm systems. 
        This calculation is based on the net excretion rate of nutrients from cattle, as determined by the DailySpread 
        class. The method considers the nutrient content in the cattle slurry and its spread rate across various farm 
        systems. Notably, sheep systems are excluded from this calculation, assuming that slurry consists only of cattle 
        slurry.

        The method calculates organic fertilization rates for both the calibration year and the target year under 
        different scenarios, considering the changes in livestock populations and management practices. 
        This is catchment specific.

        Returns:
            dict: A dictionary with keys for different scenarios. Each entry contains a DataFrame with columns 
                representing different farm systems ('dairy', 'beef', 'sheep') and rows representing years 
                (calibration year, target year). Each cell in the DataFrame represents the total organic 
                nitrogen spread for that farm system and year.

        Notes:
            - Sheep systems are excluded from this calculation.
        """
        organic_fertilization_rate = self.fert_class.compute_organic_fertilization_rate()

        return organic_fertilization_rate


    def organic_fertilisation_per_ha(self):
        """
        Calculates the rate of organic fertilization per hectare for dairy and beef farm systems. This method 
        adjusts the total organic nitrogen spread calculated in 'compute_organic_fertilization_rate' to a per 
        hectare basis, considering the area of different types of grasslands (Pasture, Grass silage) and the 
        proportion of these grasslands within each farm system.

        The calculation is performed for both the calibration year and the target year across various scenarios. 
        It provides a detailed view of how organic fertilization is distributed across different types of 
        grasslands within dairy and beef systems.

        Returns:
            dict: A dictionary with keys for different scenarios. Each entry contains a DataFrame with columns 
                for 'dairy' and 'beef' systems and rows for the calibration year and the target year. Each cell 
                in the DataFrame represents the organic nitrogen spread per hectare for that system and year.

        Notes:
            - Sheep systems are excluded from this calculation.
            - If data for the calibration year is not present, a default year is used.
        """
        spread_dict = self.compute_organic_fertilization_rate()
        grassland_areas = self.catchment_grass.get_catchment_grassland_area_caluclated()
        nfs_system_proportions = self.areas_class.get_nfs_system_proportions()
        
        dairy_nfs_system_proportions = nfs_system_proportions[0]
        beef_nfs_system_proportions = nfs_system_proportions[1]

        systems_dict = {
            "dairy": dairy_nfs_system_proportions,
            "beef": beef_nfs_system_proportions,
        }

        default_year_flag = True
        for _dict in spread_dict:
            for sys, year in product(
                spread_dict[_dict].columns, spread_dict[_dict].index[:-1]
            ):
            
                if sys != "sheep":
                    try:
                        organic_input = spread_dict[_dict].loc[int(year), sys]

                        spread_dict[_dict].loc[int(year), sys] = organic_input / (
                            (
                                grassland_areas.loc[(grassland_areas["cover_type"]=="Pasture"), "area_ha"].item()
                                * systems_dict[sys].loc[int(year), "Pasture"]
                            )
                            + (
                                grassland_areas.loc[(grassland_areas["cover_type"]=="Grass silage"), "area_ha"].item()
                                * systems_dict[sys].loc[int(year), "Grass silage"]
                            )
                        )
                    except KeyError:
                        if default_year_flag == True:
                            print(
                                f"... calibration year not present, {self.default_calibration_year} default year used for Spread Manure Dictionary..."
                            )
                            default_year_flag = False

                        organic_input = spread_dict[_dict].loc[int(year), sys]
                        spread_dict[_dict].loc[int(year), sys] = organic_input / (
                            (
                                grassland_areas.loc[(grassland_areas["cover_type"]=="Pasture"), "area_ha"].item()
                                * systems_dict[sys].loc[
                                    self.default_calibration_year, "Pasture"
                                ]
                            )
                            + (
                                grassland_areas.loc[(grassland_areas["cover_type"]=="Grass silage"), "area_ha"].item()
                                * systems_dict[sys].loc[
                                    self.default_calibration_year, "Grass silage"
                                ]
                            )
                        )

                spread_dict[_dict].loc[int(self.target_year), sys] = spread_dict[
                    _dict
                ].loc[int(self.calibration_year), sys]

        return spread_dict
