
import pandas as pd
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.grassland_area import Areas
from grassland_production.spared_area import Grasslands
from cattle_lca.lca import DailySpread
from grassland_production.fertilisation import Fertilisation


class FarmData: 
    
    def __init__(self, ef_country, calibration_year, scenario_data, scenario_animals_df, basline_animals_df):

        self.data_manager_class = DataManager(calibration_year, scenario_data, scenario_animals_df,basline_animals_df)
        
        self.calibration_year = self.data_manager_class.calibration_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.default_grassland_year = self.data_manager_class.default_grassland_year
        self.target_year = self.data_manager_class.target_year
    
        self.loader_class = Loader()
        self.data_manager_class = DataManager(calibration_year, scenario_data, scenario_animals_df,basline_animals_df)
        self.areas_class = Areas(self.target_year, self.calibration_year, self.default_calibration_year)
        self.grassland_class = Grasslands(ef_country, calibration_year, scenario_data, scenario_animals_df,basline_animals_df)
        self.fertiliser_class = Fertilisation(ef_country, calibration_year, scenario_data, scenario_animals_df,basline_animals_df)



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
        nfs_within_grassland_proportions = self.areas_class.get_nfs_within_system_grassland_distribution()
        
        nfs_system_proportions = self.areas_class.get_nfs_system_proportions()

        dairy_nfs_system_proportions = nfs_system_proportions[0]
        beef_nfs_system_proportions = nfs_system_proportions[1]
        sheep_nfs_system_proportions= nfs_system_proportions[2]
        
        grassland_type = self.data_manager_class.grasslands
        scenario_list = list(self.data_manager_class.scenario_inputs_df.Scenarios.unique())

        year_list = list(
            (
                self.calibration_year,
                self.target_year,
            )
        )

        fert_rate_total = pd.DataFrame(0, columns=scenario_list, index=year_list)

        systems = self.data_manager_class.systems

        for sc in scenario_list:
            for sys in systems:
                for g_type in grassland_type:

                    for year in year_list:

                        if year == self.target_year:

                            if sys == "dairy":
                                fert_rate_total.loc[
                                    year, sc
                                ] += fert_rate[sys][sc].loc[g_type, str(year)] * (
                                    grass_total_area.loc[year, sc]
                                    * dairy_nfs_system_proportions.loc[
                                            self.calibration_year ,
                                        g_type,
                                    ]
                                    * nfs_within_grassland_proportions[sys].loc[
                                            self.calibration_year,
                                        g_type,
                                    ]
                                )
                            elif sys == "beef":
                                fert_rate_total.loc[
                                    year, sc
                                ] += fert_rate[sys][sc].loc[g_type, str(year)] * (
                                    grass_total_area.loc[year, sc]
                                    * beef_nfs_system_proportions.loc[
                                            self.calibration_year,
                                        g_type,
                                    ]
                                    * nfs_within_grassland_proportions[sys].loc[
                                            self.calibration_year,
                                        g_type,
                                    ]
                                )
                            elif sys == "sheep":
                                fert_rate_total.loc[
                                    year, sc
                                ] += fert_rate[sys][sc].loc[g_type, str(year)] * (
                                    grass_total_area.loc[year, sc]
                                    * sheep_nfs_system_proportions.loc[
                                            self.calibration_year,
                                        g_type,
                                    ]
                                    * nfs_within_grassland_proportions[sys].loc[
                                            self.calibration_year,
                                        g_type,
                                    ]
                                )

                        else:

                            if sys == "dairy":
                                fert_rate_total.loc[
                                    year, sc
                                ] += fert_rate[sys][sc].loc[g_type, str(year)] * (
                                    grass_total_area.loc[year, sc]
                                    * dairy_nfs_system_proportions.loc[
                                        year, g_type
                                    ]
                                    * nfs_within_grassland_proportions[sys].loc[
                                        year, g_type
                                    ]
                                )
                            elif sys == "beef":
                                fert_rate_total.loc[
                                    year, sc
                                ] += fert_rate[sys][sc].loc[g_type, str(year)] * (
                                    grass_total_area.loc[year, sc]
                                    * beef_nfs_system_proportions.loc[
                                        year, g_type
                                    ]
                                    * nfs_within_grassland_proportions[sys].loc[
                                        year, g_type
                                    ]
                                )
                            elif sys == "sheep":
                                fert_rate_total.loc[
                                    year, sc
                                ] += fert_rate[sys][sc].loc[g_type, str(year)] * (
                                    grass_total_area.loc[year, sc]
                                    * sheep_nfs_system_proportions.loc[
                                        year, g_type
                                    ]
                                    * nfs_within_grassland_proportions[sys].loc[
                                        year, g_type
                                    ]
                                )
        return fert_rate_total
    

    def compute_farm_data_in_scenarios(self):
        """
        Computation of farm_data, exported for use in LCA calculation in goblin tool
        """
        calibration_year = self.calibration_year
        target_year = self.target_year

        FAO_fertilizer = self.loader_class.fao_fertilization()

        
        fert_rate_total = self.compute_fertilization_total()

        farm_data = pd.DataFrame()

        try:
            if "Urea abated" in FAO_fertilizer.columns:
                FAO_fertilizer["Total N"] = (
                    FAO_fertilizer["Urea"]
                    + FAO_fertilizer["N"]
                    + FAO_fertilizer["Urea abated"]
                )
            else:
                FAO_fertilizer["Total N"] = FAO_fertilizer["Urea"] + FAO_fertilizer["N"]
                FAO_fertilizer["Urea abated"] = 0
            N_type_list = ["Urea", "N", "Urea abated"]

            Share_fertilizer = pd.DataFrame(
                columns=N_type_list, index=[calibration_year]
            )
            for N_type in N_type_list:
                Share_fertilizer.loc[
                    calibration_year, N_type
                ] = (
                    FAO_fertilizer.loc[calibration_year, N_type]
                    / FAO_fertilizer.loc[calibration_year, "Total N"]
                )

            Share_fertilizer["prop_p"] = FAO_fertilizer["P"]/FAO_fertilizer["Total N"]
            Share_fertilizer["prop_k"] = FAO_fertilizer["K"]/FAO_fertilizer["Total N"]

        except KeyError:
            calibration_year = self.default_calibration_year
            if "Urea abated" in FAO_fertilizer.columns:
                FAO_fertilizer["Total N"] = (
                    FAO_fertilizer["Urea"]
                    + FAO_fertilizer["N"]
                    + FAO_fertilizer["Urea abated"]
                )
            else:
                FAO_fertilizer["Total N"] = FAO_fertilizer["Urea"] + FAO_fertilizer["N"]
                FAO_fertilizer["Urea abated"] = 0
            N_type_list = ["Urea", "N", "Urea abated"]

            Share_fertilizer = pd.DataFrame(
                columns=N_type_list, index=[calibration_year]
            )
            for N_type in N_type_list:
                Share_fertilizer.loc[
                    calibration_year, N_type
                ] = (
                    FAO_fertilizer.loc[calibration_year, N_type]
                    / FAO_fertilizer.loc[calibration_year, "Total N"]
                )
            print("... calibration year not present, 2015 default year used for Scenario farm data generation")

        Share_fertilizer["prop_p"] = FAO_fertilizer["P"]/FAO_fertilizer["Total N"]
        Share_fertilizer["prop_k"] = FAO_fertilizer["K"]/FAO_fertilizer["Total N"]

        new_index = 0
        for index in fert_rate_total.columns:

            farm_data.loc[new_index, "ef_country"] = "ireland"
            farm_data.loc[new_index, "farm_id"] = index
            farm_data.loc[new_index, "year"] = int(
                target_year
            )
            farm_data.loc[new_index, "total_urea"] = (
                Share_fertilizer.loc[
                    calibration_year, "Urea"
                ]
                * fert_rate_total.loc[
                    target_year, index
                ]
            )
            farm_data.loc[new_index, "total_urea_abated"] = (
                Share_fertilizer.loc[
                    calibration_year, "Urea abated"
                ]
                * fert_rate_total.loc[
                    target_year, index
                ]
            )
            farm_data.loc[new_index, "total_n_fert"] = (
                Share_fertilizer.loc[calibration_year, "N"]
                * fert_rate_total.loc[
                    target_year, index
                ]
            )

            farm_data.loc[new_index, "total_p_fert"] = (
                Share_fertilizer.loc[calibration_year, "prop_p"]
                * fert_rate_total.loc[
                    target_year, index
                ]
            )

            farm_data.loc[new_index, "total_k_fert"] = (
                Share_fertilizer.loc[calibration_year, "prop_k"]
                * fert_rate_total.loc[
                    target_year, index
                ]
            )

            farm_data.loc[new_index, "diesel_kg"] = 0
            farm_data.loc[new_index, "elec_kwh"] = 0

            new_index += 1

        return farm_data


    def compute_farm_data_in_baseline(self):
        """
        Computation of farm_data, exported for use in LCA calculation in goblin tool
        """
        calibration_year = self.calibration_year

        FAO_fertilizer = self.loader_class.fao_fertilization()


        farm_data = pd.DataFrame()

        
        if "Urea abated" in FAO_fertilizer.columns:
            FAO_fertilizer["Total N"] = (
                FAO_fertilizer["Urea"]
                + FAO_fertilizer["N"]
                + FAO_fertilizer["Urea abated"]
            )
        else:
            FAO_fertilizer["Total N"] = FAO_fertilizer["Urea"] + FAO_fertilizer["N"]
            FAO_fertilizer["Urea abated"] = 0



        new_index = 0


        try:
            farm_data.loc[new_index, "ef_country"] = "ireland"
            farm_data.loc[new_index, "farm_id"] = calibration_year
            farm_data.loc[new_index, "year"] = int(
                calibration_year
            )
            farm_data.loc[new_index, "total_urea"] = FAO_fertilizer.loc[calibration_year, "Urea"]
            farm_data.loc[new_index, "total_urea_abated"] = FAO_fertilizer.loc[calibration_year, "Urea abated"]
            farm_data.loc[new_index, "total_n_fert"] = FAO_fertilizer.loc[calibration_year, "N"]
            farm_data.loc[new_index, "total_p_fert"] = FAO_fertilizer.loc[calibration_year, "P"]
            farm_data.loc[new_index, "total_k_fert"] = FAO_fertilizer.loc[calibration_year, "K"]

            farm_data.loc[new_index, "diesel_kg"] = 0
            farm_data.loc[new_index, "elec_kwh"] = 0

        except KeyError:

            default_calibration_year = self.default_calibration_year

            farm_data.loc[new_index, "ef_country"] = "ireland"
            farm_data.loc[new_index, "farm_id"] = calibration_year
            farm_data.loc[new_index, "year"] = int(
                calibration_year
            )
            farm_data.loc[new_index, "total_urea"] = FAO_fertilizer.loc[default_calibration_year, "Urea"]
            farm_data.loc[new_index, "total_urea_abated"] = FAO_fertilizer.loc[default_calibration_year, "Urea abated"]
            farm_data.loc[new_index, "total_n_fert"] = FAO_fertilizer.loc[default_calibration_year, "N"]
            farm_data.loc[new_index, "total_p_fert"] = FAO_fertilizer.loc[default_calibration_year, "P"]
            farm_data.loc[new_index, "total_k_fert"] = FAO_fertilizer.loc[default_calibration_year, "K"]

            farm_data.loc[new_index, "diesel_kg"] = 0
            farm_data.loc[new_index, "elec_kwh"] = 0

            print("... calibration year not present, 2015 default year used for total Baseline farm data")

        return farm_data
    