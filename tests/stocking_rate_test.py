import unittest
import pandas as pd
from grassland_production.stocking_rate import StockingRate
import matplotlib.pyplot as plt
import os
import warnings

class StockingRateTestCase(unittest.TestCase):
    def setUp(self):
        # Create the DataFrame with the provided data
        warnings.simplefilter(action='ignore')
        self.path_to_data = "./data/"

        self.data_frame = pd.read_csv(os.path.join(self.path_to_data, "scenario_input_dataframe.csv"))
        self.animal_dataframe_baseline = pd.read_csv("./data/baseline_animal_data.csv")
        self.animal_dataframe_scenarios = pd.read_csv("./data/scenario_animal_data.csv")

        self.stock_class = StockingRate(
            "ireland",
            2020,
            2050,
            self.data_frame,
            self.animal_dataframe_scenarios,
            self.animal_dataframe_baseline,
        )


    def test_stocking_rate(self):
        #test1 = self.dm_class.get_total_concentrate_feed()

        #print(test1)


        test2 = self.stock_class.get_stocking_rate()

        print(test2)

if __name__ == "__main__":
    unittest.main()