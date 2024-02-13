from resource_manager.grassland_data_manager import DataManager
import pandas as pd
import os

def main():

    path_to_data = "./geo_goblin_data/"
    calibration_year = 2020
    target_year = 2050


    scenario_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"future_animals.csv"))
    baseline_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"past_animals.csv"))

    data_manager = DataManager(calibration_year, target_year, scenario_animal_dataframe, baseline_animal_dataframe)

if __name__ == '__main__':
    main()