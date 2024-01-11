"""
==================
Farm Data Module
==================

This module includes the FarmData class which is responsible for computing various aspects of farm data, 
such as fertilization totals and farm data in different scenarios. This data is essential for lifecycle 
assessment calculations and agricultural planning.

Classes:
    FarmData: Manages the computation of farm data for lifecycle assessments and scenario analysis.
"""

import pandas as pd
import itertools
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.grassland_area import Areas
from grassland_production.spared_area import Grasslands
from grassland_production.fertilisation import Fertilisation


class FarmData:
    """
    The FarmData class handles the computation of various farm-related data elements, including 
    fertilization rates and overall farm data for baseline and future scenarios. This class plays 
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
        data_manager_class (DataManager): Instance of DataManager for managing scenario and baseline data.
        areas_class (Areas): Instance of Areas for calculating areas-related data.
        grassland_class (Grasslands): Instance for calculating grassland related data.
        fertiliser_class (Fertilisation): Instance for handling fertilization-related calculations.
        calibration_year (int): The base year for data calibration.
        target_year (int): The target year for future scenario projections.

    Methods:
        compute_fertilization_total():
            Calculates the total fertilization rates across different scenarios, considering various livestock 
            systems and grassland types.

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
        self.data_manager_class = DataManager(
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.calibration_year = self.data_manager_class.calibration_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.default_grassland_year = self.data_manager_class.default_grassland_year
        self.target_year = self.data_manager_class.target_year

        self.areas_class = Areas(
            self.target_year, self.calibration_year, self.default_calibration_year
        )
        self.grassland_class = Grasslands(
            ef_country,
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

        dairy_nfs_system_proportions = nfs_system_proportions[0]
        beef_nfs_system_proportions = nfs_system_proportions[1]
        sheep_nfs_system_proportions = nfs_system_proportions[2]

        SYS_PROPS = {
            "dairy": dairy_nfs_system_proportions,
            "beef": beef_nfs_system_proportions,
            "sheep": sheep_nfs_system_proportions,
        }

        grassland_type = self.data_manager_class.grasslands
        scenario_list = list(
            self.data_manager_class.scenario_inputs_df.Scenarios.unique()
        )

        year_list = list(
            (
                self.calibration_year,
                self.target_year,
            )
        )

        fert_rate_total = pd.DataFrame(0, columns=scenario_list, index=year_list)

        systems = self.data_manager_class.systems

        for sc, sys, g_type, year in itertools.product(scenario_list, systems, grassland_type, year_list):
            if year == self.target_year:
                
                fert_rate_total.loc[year, sc] += fert_rate[sys][sc].loc[
                        g_type, str(year)
                    ] * (
                        grass_total_area.loc[year, sc]
                        * SYS_PROPS[sys].loc[
                            self.calibration_year,
                            g_type,
                        ]
                        * nfs_within_grassland_proportions[sys].loc[
                            self.calibration_year,
                            g_type,
                        ]
                    )
            else:
                fert_rate_total.loc[year, sc] += fert_rate[sys][sc].loc[
                    g_type, str(year)
                ] * (
                    grass_total_area.loc[year, sc]
                    * SYS_PROPS[sys].loc[year, g_type]
                    * nfs_within_grassland_proportions[sys].loc[
                        year, g_type
                    ]
                )
        return fert_rate_total


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

        farm_data = pd.DataFrame()

        try:
            
            Share_fertilizer = pd.DataFrame(index=[calibration_year])

            Share_fertilizer["prop_p"] = FAO_fertilizer.loc[calibration_year, "Total_P_t"].item() / NIR_fertilizer.loc[calibration_year, "Total_N_t"].item() 
            Share_fertilizer["prop_k"] = FAO_fertilizer.loc[calibration_year, "Total_K_t"].item() / NIR_fertilizer.loc[calibration_year, "Total_N_t"].item() 
            Share_fertilizer["Lime_t"] = NIR_fertilizer.loc[calibration_year,"Lime_t"].item()
        except KeyError:
            default_calibration_year = self.default_calibration_year
            Share_fertilizer = pd.DataFrame(index=[calibration_year])

            Share_fertilizer["prop_p"] = FAO_fertilizer.loc[default_calibration_year, "Total_P_t"].item() / NIR_fertilizer.loc[default_calibration_year, "Total_N_t"].item() 
            Share_fertilizer["prop_k"] = FAO_fertilizer.loc[default_calibration_year, "Total_K_t"].item() / NIR_fertilizer.loc[default_calibration_year, "Total_N_t"].item() 
            Share_fertilizer["Lime_t"] = NIR_fertilizer.loc[default_calibration_year,"Lime_t"].item()
            print(
                "... calibration year not present, 2015 default year used for Scenario farm data generation"
            )

        new_index = 0
        for index in fert_rate_total.columns:
            urea_mask = (self.data_manager_class.scenario_inputs_df["Scenarios"]==index)

            farm_data.loc[new_index, "ef_country"] = "ireland"
            farm_data.loc[new_index, "farm_id"] = index
            farm_data.loc[new_index, "year"] = int(target_year)

            share_urea = self.data_manager_class.scenario_inputs_df.loc[urea_mask, "Urea proportion"].unique()
            share_urea_abated = self.data_manager_class.scenario_inputs_df.loc[urea_mask, "Urea abated proportion"].unique()

            urea_t = ((
                share_urea
                * fert_rate_total.loc[target_year, index].item()
            )* 100)/46


            farm_data.loc[new_index, "total_urea_kg"] = urea_t 

            farm_data.loc[new_index, "total_lime_kg"] = Share_fertilizer.loc[
                calibration_year, "Lime_t"
            ].item()

            farm_data.loc[new_index, "an_n_fert"] = (
                (1-share_urea)
                * fert_rate_total.loc[target_year, index].item()
            )


            farm_data.loc[new_index, "urea_n_fert"] = (
                share_urea
                * fert_rate_total.loc[target_year, index].item()
            ) * (1 - share_urea_abated)

            farm_data.loc[new_index, "urea_abated_n_fert"] = (
                share_urea
                * fert_rate_total.loc[target_year, index].item()
            ) * share_urea_abated


            farm_data.loc[new_index, "total_p_fert"] = (
                Share_fertilizer.loc[calibration_year, "prop_p"].item()
                * fert_rate_total.loc[target_year, index].item()
            )

            farm_data.loc[new_index, "total_k_fert"] = (
                Share_fertilizer.loc[calibration_year, "prop_k"].item()
                * fert_rate_total.loc[target_year, index].item()
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
            - The method attempts to use the data from the calibration year; if unavailable, it falls back to a 
            default year.
            - This method is essential for establishing a baseline in LCA studies, against which future scenarios 
            and changes in agricultural practices can be compared.
            - Data includes total amounts of urea, lime, nitrogenous (N), phosphorus (P), and potassium (K) fertilizers, 
            along with diesel and electricity usage.
            - Diesel and Eelectricity usage are set to 0 for now, as they are not used in the current GOBLIN model.
        """
        calibration_year = self.calibration_year

        FAO_fertilizer = self.loader_class.fao_fertilization()
        NIR_fertilizer = self.loader_class.nir_fertilization()

        farm_data = pd.DataFrame()


        new_index = 0

        try:
            
            AN_fert = NIR_fertilizer.loc[calibration_year, "Total_N_t"].item() - NIR_fertilizer.loc[calibration_year, "Urea_N_t"].item()

            farm_data.loc[new_index, "ef_country"] = "ireland"
            farm_data.loc[new_index, "farm_id"] = calibration_year
            farm_data.loc[new_index, "year"] = int(calibration_year)
            farm_data.loc[new_index, "total_urea_kg"] = NIR_fertilizer.loc[
                calibration_year, "Urea_t"
            ].item()
            farm_data.loc[new_index, "total_lime_kg"] = NIR_fertilizer.loc[
                calibration_year, "Lime_t"
            ].item()
            farm_data.loc[new_index, "an_n_fert"] = AN_fert

            farm_data.loc[new_index, "urea_n_fert"] = NIR_fertilizer.loc[
                calibration_year, "Urea_N_t"
            ].item()

            farm_data.loc[new_index, "urea_abated_n_fert"] = 0

            farm_data.loc[new_index, "total_p_fert"] = FAO_fertilizer.loc[
                calibration_year, "Total_P_t"
            ].item()
            farm_data.loc[new_index, "total_k_fert"] = FAO_fertilizer.loc[
                calibration_year, "Total_K_t"
            ].item()

            farm_data.loc[new_index, "diesel_kg"] = 0
            farm_data.loc[new_index, "elec_kwh"] = 0

        except KeyError:
            default_calibration_year = self.default_calibration_year

            AN_fert = NIR_fertilizer.loc[calibration_year, "Total_N_t"].item() - NIR_fertilizer.loc[calibration_year, "Urea_N_t"].item()

            farm_data.loc[new_index, "ef_country"] = "ireland"
            farm_data.loc[new_index, "farm_id"] = calibration_year
            farm_data.loc[new_index, "year"] = int(calibration_year)
            farm_data.loc[new_index, "total_urea_kg"] = NIR_fertilizer.loc[
                default_calibration_year, "Urea_t"
            ].item()
            farm_data.loc[new_index, "total_lime_kg"] = NIR_fertilizer.loc[
                default_calibration_year, "Lime_t"
            ].item()
            farm_data.loc[new_index, "an_n_fert"] = AN_fert

            farm_data.loc[new_index, "urea_n_fert"] = NIR_fertilizer.loc[
                default_calibration_year, "Urea_N_t"
            ].item()
            farm_data.loc[new_index, "urea_abated_n_fert"] = 0

            farm_data.loc[new_index, "total_p_fert"] = FAO_fertilizer.loc[
                default_calibration_year, "Total_P_t"
            ].item()
            farm_data.loc[new_index, "total_k_fert"] = FAO_fertilizer.loc[
                default_calibration_year, "Total_K_t"
            ].item()

            farm_data.loc[new_index, "diesel_kg"] = 0
            farm_data.loc[new_index, "elec_kwh"] = 0

            print(
                "... calibration year not present, 2015 default year used for total Baseline farm data"
            )

        return farm_data