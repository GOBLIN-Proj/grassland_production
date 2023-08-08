import pandas as pd
from grassland_production.data_loader import Loader
        

class Areas:
    def __init__(self, target_year, calibration_year, default_calibration_year):
        
        self.loader_class = Loader()
        self.target_year = target_year
        self.calibration_year = calibration_year
        self.default_calibration_year = default_calibration_year


    def get_proportion_weight(self, area_nfs, farm_system_number, calibration_year, system, dairy_area_nfs, beef_area_nfs, sheep_area_nfs): #daniel

        return (area_nfs * (farm_system_number.loc[calibration_year, system]/((dairy_area_nfs *farm_system_number.loc[calibration_year, "dairy"])+(beef_area_nfs *farm_system_number.loc[calibration_year, "beef"])+(sheep_area_nfs *farm_system_number.loc[calibration_year, "sheep"]))))


    def get_nfs_system_proportions(self): #daniel
        grassland_types = ["Grass silage", "Hay", "Pasture", "Rough grazing in use"]

        dairy_area_nfs = self.loader_class.dairy_area_nfs()
        beef_area_nfs = self.loader_class.beef_area_nfs()
        sheep_area_nfs = self.loader_class.sheep_area_nfs()

        farm_system_number = self.loader_class.nfs_farm_numbers()
        
        dairy_nfs_system_proportions = pd.DataFrame(0, columns=dairy_area_nfs.columns, index=dairy_area_nfs.index)
        beef_nfs_system_proportions = pd.DataFrame(0, columns=dairy_area_nfs.columns, index=dairy_area_nfs.index)
        sheep_nfs_system_proportions = pd.DataFrame(0, columns=dairy_area_nfs.columns, index=dairy_area_nfs.index)

        for ix in dairy_nfs_system_proportions.index:

            for grassland_type in grassland_types:
                try:
                    dairy_nfs_system_proportions.loc[ix, grassland_type] = self.get_proportion_weight(dairy_area_nfs.loc[ix, grassland_type], farm_system_number, ix, "dairy", dairy_area_nfs.loc[ix, grassland_type], beef_area_nfs.loc[ix, grassland_type], sheep_area_nfs.loc[ix, grassland_type])
                except KeyError:
                    dairy_nfs_system_proportions.loc[ix, grassland_type] = self.get_proportion_weight(dairy_area_nfs.loc[ix, grassland_type], farm_system_number, self.default_calibration_year, "dairy", dairy_area_nfs.loc[ix, grassland_type], beef_area_nfs.loc[ix, grassland_type], sheep_area_nfs.loc[ix, grassland_type])
                    print("... calibration year not present, 2015 default year used for NFS system proportions: Dairy")
                try:
                    beef_nfs_system_proportions.loc[ix, grassland_type] = self.get_proportion_weight(beef_area_nfs.loc[ix, grassland_type], farm_system_number, ix, "beef", dairy_area_nfs.loc[ix, grassland_type], beef_area_nfs.loc[ix, grassland_type], sheep_area_nfs.loc[ix, grassland_type])
                except KeyError:
                    beef_nfs_system_proportions.loc[ix, grassland_type] = self.get_proportion_weight(beef_area_nfs.loc[ix, grassland_type], farm_system_number, self.default_calibration_year, "beef", dairy_area_nfs.loc[ix, grassland_type], beef_area_nfs.loc[ix, grassland_type], sheep_area_nfs.loc[ix, grassland_type])
                    print("... calibration year not present, 2015 default year used for NFS system proportions: Beef")
                try:
                    sheep_nfs_system_proportions.loc[ix, grassland_type] = self.get_proportion_weight(sheep_area_nfs.loc[ix, grassland_type], farm_system_number, ix, "sheep", dairy_area_nfs.loc[ix, grassland_type], beef_area_nfs.loc[ix, grassland_type], sheep_area_nfs.loc[ix, grassland_type])
                except KeyError:
                    sheep_nfs_system_proportions.loc[ix, grassland_type] = self.get_proportion_weight(sheep_area_nfs.loc[ix, grassland_type], farm_system_number, self.default_calibration_year, "sheep", dairy_area_nfs.loc[ix, grassland_type], beef_area_nfs.loc[ix, grassland_type], sheep_area_nfs.loc[ix, grassland_type])
                    print("... calibration year not present, 2015 default year used for NFS system proportions: Sheep")
        return dairy_nfs_system_proportions, beef_nfs_system_proportions, sheep_nfs_system_proportions


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
            "sheep": zeros.copy()
        }

        for ix in index:
            for system in proportions.keys():
                system_area_nfs = locals()[f"{system}_area_nfs"]

                for column in columns:
                    total = sum(system_area_nfs.loc[ix, col] for col in columns)
                    proportions[system].loc[ix, column] = system_area_nfs.loc[ix, column] / total


        return proportions


