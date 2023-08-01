from grassland_production.spared_area import Grasslands
from grassland_production.farm_data_generation import FarmData


class GrasslandOutput:
    def __init__(self,ef_country, calibration_year, scenario_data, scenario_animals_df,baseline_animals_df):

        self.grassland_class = Grasslands(ef_country, calibration_year, scenario_data, scenario_animals_df,baseline_animals_df)
        self.farm_data_class = FarmData(ef_country, calibration_year, scenario_data, scenario_animals_df,baseline_animals_df)

    def total_spared_area(self):
        return self.grassland_class.get_non_grass_total_area()


    def total_grassland_area(self):
        return self.grassland_class.get_grass_total_area()


    def farm_inputs_data(self):
        return self.farm_data_class.compute_farm_data_in_scenarios()
    

    def baseline_farm_inputs_data(self):
        return self.farm_data_class.compute_farm_data_in_baseline()