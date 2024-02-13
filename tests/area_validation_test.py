import unittest
import pandas as pd
import shutil
import os
from grassland_production.grassland_output import GrasslandOutput

class TestGrasslandOutput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up method to prepare the environment before running tests."""
        cls.ef_country = "ireland"
        cls.calibration_year = 2020
        cls.target_year = 2050

        # Assuming the test data paths are adjusted to where the test data is located
        cls.path_to_data = "./data/"
        cls.scenario_dataframe = pd.read_csv(os.path.join(cls.path_to_data, "scenario_input_dataframe2.csv"))
        cls.scenario_animal_dataframe = pd.read_csv(os.path.join(cls.path_to_data, "scenario_animal_data.csv"))
        cls.baseline_animal_dataframe = pd.read_csv(os.path.join(cls.path_to_data, "baseline_animal_data.csv"))

        # Initialize GrasslandOutput instance
        cls.grassland = GrasslandOutput(
            cls.ef_country,
            cls.calibration_year,
            cls.target_year,
            cls.scenario_dataframe,
            cls.scenario_animal_dataframe,
            cls.baseline_animal_dataframe,
        )

    def test_spared_area_validation(self):
        """Test if spared_area equals spared area + target_year value in grassland_area."""
        spared_area = self.grassland.total_spared_area().loc[self.target_year].sum()
        grassland_area = self.grassland.total_grassland_area().loc[self.target_year].sum()

        total_grassland_area = spared_area + grassland_area
        baseline_grassland_area = self.grassland.total_grassland_area().loc[self.calibration_year].sum()

        # Assuming grassland_area is a dict with years as keys
        self.assertAlmostEqual(baseline_grassland_area, total_grassland_area, places=2, msg="Spared area does not match grassland area for target year.")

    def test_breakdown_area_validation(self):
        """Test if sum of area ha in breakdown matches spared_area for each scenario."""
        breakdown = self.grassland.total_spared_area_breakdown()
        spared_area = self.grassland.total_spared_area()

        ## Calculate the sum of breakdown areas
        for col in spared_area.columns:
            spared = spared_area.at[self.target_year,col]
            total_breakdown_area = breakdown.loc[breakdown['Scenario'] == col, 'area_ha'].sum()

            if total_breakdown_area != 0:
                self.assertAlmostEqual(spared, total_breakdown_area, places=2, msg="Breakdown area sum for scenario {col} does not match spared area.")
            else:
                print(f"Breakdown area sum for scenario {col} is zero.")
                
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        #if os.path.exists("./geo_test_data"):
            #shutil.rmtree("./geo_test_data")

if __name__ == '__main__':
    unittest.main()