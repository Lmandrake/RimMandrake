# ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR (MOD, Pyrelands)

**Bar:** `pyre_plant_distribution_correct`: "every wild plant on a fresh Pyrelands map is ember grass, quick grass or
scorch-fruit; no other wild plant species grows there."

**Measured (2026-10-11 ratchet pilot, 22-mod tier, all 5 DLCs):** the gen census of the Pyrelands site found
`Plant_TreeAnima: 1` beside 33029 ember grass and 21580 quick grass. Evidence:
`Transient/bench_live_20261011/pilot_pyrelands_ns.log` line 6, `pilot_Pyrelands_20261012T061745Z.json`.

**Route:** Royalty's `GenStep_AnimaTrees` (`Data/Royalty/Defs/MapGeneration/BasePlayerMapGenerator.xml`, def
`AnimaTrees`, `treeDef Plant_TreeAnima`) runs on every player home map. It never goes through
`WildPlantSpawner.CalculatePlantsWhichCanGrowAt`, so the allowlist postfix in
`src/RimMandrake/Pyrelands/Source/WildPlantAllowlist.cs:98-121` cannot see it. Every DLC is assumed, so every
player colony founded in the Pyrelands gets this tree.

**Fix options (owner's call, design):** (a) skip/strip the anima genstep on an RM_Pyrelands map (a Harmony prefix
on `GenStep_AnimaTrees.Generate` gated on `wildPlantAllowlistEnabled`), or (b) rule the anima tree an allowed
DLC landmark and add it to the plant manifest (validation.py `PLANT_MANIFEST`, preflight `PLANTS`). Not a
harness or site artefact: a real player's start map takes the same genstep.

NEXT: ask the owner (a) strip or (b) allow, then build it, with its selftest.
