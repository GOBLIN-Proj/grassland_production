import pandas as pd
from grassland_production.grassland_output import GrasslandOutput


def main():
    ef_country = "ireland"
    calibration_year = 2020
    target_year = 2050

    scenario_dataframe = pd.read_csv("./data/scenario_dataframe1.csv")
    scenario_animal_dataframe = pd.read_csv("./data/future_animals.csv")
    baseline_animal_dataframe = pd.read_csv("./data/past_animals.csv")

    grassland = GrasslandOutput(
        ef_country,
        calibration_year,
        target_year,
        scenario_dataframe,
        scenario_animal_dataframe,
        baseline_animal_dataframe,
    )

    print(grassland.total_spared_area())

    print(grassland.total_grassland_area())

    print(grassland.farm_inputs_data())

    print(grassland.baseline_farm_inputs_data())

    grassland.total_spared_area().to_csv("./data/spared_area.csv")
    grassland.total_grassland_area().to_csv("./data/total_grassland_area.csv")


if __name__ == "__main__":
    main()
