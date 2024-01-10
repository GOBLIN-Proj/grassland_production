import sqlalchemy as sqa
import pandas as pd
from grassland_production.database import get_local_dir
import os


class DataManager:
    def __init__(self):
        self.database_dir = get_local_dir()
        self.engine = self.data_engine_creater()

    def data_engine_creater(self):
        database_path = os.path.abspath(
            os.path.join(self.database_dir, "grassland_management_database.db")
        )
        engine_url = f"sqlite:///{database_path}"

        return sqa.create_engine(engine_url)

    def get_cso_grassland_data(self):
        table = "CSO_grassland_areas"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Year"],
        )

        # Scale the values by 1000
        dataframe *= 1000

        return dataframe

    def get_grassland_fertilization_by_system(self):
        table = "grassland_fertilization_by_system"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Grasslandtype", "Farmsystem"],
        )

        return dataframe

    def get_dairy_area_nfs(self):
        table = "dairy_nfs_areas"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_beef_area_nfs(self):
        table = "cattle_nfs_areas"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_sheep_area_nfs(self):
        table = "sheep_nfs_areas"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_nfs_farm_numbers(self):
        table = "national_farm_survey_system_numbers"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_dairy_soil_group(self):
        table = "dairy_soil_group"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_cattle_soil_group(self):
        table = "cattle_soil_group"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_sheep_soil_group(self):
        table = "sheep_soil_group"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_fao_fertiliser_data(self):
        table = "FAO_fertilization"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Year"],
        )

        dataframe *= 1000

        return dataframe
    

    def get_nir_fertiliser_data(self):
        table = "NIR_fertilization"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        dataframe *= 1000

        return dataframe


    def get_dairy_nfs_animals(self):
        table = "dairy_nfs_animals"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_cattle_nfs_animals(self):
        table = "cattle_nfs_animals"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe

    def get_sheep_nfs_animals(self):
        table = "sheep_nfs_animals"

        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        return dataframe