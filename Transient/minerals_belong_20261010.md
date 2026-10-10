# MINERALS_WHERE_THEY_BELONG_1 report (2026-10-10)

Built (offline, wave R1 validator half): src/RimMandrake/Utils/mineral_registry_check.py (+ --selftest).
Registry CSV: 53 rows, 24 RULED/BUILT emit-eligible, 0 hard defects, all biome columns resolve. Values PROVISIONAL (agent guesses).

Not built, and why:
- R1 emitter (RM_MineralRegistryDef XML): the CSV `defs` column is prose; emission needs an exact bindings column (item/producer defNames per row). Design says emit only RULED/BUILT rows with resolved bindings.
- R2-R5 (policy service, surface GenStep, deep prefix, quarry transpiler): C# in a new mod mandrake.rm.minerals, Windows build + live proof; owed.
- Per-biome numbers: Transient/mineral_numbers_review_2026-10-03.decisions.json has no approvals; build reads decision=approve rows only. Owner sheet owed.
- validation.py component: no Minerals mod exists to host it; UtinniPatches/validation.py is dirty with another helper's edit (avoided). The checker is the offline gate meanwhile.
- R6 durasteel/duranium/doonium: separate items PLASTEEL_DURASTEEL_MERGE_1 / CANON_MATERIALS_DESIGN_1 / DEEP_DRILL_HOME_BIOME_1.
