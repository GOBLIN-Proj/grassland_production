
from cattle_lca.models import load_livestock_data
from grassland_production.data_loader import Loader


class DataManager:

    def __init__(self, calibration_year, scenario_inputs_df, scenario_animals_df, baseline_animals_df):

        self.loader_class = Loader()

        self.calibration_year = calibration_year
        self.default_calibration_year = 2015
        self.default_grassland_year = 2018
        self.target_year = 2050

        self.COHORTS_DICT = {
            "Cattle": [
                "dairy_cows",
                "suckler_cows",
                "bulls",
                "DxD_calves_m",
                "DxD_calves_f",
                "DxB_calves_m",
                "DxB_calves_f",
                "BxB_calves_m",
                "BxB_calves_f",
                "DxD_heifers_less_2_yr",
                "DxD_steers_less_2_yr",
                "DxB_heifers_less_2_yr",
                "DxB_steers_less_2_yr",
                "BxB_heifers_less_2_yr",
                "BxB_steers_less_2_yr",
                "DxD_heifers_more_2_yr",
                "DxD_steers_more_2_yr",
                "DxB_heifers_more_2_yr",
                "DxB_steers_more_2_yr",
                "BxB_heifers_more_2_yr",
                "BxB_steers_more_2_yr",
            ],
            "Sheep": ["ewes", "lamb_less_1_yr", "lamb_more_1_yr", "male_less_1_yr", "ram"],
        }

        self.DAIRY_BEEF_COHORTS = {
            "Dairy": [
                "dairy_cows",
                "DxD_calves_m",
                "DxD_calves_f",
                "DxD_heifers_less_2_yr",
                "DxD_steers_less_2_yr",
                "DxD_heifers_more_2_yr",
                "DxD_steers_more_2_yr",
            ],
            "Beef": [
                "suckler_cows",
                "bulls",
                "DxB_calves_m",
                "DxB_calves_f",
                "BxB_calves_m",
                "BxB_calves_f",
                "DxB_heifers_less_2_yr",
                "DxB_steers_less_2_yr",
                "BxB_heifers_less_2_yr",
                "BxB_steers_less_2_yr",
                "DxB_heifers_more_2_yr",
                "DxB_steers_more_2_yr",
                "BxB_heifers_more_2_yr",
                "BxB_steers_more_2_yr",
            ],
        }

        self.scenario_inputs_df = scenario_inputs_df
        self.scenario_animals_df = scenario_animals_df
        self.baseline_animals_df = baseline_animals_df

        self.baseline_animals_dict = load_livestock_data(self.baseline_animals_df)
        self.scenario_animals_dict = load_livestock_data(self.scenario_animals_df)


        self.scenario_aggregation = self.scenario_animals_df[["Scenarios", "farm_id"]]

        self.soil_class_yield_gap = {"1": 0.85, "2": 0.8, "3": 0.7}

        self.soil_class_prop = {
            "dairy": self.loader_class.dairy_soil_group(),
            "beef": self.loader_class.cattle_soil_group(),
            "sheep": self.loader_class.sheep_soil_group(),
        }

        self.grasslands = ["Grass silage", "Hay", "Pasture", "Rough grazing in use"]
        self.systems = ["dairy", "beef", "sheep"]



