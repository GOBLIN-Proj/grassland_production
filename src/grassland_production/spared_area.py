import pandas as pd
import copy
from grassland_production.data_loader import Loader
from grassland_production.grassland_data_manager import DataManager
from grassland_production.grass_yield import Yield
from grassland_production.dry_matter import DryMatter
from grassland_production.grassland_area import Areas

    
class Grasslands:

    def __init__(self, ef_country, calibration_year, scenario_data, scenario_animals_df,basline_animals_df):

        self.data_manager_class = DataManager(calibration_year, scenario_data, scenario_animals_df,basline_animals_df)
        self.calibration_year = self.data_manager_class.calibration_year
        self.target_year = self.data_manager_class.target_year
        self.default_calibration_year = self.data_manager_class.default_calibration_year
        self.loader_class = Loader()
        self.yield_class = Yield(ef_country, calibration_year, scenario_data, scenario_animals_df,basline_animals_df)
        self.areas_class = Areas(self.target_year, self.calibration_year, self.default_calibration_year)
        self.dm_class = DryMatter(ef_country, self.calibration_year, scenario_data, scenario_animals_df, basline_animals_df)
        
    
    def get_grass_total_area(self):

        """
        for years 2005 to 2015, for each scenario, for each system, the yearly grassland yield is calculated.

        A single weighted number is produced based on the yield of each grassland type for each system. The weights used
        are the proportions of each grassland type in each system.

        The total area then is calculated as the dry matter requirment for each system divided by the weighted yield for each
        system divided by that systems utilisation rate.

        The ouputs are then aggregated into a single dataframe.

        """

        # grass drymatter requirement for cattle and sheep, is dictionary
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        keys = self.data_manager_class.systems

        transposed_yield_per_ha = self.yield_class.get_yield()
        dry_matter_req = self.dm_class.actual_dry_matter_required()
        utilisation_rate = self.dm_class.get_utilisation_rate()


        nfs_within_grassland_proportions = self.areas_class.get_nfs_within_system_grassland_distribution()

        grass_total_area = pd.DataFrame(0, index=year_list, columns=scenario_list)

        average_yield = 0

        for sc in scenario_list:

            for sys in keys:

                for year in year_list:

                    for grassland_type in transposed_yield_per_ha[sc][sys].columns:

                        if year != self.target_year:
                                average_yield += (
                                    transposed_yield_per_ha[sc][sys].loc[
                                        year, grassland_type
                                    ]
                                    * nfs_within_grassland_proportions[sys].loc[
                                        year, grassland_type
                                    ]
                                )
                        else:
                            average_yield += (
                                    transposed_yield_per_ha[sc][sys].loc[
                                        self.target_year,
                                        grassland_type,
                                    ]
                                    * nfs_within_grassland_proportions[sys].loc[
                                            self.calibration_year,
                                        grassland_type,
                                    ]
                                )

                    grass_total_area.loc[year, sc] += (
                        dry_matter_req[sc][sys].loc[year]
                        / average_yield
                        / utilisation_rate[sc][sys].loc[year]
                    )

                    average_yield = 0
    
        return grass_total_area
    

    def get_non_grass_total_area(self):

        """
        A single dataframe is produced with spared area. If the row does not equal the target year,
        then the value is assumed as zero. If the row is the target year, the output value is equal to the
        self.imported_specifications.calibration_year value for total grassland area minus the self.imported_specifications.target_year value for total grassland area

        """
        year_list = [self.calibration_year, self.target_year]
        scenario_list = self.data_manager_class.scenario_inputs_df.Scenarios.unique()

        spared_area = pd.DataFrame(0, index=year_list, columns=scenario_list)

        grass_total_area = self.get_grass_total_area()
            
                
        for sc in scenario_list:
            spared_area.loc[self.target_year, sc] = (
                grass_total_area.loc[
                    self.calibration_year, sc
                ]
                - grass_total_area.loc[
                    self.target_year, sc
                ]
            )

        return spared_area