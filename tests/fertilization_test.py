import unittest
import pandas as pd
from grassland_production.fertilisation import Fertilisation
import os
import warnings

class FertilizationTestCase(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter(action="ignore")
        # Create the DataFrame with the provided data

        self.scenario_dataframe = pd.read_csv("./data/scenario_input_dataframe.csv")
        self.scenario_animal_dataframe = pd.read_csv("./data/scenario_animal_data.csv")
        self.baseline_animal_dataframe = pd.read_csv("./data/baseline_animal_data.csv")

        self.fert_class = Fertilisation(
            "ireland",
            2020,
            2050,
            self.scenario_dataframe,
            self.scenario_animal_dataframe,
            self.baseline_animal_dataframe,
        )

    def test_fertilisation(self):
        test = self.fert_class.organic_fertilisation_per_ha()

        test2 = self.fert_class.compute_organic_fertilization_rate()

        test3 = self.fert_class.compute_inorganic_fertilization_rate()

        print(f"organic fert: {test}")

        print("#"*50)
        print(f"organic fert rate: {test2}")
        print("#"*50)
        print(f"inorganic fert rate: {test3}")


if __name__ == "__main__":
    unittest.main()
