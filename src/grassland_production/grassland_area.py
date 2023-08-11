import pandas as pd
from itertools import product
from grassland_production.data_loader import Loader


class Areas:
    def __init__(self, target_year, calibration_year, default_calibration_year):
        self.loader_class = Loader()
        self.target_year = target_year
        self.calibration_year = calibration_year
        self.default_calibration_year = default_calibration_year


    def get_proportion_weight(
        self, area_nfs, farm_system_number, nfs_dict, calibration_year, system, grassland_type
    ):
        
        total = (
                (nfs_dict["dairy"].loc[calibration_year,grassland_type].item() * farm_system_number.loc[calibration_year, "dairy"].item())
                + (nfs_dict["beef"].loc[calibration_year,grassland_type].item() * farm_system_number.loc[calibration_year, "beef"].item())
                + (nfs_dict["sheep"].loc[calibration_year,grassland_type].item()* farm_system_number.loc[calibration_year, "sheep"].item())
            )
        
        system_area = area_nfs * farm_system_number.loc[calibration_year, system].item()
        
        result = system_area/total

        return result
        

    def get_total_nfs_areas_for_proportions(self, dairy_area_nfs, beef_area_nfs, sheep_area_nfs):

        combined_dataframe = dairy_area_nfs + beef_area_nfs + sheep_area_nfs

        return combined_dataframe
    

    def get_nfs_system_proportions(self):
        grassland_types = ["Grass silage", "Hay", "Pasture", "Rough grazing in use"]

        dairy_area_nfs = self.loader_class.dairy_area_nfs()
        beef_area_nfs = self.loader_class.beef_area_nfs()
        sheep_area_nfs = self.loader_class.sheep_area_nfs()

        nfs_dict= {
            "dairy": dairy_area_nfs,
            "beef": dairy_area_nfs,
            "sheep": dairy_area_nfs,
        }

        #total_areas_nfs = self.get_total_nfs_areas_for_proportions(dairy_area_nfs, beef_area_nfs, sheep_area_nfs)

        farm_system_number = self.loader_class.nfs_farm_numbers()

        dairy_nfs_system_proportions = pd.DataFrame(
            0, columns=dairy_area_nfs.columns, index=dairy_area_nfs.index
        )
        beef_nfs_system_proportions = pd.DataFrame(
            0, columns=dairy_area_nfs.columns, index=dairy_area_nfs.index
        )
        sheep_nfs_system_proportions = pd.DataFrame(
            0, columns=dairy_area_nfs.columns, index=dairy_area_nfs.index
        )



        systems_dict = {
            "dairy": dairy_nfs_system_proportions,
            "beef": beef_nfs_system_proportions,
            "sheep": sheep_nfs_system_proportions,
        }

        default_year_flag = False
        for sys, grassland_type, ix in product(
            systems_dict.keys(), grassland_types, dairy_nfs_system_proportions.index
        ):
            
            try:
                systems_dict[sys].at[ix, grassland_type] = self.get_proportion_weight(
                    nfs_dict[sys].loc[ix, grassland_type], farm_system_number, nfs_dict, ix, sys, grassland_type
                )
            except KeyError:
                if default_year_flag == True:
                    print(
                        f"... calibration year not present, {self.default_calibration_year} default year used for NFS systems proportion..."
                    )
                    default_year_flag = False

                systems_dict[sys].at[ix, grassland_type] = self.get_proportion_weight(
                    nfs_dict[sys].loc[self.default_calibration_year, grassland_type],
                    farm_system_number,
                    nfs_dict,
                    self.default_calibration_year,
                    sys,
                    grassland_type
                )

        return systems_dict["dairy"], systems_dict["beef"], systems_dict["sheep"]
    

    def get_nfs_within_system_grassland_distribution(self):
        dairy_area_nfs = self.loader_class.dairy_area_nfs()
        beef_area_nfs = self.loader_class.beef_area_nfs()
        sheep_area_nfs = self.loader_class.sheep_area_nfs()

        columns = dairy_area_nfs.columns
        index = dairy_area_nfs.index

        zeros = pd.DataFrame(0, columns=columns, index=index)

        proportions = {
            "dairy": zeros.copy(),
            "beef": zeros.copy(),
            "sheep": zeros.copy(),
        }

        for ix in index:
            for system in proportions.keys():
                system_area_nfs = locals()[f"{system}_area_nfs"]

                for column in columns:
                    total = sum(system_area_nfs.loc[ix, col] for col in columns)
                    proportions[system].loc[ix, column] = (
                        system_area_nfs.loc[ix, column] / total
                    )

        return proportions
