import pandas as pd
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.spared_area import Grasslands
import itertools

class SoilGroups:

    def __init__(self, ef_country, calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df):

        self.data_manager_class = DataManager(calibration_year, target_year, scenario_data, scenario_animals_df,baseline_animals_df)
        self.calibration_year = self.data_manager_class.calibration_year
        self.target_year = self.data_manager_class.target_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.loader_class = Loader()
        self.scenario_animals_df = scenario_animals_df
        self.baseline_animals_df = baseline_animals_df
        self.dairy_soil_distribution = self.loader_class.dairy_soil_group()
        self.beef_soil_distribution = self.loader_class.cattle_soil_group()
        self.sheep_soil_distribution = self.loader_class.sheep_soil_group()
        self.grassland_class = Grasslands(ef_country, self.calibration_year, target_year, scenario_data, scenario_animals_df, baseline_animals_df)



    def get_cohort_soil_groups(self):
        spared_area_cohorts = self.grassland_class.get_cohort_spared_area()

        soil_distribution = {
            "dairy": self.dairy_soil_distribution,
            "beef": self.beef_soil_distribution,
            "sheep": self.sheep_soil_distribution,
        }

        groups = ("1", "2", "3")
        cohorts = soil_distribution.keys()
        scenarios = spared_area_cohorts.keys()

        data = []

        for sc, sg, cohort in itertools.product(scenarios, groups, cohorts):
            try:
                area_multiplier = soil_distribution[cohort].loc[self.calibration_year, sg].item()
            except KeyError:
                print(f"KeyError encountered for {cohort} in year {self.calibration_year}. Using default calibration year {self.default_calibration_year} instead.")
                area_multiplier = soil_distribution[cohort].loc[self.default_calibration_year, sg].item()

            row_data = {
                "Scenario": sc,
                "year": self.target_year,
                "cohort": cohort,
                "soil_group": sg,
                "area_ha": spared_area_cohorts[sc][cohort] * area_multiplier,
            }
            data.append(row_data)
        
        cohort_soil_groups = pd.DataFrame(data)

        return cohort_soil_groups

