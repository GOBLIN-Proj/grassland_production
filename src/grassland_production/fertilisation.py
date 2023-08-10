from itertools import product
import pandas as pd
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.grassland_area import Areas
from cattle_lca.lca import DailySpread


class Fertilisation:
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

        self.calibration_year = self.data_manager_class.calibration_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.default_grassland_year = self.data_manager_class.default_grassland_year
        self.target_year = self.data_manager_class.target_year

        self.loader_class = Loader()
        self.areas_class = Areas(
            self.target_year, calibration_year, self.default_calibration_year
        )

        self.cattle_spread_class = DailySpread(ef_country)

    def compute_inorganic_fertilization_rate(self):
        """
        Firstly, the fertilisation by system is imported, then, the number of farms by
        farm system. This is used to calculated the average fertilisation rate among
        the total farm system per grassland type [Pasture, Silage, Hay].

        Target year to be set in the scenario inputs, currently using a placeholder value (temp) for
        dairy and beef systems. Sheep systems to use an average value based on past data.
        """

        fertilization_by_system_data_frame = (
            self.loader_class.grassland_fertilization_by_system()
        )

        fertilization_index = fertilization_by_system_data_frame.index.levels[0]

        fert_rate = {"dairy": {}, "beef": {}, "sheep": {}}

        # empty dataframe with grass types  for Dairy
        dairy_fertilization_data_frame = pd.DataFrame(index=fertilization_index)

        # empty dataframe with grass types  for Dairy
        beef_fertilization_data_frame = pd.DataFrame(index=fertilization_index)

        # empty dataframe with grass types  for Dairy
        sheep_fertilization_data_frame = pd.DataFrame(index=fertilization_index)

        scenarios = list(
            self.data_manager_class.scenario_inputs_df["Scenarios"].unique()
        )

        self.fert_rate = {"dairy": {}, "beef": {}, "sheep": {}}
        # for each scenario
        for sc in scenarios:
            beef_mask = (
                (self.data_manager_class.scenario_inputs_df["Scenarios"] == sc)
                & (
                    self.data_manager_class.scenario_inputs_df["Cattle systems"]
                    == "Beef"
                )
                & (
                    self.data_manager_class.scenario_inputs_df["Manure management"]
                    == "tank liquid"
                )
            )
            dairy_mask = (
                (self.data_manager_class.scenario_inputs_df["Scenarios"] == sc)
                & (
                    self.data_manager_class.scenario_inputs_df["Cattle systems"]
                    == "Dairy"
                )
                & (
                    self.data_manager_class.scenario_inputs_df["Manure management"]
                    == "tank liquid"
                )
            )

            _dairy = dairy_fertilization_data_frame.copy(deep=True)
            _beef = beef_fertilization_data_frame.copy(deep=True)
            _sheep = sheep_fertilization_data_frame.copy(deep=True)
            # for each grassland type
            for grassland_type in fertilization_index:
                # add past data to the system dataframes
                if self.calibration_year > self.default_calibration_year:
                    _dairy.loc[
                        grassland_type,
                        str(self.calibration_year),
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Dairy"), str(self.default_calibration_year)
                    ]
                    _beef.loc[
                        grassland_type,
                        str(self.calibration_year),
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Cattle"), str(self.default_calibration_year)
                    ]
                    _sheep.loc[
                        grassland_type,
                        str(self.calibration_year),
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Sheep"), str(self.default_calibration_year)
                    ]
                else:
                    _dairy.loc[
                        grassland_type,
                        str(self.calibration_year),
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Dairy"), str(self.default_calibration_year)
                    ]
                    _beef.loc[
                        grassland_type,
                        str(self.calibration_year),
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Cattle"), str(self.default_calibration_year)
                    ]
                    _sheep.loc[
                        grassland_type,
                        str(self.calibration_year),
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Sheep"), str(self.default_calibration_year)
                    ]

                # if pasture use scenario values for beef and dairy, average for sheep
                if grassland_type == "Pasture" or grassland_type == "Grass silage":
                    _dairy.loc[
                        grassland_type, str(self.target_year)
                    ] = self.data_manager_class.scenario_inputs_df.loc[
                        dairy_mask, "Dairy Pasture fertilisation"
                    ].values[
                        0
                    ]
                    _beef.loc[
                        grassland_type, str(self.target_year)
                    ] = self.data_manager_class.scenario_inputs_df.loc[
                        beef_mask, "Beef Pasture fertilisation"
                    ].values[
                        0
                    ]
                    _sheep.loc[
                        grassland_type, str(self.target_year)
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Sheep"), :
                    ].mean()

                else:
                    # if not pasture, use the average of the past data for the target year
                    _dairy.loc[
                        grassland_type, str(self.target_year)
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Dairy"), :
                    ].mean()
                    _beef.loc[
                        grassland_type, str(self.target_year)
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Cattle"), :
                    ].mean()
                    _sheep.loc[
                        grassland_type, str(self.target_year)
                    ] = fertilization_by_system_data_frame.loc[
                        (grassland_type, "Sheep"), :
                    ].mean()

            # add each scenario to the system keys, and add the specific dataframe for that scenario
            fert_rate["dairy"][sc] = _dairy
            fert_rate["beef"][sc] = _beef
            fert_rate["sheep"][sc] = _sheep

        return fert_rate

    def compute_organic_fertilization_rate(self):
        """
        computation of organic fertilsation and spread rate, based on the farm_LCA net_excretion  from spreading
        function. This is done for each system. However, their is no spreading or application for sheep systems,
        it is assumed that slurry is made of up cattle slurry only.
        """

        cols = self.data_manager_class.systems

        year_list = list(
            (
                self.calibration_year,
                self.target_year,
            )
        )

        animal_list = list(self.data_manager_class.COHORTS_DICT["Cattle"]) + list(
            self.data_manager_class.COHORTS_DICT["Sheep"]
        )

        scenario_list = list(
            self.data_manager_class.scenario_inputs_df.Scenarios.unique()
        )

        spread_dict = {}

        N_spread_past = pd.DataFrame(0, columns=cols, index=year_list)

        baseline_animals_df = self.data_manager_class.baseline_animals_df
        scenario_animals_df = self.data_manager_class.scenario_animals_df

        for animal_name in animal_list:
            animal_past = getattr(
                self.data_manager_class.baseline_animals_dict[self.calibration_year][
                    "animals"
                ],
                animal_name,
            )
            mask_validation = (baseline_animals_df["year"] == self.calibration_year) & (
                baseline_animals_df["cohort"] == animal_name
            )

            if animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Dairy"]:
                N_spread_past.loc[int(self.calibration_year), "dairy"] += (
                    self.cattle_spread_class.net_excretion_SPREAD(animal_past)
                    * baseline_animals_df.loc[mask_validation, "pop"].values[0]
                )

            elif animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Beef"]:
                N_spread_past.loc[int(self.calibration_year), "beef"] += (
                    self.cattle_spread_class.net_excretion_SPREAD(animal_past)
                    * baseline_animals_df.loc[mask_validation, "pop"].values[0]
                )

            elif animal_name in self.data_manager_class.COHORTS_DICT["Sheep"]:
                N_spread_past.loc[int(self.calibration_year), "sheep"] = 0

        # Scenario future inputs
        for scenario in scenario_list:
            N_spread = N_spread_past.copy(deep=True)

            farm_mask = (
                self.data_manager_class.scenario_aggregation["Scenarios"] == scenario
            )

            for farm_name in self.data_manager_class.scenario_aggregation.loc[
                farm_mask, "farm_id"
            ].unique():
                for animal_name in animal_list:
                    if (
                        animal_name
                        in self.data_manager_class.scenario_animals_dict[farm_name][
                            "animals"
                        ].__dict__.keys()
                    ):
                        animal = getattr(
                            self.data_manager_class.scenario_animals_dict[farm_name][
                                "animals"
                            ],
                            animal_name,
                        )
                        mask = (scenario_animals_df["farm_id"] == farm_name) & (
                            scenario_animals_df["cohort"] == animal_name
                        )

                        if (
                            animal_name
                            in self.data_manager_class.DAIRY_BEEF_COHORTS["Dairy"]
                        ):
                            N_spread.loc[int(self.target_year), "dairy"] += (
                                self.cattle_spread_class.net_excretion_SPREAD(animal)
                                * scenario_animals_df.loc[mask, "pop"].values[0]
                            )
                        elif (
                            animal_name
                            in self.data_manager_class.DAIRY_BEEF_COHORTS["Beef"]
                        ):
                            N_spread.loc[int(self.target_year), "beef"] += (
                                self.cattle_spread_class.net_excretion_SPREAD(
                                    animal,
                                )
                                * scenario_animals_df.loc[mask, "pop"].values[0]
                            )

                        elif (
                            animal_name in self.data_manager_class.COHORTS_DICT["Sheep"]
                        ):
                            N_spread.loc[int(self.target_year), "sheep"] = 0

            spread_dict[scenario] = N_spread

        return spread_dict

    def organic_fertilisation_per_ha(self):
        spread_dict = self.compute_organic_fertilization_rate()
        grassland_areas = self.loader_class.cso_grassland_areas()
        nfs_system_proportions = self.areas_class.get_nfs_system_proportions()

        dairy_nfs_system_proportions = nfs_system_proportions[0]
        beef_nfs_system_proportions = nfs_system_proportions[1]

        systems_dict = {
            "dairy": dairy_nfs_system_proportions,
            "beef": beef_nfs_system_proportions,
        }

        default_year_flag = True
        for _dict in spread_dict:
            for sys, year in product(
                spread_dict[_dict].columns, spread_dict[_dict].index[:-1]
            ):
                if sys != "sheep":
                    try:
                        organic_input = spread_dict[_dict].loc[int(year), sys]

                        spread_dict[_dict].loc[int(year), sys] = organic_input / (
                            (
                                grassland_areas.loc[int(year), "Pasture"]
                                * systems_dict[sys].loc[int(year), "Pasture"]
                            )
                            + (
                                grassland_areas.loc[int(year), "Grass silage"]
                                * systems_dict[sys].loc[int(year), "Grass silage"]
                            )
                        )
                    except KeyError:
                        if default_year_flag == True:
                            print(
                                f"... calibration year not present, {self.default_calibration_year} default year used for Spread Manure Dictionary..."
                            )
                            default_year_flag = False

                        organic_input = spread_dict[_dict].loc[int(year), sys]
                        spread_dict[_dict].loc[int(year), sys] = organic_input / (
                            (
                                grassland_areas.loc[
                                    self.default_calibration_year, "Pasture"
                                ]
                                * systems_dict[sys].loc[
                                    self.default_calibration_year, "Pasture"
                                ]
                            )
                            + (
                                grassland_areas.loc[
                                    self.default_calibration_year, "Grass silage"
                                ]
                                * systems_dict[sys].loc[
                                    self.default_calibration_year, "Grass silage"
                                ]
                            )
                        )

                spread_dict[_dict].loc[int(self.target_year), sys] = spread_dict[
                    _dict
                ].loc[int(self.calibration_year), sys]

        return spread_dict
