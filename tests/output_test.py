import unittest
import os
from tempfile import TemporaryDirectory
import pandas as pd
from grassland_production.grassland_output import GrasslandOutput

class TestGenerateData(unittest.TestCase):

    def test_generate_scenario_dataframe_creates_file(self):
        # Use a temporary directory
        with TemporaryDirectory() as tmp_dir:
            path_to_data = "./data" # Use the temporary directory
            ef_country = "ireland"
            calibration_year = 2020
            target_year = 2050

            scenario_dataframe = pd.read_csv(os.path.join(path_to_data,"scenario_input_dataframe.csv"))
            scenario_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"scenario_animal_data.csv"))
            baseline_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"baseline_animal_data.csv"))


            # Instantiate class
            grassland = GrasslandOutput(
                ef_country,
                calibration_year,
                target_year,
                scenario_dataframe,
                scenario_animal_dataframe,
                baseline_animal_dataframe,
            )

            
            grassland.total_spared_area().to_csv(os.path.join(tmp_dir,"spared_area.csv"))
            grassland.total_grassland_area().to_csv(os.path.join(tmp_dir,"total_grassland_area.csv"))
            grassland.total_spared_area_breakdown().to_csv(os.path.join(tmp_dir,"spared_area_breakdown.csv"))
            grassland.total_concentrate_feed().to_csv(os.path.join(tmp_dir,"concentrate_feed.csv"))
            grassland.grassland_stocking_rate().to_csv(os.path.join(tmp_dir,"stocking_rate.csv"))


            # Check if the file was created as expected
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, "spared_area.csv")), f"File spared_area.csv was not created in temporary directory.")
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, "total_grassland_area.csv")), f"File total_grassland_area.csv was not created in temporary directory.")
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, "spared_area_breakdown.csv")), f"File spared_area_breakdown.csv was not created in temporary directory.")
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, "concentrate_feed.csv")), f"File concentrate_feed.csv was not created in temporary directory.")
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, "stocking_rate.csv")), f"File stocking_rate.csv was not created in temporary directory.")

# Running the tests
if __name__ == '__main__':
    unittest.main()
