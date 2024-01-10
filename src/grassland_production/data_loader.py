from grassland_production.database_manager import DataManager


class Loader:
    def __init__(self):
        self.dataframes = DataManager()

    def grassland_fertilization_by_system(self):
        return self.dataframes.get_grassland_fertilization_by_system()

    def cso_grassland_areas(self):
        return self.dataframes.get_cso_grassland_data()

    def dairy_area_nfs(self):
        return self.dataframes.get_dairy_area_nfs()

    def beef_area_nfs(self):
        return self.dataframes.get_beef_area_nfs()

    def sheep_area_nfs(self):
        return self.dataframes.get_sheep_area_nfs()

    def nfs_farm_numbers(self):
        return self.dataframes.get_nfs_farm_numbers()

    def dairy_soil_group(self):
        return self.dataframes.get_dairy_soil_group()

    def cattle_soil_group(self):
        return self.dataframes.get_cattle_soil_group()

    def sheep_soil_group(self):
        return self.dataframes.get_sheep_soil_group()

    def fao_fertilization(self):
        return self.dataframes.get_fao_fertiliser_data()
    
    def nir_fertilization(self):
        return self.dataframes.get_nir_fertiliser_data()

    def dairy_nfs_animals(self):
        return self.dataframes.get_dairy_nfs_animals()

    def cattle_nfs_animals(self):
        return self.dataframes.get_cattle_nfs_animals()

    def sheep_nfs_animals(self):
        return self.dataframes.get_sheep_nfs_animals()