import unittest
import warnings
import os
import pandas as pd
from grassland_production.utilisation_rate import UtilisationRate


class TestUtilisationFunctions(unittest.TestCase):

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

        self.instance = UtilisationRate(self.ef_country, self.calibration_year, self.target_year, self.scenario_data, self.scenario_animals_df, self.baseline_animals_df)

    def test_get_farm_type_dry_matter_produced(self):
        print(self.instance.get_farm_based_utilisation_rate_old())


if __name__ == '__main__':
    unittest.main()
