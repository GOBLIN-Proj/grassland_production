"""
====================
Geo Farm Data Module
====================

This module includes the FarmData class which is responsible for computing various aspects of farm data, 
such as fertilization totals and farm data in different scenarios in a specific catchment. This data is essential for lifecycle 
assessment calculations and agricultural planning.

Classes:
    FarmData: Manages the computation of farm data for lifecycle assessments and scenario analysis.
"""

import pandas as pd
import itertools
from grassland_production.resource_manager.data_loader import Loader
from grassland_production.resource_manager.grassland_data_manager import DataManager
from grassland_production.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from grassland_production.grassland_area import Areas
from grassland_production.geo_grassland_production.geo_spared_area import GeoGrasslands
from grassland_production.geo_grassland_production.geo_fertilisation import GeoFertilisation


class FarmData:
    """
    The FarmData class handles the computation of various farm-related data elements, including 
    fertilization rates and overall farm data for baseline and future scenarios in specific catchments. This class plays 
    a pivotal role in lifecycle assessment and agricultural scenario analysis by providing essential 
    data for these processes.

    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.

    Attributes:
        loader_class (Loader): Instance of Loader to load various datasets.
        sc_class (ScenarioDataFetcher): Instance of ScenarioDataFetcher for fetching scenario data.
        scenario_list (list): List of scenarios for analysis.
        data_manager_class (DataManager): Instance of DataManager for managing scenario and baseline data.
        ef_country (str): The country for which the analysis is performed.
        areas_class (Areas): Instance of Areas for calculating areas-related data.
        grassland_class (Grasslands): Instance for calculating grassland related data.
        fertiliser_class (Fertilisation): Instance for handling fertilization-related calculations.
        calibration_year (int): The base year for data calibration.
        target_year (int): The target year for future scenario projections.
        default_calibration_year (int): The default calibration year.
        default_grassland_year (int): The default grassland year.
        default_urea (float): The default proportion of urea.
        default_urea_abated (float): The default proportion of abated urea.

    Methods:
        compute_fertilization_total():
            Calculates the total fertilization rates across different scenarios, considering various livestock 
            systems and grassland types.
        
        compute_npk_value():
            Calculates the NPK value for a given year, scenario, livestock system, and grassland type.

        compute_lime_value():
            Calculates the lime value for a given year, scenario, livestock system, and grassland type.

        compute_farm_data_in_scenarios():
            Computes farm data required for lifecycle assessment in different future scenarios.

        compute_farm_data_in_baseline():
            Computes baseline farm data for use in lifecycle assessments and scenario comparisons.
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
        self.loader_class = Loader()
        
        self.sc_class = ScenarioDataFetcher(scenario_data)
        self.scenario_list = self.sc_class.get_scenario_list()

        self.data_manager_class = DataManager(
            calibration_year,
            target_year,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.ef_country = self.data_manager_class.get_ef_country()
        self.calibration_year = self.data_manager_class.get_calibration_year()
        self.default_calibration_year = self.data_manager_class.get_default_calibration_year()
        self.default_grassland_year = self.data_manager_class.get_default_grassland_year()
        self.target_year = self.data_manager_class.get_target_year()
        self.default_urea = self.data_manager_class.get_default_urea_proportion()
        self.default_urea_abated = self.data_manager_class.get_default_urea_abated_proportion()

        self.areas_class = Areas(
            self.target_year, self.calibration_year, self.default_calibration_year
        )
        self.grassland_class = GeoGrasslands(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.fertiliser_class = GeoFertilisation(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )

    def compute_fertilization_total(self):
        """
        Calculation of total fertilisation rate across scenarios.

        This function aggregates the values for the livestock systems (Dairy, Beef, Sheep) and grassland types (Pasture, Silage, Hay, Rough grazing in use).

        If the year is less than 2005, outside the NFS range, a mean value across years is used.

        For past years, the livestock system proportions for that year are utilised in the calculations as weights for grassland types.
        Again, a mean value is used for past years outside the NFS range.
        In relation to the target year and the grassland type weights, the calibration year is used.

        The self.fert_rate_total is used to set the farm_data

        """
        fert_rate = self.fertiliser_class.compute_inorganic_fertilization_rate()

        grass_total_area = self.grassland_class.get_grass_total_area()
        nfs_within_grassland_proportions = (
            self.areas_class.get_nfs_within_system_grassland_distribution()
        )

        nfs_system_proportions = self.areas_class.get_nfs_system_proportions()

        lime_proportions = self.loader_class.lime_fertiliser_proportion_by_system()

        dairy_nfs_system_proportions = nfs_system_proportions[0]
        beef_nfs_system_proportions = nfs_system_proportions[1]
        sheep_nfs_system_proportions = nfs_system_proportions[2]

        SYS_PROPS = {
            "dairy": dairy_nfs_system_proportions,
            "beef": beef_nfs_system_proportions,
            "sheep": sheep_nfs_system_proportions,
        }

        grassland_type = self.data_manager_class.get_grassland_types()

        dataframes = {
            "fert_rate": fert_rate,
            "grass_total_area": grass_total_area,
            "nfs_within_grassland_proportions": nfs_within_grassland_proportions,
            "SYS_PROPS": SYS_PROPS,
            "grassland_type": grassland_type,
            "lime_proportions": lime_proportions,
        }

        scenario_list = self.scenario_list

        year_list = list(
            (   
                self.calibration_year,
                self.target_year,
            )
        )

        columns = ["type"] + scenario_list

        fert_type = ["NPK", "Lime"]
        # Create the MultiIndex
        multi_index = pd.MultiIndex.from_product([year_list, fert_type], names=['Year', 'Fertilizer Type'])
        fert_rate_total = pd.DataFrame(None, columns=columns, index=multi_index)

        systems = self.data_manager_class.get_farming_systems()

        for sc, sys, g_type, fert, year in itertools.product(scenario_list, systems, grassland_type, fert_type, year_list):
            fert_rate_total.loc[(year, fert), "type"] = fert

            if pd.isna(fert_rate_total.loc[(year, fert), sc]):  # Or use .isnull()
                fert_rate_total.loc[(year, fert), sc] = 0 
            if fert == "NPK":
                fert_rate_total.loc[(year, fert), sc] += self.compute_npk_value(year, sc, sys, g_type, dataframes)
            elif fert == "Lime":
                fert_rate_total.loc[(year, fert), sc] += self.compute_lime_value(year, sc, sys, g_type, dataframes)

        return fert_rate_total
        

    def compute_npk_value(self, year, sc, sys, g_type, dataframes):

        def calculate_npk_value(year, cal_year, sc, g_type, sys, dataframes):

            sc_year = year
            
            fert_rate= dataframes.get("fert_rate")[sys][sc].loc[g_type, str(year)].item()
            grass_total_area = dataframes["grass_total_area"].loc[sc_year, sc].item()
            system_proportions = dataframes["SYS_PROPS"][sys].loc[cal_year, g_type].item()
            nfs_proportions = dataframes["nfs_within_grassland_proportions"][sys].loc[cal_year, g_type].item()


            return fert_rate * grass_total_area * system_proportions * nfs_proportions
        
        try:
            cal_year = self.calibration_year if year == self.target_year else year

            return calculate_npk_value(year, cal_year, sc, g_type, sys,dataframes)
        
        except KeyError:
            print("Calibration year not present, default year 2015 used for NPK value")
            cal_year = self.default_calibration_year

            return calculate_npk_value(year, cal_year, sc, g_type, sys, dataframes)


    def compute_lime_value(self, year, sc, sys, g_type, dataframes):

        system_names = {
            "dairy": "Dairy",
            "beef": "Cattle",
            "sheep": "Sheep",
        }


        lime_proportions = dataframes.get("lime_proportions")
        lime_rate = self.data_manager_class.get_lime_rate()


        def calculate_lime_value(year, cal_year, sc, g_type, sys, lime_proportions, lime_rate, dataframes):

            sc_year = year

            grass_total_area = dataframes["grass_total_area"].loc[sc_year, sc].item()
            system_proportions = dataframes["SYS_PROPS"][sys].loc[cal_year, g_type].item()
            nfs_proportions = dataframes["nfs_within_grassland_proportions"][sys].loc[cal_year, g_type].item()
            lime_prop = lime_proportions.loc[system_names[sys], str(cal_year)].item()

            return lime_rate * grass_total_area * system_proportions * nfs_proportions * lime_prop
        
        try:
            cal_year = self.calibration_year if year == self.target_year else year

            return calculate_lime_value(year, cal_year, sc, g_type, sys, lime_proportions, lime_rate, dataframes)
        
        except KeyError:
            print("Calibration year not present, default year 2015 used for Lime value")
            cal_year = self.default_calibration_year

            return calculate_lime_value(year, cal_year, sc, g_type, sys, lime_proportions, lime_rate, dataframes)




    def compute_farm_data_in_scenarios(self):
        """
        Computes farm data for various future scenarios to be used in lifecycle assessment (LCA) calculations. 
        This method integrates data on fertilizer usage, urea proportions, and other farm-specific details to 
        generate a comprehensive dataset for each scenario.

        The computation involves determining the proportions of different types of fertilizers (P, K, Lime) and 
        calculating the total usage of each based on the fertilization rates and scenarios. It also accounts for 
        urea usage and abatement (abated urea) in the scenarios.

        Returns:
            DataFrame: A pandas DataFrame with farm data for each scenario. Each row corresponds to a scenario, 
                    including information about fertilizer usage, urea proportions, and other essential data 
                    for LCA calculations.

        Notes:
            - The method attempts to use the calibration year data; if unavailable, it falls back to a default year.
            - Data includes total amounts of urea, lime, nitrogenous (N), phosphorus (P), and potassium (K) fertilizers,
            along with diesel and electricity usage.
            - Diesel and Eelectricity usage are set to 0 for now, as they are not used in the current GOBLIN model.
        """
        calibration_year = self.calibration_year
        target_year = self.target_year

        FAO_fertilizer = self.loader_class.fao_fertilization()
        NIR_fertilizer = self.loader_class.nir_fertilization()

        fert_rate_total = self.compute_fertilization_total()

        scenario_inputs_df = self.sc_class.get_scenario_dataframe()

        farm_data = pd.DataFrame()

        try:
            
            Share_fertilizer = pd.DataFrame(index=[calibration_year])

            Share_fertilizer["prop_p"] = FAO_fertilizer.loc[calibration_year, "Total_P_t"].item() / NIR_fertilizer.loc[calibration_year, "Total_N_t"].item() 
            Share_fertilizer["prop_k"] = FAO_fertilizer.loc[calibration_year, "Total_K_t"].item() / NIR_fertilizer.loc[calibration_year, "Total_N_t"].item() 

        except KeyError:
            default_calibration_year = self.default_calibration_year
            Share_fertilizer = pd.DataFrame(index=[calibration_year])

            Share_fertilizer["prop_p"] = FAO_fertilizer.loc[default_calibration_year, "Total_P_t"].item() / NIR_fertilizer.loc[default_calibration_year, "Total_N_t"].item() 
            Share_fertilizer["prop_k"] = FAO_fertilizer.loc[default_calibration_year, "Total_K_t"].item() / NIR_fertilizer.loc[default_calibration_year, "Total_N_t"].item() 

            print(
                "... calibration year not present, 2015 default year used for Scenario farm data generation"
            )

        new_index = 0
        for index in self.scenario_list:
            urea_mask = (scenario_inputs_df["Scenarios"]==index)

            farm_data.loc[new_index, "ef_country"] = self.ef_country
            farm_data.loc[new_index, "farm_id"] = index
            farm_data.loc[new_index, "year"] = int(target_year)

            share_urea = scenario_inputs_df.loc[urea_mask, "Urea proportion"].unique()
            share_urea_abated = scenario_inputs_df.loc[urea_mask, "Urea abated proportion"].unique()

        
            urea_t = ((
                share_urea
                * fert_rate_total.loc[(target_year,"NPK"), index]
            )* 100)/46


            farm_data.loc[new_index, "total_urea_kg"] = urea_t 

            farm_data.loc[new_index, "total_lime_kg"] = fert_rate_total.loc[(target_year,"Lime"), index]

            farm_data.loc[new_index, "an_n_fert"] = (
                (1-share_urea)
                * fert_rate_total.loc[(target_year,"NPK"), index]
            )


            farm_data.loc[new_index, "urea_n_fert"] = (
                share_urea
                * fert_rate_total.loc[(target_year,"NPK"), index]
            ) * (1 - share_urea_abated)

            farm_data.loc[new_index, "urea_abated_n_fert"] = (
                share_urea
                * fert_rate_total.loc[(target_year,"NPK"), index]
            ) * share_urea_abated


            farm_data.loc[new_index, "total_p_fert"] = (
                Share_fertilizer.loc[calibration_year, "prop_p"].item()
                * fert_rate_total.loc[(target_year,"NPK"), index]
            )

            farm_data.loc[new_index, "total_k_fert"] = (
                Share_fertilizer.loc[calibration_year, "prop_k"].item()
                * fert_rate_total.loc[(target_year,"NPK"), index]
            )

            farm_data.loc[new_index, "diesel_kg"] = 0
            farm_data.loc[new_index, "elec_kwh"] = 0

            new_index += 1

        return farm_data


    def compute_farm_data_in_baseline(self):
        """
        Computes baseline farm data for use in lifecycle assessment (LCA) calculations. This method focuses on 
        generating a dataset reflecting the baseline agricultural practices and inputs for the calibration year, 
        which serves as a reference point.

        The computation includes the assessment of various types of fertilizers (P, K, Lime, Urea) and their 
        quantities used in the calibration year. It also accounts for diesel and electricity (currently set to zero) usage in farming 
        operations.

        Returns:
            DataFrame: A pandas DataFrame containing baseline farm data. It includes detailed information about 
                    fertilizer usage, urea proportions, and other essential data elements for LCA calculations.

        Notes:
            - Data includes total amounts of urea, lime, nitrogenous (N), phosphorus (P), and potassium (K) fertilizers, 
            along with diesel and electricity usage.
            - Diesel and Eelectricity usage are set to 0 for now, as they are not used in the current GOBLIN model.
        """
        calibration_year = self.calibration_year

        FAO_fertilizer = self.loader_class.fao_fertilization()
        NIR_fertilizer = self.loader_class.nir_fertilization()
        fert_rate_total = self.compute_fertilization_total()
        index_col = 0
        
        farm_data = pd.DataFrame()

        try:
            
            Share_fertilizer = pd.DataFrame(index=[calibration_year])

            Share_fertilizer["prop_p"] = FAO_fertilizer.loc[calibration_year, "Total_P_t"].item() / NIR_fertilizer.loc[calibration_year, "Total_N_t"].item() 
            Share_fertilizer["prop_k"] = FAO_fertilizer.loc[calibration_year, "Total_K_t"].item() / NIR_fertilizer.loc[calibration_year, "Total_N_t"].item() 

        except KeyError:
            default_calibration_year = self.default_calibration_year
            Share_fertilizer = pd.DataFrame(index=[calibration_year])

            Share_fertilizer["prop_p"] = FAO_fertilizer.loc[default_calibration_year, "Total_P_t"].item() / NIR_fertilizer.loc[default_calibration_year, "Total_N_t"].item() 
            Share_fertilizer["prop_k"] = FAO_fertilizer.loc[default_calibration_year, "Total_K_t"].item() / NIR_fertilizer.loc[default_calibration_year, "Total_N_t"].item() 

            print(
                "... calibration year not present, 2015 default year used for Scenario farm data generation"
            )

        urea_t = ((
                self.default_urea
                * fert_rate_total.loc[(calibration_year,"NPK"), index_col]
            )* 100)/46

        new_index = 0
            
        farm_data.loc[new_index, "ef_country"] = self.ef_country
        farm_data.loc[new_index, "farm_id"] = calibration_year
        farm_data.loc[new_index, "year"] = int(calibration_year)
        farm_data.loc[new_index, "total_urea_kg"] = urea_t 

        farm_data.loc[new_index, "total_lime_kg"] = fert_rate_total.loc[(calibration_year,"Lime"), index_col]

        farm_data.loc[new_index, "an_n_fert"] = ((1-self.default_urea) * fert_rate_total.loc[(calibration_year,"NPK"), index_col])

        farm_data.loc[new_index, "urea_n_fert"] = (
            self.default_urea
            * fert_rate_total.loc[(calibration_year,"NPK"), index_col]
        ) * (1 - self.default_urea_abated)

        farm_data.loc[new_index, "urea_abated_n_fert"] = (
            self.default_urea
            * fert_rate_total.loc[(calibration_year,"NPK"), index_col]
        ) * self.default_urea_abated


        farm_data.loc[new_index, "total_p_fert"] = (
            Share_fertilizer.loc[calibration_year, "prop_p"].item()
            * fert_rate_total.loc[(calibration_year,"NPK"), index_col]
        )

        farm_data.loc[new_index, "total_k_fert"] = (
            Share_fertilizer.loc[calibration_year, "prop_k"].item()
            * fert_rate_total.loc[(calibration_year,"NPK"), index_col]
        )

        farm_data.loc[new_index, "diesel_kg"] = 0
        farm_data.loc[new_index, "elec_kwh"] = 0

        farm_data.loc[new_index, "diesel_kg"] = 0
        farm_data.loc[new_index, "elec_kwh"] = 0

        return farm_data