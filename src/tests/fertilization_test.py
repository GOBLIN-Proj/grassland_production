import unittest
import pandas as pd
from grassland_production.fertilisation import Fertilisation
import matplotlib.pyplot as plt
import os


class FertilizationTestCase(unittest.TestCase):
    def setUp(self):
        # Create the DataFrame with the provided data


        data = [
            [0, "Dairy", "tank solid", 0, 0, 0.0879077282507005, 0.500607270596862, 0, 0, 0, 0.801458098547012, 0.36840211684271, 0.0555663357895664, 0.126070113756632, 0, 0, 0.0784928061838073, 0.120049095269181, 0, 0.0879200186051467, 0, 0, 0, 0, 136.870524806694, 105.00171069052, 0.591628596827221, 2080],
            [0, "Dairy", "tank liquid", 172390.09063152, 0, 0.0879077282507005, 0.500607270596862, 0, 0, 0, 0.801458098547012, 0.36840211684271, 0.0555663357895664, 0.126070113756632, 0, 0, 0.0784928061838073, 0.120049095269181, 0, 0.0879200186051467, 0, 0, 0, 0, 136.870524806694, 105.00171069052, 0.591628596827221, 2080],
            [0, "Beef", "tank solid", 0, 0, 0.0879077282507005, 0.500607270596862, 0, 0, 0, 0.801458098547012, 0.36840211684271, 0.0555663357895664, 0.126070113756632, 0, 0, 0.0784928061838073, 0.120049095269181, 0, 0.0879200186051467, 0, 0, 0, 0, 136.870524806694, 105.00171069052, 0.591628596827221, 2080],
            [0, "Beef", "tank liquid", 0, 27807.487070967, 0.0879077282507005, 0.500607270596862, 0, 0, 0, 0.801458098547012, 0.36840211684271, 0.0555663357895664, 0.126070113756632, 0, 0, 0.0784928061838073, 0.120049095269181, 0, 0.0879200186051467, 0, 0, 0, 0, 136.870524806694, 105.00171069052, 0.591628596827221, 2080],
            [0, "Lowland sheep", "tank liquid", 0, 0, 0.0879077282507005, 0.500607270596862, 0, 0, 0, 0.801458098547012, 0.36840211684271, 0.0555663357895664, 0.126070113756632, 0, 0, 0.0784928061838073, 0.120049095269181, 0, 0.0879200186051467, 0, 0, 37812, 0, 136.870524806694, 105.00171069052, 0.591628596827221, 2080],
            [0, "Upland sheep", "tank liquid", 0, 0, 0.0879077282507005, 0.500607270596862, 0, 0, 0, 0.801458098547012, 0.36840211684271, 0.0555663357895664, 0.126070113756632, 0, 0, 0.0784928061838073, 0.120049095269181, 0, 0.0879200186051467, 9453, 0, 0, 0, 136.870524806694, 105.00171069052, 0.591628596827221, 2080]
        ]

        columns = ["Scenarios", "Cattle systems", "Manure management", "Dairy pop", "Beef pop", "Dairy prod", "Beef prod", "mm_storage", "Cattle EF", "AD prod", "Forest area", "Conifer proportion", "Conifer harvest", "Conifer thinned", "Broadleaf harvest", "Bioenergy area", "Crop area", "Wetland area", "Land rewetting", "Grass management", "Upland sheep pop", "Upland sheep prod", "Lowland sheep pop", "Lowland sheep prod", "Dairy Pasture fertilisation", "Beef Pasture fertilisation", "Broadleaf proportion", "Afforest Year"]


        animal_data_baseline = [
            [
                "ireland",
                2018,
                2018,
                "dairy_cows",
                175298,
                538,
                14.953,
                "irish_grass",
                "pasture",
                "concentrate",
                2.992828296,
                13.5890411,
                10.4109589,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "suckler_cows",
                30587,
                600,
                1.410958904,
                "irish_grass",
                "pasture",
                "concentrate",
                0.842751605,
                12.2739726,
                11.7260274,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxD_heifers_more_2_yr",
                384.1446311,
                122.125,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                12.98630137,
                11.01369863,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxB_heifers_more_2_yr",
                0,
                94.75,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                12.98630137,
                11.01369863,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "BxB_heifers_more_2_yr",
                0,
                103.875,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                12.38356164,
                11.61643836,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxD_heifers_less_2_yr",
                49298.56099,
                395.875,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                11.56164384,
                12.43835616,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxB_heifers_less_2_yr",
                30347.42586,
                346.6,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                11.56164384,
                12.43835616,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "BxB_heifers_less_2_yr",
                14763.98982,
                412.3,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                11.56164384,
                12.43835616,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxD_steers_less_2_yr",
                37646.17385,
                463.475,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                11.56164384,
                12.43835616,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxB_steers_less_2_yr",
                29323.04018,
                474.425,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                11.56164384,
                12.43835616,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "BxB_steers_less_2_yr",
                14327.92261,
                479.9,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                11.56164384,
                12.43835616,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxD_steers_more_2_yr",
                5506.073046,
                140.45,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                18.73972603,
                5.260273973,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxB_steers_more_2_yr",
                4225.590942,
                129.5,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                18.73972603,
                5.260273973,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "BxB_steers_more_2_yr",
                2273.779022,
                162.35,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0,
                18.73972603,
                5.260273973,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxD_calves_f",
                46993.69321,
                149.575,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                1,
                7.945205479,
                16.05479452,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxB_calves_f",
                33164.48649,
                116.725,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                1,
                7.945205479,
                16.05479452,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "BxB_calves_f",
                13985.29837,
                175.125,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                1,
                7.945205479,
                16.05479452,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxD_calves_m",
                32140.1008,
                122.2,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                1,
                7.945205479,
                16.05479452,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "DxB_calves_m",
                31755.95617,
                118.55,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                1,
                7.945205479,
                16.05479452,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "BxB_calves_m",
                13424.64053,
                178.775,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                1,
                7.945205479,
                16.05479452,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            [
                "ireland",
                2018,
                2018,
                "bulls",
                4641.388771,
                773,
                0,
                "irish_grass",
                "pasture",
                "concentrate",
                0.654140961,
                11.56164384,
                12.43835616,
                0,
                0,
                "tank liquid",
                "broadcast",
                0,
                0,
            ],
            ["ireland", 2018, 2018, "ewes", 37812.8, 68, 0, "average", "flat_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0],
                ["ireland", 2018, 2018, "ewes", 9453.199999, 68, 0, "average", "hilly_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0],
                ["ireland", 2018, 2018, "ram", 1146.40273838631, 86, 0, "average", "flat_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0],
                ["ireland", 2018, 2018, "ram", 295.990606622309, 86, 0, "average", "hilly_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0],
                ["ireland", 2018, 2018, "lamb_more_1_yr", 2237.33437652812, 68, 0, "average", "flat_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0],
                ["ireland", 2018, 2018, "lamb_more_1_yr", 554.98238741683, 68, 0, "average", "hilly_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0],
                ["ireland", 2018, 2018, "lamb_less_1_yr", 17417.9254767726, 33, 0, "average", "flat_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0],
                ["ireland", 2018, 2018, "lamb_less_1_yr", 4365.86144767906, 33, 0, "average", "hilly_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0],
                ["ireland", 2018, 2018, "male_less_1_yr", 10891.8934622258, 33, 0, "average", "flat_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0],
                ["ireland", 2018, 2018, "male_less_1_yr", 7628.87745495245, 33, 0, "average", "hilly_pasture", "concentrate", 0, 21.36, 2.64, 4.5, 0, "solid", "broadcast", 0, 0]
            ]

        animal_columns_basleine = [
            "ef_country",
            "farm_id",
            "year",
            "cohort",
            "pop",
            "weight",
            "daily_milk",
            "forage",
            "grazing",
            "con_type",
            "con_amount",
            "t_outdoors",
            "t_indoors",
            "wool",
            "t_stabled",
            "mm_storage",
            "daily_spreading",
            "n_sold",
            "n_bought",
        ]


        self.data_frame = pd.DataFrame(data, columns=columns)
        self.animal_dataframe_baseline = pd.DataFrame(animal_data_baseline, columns=animal_columns_basleine)
        self.animal_dataframe_scenarios = pd.read_csv("./data/future_animals.csv")


        self.fert_class = Fertilisation("ireland", 2018, self.data_frame, self.animal_dataframe_scenarios, self.animal_dataframe_baseline)

    def test_fertilisation(self):
        
        test = self.fert_class.compute_organic_fertilization_rate()

        test2 = self.fert_class.compute_fertilization_total()
        print(test2)


if __name__ == "__main__":
    unittest.main()
