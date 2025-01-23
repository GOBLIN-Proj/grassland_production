import unittest
import pandas as pd
from grassland_production.farm_data_generation import FarmData
import matplotlib.pyplot as plt
import warnings


class FarmDataTestCase(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter(action="ignore")
        # Create the DataFrame with the provided data
        self.scenario_dataframe = pd.read_csv("./data/scenario_input_dataframe.csv")
        self.scenario_animal_dataframe = pd.read_csv("./data/scenario_animal_data.csv")
        self.baseline_animal_dataframe = pd.read_csv("./data/baseline_animal_data.csv")


        self.farm_class = FarmData(
            "ireland",
            2020,
            2050,
            self.scenario_dataframe,
            self.scenario_animal_dataframe,
            self.baseline_animal_dataframe,
        )

    def test_farm_data(self):
        test = self.farm_class.compute_farm_data_in_scenarios()

        print(test)


if __name__ == "__main__":
    unittest.main()
