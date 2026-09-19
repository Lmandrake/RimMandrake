# WORLD_MUTATOR_LANDMARK_IMPORTERS_1 — the two bundles that cannot be carried by a file

Measured 2026-08-26 while costing the Ash'karr ideology rebuild
(`ASHKARR_IDEOLOGY_MODE_CALL_1`).

Four planet bundles import from a path in one call — `jawa/world_tile_import`,
`world_links_import`, `world_settlements_import`, `world_features_import`. **Two do not:**

* **mutators** — `jawa/world_mutators_set` takes `tiles` + `mutators` per batch. **13,569 tiles**
  carry mutators on Ash'karr.
* **landmarks** — `jawa/world_landmarks_set` takes `def` + `tiles` per batch. **579** placed.

Both are replayable by re-running the authoring scripts against the CSV bundles — that is how they
were placed. ⚠️ **But a replay is not a restore.** A landmark's own `mutatorChances` rolls when it is
placed; the 2026-08-26 pass measured those rolls dropping `MixedBiome`, `AnimalLife_Decreased`,
`Stockpile`, `AnimalHabitat` and `WildPlants` onto tiles nobody chose. Roll again and the incidental
texture differs.

## What to build, IF the rebuild is chosen

`jawa/world_mutators_import` and `jawa/world_landmarks_import`, matching the four that exist:
`path` · `apply` (dry run by default) · `clearExisting` · `expectTiles`. Read the same CSV shape the
exporters already write (`world/_final/live_mutators.csv`, `live_landmarks.csv`).

🔑 **The landmark importer must place with `mutatorChances` SUPPRESSED, or it is not an importer** —
it would author new mutators while claiming to restore old ones. If the engine gives no way to
suppress the roll, the importer must place the landmark and then diff-and-repair the tile's mutator
list against the CSV, and **say in its result which mutators it had to remove.** Silence there would
make it exactly the class of tool this project keeps catching.

⛔ **Do not build this speculatively.** It is only worth writing if the owner chooses the rebuild in
`ASHKARR_IDEOLOGY_MODE_CALL_1`. Filed so the cost is visible when he decides, not so someone starts.
