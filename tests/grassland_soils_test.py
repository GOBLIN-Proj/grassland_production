import unittest
from grassland_production.grassland_soils import SoilGroups
from unittest.mock import Mock
import os
import pandas as pd
import warnings


class TestSoilGroupFunctions(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter(action='ignore')
        # Create an instance of YourClass here, and set up mocks as needed
        self.path_to_data = "data/"
        self.ef_country = "ireland"
        self.calibration_year = 2020
        self.target_year = 2050
        self.scenario_data = pd.read_csv(os.path.join(self.path_to_data, "scenario_dataframe1.csv"))
        self.scenario_animals_df = pd.read_csv(os.path.join(self.path_to_data, "future_animals.csv"))
        self.baseline_animals_df = pd.read_csv(os.path.join(self.path_to_data, "past_animals.csv"))

        self.instance = SoilGroups(self.ef_country, self.calibration_year, self.target_year, self.scenario_data, self.scenario_animals_df, self.baseline_animals_df)

    def test_get_cohort_proportions(self):
        print(self.instance.get_cohort_soil_groups())


if __name__ == '__main__':
    unittest.main()
