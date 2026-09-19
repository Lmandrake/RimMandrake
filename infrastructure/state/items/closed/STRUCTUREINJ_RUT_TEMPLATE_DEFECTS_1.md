# STRUCTUREINJ_RUT_TEMPLATE_DEFECTS_1 — two baked-plan defects found by review (2026-09-06)

Full-file review of `src/RimUtinni/StructureInjectionsRUT/` (DIRTY_CODE_REVIEW_STANDING_LOOP_1). The undeclared DesertFixtures dependency was fixed in About.xml the same day; these two need the rimplace compiler, not a hand edit (Templates/*.txt are generated).

## spec

1. **`Templates/toll_gap.txt:39` — `THING DiningChair … rot=4`.** Rot4 is 0-3; 4 is invalid (the engine wraps or errors at SpawnSetup). Root cause is in `design/Jawa/templates/toll_gap.lua` (a rotation drawn 1-4 or an off-by-one); fix the Lua, recompile with the rimplace CLI, confirm the baked line reads rot 0-3, and grep every other baked template for `rot=4` (`grep -rn "rot=4" src/*/StructureInjections*/Templates/`) — one template wrong suggests a shared helper.
2. **`Templates/glass_sea.txt` (597 lines) is referenced by no GenStepDef/TileMutatorDef** in this mod — dead content. Either wire it (a `TileMutatorDef` like the Batch5/6 ones, for the biome it was written for) or delete the baked file and note the Lua stays.

## verify

```
PROVE   rimplace render of toll_gap after the fix shows every rot in 0-3; grep finds no rot=4 in any baked template; glass_sea either has a def citing it or no longer exists
EXPECT  0 hits for rot=4; the toll gap quicktest-builds with the chair facing a table (screenshot)
LIES    rimplace `verify` sharing the default rect reports 0/0 on a refused template (P5 finding) — check the guard passed
```
