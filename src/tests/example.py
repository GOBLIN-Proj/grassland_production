import pandas as pd
from grassland_production.grassland_output import GrasslandOutput


def main():

    ef_country = "ireland"
    calibration_year = 2018 

    scenario_dataframe = pd.read_csv("./data/scenario_dataframe.csv")
    scenario_animal_dataframe = pd.read_csv("./data/future_animals.csv")
    baseline_animal_dataframe = pd.read_csv("./data/past_animals.csv")

    grassland = GrasslandOutput(ef_country, calibration_year, scenario_dataframe, scenario_animal_dataframe, baseline_animal_dataframe)

    print(grassland.total_spared_area())

    print(grassland.total_grassland_area())

    print(grassland.farm_inputs_data())

if __name__ == "__main__":
    main()
