# 🌱 Grassland_production, a grassland balance tool for Ireland

 Based on the [GOBLIN](https://gmd.copernicus.org/articles/15/2239/2022/) (**G**eneral **O**verview for a **B**ackcasting approach of **L**ivestock **IN**tensification) Grassland module, the Grassland_production module decouples this module making it an independent distribution package.

 The package is shipped with key data for Central Statistics Office grassland areas, Irish National Farm Survey data and FAO fertiliser data. 

 Currently parameterised for Ireland, refactoring is possible, however, this is designed to work alongside other GOBLIN modules specifically for producing scenarios in an Irish context. The module uses the energy requirements of livestock as well as organic and inorganic field inputs to estimate the area required to support the herd.  

 The final outputs are dataframes for:

    -   Total spared area relative to a given baseline year
    -   Total remaining grassland area
    -   Total fertiliser (inorganic) inputs


## Installation

Install from git hub. 

When prompted enter your ```<username>``` and password, which is your ```<access_token>```.

```<access_token>``` is provided by the repo manager.

```<username>``` pass your own github username.


```bash
pip install "grassland_production@git+https://github.com/colmduff/grassland_production.git@main" 

```

## Usage
```python
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
```
## License
This project is licensed under the terms of the MIT license.
