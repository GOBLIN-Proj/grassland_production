from resource_manager.data_loader import Loader
from geo_grassland_production.catchment_grassland import CatchmentGrass
import pandas as pd
import shutil
import os

def main():

    #check for previous test data and remove if exists
    if os.path.exists("./geo_test_data"):
        shutil.rmtree("./geo_test_data")

    #create new test data directory
    os.mkdir("./geo_test_data")

    #set up test data
    path_to_data = "./geo_goblin_data/"

    ef_country = "ireland"
    calibration_year = 2020
    target_year = 2050

    scenario_dataframe = pd.read_csv(os.path.join(path_to_data,"scenario_input_dataframe.csv"))
    scenario_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"future_animals.csv"))
    baseline_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"past_animals.csv"))

    data_loader = Loader()
    catchment = CatchmentGrass('blackwater', calibration_year, target_year, scenario_dataframe, scenario_animal_dataframe, baseline_animal_dataframe)

    print(data_loader.cso_grassland_area_percent())
    print(catchment.get_catchment_grassland_areas())
    print(catchment.get_catchment_grassland_area_caluclated())

if __name__ == '__main__':  
    main()