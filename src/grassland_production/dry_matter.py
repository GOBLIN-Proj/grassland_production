import pandas as pd
import copy
from itertools import product
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.grass_yield import Yield
from grassland_production.fertilisation import Fertilisation
from grassland_production.grassland_area import Areas
import cattle_lca.lca as cattle_lca
import sheep_lca.lca as sheep_lca
from cattle_lca.animal_data import AnimalData as cattle_data
from sheep_lca.animal_data import AnimalData as sheep_data

class DryMatter:
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
        self.target_year = self.data_manager_class.target_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.yield_class = Yield(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )
        self.areas_class = Areas(
            target_year, calibration_year, self.default_calibration_year
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
        self.grass_feed_class = cattle_lca.GrassFeed(ef_country)
        self.sheep_grass_feed_class = sheep_lca.GrassFeed(ef_country)



    def get_actual_dry_matter_produced(self):
        """
        returns the actually dry matter produced in each system, based on the yield per grassland type of each system
        with inputs for grassland type specific to each system.

        Years earlier than 2005 are interpolated, thus not very accurate. However, they are not really needed.

        """
        fertilization_by_system_data_frame = (
            self.loader_class.grassland_fertilization_by_system()
        )
        yield_per_ha = self.yield_class.get_yield()

        grassland_areas = self.loader_class.cso_grassland_areas()
        nfs_system_proportions = self.areas_class.get_nfs_system_proportions()

        dairy_nfs_system_proportions = nfs_system_proportions[0]
        beef_nfs_system_proportions = nfs_system_proportions[1]
        sheep_nfs_system_proportions = nfs_system_proportions[2]

        nfs_system_proportions = {
            "dairy": dairy_nfs_system_proportions,
            "beef": beef_nfs_system_proportions,
            "sheep": sheep_nfs_system_proportions,
        }

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        keys = ["dairy", "beef", "sheep"]

        dry_matter_produced = {
            sc: {
                farm_type: pd.DataFrame(
                    0,
                    index=fertilization_by_system_data_frame.index.levels[0],
                    columns=year_list,
                )
                for farm_type in keys
            }
            for sc in scenario_list
        }

        default_year_flag = True
        for sc, year, farm_type, grassland_type in product(
            scenario_list,
            year_list,
            keys,
            fertilization_by_system_data_frame.index.levels[0],
        ):
            total_dm = dry_matter_produced[sc][farm_type]

            calibration_year_value = self.calibration_year

            try:
                proportion = nfs_system_proportions[farm_type].loc[
                    calibration_year_value, grassland_type
                ]

                total_dm.loc[grassland_type, year] += yield_per_ha[sc][farm_type].loc[
                    year, grassland_type
                ] * (
                    grassland_areas.loc[calibration_year_value, grassland_type]
                    * proportion
                )

            except KeyError:
                calibration_year_value = int(self.default_calibration_year)

                if default_year_flag == True:
                    print(
                        f"... calibration year not present, {calibration_year_value} default year used for total Dry Matter..."
                    )
                    default_year_flag = False

                proportion = nfs_system_proportions[farm_type].loc[
                    calibration_year_value, grassland_type
                ]

                total_dm.loc[grassland_type, year] += yield_per_ha[sc][farm_type].loc[
                    year, grassland_type
                ] * (
                    grassland_areas.loc[calibration_year_value, grassland_type]
                    * proportion
                )

        transposed_dry_matter_produced = {
            sc: {farm_type: dry_matter_produced[sc][farm_type].T for farm_type in keys}
            for sc in scenario_list
        }

        for sc, farm_type in product(scenario_list, keys):
            transposed_dry_matter_produced[sc][farm_type][
                "total"
            ] = transposed_dry_matter_produced[sc][farm_type].sum(axis=1)

        return transposed_dry_matter_produced
    


    def actual_dry_matter_required_past(self):
        """
        Produces the dry matter requirement for each of the livestock systems. The lca_farm.dry_matter_from_grass function
        is used to produce this.

        """

        kg_to_t = 1e-3

        baseline_animals_df = self.data_manager_class.baseline_animals_df

        cols = ["dairy", "beef", "sheep", "total"]

        animal_list = list(self.data_manager_class.COHORTS_DICT["Cattle"]) + list(
            self.data_manager_class.COHORTS_DICT["Sheep"]
        )

        past_total_dm_df = pd.DataFrame(0, index=[self.calibration_year], columns=cols)

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
                past_total_dm_df.loc[self.calibration_year, "dairy"] += (
                    self.grass_feed_class.dry_matter_from_grass(
                        animal_past,
                    )
                    * kg_to_t
                    * 365
                    * baseline_animals_df.loc[mask_validation, "pop"].values[0]
                )

            if animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Beef"]:
                past_total_dm_df.loc[self.calibration_year, "beef"] += (
                    self.grass_feed_class.dry_matter_from_grass(
                        animal_past,
                    )
                    * kg_to_t
                    * 365
                    * baseline_animals_df.loc[mask_validation, "pop"].values[0]
                )

            elif animal_name in self.data_manager_class.COHORTS_DICT["Sheep"]:
                for landtype in ["flat_pasture", "hilly_pasture"]:
                    sheep_mask_validation = (
                        (baseline_animals_df["year"] == self.calibration_year)
                        & (baseline_animals_df["cohort"] == animal_name)
                        & (baseline_animals_df["grazing"] == landtype)
                    )
                    past_total_dm_df.loc[self.calibration_year, "sheep"] += (
                        self.sheep_grass_feed_class.dry_matter_from_grass(
                            animal_past,
                        )
                        * kg_to_t
                        * 365
                        * baseline_animals_df.loc[sheep_mask_validation, "pop"].values[
                            0
                        ]
                    )

        past_total_dm_df["total"] = (past_total_dm_df["dairy"]+ past_total_dm_df["beef"]+ past_total_dm_df["sheep"])

        return past_total_dm_df
    

    def actual_dry_matter_required_future(self):
        kg_to_t = 1e-3

        cols = ["dairy", "beef", "sheep", "total"]

        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        scenario_animals_df = self.data_manager_class.scenario_animals_df

        future_total_dm_df = pd.DataFrame(0, index=[self.target_year], columns=cols)

        dry_matter_req = {}
        
        animal_list = list(self.data_manager_class.COHORTS_DICT["Cattle"]) + list(
            self.data_manager_class.COHORTS_DICT["Sheep"]
        )

        for sc in scenario_list:
            total_dm_df = future_total_dm_df
            dry_matter_req[sc] = total_dm_df.copy(deep=True)

            farm_mask = self.data_manager_class.scenario_aggregation["Scenarios"] == sc
            farm_ids = self.data_manager_class.scenario_aggregation.loc[
                farm_mask, "farm_id"
            ].unique()

            for farm_id in farm_ids:
                for animal_name in animal_list:
                    if (
                        animal_name
                        in self.data_manager_class.scenario_animals_dict[farm_id][
                            "animals"
                        ].__dict__.keys()
                    ):
                        animal_scenario = getattr(
                            self.data_manager_class.scenario_animals_dict[farm_id][
                                "animals"
                            ],
                            animal_name,
                        )
                        mask = (scenario_animals_df["farm_id"] == farm_id) & (
                            scenario_animals_df["cohort"] == animal_name
                        )

                        if (
                            animal_name
                            in self.data_manager_class.DAIRY_BEEF_COHORTS["Dairy"]
                        ):
                            dry_matter_req[sc].loc[self.target_year, "dairy"] += (
                                self.grass_feed_class.dry_matter_from_grass(
                                    animal_scenario
                                )
                                * kg_to_t
                                * 365
                                * scenario_animals_df.loc[mask, "pop"].values[0]
                            )
                        elif (
                            animal_name
                            in self.data_manager_class.DAIRY_BEEF_COHORTS["Beef"]
                        ):
                            dry_matter_req[sc].loc[self.target_year, "beef"] += (
                                self.grass_feed_class.dry_matter_from_grass(
                                    animal_scenario
                                )
                                * kg_to_t
                                * 365
                                * scenario_animals_df.loc[mask, "pop"].values[0]
                            )
                        elif (
                            animal_name in self.data_manager_class.COHORTS_DICT["Sheep"]
                        ):
                            for landtype in ["flat_pasture", "hilly_pasture"]:
                                sheep_mask = (
                                    (scenario_animals_df["farm_id"] == farm_id)
                                    & (scenario_animals_df["cohort"] == animal_name)
                                    & (scenario_animals_df["grazing"] == landtype)
                                )
                                dry_matter_req[sc].loc[self.target_year, "sheep"] += (
                                    self.sheep_grass_feed_class.dry_matter_from_grass(
                                        animal_scenario
                                    )
                                    * kg_to_t
                                    * 365
                                    * scenario_animals_df.loc[sheep_mask, "pop"].values[
                                        0
                                    ]
                                )

            dry_matter_req[sc]["total"] = (
                dry_matter_req[sc]["dairy"]
                + dry_matter_req[sc]["beef"]
                + dry_matter_req[sc]["sheep"]
            )

        return dry_matter_req
    

    def actual_dry_matter_required(self):
        """
        Produces the dry matter requirement for each of the livestock systems. The lca_farm.dry_matter_from_grass function
        is used to produce this.

        """
        past_dm = self.actual_dry_matter_required_past()
        future_dm = self.actual_dry_matter_required_future()

        for sc in future_dm.keys():
            future_dm[sc].loc[self.calibration_year] = past_dm.loc[self.calibration_year]

        return future_dm
    
    def get_dm_proportional_reduction(self):
        past_dm = self.actual_dry_matter_required_past()
        future_dm = self.actual_dry_matter_required_future()

        proportion_reduction = {}

        for sc in future_dm.keys():
            proportion_reduction[sc] = {}
            for cohort in past_dm.columns:
                if cohort != "total":

                    proportion = 1-(future_dm[sc].loc[self.target_year,cohort]/past_dm.loc[self.calibration_year, cohort])

                    if proportion < 0:
                        proportion = 0
                
                    proportion_reduction[sc][cohort] = proportion
            
            proportion_reduction[sc]["total"] = sum(proportion_reduction[sc].values())
            
        return proportion_reduction


    def weighted_dm_reduction_contribution(self):

        proprotion_reduction = self.get_dm_proportional_reduction()

        weights = {} 

        for sc in proprotion_reduction.keys():
            weights[sc] = {}
            for cohort in proprotion_reduction[sc].keys():
                if cohort != "total":
                    weights[sc][cohort] = proprotion_reduction[sc][cohort]/proprotion_reduction[sc]["total"]

        return weights

    def get_total_concentrate_feed(self):
            """
            Calculates the total amount of concentrate feed that is required by all livestock within each farm system in tonnes per year.
            """
            kg_to_t = 1e-3
            year_list = [self.calibration_year, self.target_year]
            scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

            baseline_animals_df = self.data_manager_class.baseline_animals_df
            scenario_animals_df = self.data_manager_class.scenario_animals_df

            cols = ["dairy", "beef", "sheep", "total"]

            animal_list = list(self.data_manager_class.COHORTS_DICT["Cattle"]) + list(
                self.data_manager_class.COHORTS_DICT["Sheep"]
            )

            past_total_conc_df = pd.DataFrame(0, index=year_list, columns=cols)

            total_concentrate_feed = {}

            for animal_name in animal_list:

                animal_past = getattr(self.data_manager_class.baseline_animals_dict[self.calibration_year]["animals"], animal_name)

                mask_validation = (baseline_animals_df["year"]== self.calibration_year) & (baseline_animals_df["cohort"] == animal_name)

                if animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Dairy"]:

                    past_total_conc_df.loc[self.calibration_year, "dairy"] += (cattle_data.get_animal_concentrate_amount(animal_past,) * kg_to_t * 365 * baseline_animals_df.loc[mask_validation, "pop"].values[0])

                if animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Beef"]:
                    past_total_conc_df.loc[self.calibration_year, "beef"] += (cattle_data.get_animal_concentrate_amount(animal_past,) * kg_to_t * 365 * baseline_animals_df.loc[mask_validation, "pop"].values[0])

                elif animal_name in self.data_manager_class.COHORTS_DICT["Sheep"]:
                    for landtype in ["flat_pasture", "hilly_pasture"]:
                        sheep_mask_validation = ((baseline_animals_df["year"]== self.calibration_year)& (baseline_animals_df["cohort"] == animal_name)& (baseline_animals_df["grazing"] == landtype))
                        past_total_conc_df.loc[self.calibration_year, "sheep"] += (sheep_data.get_animal_concentrate_amount(animal_past,) * kg_to_t * 365 * baseline_animals_df.loc[sheep_mask_validation, "pop"].values[0])

            past_total_conc_df["total"] = (
                past_total_conc_df["dairy"]
                + past_total_conc_df["beef"]
                + past_total_conc_df["sheep"]
            )

            for sc in scenario_list:
                total_conc_df = past_total_conc_df.copy(deep=True)
                total_concentrate_feed[sc] = total_conc_df

                farm_mask = self.data_manager_class.scenario_aggregation["Scenarios"] == sc
                farm_ids = self.data_manager_class.scenario_aggregation.loc[farm_mask, "farm_id"].unique()

                for farm_id in farm_ids:
                    for animal_name in animal_list:
                        if animal_name in self.data_manager_class.scenario_animals_dict[farm_id]["animals"].__dict__.keys():
                            animal_scenario = getattr(self.data_manager_class.scenario_animals_dict[farm_id]["animals"], animal_name)
                            mask = ((scenario_animals_df["farm_id"] == farm_id)& (scenario_animals_df["cohort"] == animal_name))

                            if animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Dairy"]:
                                total_concentrate_feed[sc].loc[self.target_year, "dairy"] += (cattle_data.get_animal_concentrate_amount(animal_scenario) * kg_to_t * 365 * scenario_animals_df.loc[mask, "pop"].values[0])

                            elif animal_name in self.data_manager_class.DAIRY_BEEF_COHORTS["Beef"]:
                                total_concentrate_feed[sc].loc[self.target_year, "beef"] += (cattle_data.get_animal_concentrate_amount(animal_scenario) * kg_to_t * 365 * scenario_animals_df.loc[mask, "pop"].values[0])
                            elif animal_name in self.data_manager_class.COHORTS_DICT["Sheep"]:
                                for landtype in ["flat_pasture", "hilly_pasture"]:
                                    sheep_mask = ((scenario_animals_df["farm_id"] == farm_id)& (scenario_animals_df["cohort"] == animal_name)& (scenario_animals_df["grazing"] == landtype))
                                    total_concentrate_feed[sc].loc[self.target_year, "sheep"] += (sheep_data.get_animal_concentrate_amount(animal_scenario) * kg_to_t * 365 * scenario_animals_df.loc[sheep_mask, "pop"].values[0])

                total_concentrate_feed[sc]["total"] = (
                    total_concentrate_feed[sc]["dairy"]
                    + total_concentrate_feed[sc]["beef"]
                    + total_concentrate_feed[sc]["sheep"]
                )

            return total_concentrate_feed
    

    def get_utilisation_rate(self):
            """
            A utilisation rate is produced for each livestock system and each scenario.
            For years earlier than the target year, the utilisation rate is the aggregation of the dry matter produced
            for each livestock system and grassland type. The dry matter requirement is then divided by the aggregated
            dry matter produced.
            For the target year, the utilisation rate is equal to the utilisation rate in the self.imported_specifications.calibration_year + the
            utilisation rate increase specified in the scenario parameters.
            """
            grasslands = self.data_manager_class.grasslands
            year_list = [self.calibration_year, self.target_year]
            scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()
            cols = ["dairy", "beef", "sheep"]

            utilisation_rate = {}

            scenario_df = self.data_manager_class.scenario_inputs_df
            dry_matter_produced = self.get_actual_dry_matter_produced()
            dry_matter_req = self.actual_dry_matter_required()

            for sc in scenario_list:
                scenario_mask = scenario_df["Scenarios"] == sc
                dairy_mask =(scenario_df["Scenarios"] == sc) & (scenario_df["Cattle systems"] == "Dairy") \
                            & (scenario_df["Manure management"] == "tank liquid")
                beef_mask = (scenario_df["Scenarios"] == sc) & (scenario_df["Cattle systems"] == "Beef") \
                            & (scenario_df["Manure management"] == "tank liquid")
                
                dairy_GUE_scenario_increase = scenario_df.loc[dairy_mask, "Dairy GUE"].unique()
                beef_GUE_scenario_increase = scenario_df.loc[beef_mask, "Beef GUE"].unique()

                utilisation_rate_df = pd.DataFrame(0, index=year_list, columns=cols)

                for farm_type in cols:
                    for year in year_list:
                        if year == self.target_year:
                            if farm_type == "dairy":
                                utilisation_rate_df.loc[year, "dairy"] = \
                                    (utilisation_rate_df.loc[self.calibration_year, farm_type]) \
                                    + dairy_GUE_scenario_increase

                            elif farm_type == "beef":
                                utilisation_rate_df.loc[year, "beef"] = \
                                    (utilisation_rate_df.loc[self.calibration_year, farm_type]) \
                                    + beef_GUE_scenario_increase

                            else:
                                utilisation_rate_df.loc[year, farm_type] = \
                                    (utilisation_rate_df.loc[self.calibration_year, farm_type])

                        else:
                            for grassland_type in grasslands:
                                utilisation_rate_df.loc[year, farm_type] += \
                                    dry_matter_produced[sc][farm_type].loc[year, grassland_type]
                            utilisation_rate_df.loc[year, farm_type] = (dry_matter_req[sc].loc[year, farm_type]/ \
                                                                        utilisation_rate_df.loc[year, farm_type])

                utilisation_rate[sc] = copy.deepcopy(utilisation_rate_df)

            return utilisation_rate