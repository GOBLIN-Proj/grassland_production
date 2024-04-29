# 🌱 Grassland_production, a grassland balance tool for catchment and national level analysis in the Irish context
[![license](https://img.shields.io/badge/License-MIT-red)](https://github.com/GOBLIN-Proj/grassland_production/blob/0.1.0/LICENSE)
[![python](https://img.shields.io/badge/python-3.9-blue?logo=python&logoColor=white)](https://github.com/GOBLIN-Proj/grassland_production)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

 Based on the [GOBLIN](https://gmd.copernicus.org/articles/15/2239/2022/) (**G**eneral **O**verview for a **B**ackcasting approach of **L**ivestock **IN**tensification) Grassland module, the Grassland_production library decouples this module making it an independent distribution package.

## Structure
 The package is structured for use in national and catchment level analysis. 

 The geo_grassland_production sub module is intended for use at the catchment level and interfaces with the catchment_data_api to 
 retrieve catchment specific grassland data that has been retrieved from [Ireland's National Land Cover map](https://www.epa.ie/our-services/monitoring--assessment/assessment/mapping/national-land-cover-map/)

 ```
    src/
    │
    ├── grassland_production/
    │   └── ... (other modules and sub-packages)
        │
        ├── geo_grassland_production/
        |   └── ... (other modules and sub-packages)

 ```

 For national level analysis, the package is shipped with key data for [Central Statistics Office](https://www.cso.ie/en/index.html) grassland areas, Irish [National Farm Survey](https://www.teagasc.ie/rural-economy/rural-economy/national-farm-survey/) data and [FAO](https://www.fao.org/faostat/en/#home) fertiliser data. 

 Currently parameterised for Ireland, refactoring is possible, however, this is designed to work alongside other GOBLIN (and GOBLIN derivative) modules specifically for producing scenarios in an Irish national and catchment context. The module uses the energy requirements of livestock as well as organic and inorganic field inputs to estimate the area required to support the herd.  

 The final outputs are dataframes for:

    -   Total spared (destocked) area relative to a given baseline year
    -   Total remaining grassland area
    -   Total fertiliser (inorganic) inputs
    -   Spared area soil group breakdown
    -   Total concentrate feed
    -   Per ha stocking rate


## Installation

Install from git hub. 

```bash
pip install "grassland_production@git+https://github.com/GOBLIN-Proj/grassland_production.git@main" 

```

Install from PyPI

```bash
pip install grassland_production
```

## Usage
Below is an example usage of the grassland_production submodule, for the national level. 

```python
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

    scenario_dataframe = pd.read_csv(os.path.join(path_to_data,"scenario_dataframe1.csv"))
    scenario_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"future_animals.csv"))
    baseline_animal_dataframe = pd.read_csv(os.path.join(path_to_data,"past_animals.csv"))

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

    grassland.total_spared_area().to_csv(os.path.join(test_data_path,"spared_area.csv"))
    grassland.total_grassland_area().to_csv(os.path.join(test_data_path,"total_grassland_area.csv"))
    grassland.total_spared_area_breakdown().to_csv(os.path.join(test_data_path,"spared_area_breakdown.csv"))
    grassland.total_concentrate_feed().to_csv(os.path.join(test_data_path,"concentrate_feed.csv"))
    grassland.grassland_stocking_rate().to_csv(os.path.join(test_data_path,"stocking_rate.csv"))


if __name__ == "__main__":
    main()
```
## License
This project is licensed under the terms of the MIT license.
