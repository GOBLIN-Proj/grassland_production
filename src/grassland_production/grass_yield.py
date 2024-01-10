import pandas as pd
from itertools import product
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.fertilisation import Fertilisation


class Yield:
    def __init__(
        self,
        ef_country,
        calibration_year,
        target_year,
        scenario_data,
        scenario_animals_df,
        baseline_animals_df,
    ):
        self.data_manager_class = DataManager(
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.fertiliser_class = Fertilisation(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.loader_class = Loader()
        self.calibration_year = self.data_manager_class.calibration_year
        self.target_year = self.data_manager_class.target_year

        self.soil_class_yield_gap = self.data_manager_class.soil_class_yield_gap

        self.soil_class_prop = self.data_manager_class.soil_class_prop


    def get_clover_parameters(self):
        """
        Defines clover proportion and rate from each scenario that is used to differentiate between conventional yield response
        curves and clover-grass systems. Only dairy and beef (liquid manure) are considered here.
        """
        scenario_df = self.data_manager_class.scenario_inputs_df

        keys = ["dairy", "beef", "sheep"]
        inner_keys = ["proportion", "fertilisation"]

        clover_dict = {key: {inner_key: {} for inner_key in inner_keys} for key in keys}

        conditions = {
            "dairy": (
                    (scenario_df["Cattle systems"] == "Dairy")
                    & (scenario_df["Manure management"] == "tank liquid")
            ),
            "beef": (
                    (scenario_df["Cattle systems"] == "Beef")
                    & (scenario_df["Manure management"] == "tank liquid")
            ),
            "sheep": (
                    (scenario_df["Cattle systems"] == "Lowland sheep")
                    & (scenario_df["Manure management"] == "tank solid")
            )
        }

        for key in keys:
            for sc in scenario_df["Scenarios"]:
                mask = (scenario_df["Scenarios"] == sc) & conditions[key]
                clover_proportion = scenario_df.loc[mask, "Clover proportion"].item()
                clover_fertilisation = scenario_df.loc[mask, "Clover fertilisation"].item()
                clover_dict[key]["proportion"][sc] = clover_proportion
                clover_dict[key]["fertilisation"][sc] = clover_fertilisation


        return clover_dict
       

    def get_yield(self):
        fertilization_by_system_data_frame = (
            self.loader_class.grassland_fertilization_by_system()
        )
        fert_rate = self.fertiliser_class.compute_inorganic_fertilization_rate()
        organic_manure = self.fertiliser_class.organic_fertilisation_per_ha()

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        clover_parameters_dict = self.get_clover_parameters()

        keys = ["dairy", "beef", "sheep"]

        yield_per_ha = {
            farm_type: {
                sc: pd.DataFrame(
                    0,
                    index=fertilization_by_system_data_frame.index.levels[0],
                    columns=year_list,
                )
                for sc in scenario_list
            }
            for farm_type in keys
        }

        for sc, farm_type, grassland_type, soil_group in product(
            scenario_list,
            keys,
            fertilization_by_system_data_frame.index.levels[0],
            self.soil_class_yield_gap.keys(),
        ):
            yield_per_ha_df = yield_per_ha[farm_type][sc]
            soil_class_prop = self.soil_class_prop[farm_type].loc[
                int(self.calibration_year), soil_group
            ]

            yield_per_ha_df.loc[grassland_type, int(self.calibration_year)] += (
                self._yield_response_function_to_fertilizer(
                    fert_rate[farm_type][sc].loc[
                        grassland_type, str(self.calibration_year)
                    ],
                    grassland_type,
                    manure_spread=organic_manure[sc].loc[int(self.calibration_year), farm_type],
                )
                * self.soil_class_yield_gap[soil_group]
            ) * soil_class_prop

            clover_prop = clover_parameters_dict[farm_type]["proportion"][sc]
            clover_fert = clover_parameters_dict[farm_type]["fertilisation"][sc]

            yield_per_ha_df.loc[grassland_type, int(self.target_year)] += (
                self._yield_response_function_to_fertilizer(
                    fert_rate[farm_type][sc].loc[grassland_type, str(self.target_year)],
                    grassland_type,
                    clover_prop=clover_prop,
                    clover_fert=clover_fert,
                    manure_spread=organic_manure[sc].loc[int(self.target_year), farm_type],
                )
                * self.soil_class_yield_gap[soil_group]
            ) * soil_class_prop

        transposed_yield_per_ha = {
            sc: {farm_type: yield_per_ha[farm_type][sc].T for farm_type in keys}
            for sc in scenario_list
        }

        return transposed_yield_per_ha


    def _yield_response_function_to_fertilizer(
        self, fertilizer, grassland, clover_prop=0, clover_fert=0, manure_spread=0
    ):
        """
        This yield response function to fertilizer is taken from Finneran et al. (2011)
        Yield is the theroretical yield

        """

        kg_to_t = 1e-3
        if grassland == "Grass silage" or grassland == "Pasture":
         
            yield_response_default = ((-0.0444 * ((fertilizer + manure_spread) ** 2)
                + 38.419 * (fertilizer + manure_spread)
                + 6257) * (1 - clover_prop)) 
            
            yield_response_clover = (0.7056 * (clover_fert + manure_spread) + 12829) * clover_prop

            yield_response = yield_response_default + yield_response_clover

        else:
            yield_response = -0.0444 * (fertilizer**2) + 38.419 * fertilizer + 6257

        yield_response = yield_response * kg_to_t

        return yield_response
