import unittest
import pandas as pd
from grassland_production.fertilisation import Fertilisation
import os
import warnings

class FertilizationTestCase(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter(action="ignore")
        # Create the DataFrame with the provided data

        self.scenario_dataframe = pd.read_csv("./data/scenario_dataframe.csv")
        self.scenario_animal_dataframe = pd.read_csv("./data/future_animals.csv")
        self.baseline_animal_dataframe = pd.read_csv("./data/past_animals.csv")

        self.fert_class = Fertilisation(
            "ireland",
            2020,
            2050,
            self.scenario_dataframe,
            self.scenario_animal_dataframe,
            self.baseline_animal_dataframe,
        )

    def test_fertilisation(self):
        test = self.fert_class.compute_inorganic_fertilization_rate()

        print(test)


if __name__ == "__main__":
    unittest.main()
