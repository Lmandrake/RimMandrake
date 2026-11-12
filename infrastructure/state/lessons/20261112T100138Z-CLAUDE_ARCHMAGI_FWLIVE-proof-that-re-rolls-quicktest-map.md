A proof that re-rolls a quicktest map for a biome must refuse when no roll lands on it: pit_exposure_live.py's run 12 fell through to a TemperateForest after 6 rolls and passed its 'desert noon' row silently. Write one UNMEASURED SITE row and exit instead. Quicktest desert hit rate measured 2026-11-12: 2 desert maps in 11 rolls across runs 11-13 (run 10: 1 in 2).
item: PIT_TEMPERATURE_SOFTENING_1
