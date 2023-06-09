import unittest
import pandas as pd
from grassland_production.grassland_area import Areas
import matplotlib.pyplot as plt
import os


class AreasTestCase(unittest.TestCase):
    
    def test_fertilisation(self):
        self.areas_class = Areas(2050, 2015, 2015)
        test = self.areas_class.get_nfs_within_system_grassland_distribution()

        print(test)




if __name__ == "__main__":
    unittest.main()
