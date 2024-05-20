"""
===========================
Geo Utilisation Rate Module
===========================
This module contains the GeoUtilisationRate class, which is focused on calculating and 
managing the utilisation rates of grassland for different farm types across various scenarios. 
This class is a crucial part of the grassland_production package, integrating components 
like grassland yield, fertilisation, and dry matter production for comprehensive analysis.

Classes:
    GeoUtilisationRate: Manages and computes utilisation rates of grassland.
"""
from grassland_production.geo_grassland_production.geo_grass_yield import GeoYield
from grassland_production.geo_grassland_production.geo_fertilisation import GeoFertilisation
from grassland_production.geo_grassland_production.geo_dry_matter import GeoDryMatter
from grassland_production.utilisation_rate import UtilisationRate

class GeoUtilisationRate:
    """
    A class to manage and compute the utilisation rates of grassland for different farm types and scenarios.

    The UtilisationRate class calculates the utilisation rate, defined as the ratio of dry matter required 
    by livestock to the dry matter produced on grasslands. It integrates data from various sources, including 
    grass yield, fertilisation, and livestock needs, to compute the utilisation rates for dairy, beef, 
    and sheep farms under various scenarios. This information is vital for sustainable grassland and livestock management.
    
    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.

    Attributes:
        utilisation_class (UtilisationRate): An instance of the UtilisationRate class.


    Methods:
        get_farm_type_dry_matter_produced(): Calculates dry matter produced by each farm type (uses NFS areas).
        get_farm_type_dry_matter_required(): Calculates dry matter required by each farm type (uses NFS areas).
        get_farm_based_utilisation_rate(): Computes utilisation rate based on farm type and scenario.
        get_dynamic_utilisation_rate(): Calculates dynamic utilisation rate considering scenario-specific parameters.
    """

    def __init__(
        self,
        ef_country,
        calibration_year,
        target_year,
        scenario_data,
        scenario_animals_df,
        baseline_animals_df,

    ):
        yield_class = GeoYield(ef_country,
                calibration_year,
                target_year,
                scenario_data,
                scenario_animals_df,
                baseline_animals_df)
       
        fertilisation_class = GeoFertilisation(ef_country,
                calibration_year,
                target_year,
                scenario_data,
                scenario_animals_df,
                baseline_animals_df)
        
        dry_matter_class = GeoDryMatter(ef_country,
                calibration_year,
                target_year,
                scenario_data,
                scenario_animals_df,
                baseline_animals_df,)
        
        self.utilisation_class = UtilisationRate(ef_country, 
                                                 calibration_year, 
                                                 target_year, 
                                                 scenario_data, 
                                                 scenario_animals_df, 
                                                 baseline_animals_df,
                                                 yield_class=yield_class,
                                                 fertilisation_class=fertilisation_class,
                                                 dry_matter_class=dry_matter_class
                                                 )
        



    def get_farm_type_dry_matter_produced(self):
        """
        Calculates and returns the dry matter produced by different farm types across various scenarios.

        This method utilizes the grass yield per hectare, obtained from the Yield class, combined with 
        area data from the National Farm Survey (NFS) to compute the total dry matter produced on dairy, 
        beef, and sheep farms. The calculations are performed for both the calibration year and the target year.

        The method iterates over each scenario and farm type, summing the product of yield per hectare and 
        the corresponding area for each type of grassland.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. Each DataFrame 
                has years as the index and farm types (dairy, beef, sheep) as columns. Each cell contains 
                the total dry matter produced for that farm type in the respective year.
        """
        return self.utilisation_class.get_farm_type_dry_matter_produced()


    def get_farm_type_dry_matter_required(self):
        """
        Calculates and returns the dry matter required by the National Farm Survey (NFS) average livestock population on each of 
        the three farm types (dairy, beef, sheep).

        This method determines the amount of dry matter required by dairy, beef, and sheep farms based on 
        the average livestock populations from NFS data. It involves converting the NFS data into dry matter 
        requirements from grass. The calculation is performed for both the calibration year and the target year across various scenarios.

        The method iterates through each scenario, farm type, and animal cohort, using the grass feed class 
        to calculate the dry matter required from grass for each animal type. This provides essential insights 
        into the feed requirements of different farm types.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. Each DataFrame has years 
                as the index and farm types (dairy, beef, sheep) as columns. Each cell contains the total dry matter 
                required for that farm type in the respective year.
        """
        return self.utilisation_class.get_farm_type_dry_matter_required()

    def get_farm_based_utilisation_rate(self):
        """
        Calculates and returns the utilisation rate of grassland for different farm types across various scenarios.

        This method computes the grassland utilisation rate, defined as the ratio of dry matter demand to dry matter 
        availability, for dairy, beef, and sheep farms. The calculations consider both the calibration year and the 
        target year, and they incorporate scenario-specific adjustments for dairy and beef Grass Use Efficiency (GUE) increases.

        This method incorporates NFS data related to dry matter demand and dry matter availability.

        The utilisation rate is calculated separately for each scenario and farm type. For years other than the target 
        year, it is the ratio of the dry matter demand in the calibration year to the dry matter availability in the 
        calibration year. For the target year, the utilisation rate includes additional adjustments based on the 
        scenario-specific GUE increases for dairy and beef farms.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. The DataFrame has years 
                as the index and farm types (dairy, beef, sheep) as columns. Each cell contains the utilisation 
                rate for that farm type in the respective year and scenario.
        """
        return self.utilisation_class.get_farm_based_utilisation_rate()


    def get_dynamic_utilisation_rate(self):
        """
        Calculates and returns a dynamic utilisation rate for each livestock system and scenario.

        This method computes the utilisation rate, which is the ratio of dry matter required to dry matter produced, 
        for dairy, beef, and sheep farms. For years prior to the target year, the utilisation rate is calculated by 
        aggregating the dry matter produced for each livestock system and grassland type, then dividing the dry matter 
        requirement by this aggregated amount. For the target year, the utilisation rate is determined by adding the 
        utilisation rate increase specified in the scenario parameters to the utilisation rate of the calibration year.

        The method considers various scenarios and adjusts the utilisation rates based on scenario-specific parameters 
        for dairy and beef Grass Use Efficiency (GUE) increases.

        Returns:
            dict: A dictionary where each key is a scenario, and its value is a DataFrame. The DataFrame has years 
                as the index and farm types (dairy, beef, sheep) as columns. Each cell contains the dynamic 
                utilisation rate for that farm type in the respective year and scenario.
        """
        return self.utilisation_class.get_dynamic_utilisation_rate()