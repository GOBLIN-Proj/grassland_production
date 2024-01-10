import pandas as pd
import copy
import itertools
from itertools import product
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.grass_yield import Yield
from grassland_production.fertilisation import Fertilisation
from grassland_production.grassland_area import Areas
import cattle_lca.lca as cattle_lca
import sheep_lca.lca as sheep_lca

class UtilisationRate:
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
        self.cattle_grass_feed_class = cattle_lca.GrassFeed(ef_country)
        self.sheep_grass_feed_class = sheep_lca.GrassFeed(ef_country)
        self.concentrate_feed_class = cattle_lca.Energy(ef_country)
        self.sheep_concentrate_feed_class = sheep_lca.Energy(ef_country)


    def get_farm_type_dry_matter_produced(self):
        yield_per_ha = self.yield_class.get_yield()

        # Getting area data
        area_data = {
            "dairy": self.loader_class.dairy_area_nfs(),
            "beef": self.loader_class.beef_area_nfs(),
            "sheep": self.loader_class.sheep_area_nfs()
        }

        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()


        farm_dm_production = {}
        keys = ["dairy", "beef", "sheep"]

        for sc in scenario_list:
            farm_dm_production_df = pd.DataFrame(0, index=year_list, columns=keys)

            for key in keys:
                for year in year_list:
                    total = 0
                    for grassland in self.data_manager_class.grasslands:
                        total += yield_per_ha[sc][key].loc[year, grassland] * area_data[key].loc[self.calibration_year, grassland]
                    farm_dm_production_df.loc[year, key] = total

            farm_dm_production[sc] = farm_dm_production_df.copy(deep=True)

        return farm_dm_production


    def get_farm_type_dry_matter_required(self):
        """
        Dry matter required by the NFS average lievstock population on each of the three farm types.
        """
        kg_to_t = 1e-3
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        NFS_data = {
            "NFS_dairy":{"dairy": self.loader_class.dairy_nfs_animals()},
            "NFS_beef":{"beef":self.loader_class.cattle_nfs_animals()},
            "NFS_sheep":{"sheep":self.loader_class.sheep_nfs_animals()}
        }

        COHORTS = {
            "dairy": self.data_manager_class.DAIRY_BEEF_COHORTS["Dairy"],
            "beef": self.data_manager_class.DAIRY_BEEF_COHORTS["Beef"],
            "sheep": self.data_manager_class.COHORTS_DICT["Sheep"],
        }

        grass_feed_class = {"dairy": self.cattle_grass_feed_class,
                            "beef": self.cattle_grass_feed_class,
                            "sheep": self.sheep_grass_feed_class}

        keys = ["dairy", "beef", "sheep"]

        animal_list = list(self.data_manager_class.COHORTS_DICT["Cattle"]) + list(
            self.data_manager_class.COHORTS_DICT["Sheep"]
        )

        dry_matter_req = {}

        for sc in scenario_list:
            NFS_farm_dm_df = pd.DataFrame(0, index=year_list, columns=keys)

            for animal_name in animal_list:

                animal_past = getattr(self.data_manager_class.baseline_animals_dict[self.calibration_year]["animals"],
                                  animal_name,)

                for key in keys:
                    if animal_name in COHORTS[key]:
                        NFS_farm_dm_df.loc[year_list, key] += (
                            grass_feed_class[key].dry_matter_from_grass(animal_past,)
                            * kg_to_t
                            * 365
                            * NFS_data[f"NFS_{key}"][key].loc[self.calibration_year, animal_name]
                        )

            dry_matter_req[sc] = NFS_farm_dm_df

        return dry_matter_req


    def get_farm_based_utilisation_rate(self):
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()
        scenario_df = self.data_manager_class.scenario_inputs_df

        dry_matter_demand = self.get_farm_type_dry_matter_required()
        dry_matter_available = self.get_farm_type_dry_matter_produced()

        cols = ["dairy", "beef", "sheep"]
        utilisation_rate = {}

        for sc in scenario_list:
            utilisation_rate_df = pd.DataFrame(0, index=year_list, columns=cols)

            dairy_mask = (scenario_df["Scenarios"] == sc) & (scenario_df["Cattle systems"] == "Dairy") & (scenario_df["Manure management"] == "tank liquid")
            beef_mask = (scenario_df["Scenarios"] == sc) & (scenario_df["Cattle systems"] == "Beef") & (scenario_df["Manure management"] == "tank liquid")
            dairy_GUE_scenario_increase = scenario_df.loc[dairy_mask, "Dairy GUE"].unique()
            beef_GUE_scenario_increase = scenario_df.loc[beef_mask, "Beef GUE"].unique()

            for year in year_list:
                for col in cols:
                    if year != self.target_year:
                        utilisation_rate_df.loc[year, col] = dry_matter_demand[sc].loc[self.calibration_year, col] / dry_matter_available[sc].loc[self.calibration_year, col]
                    else:
                        if col == "dairy":
                            utilisation_rate_df.loc[self.target_year, col] = dry_matter_demand[sc].loc[self.calibration_year, col] / dry_matter_available[sc].loc[self.calibration_year, col] + dairy_GUE_scenario_increase
                        elif col == "beef":
                            utilisation_rate_df.loc[self.target_year, col] = dry_matter_demand[sc].loc[self.calibration_year, col] / dry_matter_available[sc].loc[self.calibration_year, col] + beef_GUE_scenario_increase
                        else:  # Assuming sheep has no GUE increase
                            utilisation_rate_df.loc[self.target_year, col] = dry_matter_demand[sc].loc[self.calibration_year, col] / dry_matter_available[sc].loc[self.calibration_year, col]

            utilisation_rate[sc] = utilisation_rate_df.copy(deep=True)

        return utilisation_rate
