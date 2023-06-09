from geo_goblin.goblin_tool.data_engines import (
    get_scenario_output_datatable,
    save_grassland_output_datatable,
)

from geo_goblin.grassland_management_tool.models.grassland_models import Grassland


def main(imported_specifications):
    # from Classes import Grassland
    # data

    scenario_data_frame = get_scenario_output_datatable("scenarios")

    # Classes

    grassland_Class = Grassland(scenario_data_frame, imported_specifications)

    # DM requirement
    grassland_Class.dm_requirement()

    # Fertiliser calc
    grassland_Class.compute_fertilization_rate()

    # Organic fertiliser calc
    grassland_Class.get_nfs_within_system_grassland_distribution()

    # grassland_Class.interpolate_nfs_areas()

    grassland_Class.get_nfs_system_proportions()

    grassland_Class.compute_organic_fertilization_rate()

    # Yield estimations

    grassland_Class.get_yield()

    # Dry matter production

    grassland_Class.get_actual_dry_matter_produced()

    # Utilisation rate caluclation
    grassland_Class.get_utilisation_rate()

    # Calculate grassland area and spared area
    grassland_Class.get_grass_total_area()

    grassland_Class.get_non_grass_total_area()

    grassland_Class.compute_fertilization_total()

    grassland_Class.compute_farm_data_in_scenarios()

    # Export data

    save_grassland_output_datatable(
        grassland_Class.grass_total_area, "total_grassland_area"
    )

    save_grassland_output_datatable(grassland_Class.spared_area, "total_spared_area")


    save_grassland_output_datatable(grassland_Class.farm_data, "farm_data")

    print("")
    print("Grassland Tool Completed...")
    print("")
