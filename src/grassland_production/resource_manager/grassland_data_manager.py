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
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.
    
    Attributes:
        loader_class (Loader): Instance of the Loader class for loading various datasets.
        ef_country (str): The EF country.
        calibration_year (int): The calibration year for data reference.
        default_calibration_year (int): The default calibration year used as a fallback when data for the specified year is not available.
        default_grassland_year (int): The default year used for grassland data when it is not specified.
        target_year (int): The target year for future scenario projections.
        COHORTS_DICT (dict): A dictionary mapping livestock categories to their cohorts.
        DAIRY_BEEF_COHORTS (dict): A dictionary mapping livestock categories to cohorts for dairy and beef systems.
        COHORTS_GROUPS (dict): A dictionary mapping farm systems to the corresponding livestock cohorts.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.
        baseline_animals_dict (dict): A dictionary containing baseline livestock data.
        scenario_animals_dict (dict): A dictionary containing scenario livestock data.
        scenario_aggregation (DataFrame): DataFrame containing scenario aggregation data.
        soil_class_yield_gap (dict): A dictionary mapping soil classes to yield gaps.
        soil_class_prop (dict): A dictionary containing soil properties for different farm systems.
        grasslands (list): A list of grassland types.
        systems (list): A list of farm systems.
        lime_rate (float): The lime rate.
        default_urea_proportion (float): The default proportion of urea.
        default_urea_abated_proportion (float): The default proportion of abated urea.

    Methods:
        get_ef_country(): Returns the EF country.
        get_cohort_groups(): Returns the livestock cohorts for farm systems.
        get_dairy_beef_cohorts(): Returns the livestock cohorts for dairy and beef systems.
        get_cohorts(): Returns the livestock cohorts for farm systems (Cattle, Sheep).
        get_soil_properties(): Returns the soil properties for farm systems.
        get_yield_gap(soil_class): Returns the yield gap for soil classes.
        get_default_calibration_year(): Returns the default calibration year used as a fallback when data for the specified year is not available.
        get_default_grassland_year(): Returns the default year used for grassland data when it is not specified.
        get_target_year(): Returns the target year for future scenario projections.
        get_baseline_animals_dict(): Returns the baseline livestock data as dict.
        get_baseline_animals_dataframe(): Returns the baseline livestock data as DataFrame.
        get_scenario_animals_dict(): Returns the scenario livestock data as dict.
        get_scenario_animals_dataframe(): Returns the scenario livestock data as DataFrame.
        get_scenario_aggregation(): Returns the scenario aggregation data.
        get_grassland_types(): Returns a list of grassland types.
        get_farming_systems(): Returns a list of farm systems.
        get_lime_rate(): Returns the lime rate.
        get_default_urea_proportion(): Returns the default proportion of urea.
        get_default_urea_abated_proportion(): Returns the default proportion of abated urea.
    """
    def __init__(
        self,
        calibration_year,
        target_year,
        scenario_animals_df,
        baseline_animals_df,
    ):
        self.ef_country = "ireland"
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

        self.lime_rate = 3.25

        self.default_urea_proportion = 0.2
        self.default_urea_abated_proportion = 0

    def get_ef_country(self):
        """
        Returns the EF country.

        Returns:
            str: The EF country.
        """
        return self.ef_country
    
    def get_cohort_groups(self):
        """
        Returns the livestock cohorts for a specified farm system.

        Args:
            system (str): The farm system for which to return livestock cohorts.

        Returns:
            list: A list of livestock cohorts for the specified farm system.
        """
        return self.COHORTS_GROUPS
    
    def get_dairy_beef_cohorts(self):
        """
        Returns the livestock cohorts for dairy and beef systems.

        Returns:
            dict: A dictionary mapping livestock categories to cohorts for dairy and beef systems.
        """
        return self.DAIRY_BEEF_COHORTS
    
    def get_cohorts(self):
        """
        Returns the livestock cohorts for farm systems (Cattle, Sheep).

        Returns:
            dict: A dictionary mapping livestock categories to their cohorts.
        """
        return self.COHORTS_DICT
    
    def get_soil_properties(self):
        """
        Returns the soil properties for farm systems.

        Returns:
            dict: A dictionary containing soil properties for different farm systems.
        """
        return self.soil_class_prop
    
    def get_yield_gap(self):
        """
        Returns the yield gap for soil classes.

        Returns:
            dict: A dictionary mapping soil classes to yield gaps.
        """
        return self.soil_class_yield_gap
    
    def get_calibration_year(self):
        """
        Returns the calibration year for data reference.

        Returns:
            int: The calibration year.
        """
        return self.calibration_year
    
    def get_default_calibration_year(self):
        """
        Returns the default calibration year used as a fallback when data for the specified year is not available.

        Returns:
            int: The default calibration year.
        """
        return self.default_calibration_year
    
    def get_default_grassland_year(self):
        """
        Returns the default year used for grassland data when it is not specified.

        Returns:
            int: The default grassland year.
        """
        return self.default_grassland_year
    
    def get_target_year(self):
        """
        Returns the target year for future scenario projections.

        Returns:
            int: The target year.
        """
        return self.target_year
    
    def get_baseline_animals_dict(self):
        """
        Returns the baseline livestock data.

        Returns:
            Dict: A dictionary containing baseline livestock data.
        """
        return self.baseline_animals_dict
    
    def get_baseline_animals_dataframe(self):
        """
        Returns the baseline livestock data.

        Returns:
            DataFrame: A DataFrame containing baseline livestock data.
        """
        return self.baseline_animals_df

    def get_scenario_animals_dict(self):
        """
        Returns the scenario livestock data.
        
        Returns:
            Dict: A dictionary containing scenario livestock data.
        """
        return self.scenario_animals_dict
    
    def get_scenario_animals_dataframe(self):
        """
        Returns the scenario livestock data.

        Returns:
            DataFrame: A DataFrame containing scenario livestock data.
        """
        return self.scenario_animals_df
    
    def get_scenario_aggregation(self):
        """
        Returns the scenario aggregation data.

        Returns:
            DataFrame: A DataFrame containing scenario aggregation data.
        """
        return self.scenario_aggregation
    
    def get_grassland_types(self):
        """
        Returns a list of grassland types.

        Returns:
            list: A list of grassland types.
        """
        return self.grasslands
    
    def get_farming_systems(self):
        """
        Returns a list of farm systems.

        Returns:
            list: A list of farm systems.
        """
        return self.systems
    
    def get_lime_rate(self):
        """
        Returns the lime rate. This rate is based on maximum lime application rates provided by the 
        Department of Agriculture, Food and the Marine (DAFM) in Ireland. The maximum lime application 
        is 7.5 tonnes per hectare every 3 years. The lime rate is calculated as half of the maximum, which 
        can be applied in year 1, with the balance applied in year 3.

        Returns:
            float: The lime rate.
        """
        return self.lime_rate
    
    def get_default_urea_proportion(self):
        """
        Returns the default proportion of urea.

        Returns:
            float: The default proportion of urea.
        """
        return self.default_urea_proportion
    
    def get_default_urea_abated_proportion(self):
        """
        Returns the default proportion of abated urea.

        Returns:
            float: The default proportion of abated urea.
        """
        return self.default_urea_abated_proportion