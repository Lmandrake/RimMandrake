# FlowWorks: plan (Designer stage 3, run rm-role-designer-1793863469, 2026-11-05)

Reads with `sheet.md` (what he reads), `tree.json` (27 leaves; 31 at the lock, three wetting leaves and the raid since moved to 0.2.0), `scenes.json` (25 scenes, 2 showcases) and
`floor.json`. Writes no code: every missing part is a filed item below.

## Structure

- **Built and kept (24 leaves).** The north star's 83 lines map onto 17 positive leaves and 5 `cannot_show` leaves,
  grouped by what one scene can show: dig and depth, fill and level, the source, fire, slime, pawn height, pits, covers
  and spikes, ways in and out, sluice, hoses, the liquid network, trench cover, hung bridges, ice, rivers. Each has an
  acceptance scene; most reuse a staging function that already exists (`extensions.py`, `validation_v2.py`,
  `live_session.py`, `suspension_bridge_proof.py`, `river_scenes_walk.py`).
- **Owed by his words (2 leaves):** `drained_hole_is_a_prison`, `toss_flame_from_rim`. `raiders_fetch_their_fallen` and
  the raid proof of every moat, trench, island and pit bar left 0.1.0 for 0.2.0 by his word 2026-11-23
  (OWNER:1795504867390195471; `version/next_version/README.md`).
  They are new mechanics, so they are build items, not scenes. The two wetting leaves (`canal_wets_two_squares`,
  `wetting_is_not_flood`) and their instrument `wetness_probe` left 0.1.0 for 0.2.0 by his card 2026-11-14
  (OWNER:1794721673433243094; `version/next_version/README.md`).
- **The flagship (`moat_drains_and_burns`; `moat_raid_sequence` is 0.2.0)** joins swim, sluice, pit, prison, pump and fire in his order. It needs the
  owed prison and toss-flame mechanics first.
- **His other scenes.** The pit-trap raid (showcase 3, `sc_pit_trap_raid`) is 0.2.0. The island bridges are an
  acceptance scene (`sc_islands_walker`), not a showcase: their bridges and drawbridges are already in the moat.
- **Walk:** `walk_moat_season` on his full list: reload from a save made mid-swim, repeat the fill, run the actions in
  a second order, master switch off and on, the garden running throughout.

## Order

1. `FLOWWORKS_SCENES_BUILD_EACH_WITH_A_FOIL`: the per-leaf acceptance entry points in
   `src/RimMandrake/FlowWorks/northstar/concept_scenes.py`, plus the missing start assertions, controls and snapshot
   restores on the reused functions (the stage-0 audit: 86 of 175 scenes lack a discriminating control; 96 restore only
   partly). Each scene's control in `scenes.json` says what it must rule out.
2. The owed mechanics, in any order: `FLOWWORKS_PRISON_BUILD_NO_BED_REQUIRED`, `FLOWWORKS_FLAME_BUILD_TOSS_FROM_THE_RIM`,
   `FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN`.
3. `FLOWWORKS_SHOWCASES_BUILD_THREE_FACES_STAGED`: `sc_moat_walkers`, `sc_islands_walker`, `sc_garden`, `sc_walk` (the
   raid scenes `sc_moat_raid`, `sc_islands` and `sc_pit_trap_raid` are built and are 0.2.0).

## Showcases (`designer_stage.py showcases`: accepted)

| # | showcase | new | overlap | why it is here |
|---|---|---|---|---|
| 1 | moat | 13 | 0 | his flagship pick (decision `d_scene_moat`) |
| 2 | garden | 7 | 0.12 (the pumped network) | flood drinking, sprinklers, hoses, bottles, well, converter: the most new ground (counts at the lock, with `inv_irrigation`, since moved to 0.2.0) |

Left to cheaper checks (`coverage_rest`): rivers (`sc_river`), slime (`sc_slime`), quarry finds (`sc_dig_finds`),
map-maker taps (`sc_source_pays`, which drives the Sink tap and flow meter), Mod Settings (`sc_walk`, plus the floor's
`mod_settings` line). The numbers in `showcase_rules.json` are UNMEASURED first guesses: FlowWorks is their first replay.
The pit-trap showcase left for 0.2.0; ladders (`sc_ways_out`) and trench cover (`sc_trench_cover_pawns`) are in
`coverage_rest` since.

## Risks

- **Built is not proven** (`c_proof_stale`): no live row has a result at the current mod hash. Every reused function
  is rerun inside its new scene; none is trusted by its old result.
- **Roots for the owed leaves.** The north star has no bed-less prison or toss-flame line, so those leaves
  root at the nearest existing line (`pit_trapped_reads_as_trapped`,
  `canal_burning_reads_as_burning_liquid`). Adding bars is allowed to agents, but it changes the validated hash, so it
  is the next north-star edit's job, not this stage's.
- **Breadth** (failure mode 3): only the walk sees every system at once on the full list. `tick_cost` is applicable on
  the floor and the advisory line records the 346 to ~120 TPS drop as the thing to watch.
- **Drawbridge look** belongs to `design/concepts/FlowWorks_Drawbridge/`. These scenes need a drawbridge only to rise,
  trap and fall; its looks are not judged here.
- **No 0.1.0 scene stages a raid.** Each moat, trench and island scene orders one placed pawn; its control (drawbridge
  lowered, open ground, the winch that stands) separates the mechanism from a pathing accident.

## Designs considered for the garden showcase

1. **Garden and workshop** (picked): one farm uses sprinklers, a hose to a tank, bottles and a faucet, fed from a
   drilled well (its canal wetting left for 0.2.0 by his card 2026-11-14).
2. A river works (weir, ferry, levee, quarry by the river): three or four new, and contrived together.
3. Folding wetting into the moat map: no new showcase, but it hides irrigation behind the raid, where he would not
   judge it.
