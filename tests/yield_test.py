import unittest
import pandas as pd
from grassland_production.grass_yield import Yield
import matplotlib.pyplot as plt
import os


class YieldTestCase(unittest.TestCase):
    def setUp(self):
        # Create the DataFrame with the provided data
        path = "./data/"

        self.scenario_dataframe = pd.read_csv(os.path.join(path,"scenario_input_dataframe.csv"))
        self.animal_dataframe_baseline = pd.read_csv(os.path.join(path,"past_animals.csv"))
        self.animal_dataframe_scenarios = pd.read_csv(os.path.join(path,"future_animals.csv"))

        self.yield_class = Yield(
            "ireland",
            2020,
            2050,
            self.scenario_dataframe,
            self.animal_dataframe_scenarios,
            self.animal_dataframe_baseline,
        )

    def test_yield(self):
        test = self.yield_class.get_yield()

        print(test)


if __name__ == "__main__":
    unittest.main()
