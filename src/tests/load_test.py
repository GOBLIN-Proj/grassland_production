import unittest
import pandas as pd
import os

from crop_lca.models import (
    CropChars,
    Upstream,
    Emissions_Factors,
    Fertiliser,
)


class DatasetLoadingTestCase(unittest.TestCase):
    def setUp(self):
        self.data_dir = "./data"

    def test_dataset_loading(self):
        # Test loading the datasets as pandas DataFrames
        chars_path = os.path.join(self.data_dir, "crop_params.csv")
        ef_path = os.path.join(self.data_dir, "emission_factor_crop.csv")
        upstream_path = os.path.join(self.data_dir, "upstream_crop.csv")
        fertiliser_path = os.path.join(self.data_dir,"FAOSTAT_yield_data.csv")

        # Load the datasets as DataFrames
        crop_chars = pd.read_csv(chars_path, index_col=0)
        ef = pd.read_csv(ef_path, index_col=0)
        upstream = pd.read_csv(upstream_path, index_col=0)
        fertiliser = pd.read_csv(fertiliser_path, index_col=0)

        # Perform assertions to validate the loaded data

        crop_char_class = CropChars(crop_chars)
        ef_class = Emissions_Factors(ef)
        upstream_class = Upstream(upstream)
        fertiliser_class = Fertiliser(fertiliser)

        self.assertTrue(crop_char_class.is_loaded())
        self.assertTrue(ef_class.is_loaded())
        self.assertTrue(upstream_class.is_loaded())
        self.assertTrue(fertiliser_class.is_loaded())

if __name__ == "__main__":
    unittest.main()
