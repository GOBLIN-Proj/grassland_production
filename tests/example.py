import pandas as pd
from grassland_production.grassland_output import GrasslandOutput
import shutil
import os

def main():

    #check for previous test data and remove if exists
    if os.path.exists("./test_data"):
        shutil.rmtree("./test_data")

    #create new test data directory
    os.mkdir("./test_data")

    #set up test data
    path_to_data = "./data/"

    ef_country = "ireland"
    calibration_year = 2020
    target_year = 2050

    scenario_dataframe = pd.read_csv(os.path.join(path_to_data,"scenario_input_dataframe.csv"), index_col=0)
    scenario_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"scenario_animal_data.csv"))
    baseline_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"baseline_animal_data.csv"))

    #class instance
    grassland = GrasslandOutput(
        ef_country,
        calibration_year,
        target_year,
        scenario_dataframe,
        scenario_animal_dataframe,
        baseline_animal_dataframe,
    )

    #print results

    #total destocked area
    print(grassland.total_spared_area())

    #total remaining grassland 
    print(grassland.total_grassland_area())

    #farm inputs (nitrogen, phosphorus, potassium, lime)
    print(grassland.farm_inputs_data())

    #baseline (calibration) farm inputs (nitrogen, phosphorus, potassium, lime)
    print(grassland.baseline_farm_inputs_data())

    #total destocked area by soil group
    print(grassland.total_spared_area_breakdown())

    #total concentrate feed
    print(grassland.total_concentrate_feed())

    #per hectare stocking rate
    print(grassland.grassland_stocking_rate())


    #save results to csv
    test_data_path = "./test_data"

    grassland.total_spared_area().to_csv(os.path.join(test_data_path,"spared_area_0.3.6.csv"))
    grassland.total_grassland_area().to_csv(os.path.join(test_data_path,"total_grassland_area_0.3.6.csv"))
    grassland.total_spared_area_breakdown().to_csv(os.path.join(test_data_path,"spared_area_breakdown_0.3.6.csv"))
    grassland.total_concentrate_feed().to_csv(os.path.join(test_data_path,"concentrate_feed_0.3.6.csv"))
    grassland.grassland_stocking_rate().to_csv(os.path.join(test_data_path,"stocking_rate_0.3.6.csv"))
    grassland.grass_yield_per_hectare().to_csv(os.path.join(test_data_path,"grass_yield_per_hectare_0.3.6.csv"))


if __name__ == "__main__":
    main()
