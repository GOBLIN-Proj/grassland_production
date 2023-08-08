import pandas as pd
import copy
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.spared_area import Grasslands
import cattle_lca.lca as cattle_lca
import sheep_lca.lca as sheep_lca

class StockingRate:
    def __init__(self,ef_country, calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df):
        self.data_manager_class = DataManager(calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df)
        self.calibration_year = self.data_manager_class.calibration_year
        self.target_year = self.data_manager_class.target_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.loader_class = Loader()
        self.livestock_unit_values = self.loader_class.livestock_units()
        self.grassland_class = Grasslands(ef_country, calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df)


    def get_livestock_units(self):


        """
        Produces the livestock units present on each of the three farm types

        """

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        baseline_animals_df = self.data_manager_class.baseline_animals_df
        scenario_animals_df = self.data_manager_class.scenario_animals_df

        keys = self.data_manager_class.systems

        animal_list = list(self.data_manager_class.COHORTS_DICT["Cattle"]) + list(
            self.data_manager_class.COHORTS_DICT["Sheep"]
        )

        past_livestock_units = pd.DataFrame(0, index=year_list, columns=keys)

        livestock_units = {}

        for animal_name in animal_list:

            animal_past = getattr(self.data_manager_class.baseline_animals_dict[self.calibration_year]["animals"], animal_name)

            mask_validation = (baseline_animals_df["year"]== self.calibration_year) & (baseline_animals_df["cohort"] == animal_name)

            if animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Dairy"]:

                past_livestock_units.loc[self.calibration_year, "dairy"] += (baseline_animals_df.loc[mask_validation, "pop"].values[0] * self.livestock_unit_values[animal_name].values[0])

            if animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Beef"]:
                past_livestock_units.loc[self.calibration_year, "beef"] += (baseline_animals_df.loc[mask_validation, "pop"].values[0] * self.livestock_unit_values[animal_name].values[0])

            elif animal_name in self.data_manager_class.COHORTS_DICT["Sheep"]:
                for landtype in ["flat_pasture", "hilly_pasture"]:
                    sheep_mask_validation = ((baseline_animals_df["year"]== self.calibration_year)& (baseline_animals_df["cohort"] == animal_name)& (baseline_animals_df["grazing"] == landtype))
                    past_livestock_units.loc[self.calibration_year, "sheep"] += (baseline_animals_df.loc[sheep_mask_validation, "pop"].values[0] * self.livestock_unit_values[animal_name].values[0])


        for sc in scenario_list:
            total_livestock_units = past_livestock_units.copy(deep=True)
            livestock_units[sc] = total_livestock_units

            farm_mask = self.data_manager_class.scenario_aggregation["Scenarios"] == sc
            farm_ids = self.data_manager_class.scenario_aggregation.loc[farm_mask, "farm_id"].unique()

            for farm_id in farm_ids:
                for animal_name in animal_list:
                    if animal_name in self.data_manager_class.scenario_animals_dict[farm_id]["animals"].__dict__.keys():
                        animal_scenario = getattr(self.data_manager_class.scenario_animals_dict[farm_id]["animals"], animal_name)
                        mask = ((scenario_animals_df["farm_id"] == farm_id)& (scenario_animals_df["cohort"] == animal_name))

                        if animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Dairy"]:
                            livestock_units[sc].loc[self.target_year, "dairy"] += (scenario_animals_df.loc[mask, "pop"].values[0] * self.livestock_unit_values[animal_name].values[0])

                        elif animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Beef"]:
                            livestock_units[sc].loc[self.target_year, "beef"] += (scenario_animals_df.loc[mask, "pop"].values[0] * self.livestock_unit_values[animal_name].values[0])
                        elif animal_name in self.data_manager_class.COHORTS_DICT["Sheep"]:
                            for landtype in ["flat_pasture", "hilly_pasture"]:
                                sheep_mask = ((scenario_animals_df["farm_id"] == farm_id)& (scenario_animals_df["cohort"] == animal_name)& (scenario_animals_df["grazing"] == landtype))
                                livestock_units[sc].loc[self.target_year, "sheep"] += (scenario_animals_df.loc[sheep_mask, "pop"].values[0] * self.livestock_unit_values[animal_name].values[0])

        return livestock_units

    def get_stocking_rate(self):


        """
        Produces the stocking rates on each of the three farm types - for now they are related to the total grassland
        area of each farm system and respective livestock units.
        It might be useful to subtract rough grazing and hay grassland areas.

        """

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        baseline_animals_df = self.data_manager_class.baseline_animals_df
        scenario_animals_df = self.data_manager_class.scenario_animals_df

        keys = self.data_manager_class.systems

        livestock_units = self.get_livestock_units()

        dairy_area = self.grassland_class.get_dairy_total_area()
        beef_area = self.grassland_class.get_beef_total_area()
        sheep_area = self.grassland_class.get_sheep_total_area()

        stocking_rate_df = pd.DataFrame(0, index=year_list, columns=keys)

        stocking_rate = {}

        for sc in scenario_list:

            for sys in keys:

                for year in year_list:

                    if sys == "dairy":

                        stocking_rate_df.loc[year, "dairy"] = livestock_units[sc].loc[year, "dairy"] / \
                                                                dairy_area[sc].loc[year]
                    elif sys == "beef":

                        stocking_rate_df.loc[year, "beef"] = livestock_units[sc].loc[year, "beef"] / \
                                                                beef_area[sc].loc[year]
                    elif sys == "sheep":

                        stocking_rate_df.loc[year, "sheep"] = livestock_units[sc].loc[year, "sheep"] / \
                                                                sheep_area[sc].loc[year]

            stocking_rate[sc]=stocking_rate_df.copy(deep=True)



        return stocking_rate

