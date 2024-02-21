import unittest
import pandas as pd
from grassland_production.geo_grassland_production.geo_fertilisation import Fertilisation
import os
import warnings

class FertilizationTestCase(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter(action="ignore")
        # Create the DataFrame with the provided data
   
        #set up test data
        self.path_to_data = "./geo_goblin_data/"

        self.ef_country = "ireland"
        self.calibration_year = 2020
        self.target_year = 2050

        self.scenario_dataframe = pd.read_csv(os.path.join(self.path_to_data,"scenario_input_dataframe.csv"))
        self.scenario_animal_dataframe = pd.read_csv(os.path.join(self.path_to_data,"future_animals.csv"))
        self.baseline_animal_dataframe = pd.read_csv(os.path.join(self.path_to_data,"past_animals.csv"))


        self.fert_class = Fertilisation(
            self.ef_country,
            self.calibration_year,
            self.target_year,
            self.scenario_dataframe,
            self.scenario_animal_dataframe,
            self.baseline_animal_dataframe,
        )

    def test_fertilisation(self):
        test = self.fert_class.organic_fertilisation_per_ha()

        test2 = self.fert_class.compute_organic_fertilization_rate()

        print(test)

        print(test2)


if __name__ == "__main__":
    unittest.main()
