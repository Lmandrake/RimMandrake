## spec
No design doc — this is an engine/tooling investigation, not a content build.
Discovered as a side effect of `FISH_BESTIARY_BUILD_1`'s live verification
pass (2026-09-18): every attempt to generate a fresh map at a world tile that
carries a river or a lake-type `TileMutatorDef` produced a map with **zero**
water-family terrain anywhere on it, across every biome tried.

## what was measured
Method: `jawa/colony_found` (Player faction, some runs) or bare
`jawa/world_tile_map_generate` (other runs, no difference observed) at a
tile confirmed via `jawa/world_tile_get` to carry `riverCount > 0` or a
lake-type mutator (`ToxicLake` etc, via `jawa/world_mutators_get`), then a
full-map `jawa/get_terrain_batch` scan (13 row-bands of `0,z,325,25`,
`cellsRead` summing to the exact `sizeX*sizeZ`, so no gap in coverage) for
any terrain name containing "water".

| tile | biome | riverCount / mutator | water cells found |
|---|---|---|---|
| 8501 | RUT_Greentide | riverCount 2 | 0 (of 105625 cells) |
| 2020 | RUT_Greentide | riverCount 2 | 0 (of 105625 cells) |
| 11183 | RUT_Wasteland | riverCount 0 (bad pick) | 0 — expected |
| 224 | RUT_Wasteland | `ToxicLake` mutator | 0 (of 105625) — no
  `RUT_BrineDeposit_*` scattered either, `jawa/list_things` 0 of 9992 scanned |
| 1535 | RM_FE_Pyrelands (non-Ash'karr, non-`RUT_` control) | riverCount 4 | 0 |
| 1214 | RUT_RustCathedral (fishing wiring already independently confirmed
  correct — `FISH_BESTIARY_BUILD_1` wave 5) | riverCount 2 | 0 |

Six tiles, five different biomes, one deliberately non-`RUT_` control
(`RM_FE_Pyrelands`) to rule out "something about our own biomes" — all six
came back with **zero** water terrain. `RUT_RustCathedral` is the load-bearing
result: its fishing mechanism was already read and confirmed correct in the
XML, so a live map for it SHOULD show a river; it did not.

**Positive control, same session, same tools:** `RUT_TheScald` (a whole-tile
"isWaterBiome" ocean-type biome, not a land biome with an embedded river)
DID correctly show real water terrain (`RUT_ScaldWaterOceanDeep`, sampled at
8 points across its whole map plus confirmed via `rimworld/apply_architect_
designator`'s own placement-rejection check). This proves `get_terrain_batch`
and `get_cell_info` DO correctly report water terrain when the game has
actually placed it — the six zero-water results above are not a read-side
blind spot.

**Historical positive control (different session, `references/traps.md`
"A `world_tile_map_generate`'d map can render as a blank void"):** on
2026-09-13, the SAME tool (`world_tile_map_generate`) on `ZBiome_Grasslands`
with `riverCount: 2` DID produce real `WaterMovingShallow` cells via
`get_terrain_batch`. So this tool has worked for a river tile before —
something changed between then and now, or something is specific to
tonight's session/mod state.

## what this blocks
`FISH_BESTIARY_BUILD_1`'s live-verification pass could not conclude PASS or
FAIL for Wasteland (mining), Cracked Lands, Weeping Stones or Greentide
(fishing) this session — not because their own XML wiring is wrong (three of
the four were already re-confirmed correctly wired onto their live BiomeDefs
in prior waves), but because no shallow/deep water of ANY kind materializes
on a freshly generated map to test against. The Wasteland brine-deposit
GenStep scatter is confirmed a casualty of the same root cause (scatters onto
a terrain TAG that only exists on the brine terrain family, which never
generates).

## open questions, not decided here
- Is this a `world_tile_map_generate` bridge-tool regression (e.g. it now
  takes a code path that skips `GenStep_River`/lake gensteps), or a genuine
  MapGenerator/mod-conflict regression that would ALSO hit a real player
  landing via the normal Configure-Landing-Site flow? The former is a
  companion-DLL bug (`rimbridge-companion` skill); the latter would be far
  more serious and worth the owner's attention immediately.
- Candidate recent-change suspects, NOT investigated: `EnvironmentalHazards`
  mod activated today per `infrastructure/state/modlists/
  ModsConfig_before_envhazards_activate_2026-09-18.xml`; the "rot wave"
  restart/deactivate cycle mentioned in recent commits
  (`748f6c36b`, `d0e9773c6`); `gizkastowaway`'s deactivation.
- Whether `jawa/colony_found` before `world_tile_map_generate` matters at
  all — tested both orders, no difference observed, but not exhaustively.

## verify
- **PROVE**: generate a fresh map at a tile with `riverCount > 0` on a land
  biome (any biome, does not need to be Ash'karr) and scan the full map with
  `jawa/get_terrain_batch`.
- **EXPECT**: at least some `Water*`-family terrain cells, matching the
  2026-09-13 `ZBiome_Grasslands` precedent.
- **LIES**: a screenshot alone would not settle this — `references/traps.md`
  already documents a `world_tile_map_generate`+`Change Map` map that shows a
  correct-data-but-blank-mesh screenshot; use the DATA read
  (`get_terrain_batch`/`get_cell_info`), not a screenshot, as the check.
- **THRESHOLD**: one land-biome tile that DOES show real water reopens the
  question as "some biomes, not all"; one that also shows zero water,
  tried the NORMAL (non-debug) landing-site flow, escalates this to a real
  engine/mod regression worth flagging to the owner directly.

## criteria
Closed when either (a) the root cause is found and it's a bridge-tool-only
artifact with no bearing on real play, with a note added to
`skills/rimbridge/references/traps.md`, or (b) it's confirmed to also affect
a normal player landing, at which point this item should be escalated
(`needs: owner`) rather than closed.
