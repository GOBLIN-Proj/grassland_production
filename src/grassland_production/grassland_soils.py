import pandas as pd
import copy
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.spared_area import Grasslands

class SoilGroups:

    def __init__(self, ef_country, calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df):

        self.data_manager_class = DataManager(calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df)
        self.calibration_year = self.data_manager_class.calibration_year
        self.target_year = self.data_manager_class.target_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.loader_class = Loader()
        self.dairy_soil_distribution = self.loader_class.dairy_soil_group()
        self.beef_soil_distribution = self.loader_class.cattle_soil_group()
        self.sheep_soil_distribution = self.loader_class.sheep_soil_group()
        self.grassland_class = Grasslands(ef_country, self.calibration_year, target_year, scenario_data, scenario_animals_df, baseline_animals_df)


    def get_dairy_soil_groups(self):


        """
        Produces the total area of each soil group (1,2 & 3) within dairy araes - for now we assume that additional
        or removed land area is added/subtracted at same rates from each soil group.
        For the future, it might be useful to add preferential land conversion, for example from soil group 3.

        """

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        baseline_animals_df = self.data_manager_class.baseline_animals_df
        scenario_animals_df = self.data_manager_class.scenario_animals_df

        keys = self.data_manager_class.systems

        cols = ("1", "2", "3")

        dairy_area = self.grassland_class.get_dairy_total_area()

        dairy_soil_groups_df = pd.DataFrame(0, index=year_list, columns=cols)

        dairy_soil_groups = {}

        for sc in scenario_list:

            for col in cols:

                for year in year_list:
                    if year != self.target_year:
                        dairy_soil_groups_df.loc[year, col] = dairy_area[sc].loc[year] * \
                                                              self.dairy_soil_distribution.loc[year, col]
                    else:
                        dairy_soil_groups_df.loc[self.target_year, col] = dairy_area[sc].loc[year] * \
                                                                          self.dairy_soil_distribution.loc[self.calibration_year, col]

            dairy_soil_groups[sc]=dairy_soil_groups_df.copy(deep=True)



        return dairy_soil_groups

    def get_beef_soil_groups(self):


        """
        Produces the total area of each soil group (1,2 & 3) within beef araes - for now we assume that additional
        or removed land area is added/subtracted at same rates from each soil group.
        For the future, it might be useful to add preferential land conversion, for example from soil group 3.

        """

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        baseline_animals_df = self.data_manager_class.baseline_animals_df
        scenario_animals_df = self.data_manager_class.scenario_animals_df

        keys = self.data_manager_class.systems

        cols = ("1", "2", "3")

        beef_area = self.grassland_class.get_beef_total_area()

        beef_soil_groups_df = pd.DataFrame(0, index=year_list, columns=cols)

        beef_soil_groups = {}

        for sc in scenario_list:

            for col in cols:

                for year in year_list:
                    if year != self.target_year:
                        beef_soil_groups_df.loc[year, col] = beef_area[sc].loc[year] * \
                                                              self.beef_soil_distribution.loc[year, col]
                    else:
                        beef_soil_groups_df.loc[self.target_year, col] = beef_area[sc].loc[year] * \
                                                                          self.beef_soil_distribution.loc[self.calibration_year, col]

            beef_soil_groups[sc]=beef_soil_groups_df.copy(deep=True)



        return beef_soil_groups

    def get_sheep_soil_groups(self):


        """
        Produces the total area of each soil group (1,2 & 3) within sheep araes - for now we assume that additional
        or removed land area is added/subtracted at same rates from each soil group.
        For the future, it might be useful to add preferential land conversion, for example from soil group 3.

        """

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        baseline_animals_df = self.data_manager_class.baseline_animals_df
        scenario_animals_df = self.data_manager_class.scenario_animals_df

        keys = self.data_manager_class.systems

        cols = ("1", "2", "3")

        sheep_area = self.grassland_class.get_sheep_total_area()

        sheep_soil_groups_df = pd.DataFrame(0, index=year_list, columns=cols)

        sheep_soil_groups = {}

        for sc in scenario_list:

            for col in cols:

                for year in year_list:
                    if year != self.target_year:
                        sheep_soil_groups_df.loc[year, col] = sheep_area[sc].loc[year] * \
                                                              self.sheep_soil_distribution.loc[year, col]
                    else:
                        sheep_soil_groups_df.loc[self.target_year, col] = sheep_area[sc].loc[year] * \
                                                                          self.sheep_soil_distribution.loc[self.calibration_year, col]

            sheep_soil_groups[sc]=sheep_soil_groups_df.copy(deep=True)



        return sheep_soil_groups
