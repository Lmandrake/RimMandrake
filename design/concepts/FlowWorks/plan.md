# FlowWorks: plan (Designer stage 3, run rm-role-designer-1793863469, 2026-11-05)

Reads with `sheet.md` (what he reads), `tree.json` (31 leaves), `scenes.json` (28 scenes, 3 showcases) and
`floor.json`. Writes no code: every missing part is a filed item below.

## Structure

- **Built and kept (24 leaves).** The north star's 83 lines map onto 17 positive leaves and 5 `cannot_show` leaves,
  grouped by what one scene can show: dig and depth, fill and level, the source, fire, slime, pawn height, pits, covers
  and spikes, ways in and out, sluice, hoses, the liquid network, trench cover, hung bridges, ice, rivers. Each has an
  acceptance scene; most reuse a staging function that already exists (`extensions.py`, `validation_v2.py`,
  `live_session.py`, `suspension_bridge_proof.py`, `river_scenes_walk.py`).
- **Owed by his words (5 leaves):** `drained_hole_is_a_prison`, `toss_flame_from_rim`, `canal_wets_two_squares`
  (+ `wetting_is_not_flood`), `raiders_fetch_their_fallen`. They are new mechanics, so they are build items, not scenes.
- **The flagship (`moat_raid_sequence`)** joins swim, sluice, pit, prison, pump and fire in his order. It needs the
  owed prison and toss-flame mechanics first.
- **His other scenes.** The pit-trap raid is showcase 3 (interaction scene `sc_pit_trap_raid`). The island bridges
  raid is an acceptance scene (`sc_islands`), not a showcase: its bridges and drawbridges are already in the moat.
- **Instrument:** `wetness_probe`, needed by both wetting leaves. Nothing reads wetting today.
- **Walk:** `walk_moat_season` on his full list: reload from a save made mid-swim, repeat the fill, run the actions in
  a second order, master switch off and on, a wetted garden running throughout.

## Order

1. `FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST` (instrument first).
2. `FLOWWORKS_SCENES_BUILD_EACH_WITH_A_FOIL`: the per-leaf acceptance entry points in
   `src/RimMandrake/FlowWorks/northstar/concept_scenes.py`, plus the missing start assertions, controls and snapshot
   restores on the reused functions (the stage-0 audit: 86 of 175 scenes lack a discriminating control; 96 restore only
   partly). Each scene's control in `scenes.json` says what it must rule out.
3. The owed mechanics, in any order: `FLOWWORKS_PRISON_BUILD_NO_BED_REQUIRED`, `FLOWWORKS_FLAME_BUILD_TOSS_FROM_THE_RIM`,
   `FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP`, `FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN`.
4. `FLOWWORKS_SHOWCASES_BUILD_THREE_FACES_STAGED`: `sc_moat_raid`, `sc_islands`, `sc_pit_trap_raid`, `sc_garden`,
   `sc_walk`. The moat and pit-trap showcases are held for his review (`hold: owner_review`).

## Showcases (`designer_stage.py showcases`: accepted)

| # | showcase | new | overlap | why it is here |
|---|---|---|---|---|
| 1 | moat | 13 | 0 | his flagship pick (decision `d_scene_moat`) |
| 2 | garden | 7 | 0.12 (the pumped network) | wetting, flood drinking, sprinklers, hoses, bottles, well, converter: the most new ground |
| 3 | pit_trap | 3 | 0.40 (pit, prison) | his second scene; ladders, the raider rescue, trench cover. The overlap is his staging |

Left to cheaper checks (`coverage_rest`): rivers (`sc_river`), slime (`sc_slime`), quarry finds (`sc_dig_finds`),
map-maker taps (`sc_source_pays`, which drives the Sink tap and flow meter), Mod Settings (`sc_walk`, plus the floor's
`mod_settings` line). The numbers in `showcase_rules.json` are UNMEASURED first guesses: FlowWorks is their first replay.
With 0.25 the pit-trap showcase needs staging reasons for two shared capabilities; that seems right for a scene he
named.

## Risks

- **Built is not proven** (`c_proof_stale`): no live row has a result at the current mod hash. Every reused function
  is rerun inside its new scene; none is trusted by its old result.
- **Roots for the owed leaves.** The north star has no wetting, bed-less prison or toss-flame line, so those leaves
  root at the nearest existing line (`canal_holds_only_the_channel`, `pit_trapped_reads_as_trapped`,
  `canal_burning_reads_as_burning_liquid`). Adding bars is allowed to agents, but it changes the validated hash, so it
  is the next north-star edit's job, not this stage's.
- **Breadth** (failure mode 3): only the walk sees every system at once on the full list. `tick_cost` is applicable on
  the floor and the advisory line records the 346 to ~120 TPS drop as the thing to watch.
- **Drawbridge look** belongs to `design/concepts/FlowWorks_Drawbridge/`. These scenes need a drawbridge only to rise,
  trap and fall; its looks are not judged here.
- **Raid scenes are stochastic.** The controls (drawbridge lowered, cover off, winches indestructible, no-one fallen)
  separate the mechanism from pathing accidents; a scene that passes its positive case and not its control is a fail.

## Designs considered for the garden showcase

1. **Garden and workshop** (picked): one farm uses canal wetting, sprinklers, a hose to a tank, bottles and a faucet,
   fed from a drilled well. Seven new capabilities, one shared.
2. A river works (weir, ferry, levee, quarry by the river): three or four new, and contrived together.
3. Folding wetting into the moat map: no new showcase, but it hides irrigation behind the raid, where he would not
   judge it.
