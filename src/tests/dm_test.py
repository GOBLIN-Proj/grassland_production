import unittest
import pandas as pd
from grassland_production.dry_matter import DryMatter
import matplotlib.pyplot as plt
import os
import warnings

class DryMatterTestCase(unittest.TestCase):
    def setUp(self):
        # Create the DataFrame with the provided data
        warnings.simplefilter(action='ignore')
        self.path_to_data = "./data/"

        self.data_frame = pd.read_csv(os.path.join(self.path_to_data, "scenario_dataframe1.csv"))
        self.animal_dataframe_baseline = pd.read_csv("./data/past_animals.csv")
        self.animal_dataframe_scenarios = pd.read_csv("./data/future_animals.csv")

        self.dm_class = DryMatter(
            "ireland",
            2020,
            2050,
            self.data_frame,
            self.animal_dataframe_scenarios,
            self.animal_dataframe_baseline,
        )


    def test_concentrate_and_dry_matter(self):
        #test1 = self.dm_class.get_total_concentrate_feed()

        #print(test1)


        test2 = self.dm_class.get_actual_dm_weights()

        print(test2)

if __name__ == "__main__":
    unittest.main()
