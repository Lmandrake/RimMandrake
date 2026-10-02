# SUMP_FREE_TIER_MOVE_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §1 (Findings 1, 2) and §4 row 0. Owner, typed, turn 1: *"Move it all into the free mod that is now part of the Baroque Biomes mod"*.

1. Move from `mandrake.rut.patches` (UtinniPatches) into `src/RimMandrake/TheSump/` (Sump-specific) and `src/RimMandrake/EnvironmentalHazards/` (generic), both composed into `mandrake.rm.biomes` by `biomes_compose.py`: tar coating, `RUT_Tarred` → `RM_Tarred`, solvents and `RUT_Tarred_Surgery`, walkways (duckboards, glasswalk), gaslight lamp, the gas, tar vault, `RUT_TarRuinedGoods`, the tarred thoughts, both research projects. `RM_` names. The campaign keeps only the Sumpgas label (a relabel patch), the Holy Flame precept and the arrival letter.
2. Repoint `RM_TheSump`'s `RM_CarriedFilthHediffExtension` (today it names campaign-only `RUT_Tarred`: an unresolved reference on the free tier).
3. Re-gate `UtinniPatches/Patches/WildAnimals_Sump.xml`: its `<Operation MayRequire="mandrake.rsw.swbestiary">` is inert; gate on the `RSW_Hssiss` def through a Conditional.
4. ⚠ No new `modDependencies` (Helixien or other) in `TheSump/About.xml`: it would be unioned into all of Baroque Biomes. The gas is its own ThingDef already.
5. ⚠ Frozen world: every renamed def that a campaign save can hold (placed buildings, items, the hediff) needs a back-compat alias; read the 1.6 mechanism first (UNMEASURED which).
6. Mod Settings: each moved feature keeps its toggle in the Baroque Biomes settings screen.

## verify
- Free tier alone (no RimUtinni): a Sump quicktest map has tar coating, tarred pawns, acid cleaning, walkways, gaslight, vault and both research rows; `Player.log` carries no unresolved reference.
- With RimUtinni: the gas reads Sumpgas; a campaign save loads with no lost defs.
