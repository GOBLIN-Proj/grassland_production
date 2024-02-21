"""
===========================
Catchment Grassland Module
===========================
This module provides functionality for managing and analyzing grassland data within specified catchment areas. 
It is designed to support environmental and agricultural studies, focusing on grassland distribution, usage, and management strategies under 
various scenarios.

The module primarily includes the CatchmentGrass class, which interfaces with different data sources to aggregate, process, 
and calculate grassland areas. It utilizes a combination of catchment-specific grassland data, proportion data for grassland areas, 
and scenario-based analysis to derive insights about grassland utilization and distribution.

Key Features:
- Aggregation of grassland area data by cover type for specific catchment areas.
- Calculation of grassland area proportions based on different environmental and agricultural scenarios.
- Utilization of external data sources and APIs for up-to-date and accurate grassland data retrieval.
- Support for scenario-based analysis to aid in environmental impact studies and agricultural planning.

Classes:
- CatchmentGrass: Manages and processes grassland data for a given catchment area.

Dependencies:
- catchment_data_api.CatchmentDataAPI: For fetching catchment-specific grassland data.
- resource_manager.data_loader.Loader: For loading necessary proportion data.
- resource_manager.grassland_data_manager.DataManager: For additional data management and calculation needs.
- grassland_production.grassland_data_manager.DataManager: For additional data management and calculation needs.
- pandas: For data handling and processing.

Note:
This module is part of a larger suite of environmental analysis tools and should be used in conjunction with other related 
modules and datasets for comprehensive analysis.

"""
from catchment_data_api.catchment_data_api import CatchmentDataAPI
from grassland_production.resource_manager.data_loader import Loader
from grassland_production.resource_manager.grassland_data_manager import DataManager
import pandas as pd 

class CatchmentGrass:
    """
    A class to manage and process grassland data for a specified catchment.

    This class interfaces with various data sources to aggregate and calculate
    grassland area data relevant to a given catchment area. It leverages data
    from CatchmentDataAPI for catchment-specific grassland data, uses Loader 
    to retrieve grassland area proportions, and utilizes DataManager for 
    additional data management and calculations.

    Attributes:
        api (CatchmentDataAPI): An instance of CatchmentDataAPI to fetch catchment-specific grassland data.
        loader_class (Loader): An instance of Loader to load necessary proportion data.
        data_manager_class (DataManager): An instance of DataManager for data management and calculation.
        catchment (str): The name of the catchment area.
        calibration_year (int): The year for which calibration is done.
        default_grassland_year (int): Default year for grassland data, set from the DataManager instance.

    Args:
        catchment (str): The name of the catchment area.
        calibration_year (int): The year for which calibration is done.
        target_year (int): The target year for the analysis.
        scenario_data (pandas.DataFrame): DataFrame containing scenario data.
        scenario_animals_df (pandas.DataFrame): DataFrame containing animal data for the scenario.
        baseline_animals_df (pandas.DataFrame): DataFrame containing baseline animal data.

    Methods:
        get_catchment_grassland_areas(self):
            Retrieves and sums grassland areas by cover type for the catchment.
            Returns a DataFrame with area in hectares.

        get_catchment_grassland_area_calculated(self):
            Calculates grassland area based on catchment data and proportion data.
            Returns a DataFrame with calculated grassland areas.
    """
    def __init__(self, catchment,
                        calibration_year,
                        target_year,
                        scenario_animals_df,
                        baseline_animals_df):
        
        self.api = CatchmentDataAPI()
        self.loader_class = Loader()

        self.data_manager_class = DataManager(calibration_year,
                                    target_year,
                                    scenario_animals_df,
                                    baseline_animals_df)
        
        self.catchment = catchment
        self.calibration_year = calibration_year
        self.default_grassland_year = self.data_manager_class.default_grassland_year


    def get_catchment_grassland_areas(self):
        """
        Retrieves and processes grassland areas by cover type for a specified catchment.

        This method fetches grassland data for the catchment area defined in the class instance. 
        It transposes the data for better organization, groups it by cover type ('cover_type'), 
        and sums the areas. The resulting DataFrame has the total area for each grassland type 
        within the catchment, expressed in hectares.

        Returns:
            pandas.DataFrame: A DataFrame with cover types as the index and a single column 'area_ha' 
                            representing the total area in hectares for each cover type.
        """
        grassland_catchment_areas = self.api.get_catchment_grass_data_by_catchment_name(self.catchment)

        grouped_df = grassland_catchment_areas.T.groupby(level='cover_type').sum()

        # Rename the first (and only) column to 'area_ha'
        grouped_df.columns = ['area_ha']

        return grouped_df
    

    def get_catchment_grassland_area_caluclated(self):
        """
        Calculates the grassland area distribution for the catchment based on the calibration year.

        This method combines the grassland area data for the catchment with proportion data 
        (such as the percentages of different grassland types). It takes into account the 
        calibration year specified in the class. If the calibration year is not present in the 
        proportion data, it defaults to using a predefined grassland year.

        The calculated data includes the area in hectares for different grassland cover types, 
        adjusted according to the proportions for the selected year. It also includes data for 
        'Rough grazing in use', calculated separately.

        Returns:
            pandas.DataFrame: A DataFrame with each row representing a grassland cover type and 
                            its calculated area in hectares ('area_ha').
        """
        catchment_grassland_area = self.get_catchment_grassland_areas()
        grassland_proprotions = self.loader_class.cso_grassland_area_percent()

        data =[]

        mask = (catchment_grassland_area.index == "Pasture")
        for col in grassland_proprotions.columns:

            if self.calibration_year in grassland_proprotions.index:
                year = self.calibration_year
            else:
                print(
                        f"... calibration year not present, {self.default_grassland_year} default year used for catchment grass distribution"
                    )
                year = self.default_grassland_year

            row = {
                'cover_type': col,
                'area_ha': catchment_grassland_area.loc[mask, "area_ha"].item() * grassland_proprotions.loc[year,col].item()
            }

            data.append(row)

        rough_grazing_mask = (catchment_grassland_area.index == "Rough_grazing_in_use")

        row = {
            'cover_type': 'Rough grazing in use',
            'area_ha': catchment_grassland_area.loc[rough_grazing_mask,"area_ha"].item()
        }

        data.append(row)

        return pd.DataFrame(data)

        
