"""
=========================
ScenarioDataFetcher Module
=========================
This module contains the ScenarioDataFetcher class, which is responsible for fetching and manipulating scenario data from a pandas DataFrame.

"""

import pandas as pd

class ScenarioDataFetcher:
    """
    A class for fetching and manipulating scenario data from a pandas DataFrame.

    Attributes:
        scenario_data (pd.DataFrame): A pandas DataFrame containing scenario data.

    Methods:
        get_scenario_dataframe(): Returns the entire scenario data DataFrame.
        get_catchment_name(): Returns the unique catchment name from the scenario data.
        get_scenario_list(): Returns a list of unique scenarios present in the scenario data.
        get_scenarios_col(): Returns the 'Scenarios' column from the scenario data.
        get_cattle_system_col(): Returns the 'Cattle systems' column from the scenario data.
        get_manure_system_col(): Returns the 'Manure management' column from the scenario data.
        get_dairy_fertilisation_value(mask): Returns the 'Dairy Pasture fertilisation' value based on the provided mask.
        get_beef_fertilisation_value(mask): Returns the 'Beef Pasture fertilisation' value based on the provided mask.
        get_clover_proportion_value(mask): Returns the 'Clover proportion' value based on the provided mask.
        get_clover_fertilisation_value(mask): Returns the 'Clover fertilisation' value based on the provided mask.
    """

    def __init__(self, scenario_data):
        """
        Constructs all the necessary attributes for the ScenarioDataFetcher object.

        Parameters:
            scenario_data (pd.DataFrame): The scenario data as a pandas DataFrame.
        """
        self.scenario_data = scenario_data


    def get_scenario_dataframe(self):
        """
        Returns the entire scenario data DataFrame.

        Returns:
            pd.DataFrame: The scenario data.
        """
        return self.scenario_data
    

    def get_catchment_name(self):
        """
        Returns the unique catchment name from the scenario data.

        Returns:
            str: The unique catchment name.
        """
        return self.scenario_data["Catchment"].unique().item()
    

    def get_scenario_list(self):
        """
        Returns a list of unique scenarios present in the scenario data.

        Returns:
            List[str]: A list of unique scenario names.
        """
        return self.scenario_data["Scenarios"].unique().tolist()
    

    def get_scenarios_col(self):
        """
        Returns the 'Scenarios' column from the scenario data.

        Returns:
            pd.Series: The 'Scenarios' column.
        """
        return self.scenario_data["Scenarios"] 
    

    def get_cattle_system_col(self):
        """
        Returns the 'Cattle systems' column from the scenario data.

        Returns:
            pd.Series: The 'Cattle systems' column.
        """
        return self.scenario_data["Cattle systems"]
    

    def get_manure_system_col(self):
        """
        Returns the 'Manure management' column from the scenario data.

        Returns:
            pd.Series: The 'Manure management' column.
        """
        return self.scenario_data["Manure management"]
    
    def get_dairy_fertilisation_value(self, mask):
        """
        Returns the 'Dairy Pasture fertilisation' value based on the provided mask.

        Parameters:
            mask (pd.Series): A boolean Series to filter the DataFrame.

        Returns:
            float: The 'Dairy Pasture fertilisation' value.
        """
        return self.scenario_data.loc[mask, "Dairy Pasture fertilisation"].item()

    def get_beef_fertilisation_value(self, mask):
        """
        Returns the 'Beef Pasture fertilisation' value based on the provided mask.

        Parameters:
            mask (pd.Series): A boolean Series to filter the DataFrame.

        Returns:
            float: The 'Beef Pasture fertilisation' value.
        """
        return self.scenario_data.loc[mask, "Beef Pasture fertilisation"].item()
    
    def get_clover_proportion_value(self, mask):
        """
        Returns the 'Clover proportion' value based on the provided mask.

        Parameters:
            mask (pd.Series): A boolean Series to filter the DataFrame.

        Returns:
            float: The 'Clover proportion' value.
        """
        return self.scenario_data.loc[mask, "Clover proportion"].item()
    
    def get_clover_fertilisation_value(self, mask):
        """
        Returns the 'Clover fertilisation' value based on the provided mask.

        Parameters:
            mask (pd.Series): A boolean Series to filter the DataFrame.

        Returns:
            float: The 'Clover fertilisation' value.
        """
        return self.scenario_data.loc[mask, "Clover fertilisation"].item()