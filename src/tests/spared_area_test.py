import unittest
import pandas as pd
from grassland_production.spared_area import Grasslands
import matplotlib.pyplot as plt
import os
import warnings

class SpatAreasTestCase(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter(action='ignore')
        # Create the DataFrame with the provided data
        self.path_to_data = "./data/"

        self.data_frame = pd.read_csv(os.path.join(self.path_to_data, "scenario_dataframe1.csv"))
        self.animal_dataframe_baseline = pd.read_csv(os.path.join(self.path_to_data, "past_animals.csv"))
        self.animal_dataframe_scenarios = pd.read_csv(os.path.join(self.path_to_data, "future_animals.csv"))

        self.grassland_class = Grasslands(
            "ireland",
            2020,
            2050,
            self.data_frame,
            self.animal_dataframe_scenarios,
            self.animal_dataframe_baseline,
        )

    def test_fertilisation(self):
        test = self.grassland_class.get_cohort_grassland_area()

        print(test)

        test2 = self.grassland_class.get_grass_total_area()

        print(test2)


if __name__ == "__main__":
    unittest.main()
