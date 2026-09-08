# Meander pass v12 — STOPPED BEFORE MUTATION: the ruling is already satisfied (2026-09-07)

Owner's ruling "only ancient asphalt should be straight; meander the rest" is ALREADY TRUE
on WORLDMAP_V11. Live non-ancient network (1,134 edges, 159 runs): longest straight leg 3,
mean 1.45, sinuosity mean 1.323. Ancient asphalt (253 edges, all AncientAsphaltHighway):
straight legs to 9, sinuosity ~1.0. A fresh route.py pass (rerouted_v12.json / roads_import.csv,
NEVER APPLIED) would have RAISED the longest non-ancient straight chain 3→9 and deleted 121
edges — the ruling run backwards. Planet untouched: no clear, no import, no commit.

Handoff line "the owner's meander ruling is unapplied" was STALE — the meandered net survived
the save-rebase because the savegame was the carrier of the roads all along.

Live clean checks recorded here: 0 non-ancient edges past −10 °C (coldest road tile −9.9);
0 endpoints on allowRoads=false or water; river entries 652 before and after (nothing written);
hiddenByBiome 15 tiles, pre-existing. ⚠️ 652 river entries vs 634 measured at V3 (+9 edges,
unexplained) — measure again before any future river import.

Candidate artifacts kept for provenance only; loader for the CURRENT lineage is load12.py
(rcommon.load() reads the deprecated one).
