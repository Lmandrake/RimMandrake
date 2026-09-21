# DESERT_LEACHMOSS_LIVE_VERIFY_1 — prove the leachmoss actually races on a live desert map

## what is wrong

`DESERT_LEACHMOSS_BUILD_1` shipped `RM_Leachmoss` (ThingDef, wildPlants wiring
at weight 1.5 in `RUT_Desert`, and a settings toggle) entirely offline —
`validate_patch.py`, a raw `ET.parse`, and the repo's `run_selftests.py` all
pass clean, but none of that proves the spawn-competition actually reads the
way the design intends on a real map. The build pass had no bridge/game
available (another agent held it) and could not run design
§5 step 7 itself.

## why it matters

The whole point of `RM_Leachmoss` is a numeric bet — `fertilityMin 0.5`,
weight 1.5 (highest in the list), `plantRespawningCommonalityFactor 2.0` —
that it visibly dominates Gravel/Soil patch ground and never spreads onto
Sand. That bet is unproven until someone looks at a map.

## the work — a quicktest desert map, minimal list + all five DLC

Design's own verify step, `design/Jawa/worldbuilding/desert_shade_plants_design.md`
§5 step 7:

1. Spawn/generate a fresh `RUT_Desert` map (or advance an existing one) with
   `mandrake.rm.environmentalhazards` and `RUT_Desert`'s owning mod active.
2. **PROVE** moss is present on Gravel/Soil pockets and absent from Sand —
   walk the map, or `jawa/list_things`/an equivalent census filtered to
   `RM_Leachmoss`, cross-checked against the terrain grid.
3. **PROVE** re-take: cut (or otherwise clear) a stand of moss on fertile
   ground, let the map tick forward past `wildPlantRegrowDays`/normal spawn
   cadence, and confirm the regrowth on that ground is moss more often than
   not (design's own bar — "more often than not", not "always").
4. **PROVE** `RSW_Ultracactus` is still present and still confined to Sand —
   the moss must not have crowded it off the ground it actually owns.
5. **LIES**: a quicktest map generated before the art render lands will show
   `RM_Leachmoss` with no texture (magenta or a placeholder) — that is an art
   gap, not a mechanism failure, and must not be read as one. A map whose
   `plantDensity` or mod list was hand-edited away from the shipped
   `RUT_Desert`/minimal-list defaults is not evidence either way.
6. Tune the commonality weight (currently 1.5, per the design's own
   `⚠️ UNMEASURED` note) if what you see does not read as the patch ground's
   dominant cover at `plantDensity 0.05` — record what you saw and what you
   changed, do not silently leave a wrong number standing.

## verify

The four PROVEs above, each with what was actually seen (not "no error").

## criteria

Design §5 step 7 confirmed on a live map, or the commonality weight retuned
and re-confirmed. Close `DESERT_LEACHMOSS_BUILD_1`'s remaining live-proof debt
— this item, not that one, is what closes it.
