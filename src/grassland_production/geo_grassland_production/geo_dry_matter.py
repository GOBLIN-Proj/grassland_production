"""
===================
Dry Matter Module
===================

This module contains the GeoDryMatter class, which is responsible for calculating dry matter requirements 
and production in various agricultural scenarios, focusing on livestock systems. It integrates data 
from multiple sources and uses lifecycle assessment methods from the cattle and sheep lca modules.

Classes:
    GeoDryMatter: Manages the calculation of dry matter requirements and production for livestock systems.
"""
from grassland_production.dry_matter import DryMatter
from grassland_production.geo_grassland_production.geo_grass_yield import GeoYield
from grassland_production.fertilisation import Fertilisation

class GeoDryMatter:
    """
    The GeoDryMatter class calculates the dry matter requirements and production for different livestock systems.
    It utilizes various classes and modules to integrate data from the National Farm Survey, CSO, and other sources,
    and applies lifecycle assessment methods from the cattle and sheep lca modules to evaluate agricultural scenarios.

    Args:
        ef_country (str): The country for which the analysis is performed.
        calibration_year (int): The calibration year.
        target_year (int): The target year for future scenario projections.
        scenario_inputs_df (DataFrame): DataFrame containing scenario input variables data.
        scenario_animals_df (DataFrame): DataFrame containing scenario animal data.
        baseline_animals_df (DataFrame): DataFrame containing baseline animal data.


    Attributes:
        dm_class (DryMatter): An instance of the DryMatter class for managing dry matter calculations.
        yield_class (Yield): An instance of the Yield class for managing yield calculations.
        fertiliser_class (Fertilisation): An instance of the Fertilisation class for managing fertilisation calculations.

    Methods:
        get_actual_dry_matter_produced():
            Calculates the actual dry matter produced in each livestock system.

        actual_dry_matter_required_past():
            Calculates the dry matter requirement for past livestock systems.

        actual_dry_matter_required_future():
            Calculates the dry matter requirement for future livestock systems based on scenarios.

        actual_dry_matter_required():
            Integrates past and future dry matter requirements for livestock systems.

        get_actual_dm_weights():
            Calculates the proportion of dry matter required for each livestock system.

        get_dm_proportional_reduction():
            Determines the proportional reduction in dry matter requirement for each system.

        weighted_dm_reduction_contribution():
            Calculates the weighted contribution of each livestock system to the total dry matter reduction.

        get_total_concentrate_feed_past():
            Computes the total amount of concentrate feed required by livestock in the past.

        get_total_concentrate_feed_future():
            Computes the total amount of concentrate feed required by livestock in the future based on scenarios.

        get_total_concentrate_feed():
            Integrates past and future concentrate feed requirements for livestock systems.
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

        yield_class = GeoYield(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )

        fertiliser_class = Fertilisation(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
        )

        self.dm_class = DryMatter(
            ef_country,
            calibration_year,
            target_year,
            scenario_data,
            scenario_animals_df,
            baseline_animals_df,
            yield_class=yield_class,
            fertiliser_class=fertiliser_class,
        )




    def get_actual_dry_matter_produced(self):
        """
        Calculates the actual dry matter produced in each livestock system. This calculation is based on the yield per 
        hectare of grassland specific to each system, taking into account the type of grassland and the fertilization 
        practices used. The method integrates data from various sources to estimate dry matter production for different 
        farm types and scenarios.

        The method uses historical data for grassland areas and fertilization practices, and it interpolates for years 
        earlier than 2005, acknowledging that these interpolations may not be very accurate. However, data for years 
        prior to 2005 is generally not critical for the analysis.

        Returns:
            dict: A dictionary structured by scenario, then by farm type (dairy, beef, sheep), containing pandas 
                DataFrames. Each DataFrame represents the dry matter produced, indexed by grassland type and 
                segmented by year (calibration year and target year). A 'total' column is added to summarize 
                the dry matter produced across all grassland types.

        Notes:
            - If data for the calibration year is not present, a default year is used as a fallback.
            - The method assumes that the required data is available through the loader_class and yield_class 
            attributes, which are instances of the Loader and Yield classes, respectively.
        """
        return self.dm_class.get_actual_dry_matter_produced()

    


    def actual_dry_matter_required_past(self):
        """
        Calculates the dry matter requirement for each livestock system (dairy, beef, and sheep) for the calibration year. 
        The calculation is based on the livestock data available for the calibration year, using the lifecycle assessment 
        method 'dry_matter_from_grass' to estimate the dry matter required by each animal cohort.

        The method processes data for dairy, beef, and sheep livestock systems, summing up the dry matter requirements 
        for each type of livestock based on their population and specific dry matter intake rates.

        Returns:
            DataFrame: A pandas DataFrame indexed by the calibration year, with columns for dairy, beef, sheep, 
                    and a total column summing these values. Each cell in the DataFrame represents the total 
                    dry matter required in tonnes per year for that livestock type.

        Notes:
            - The method assumes that baseline animal data for the calibration year is available and structured 
            appropriately for the calculation.
            - The dry matter requirement is calculated per animal and then scaled to the total population of that 
            animal type.
            - The method differentiates between different types of animal management systems (e.g., tank liquid 
            vs. solid manure management) and different grazing types for sheep.
        """
        return self.dm_class.actual_dry_matter_required_past()
    

    def actual_dry_matter_required_future(self):
        """
        Calculates the future dry matter requirements for each livestock system (dairy, beef, and sheep) for 
        each scenario in the target year. This method considers various future scenarios based on different 
        animal population, management practices and farm types.

        The calculation is based on the data for each scenario's livestock, using the lifecycle assessment 
        method 'dry_matter_from_grass' to estimate the dry matter required by each animal type. The method 
        processes data for dairy, beef, and sheep livestock systems, summing up the dry matter requirements 
        for each type of livestock based on their population and specific dry matter intake rates.

        Returns:
            dict: A dictionary with scenario keys, each containing a pandas DataFrame indexed by the target 
                year. The DataFrame has columns for dairy, beef, sheep, and a total column summing these 
                values. Each cell represents the total dry matter required in tonnes per year for that 
                livestock type under each scenario.

        Notes:
            - The method assumes that scenario-specific animal data is available and structured appropriately 
            for the calculation.
            - The dry matter requirement is calculated per animal and then scaled to the total population of 
            that animal type in the scenario.
            - Different scenarios may represent varying farm management practices, livestock types, and animal 
            populations, reflecting possible future states of the livestock systems.
        """
        return self.dm_class.actual_dry_matter_required_future()
    

    def actual_dry_matter_required(self):
        """
        Integrates and calculates the total dry matter requirements for livestock systems, combining both past (historic) 
        and future scenarios. This method utilizes lifecycle assessment methods from cattle and sheep modules to determine the dry matter 
        requirements from grass for each livestock cohort, across various scenarios and timeframes.

        The method first computes the dry matter requirements for the calibration year (representing the past) 
        and then for the target year (representing future scenarios). It then integrates these requirements 
        into a comprehensive view, providing a complete picture of dry matter needs across different time periods 
        and scenarios.

        Returns:
            dict: A dictionary with scenario keys, each containing a pandas DataFrame that includes the dry matter 
                requirements for both the calibration year and the target year. Each DataFrame is indexed by year 
                and has columns for dairy, beef, sheep, and a total column summing these values.

        Notes:
            - The method relies on two key internal methods: 'actual_dry_matter_required_past' for calculating past 
            requirements and 'actual_dry_matter_required_future' for future scenario-based requirements.
            - This approach provides am integration of historical and projected data, facilitating analysis 
            and comparison across different time periods and scenarios.
        """
        return self.dm_class.actual_dry_matter_required()
    

    def get_actual_dm_weights(self):
        """
        Calculates the proportional weights of dry matter requirements for each livestock cohort (dairy, beef, sheep) 
        relative to the total dry matter requirements across different scenarios. This method helps in understanding 
        the contribution of each livestock type to the overall dry matter requirements in each scenario.

        The method first retrieves the total dry matter requirements for each scenario using the 
        'actual_dry_matter_required' method. It then computes the weight (as a proportion) of each cohort's 
        requirement relative to the total requirement for that scenario.

        Returns:
            dict: A dictionary with scenario keys, each containing a nested dictionary. The nested dictionary 
                maps each livestock cohort (dairy, beef, sheep) to its proportional weight of the total dry 
                matter requirement. The 'total' column is excluded from this calculation.

        Notes:
            - This method provides a percentage-like view of how much each livestock type contributes to the 
            total dry matter requirements within each scenario.
            - These weights can be used for analyses that require understanding the distribution of dry matter 
            needs among different livestock types under various future scenarios.
        """
        return self.dm_class.get_actual_dm_weights()


    def get_dm_proportional_reduction(self):
        """
        Calculates the proportional reduction in dry matter requirements for each livestock cohort (dairy, beef, sheep)
        from the calibration year to the target year under various scenarios. This method assesses the impact of 
        different future scenarios on the dry matter requirements compared to past requirements.

        The method computes the dry matter requirements for both past (calibration year) and future (target year) 
        scenarios. It then determines the proportional reduction in dry matter requirements for each cohort in each 
        scenario by comparing the future requirements with the past.

        Returns:
            dict: A dictionary with scenario keys, each containing a nested dictionary. The nested dictionary maps 
                each livestock cohort to its proportional reduction in dry matter requirement relative to the past. 
                A 'total' entry is also included, representing the sum of the proportional reductions for all cohorts.

        Notes:
            - The proportional reduction is calculated as 1 minus the ratio of future to past dry matter requirements.
            - If the calculated proportion is negative (indicating an increase rather than a decrease), it is set to 0 
            to reflect no reduction.
        """
        return self.dm_class.get_dm_proportional_reduction()


    def weighted_dm_reduction_contribution(self):
        """
        Calculates the weighted contribution of each livestock cohort (dairy, beef, sheep) to the total proportional 
        reduction in dry matter requirements across different scenarios. This method evaluates how each cohort 
        contributes to the overall reduction in dry matter needs when transitioning from the calibration year to 
        the target year under various scenarios.

        The method first determines the proportional reduction in dry matter requirements for each cohort in each 
        scenario using the 'get_dm_proportional_reduction' method. It then computes the weighted contribution of 
        each cohort's reduction relative to the total reduction in that scenario.

        Returns:
            dict: A dictionary with scenario keys, each containing a nested dictionary. The nested dictionary maps 
                each livestock cohort to its weighted contribution to the total proportional reduction. The 'total' 
                entry is not included in the calculation of weights.

        Notes:
            - The weighted contribution is calculated as the proportion of each cohort's reduction relative to the 
            total reduction in that scenario.
            - This method provides insight into which livestock cohort is contributing the most to the reduction in 
            dry matter requirements in each scenario, allowing for targeted analysis and planning.
        """
        return self.dm_class.weighted_dm_reduction_contribution()


    def get_total_concentrate_feed_past(self):
        """
        Calculates the total amount of concentrate feed required by all livestock within each farm system (dairy, beef, sheep) 
        in tonnes for the calibration year. This method estimates the concentrate feed needs based on the population and 
        specific feed requirements of different types of livestock in the calibration year.

        The calculation involves determining the amount of concentrate feed each animal requires and then aggregating these 
        amounts across all animals within each livestock cohort.

        Returns:
            DataFrame: A pandas DataFrame indexed by the calibration year, with columns for dairy, beef, sheep, 
                    and a total column summing these values. Each cell in the DataFrame represents the total 
                    concentrate feed required in tonnes per year for that livestock type.

        Notes:
            - The concentrate feed requirement is calculated per animal and then scaled to the total population of that 
            animal type.
            - The method differentiates between different types of animal management systems (e.g., tank liquid vs. 
            solid manure management) and different grazing types for sheep.
        """
        return self.dm_class.get_total_concentrate_feed_past()


    def get_total_concentrate_feed_future(self):
        """
        Calculates the total amount of concentrate feed required by all livestock within each farm system 
        (dairy, beef, sheep) in tonnes for the target year under various scenarios. This method provides 
        an estimation of future concentrate feed needs based on projected changes in livestock populations 
        and management practices across different scenarios.

        The calculation involves determining the amount of concentrate feed each animal requires in each 
        scenario and then aggregating these amounts across all animals within each livestock cohort.

        Returns:
            dict: A dictionary with scenario keys, each containing a pandas DataFrame indexed by the target year, 
                with columns for dairy, beef, sheep, and a total column summing these values. Each cell represents 
                the total concentrate feed required in tonnes per year for that livestock type under each scenario.

        Notes:
            - The concentrate feed requirement is calculated per animal and then scaled to the total population of 
            that animal type in each scenario.
            - The method accounts for different livestock management systems and grazing types for each animal 
            cohort, reflecting the varied nature of future livestock farming scenarios.
        """
        return self.dm_class.get_total_concentrate_feed_future()

    def get_total_concentrate_feed(self):
        """
        Integrates and calculates the total concentrate feed requirements for livestock systems, combining both past 
        (calibration year) and future (target year under various scenarios) data. This method provides a comprehensive 
        view of the concentrate feed needs for different livestock cohorts across time and scenarios.

        The method first calculates the concentrate feed requirements for the past (calibration year) and then for the 
        future (target year) under various scenarios. It then integrates these requirements, offering a complete 
        picture of concentrate feed needs across different time periods and scenarios.

        Returns:
            dict: A dictionary with scenario keys, each containing a pandas DataFrame that includes the concentrate 
                feed requirements for both the calibration year and the target year. Each DataFrame is indexed by 
                year and has columns for dairy, beef, sheep, and a total column summing these values.

        Notes:
            - The method relies on two key internal methods: 'get_total_concentrate_feed_past' for calculating past 
            requirements and 'get_total_concentrate_feed_future' for future scenario-based requirements.
        """
        return self.dm_class.get_total_concentrate_feed()