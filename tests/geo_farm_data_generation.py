import pandas as pd
from grassland_production.geo_grassland_production.geo_farm_data_generation import FarmData
import os



def main():
    path = "./geo_goblin_data/"

    # Create the DataFrame with the provided data
    scenario_dataframe = pd.read_csv(os.path.join(path, "scenario_input_dataframe.csv"))
    scenario_animal_dataframe = pd.read_csv(os.path.join(path, "future_animals.csv"))
    baseline_animal_dataframe = pd.read_csv(os.path.join(path, "past_animals.csv"))


    farm_class = FarmData(
            "ireland",
            2020,
            2050,
            scenario_dataframe,
            scenario_animal_dataframe,
            baseline_animal_dataframe,
        )

    test = farm_class.compute_farm_data_in_baseline()

    print(test)


if __name__ == "__main__":
    main()
