# Pyrelands progress

**State at retirement (pass 20):** the game is up on the `pyrelands` tier with build 8c548b81c5 deployed (the ash ground
cover). It sits on map x (the fresh colony replayed from `NS_Pyrelands_play_x_setup`, not saved). Bridge released.

## Seen and done this pass: the owner's "blurry grey stuff" was still there, and is now gone
Looked at pass 19's `first_look_8` (map x, day 3) at 1:1 before running anything: the loose-ash drifts on bare ground still read
as grey cloud puffs and cotton (the owner's 2026-11-07 complaint), eight sprite redraws in. The sprite approach was the problem,
not the texture. **Replaced it** (8c548b81c5, `Source/PyrelandsAshCover.cs`, textures from `ash_cover_gen.py`):
- `SectionLayer_PyrelandsAsh` draws loose ash as ground cover: a 4x4-quads-a-cell mesh per section, alpha from the bilinear
  field of cells holding ash, cut at its 0.5 contour after a wrapping value-noise bends it (3-cell and 0.75-cell octaves, so
  clumps lose the cell grid's straight sides), drawn with vanilla's `TerrainFadeRough` shader and our own edge texture
  (`RM_FE_AshCoverEdge`, mid-grain RGB noise) so the margin frays into grit like a terrain edge. Tint 0.68 grey. Opacity per
  thickness 0.9/1/1/1. Rebuilds only when the section's ash changes (Things dirties far more often than ash does).
- The filth keeps every mechanic (fire and ash fall lay it, rain washes it, expiry, indoor sweeping); its graphic is now
  `Graphic_RM_AshCoverHidden` (prints nothing; icon only).
- Tried first and rejected, live on map x with a temporary `Tune` hook through `jawa/static_call` (removed before commit):
  vanilla's snow path (`Custom/Snow`, half-cell vertices, cloudy `SnowMacro`) laid each clump as a soft fog cloud
  (`shots/cover1_x_west`, `cover2_x_west`); the terrain shader with vanilla's `RoughAlphaAdd` read as cotton (t5-t8); a grain
  edge on a bright powder read as flour (t9-t10). Kept: t13-t16's recipe. Terrain shaders tint by vertex RGB (cyan at R=0, t3).
- Result: `shots/final_x_west.png` (a day-old scar at play zoom: pale ash sheets with frayed edges beside gravel, no puffs);
  `noon_x_west.png` (a natural ash fall at noon); `first_look_9_ash_before_after_day3.png` (pass 19's day 3 over this build's
  day 3.1; not a fair pair: the after frame is under ash fall).
- Tick rate at Superfast unchanged: 351-356 t/s across the replay against pass 19's 350-353 on the old build.

## Broaden call (pass 20)
Asked (`Transient/pyre_play10/ask_broaden.md`, three shots): what does the new cover read as, and which plays next.
Answer (`D:\ClaudeWork\rimmandrake\ralph_pyrelands\gpt_help_pass020.md`): the cover reads **first as patchy snow or frost**,
then fine grey dust; the big top patch in `final_x_west` still has a soft cloudlike edge and two patches "could still be called
cottony"; dusted grass reads as frosted or dead. Its plays, ranked: (1) the cover in a messy occupied colony (door, path,
stockpile junction: do surfaces and items stay distinguishable); (2) pass 18's lead 2, a crop plot carried to its first
harvest while grass reconnects; (3) one dirty boundary through rain and clearing (any plant still dusted on a cell with no ash);
(4) perf at peak ash during comparable colony work; (5) can a newcomer learn what the pale ground is from the inspect pane.
Not yet acted on: the replay below was the only play after it. **Act on (1) and (3) next pass**, and take the snow read
seriously: try a darker tint (~0.56) and a narrower edge band (~0.18) live with the hook (`ralph/handoff/ash_cover_tune_hook.md`).

## The replay on this build went badly (map x, `Transient/pyre_play10/colx_run5.log`)
Same setup save and settings as pass 19's run 4 (which came through all alive). Gaz (old, frail, heatstroke from hour 1) wandered
while ~300 fires burned, went down at d2.12 with 8-12 burns and died by d2.25; nobody rescued him (Peyton was on BeatFire, Lady
wandering). A burn of up to 649 fires reached the base d2.3-2.8; walls needed Repair after. Lady was hunted by a barbslinger
("Barbslinger hunting Lady") and died at d2.85. Peyton alone at d3.12. Day 0-1 job tally: LayDown, GotoWander and StudyInteract
dominate; FinishFrame 3 (the room went up slowly). Questions for next pass: does idle wander avoid burning grass here (vanilla's
wander validator vs a 300-fire map)? Does anyone rescue a downed colonist while fire duty runs (our eat-before-fire node sits
at Humanlike_PostDuty; vanilla firefighting already outranks rescue)? Is a predator hunting a colonist on day 2 the cast's
ordinary behaviour or a hunger/thirst side effect? One seed: replay once more before changing anything.

## Next, in order
0. **The replay's two deaths** (section above): read them before anything else.
1. **Re-shoot `pyre_ashfall_darkens_drifts` on this build**: its drifts' look changed (sprites to cover; the grass dust
   overlay and the counts did not). `python.exe Transient/pyre_play10/ashperf.py RM_FE_Weather_AshFall 6 2500 3` on map x
   prints ash count, fires and t/s per hour with shots at h0/h3/h6 (also pass 18's lead 5, perf at peak ash).
2. **The main suite on this build.** Reload the site first:
   `python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --tag r3 --reload-only --tile 38 --map-id 1`, then
   `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py
   --skip-chains embergrass_regrow,burn_line,fresh_burn_bonus --out Transient/northstar/Pyrelands_p21_main.json`.
3. The ash cover look: GPT read snow/frost first (see the broaden call); tune live, then a clean noon before/after pair.
4. The fresh-eyes judge (north star plus shots only), then DONE.md. A broaden call was made this pass: DONE.md is allowed in
   pass 21 once leads (1) and (3) are acted on.
Tools: `Transient/pyre_play10/cap.py NAME X Z [rootSize]` and `cap.py ash` (densest ash blocks), `ashperf.py`,
`Transient/pyre_play9/colony.py reload|setup|run`.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: true
- pyre_mapgen_log_clean: true
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: true
- pyre_fresh_burn_feeds_the_field: true
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: true
- pyre_burn_line_present: true
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: true
- pyre_ruins_scorched: true
- pyre_firehawk_carries_ember: true
- pyre_furnacebeast_warmth: true
- pyre_furnacebeast_heats_room: true
- pyre_burrowers_dive: true
- pyre_ashfall_darkens_drifts: unseen (the drifts' look changed in 8c548b81c5; not re-shot as a series on this build)
- pyre_cinderfall_distinct: true
- pyre_blackrain_reads: true
- pyre_cannot_ordinary_rain: true
- (owner's card, 2026-11-08) pyre_furnacebeast_sleep_ignites: true
