"""FlowWorks composite review scenarios C1-C13 (design/RimMandrake/flowworks_composite_review_scenarios_2026-10-21.md).

Data modules only; the driver is northstar/scenarios_map.py, the selftest northstar/selftest_scenarios_map.py.
"""
from . import (c01_thirsty_terraces, c02_drowned_keep, c03_labyrinth_rescue, c04_wet_quarry, c05_fuel_depot,  # noqa: F401
               c06_tar_seep, c07_bathhouse_tower, c08_canal_lock, c09_trench_line, c10_rain_basin,
               c11_prospectors_creek, c12_oubliette_kennel, c13_spill_yard)

MODULES = [c01_thirsty_terraces, c02_drowned_keep, c03_labyrinth_rescue, c04_wet_quarry, c05_fuel_depot, c06_tar_seep,
           c07_bathhouse_tower, c08_canal_lock, c09_trench_line, c10_rain_basin, c11_prospectors_creek,
           c12_oubliette_kennel, c13_spill_yard]
ALL = [m.SCENARIO for m in MODULES]
BY_ID = {s["id"]: s for s in ALL}
