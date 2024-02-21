"""
=====================================
Grassland Static Data Manager Module
=====================================
The Grassland Static Data Manager Module is a part of the grassland production system that deals with loading and managing
static data for grassland production analysis. It is designed to provide essential data for grassland production analysis.
"""

from cattle_lca.models import load_livestock_data
from grassland_production.resource_manager.data_loader import Loader


class DataManager:
    """
    The Grassland Static Data Manager Module is responsible for loading and managing static data for grassland production analysis.
    It provides essential data for grassland production analysis, including livestock cohorts, soil data, and grassland types.

    Args:
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.
    
    Attributes:
        loader_class (Loader): Instance of the Loader class for loading various datasets.
        calibration_year (int): The calibration year for data reference.
        default_calibration_year (int): The default calibration year used as a fallback when data for the specified year is not available.
        default_grassland_year (int): The default year used for grassland data when it is not specified.
        target_year (int): The target year for future scenario projections.
        COHORTS_DICT (dict): A dictionary mapping livestock categories to their cohorts.
        DAIRY_BEEF_COHORTS (dict): A dictionary mapping livestock categories to cohorts for dairy and beef systems.
        COHORTS_GROUPS (dict): A dictionary mapping farm systems to the corresponding livestock cohorts.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.
        baseline_animals_dict (dict): A dictionary containing baseline livestock data.
        scenario_animals_dict (dict): A dictionary containing scenario livestock data.
        scenario_aggregation (DataFrame): DataFrame containing scenario aggregation data.
        soil_class_yield_gap (dict): A dictionary mapping soil classes to yield gaps.
        soil_class_prop (dict): A dictionary containing soil properties for different farm systems.
        grasslands (list): A list of grassland types.
        systems (list): A list of farm systems.
    """
    def __init__(
        self,
        calibration_year,
        target_year,
        scenario_animals_df,
        baseline_animals_df,
    ):
        self.loader_class = Loader()

        self.calibration_year = calibration_year
        self.default_calibration_year = 2015
        self.default_grassland_year = 2018
        self.target_year = target_year

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
            "Sheep": [
                "ewes",
                "lamb_less_1_yr",
                "lamb_more_1_yr",
                "male_less_1_yr",
                "ram",
            ],
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

        self.COHORTS_GROUPS = {
            "dairy": self.DAIRY_BEEF_COHORTS["Dairy"],
            "beef": self.DAIRY_BEEF_COHORTS["Beef"],
            "sheep": {"flat_pasture": self.COHORTS_DICT["Sheep"],
                    "hilly_pasture": self.COHORTS_DICT["Sheep"]}
        }

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
