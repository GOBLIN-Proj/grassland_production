"""
=======================
Grassland Area Module
=======================
The Grassland Area Module is a part of the grassland production system that deals with calculating and managing 
the proportions and distributions of grassland areas within different farming systems. 
It is designed to provide essential data for grassland production analysis, taking into account various factors and scenarios.
"""

import pandas as pd
from itertools import product
from grassland_production.data_loader import Loader


class Areas:
    """
    The `Areas` class is responsible for calculating and managing the proportions and distributions of grassland areas for 
    different farming systems within the Grassland Area Module.

    Args:
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        calibration_year (int): The calibration year.
        defaul_calibration_year (int): The default calibration year.

    Attributes:
        loader_class (Loader): An instance of the Loader class for loading various datasets.
        target_year (int): The target year for calculations.
        calibration_year (int): The calibration year for data reference.
        default_calibration_year (int): The default calibration year used for fallback when data for the specified year is not available.

    Methods:
        get_proportion_weight(
            area_nfs, farm_system_number, nfs_dict, calibration_year, system, grassland_type
        ):
            Calculates the proportion weight for a specific farming system and grassland type.

        get_total_nfs_areas_for_proportions(
            dairy_area_nfs, beef_area_nfs, sheep_area_nfs
        ):
            Computes the total areas for NFS (Nitrogen Fertilization System) proportions.

        get_nfs_system_proportions():
            Calculates the proportions of grassland areas for dairy, beef, and sheep farming systems.

        get_nfs_within_system_grassland_distribution():
            Computes the distribution of grassland areas within each farming system (dairy, beef, sheep).
    """

    def __init__(self, target_year, calibration_year, default_calibration_year):
        self.loader_class = Loader()
        self.target_year = target_year
        self.calibration_year = calibration_year
        self.default_calibration_year = default_calibration_year


    def get_proportion_weight(
        self,
        area_nfs,
        farm_system_number,
        nfs_dict,
        calibration_year,
        system,
        grassland_type,
    ):
        """
        Calculates the proportion weight for a specific farming system and grassland type.

        Args:
            area_nfs (float): The area associated with the National Farm Survey (NFS) data.
            farm_system_number (DataFrame): Farm system numbers for different years (NFS).
            nfs_dict (dict): A dictionary containing NFS data for dairy, beef, and sheep farming systems.
            calibration_year (int): The calibration year for data reference.
            system (str): The farming system (e.g., "dairy", "beef", "sheep").
            grassland_type (str): The type of grassland (e.g., "Grass silage", "Hay", "Pasture", "Rough grazing in use").

        Returns:
            float: The proportion weight for the specified farming system and grassland type.
        """
        total = (
            (
                nfs_dict["dairy"].loc[calibration_year, grassland_type].item()
                * farm_system_number.loc[calibration_year, "dairy"].item()
            )
            + (
                nfs_dict["beef"].loc[calibration_year, grassland_type].item()
                * farm_system_number.loc[calibration_year, "beef"].item()
            )
            + (
                nfs_dict["sheep"].loc[calibration_year, grassland_type].item()
                * farm_system_number.loc[calibration_year, "sheep"].item()
            )
        )

        system_area = area_nfs * farm_system_number.loc[calibration_year, system].item()

        result = system_area / total

        return result

    def get_total_nfs_areas_for_proportions(
        self, dairy_area_nfs, beef_area_nfs, sheep_area_nfs
    ):
        """
        Calculates the total areas associated with the National Farm Survey (NFS) for different farming systems.

        Args:
            dairy_area_nfs (DataFrame): Area data for dairy farming system from NFS.
            beef_area_nfs (DataFrame): Area data for beef farming system from NFS.
            sheep_area_nfs (DataFrame): Area data for sheep farming system from NFS.

        Returns:
            DataFrame: A combined DataFrame containing the total areas for NFS across dairy, beef, and sheep farming systems.
        """
        combined_dataframe = dairy_area_nfs + beef_area_nfs + sheep_area_nfs

        return combined_dataframe


    def get_nfs_system_proportions(self):
        """
        Calculates the proportions of grassland areas for different farming systems based on National Farm Survey (NFS) data.

        Returns:
            tuple: A tuple containing DataFrames for dairy, beef, and sheep farming systems, each with proportions of grassland types.
        """
        grassland_types = ["Grass silage", "Hay", "Pasture", "Rough grazing in use"]

        dairy_area_nfs = self.loader_class.dairy_area_nfs()
        beef_area_nfs = self.loader_class.beef_area_nfs()
        sheep_area_nfs = self.loader_class.sheep_area_nfs()

        nfs_dict = {
            "dairy": dairy_area_nfs,
            "beef": beef_area_nfs,
            "sheep": sheep_area_nfs,
        }

        farm_system_number = self.loader_class.nfs_farm_numbers()

        dairy_nfs_system_proportions = pd.DataFrame(
            0.0, columns=dairy_area_nfs.columns, index=dairy_area_nfs.index
        )
        beef_nfs_system_proportions = pd.DataFrame(
            0.0, columns=dairy_area_nfs.columns, index=dairy_area_nfs.index
        )
        sheep_nfs_system_proportions = pd.DataFrame(
            0.0, columns=dairy_area_nfs.columns, index=dairy_area_nfs.index
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
                    nfs_dict[sys].loc[ix, grassland_type],
                    farm_system_number,
                    nfs_dict,
                    ix,
                    sys,
                    grassland_type,
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
                    grassland_type,
                )

        return systems_dict["dairy"], systems_dict["beef"], systems_dict["sheep"]


    def get_nfs_within_system_grassland_distribution(self):
        """
        Calculates the distribution of grassland areas within different farming systems based on National Farm Survey (NFS) data.

        Returns:
            dict: A dictionary containing DataFrames for dairy, beef, and sheep farming systems, each with the distribution of grassland types.
        """
        dairy_area_nfs = self.loader_class.dairy_area_nfs()
        beef_area_nfs = self.loader_class.beef_area_nfs()
        sheep_area_nfs = self.loader_class.sheep_area_nfs()

        columns = dairy_area_nfs.columns
        index = dairy_area_nfs.index

        zeros = pd.DataFrame(0.0, columns=columns, index=index)

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
