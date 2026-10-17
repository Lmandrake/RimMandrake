# Review walk 2026-10-17 -- staging plan (offline; nothing here has been run live)

Owner by card 2026-10-17: after FOUNDRY's walk, ONE restart. Everything below assumes the bridge is held, the game is up on the
walk's mod list, `python.exe` (not python3) for bridge scripts, `| tr -d '\r'`. Never write the owner's Saves except through the
named save verbs. Repo root: `/home/mandrake/rm/bench` (paths below are repo-relative to it; absolute prefix omitted for brevity).

## 0. Before the restart (game DOWN)

1. `bash /home/mandrake/rm/bench/Transient/review_walk_2026-10-17/deploy_all.sh` (applies the plans; refuses if the game is up).
   Plans: `deploy_plan_<mod>.txt` beside it; `deploy_plan_biomes.txt` is the composed Baroque Biomes. LeaningScrub,
   EnvironmentalHazards and ExplosiveGrowth have NO standalone plan: they are folded into the composed mod and refuse standalone.
2. **Mod list gap (measured now, not a doc): live `ModsConfig.xml` has 11 active mods, only `mandrake.rm.gimmesomeslack` and
   `mandrake.rm.flowworks` of ours.** Deploy writes files only. Items (d) and (e) need `mandrake.rm.biomes` (venomvine, Scrub) and the
   SWBestiary/StarWarsPatches mods (the RSW_ creatures) ACTIVE at the one restart, with every DLC (standing rule). No tool in this
   plan sets that; `modcheck`/`modlist_swap.py` do, but `modcheck run` rewrites ModsConfig (tool_traps.md) -- FOUNDRY/owner's call.
3. (b) needs a def+texture change BEFORE the deploy: see (b).

## (a) Sprinkler heads, four looks, spraying, on a pump network
- Tool: `Transient/review_walk_2026-10-17/stage_extra.py sprinklers` (written 2026-10-17, never run live); before it nothing staged it. `review_map_coverage.py` says "no station yet"; `validation.py` SPRINKLER_LIVE rows are written, never run.
- Recipe (validation.py comment): tank (1 kL water) + 3 `RM_UniversalPipe` + `RM_SprinklerHead` on the last pipe + powered
  `RM_LiquidPump` (+ Battery) on the run; fill the tank; unpause ~2,600 ticks (pulse is hourly, spray lasts pulse+250); head reads "Spraying water".
- Reusable ops in `src/RimMandrake/FlowWorks/review_map.py` SETUPS: `build`, `tank [(x,z,Mode,LiquidDef,litres)]` (RM_NorthstarProofs.ProofTank),
  `pump [(x,z,"draw")]`, `style [(Def,x,z,StyleDef)]` = `jawa/set_thing_props style=` with `RM_SprinklerHead_Scrapper|Industrial|Modern|Futuristic`.
  Cheapest path: add one EXTRA SETUPS entry (four mini-nets in a row, one per look, with `marks`), then
  `python.exe src/RimMandrake/FlowWorks/review_map.py --build --fresh-map` and `--goto <id>`. That is a code edit nobody has made.
- Spray needs the game unpaused (step_game_ticks <=2000 per chunk); re-pause before looking. Keeper: `RM_fw_walk_sprinklers_20261017`
  via `review_map.py --save --name RM_fw_walk_sprinklers_20261017`.

## (b) Drying pond showing RM_WaterThin shallows, art in situ
- Today `RM_WaterThin` uses a PLACEHOLDER (`Terrain/Surfaces/WaterShallowRamp` + WaterDepth shader) in
  `src/RimMandrake/FlowWorks/Defs/Canals/TerrainDefs/FlowWorks_PondStageTerrain.xml`. Candidate art: `src/RimMandrake/FlowWorks/art_source/WaterThin/RM_WaterThin_master.png`
  (generator `make_water_thin.py`; tile check `check_terrain_tile.py`).
- Provisional install (needs the def edit; there is no install target path yet, `Textures/RimMandrake/FlowWorks/` has no Terrain folder):
  `python3 src/RimMandrake/Utils/art/art.py install FlowWorks Textures/RimMandrake/FlowWorks/Terrain/RM_WaterThin.png --file src/RimMandrake/FlowWorks/art_source/WaterThin/RM_WaterThin_master.png --owner-said "Same with the thin water. Must see it in situ"`
  then set the TerrainDef `texturePath` to `RimMandrake/FlowWorks/Terrain/RM_WaterThin` and drop the waterDepthShader lines (the def's own header says exactly this), then redeploy FlowWorks.
- Authorised? Plausibly: his words ask to see it in situ, and art.py takes them as `--owner-said`; but cosmetic changes need his permission and
  this is PROVISIONAL (not accepted) -- art.py refuses an install over an owner-kept picture, so run `art.py status` first. I have NOT installed it.
  Side effect to know: my `--dry-run` probe already `put` the master PNG into the art store (bytes only, nothing installed, no game file touched).
- Staging: `python.exe src/RimMandrake/FlowWorks/northstar/pond_pump.py --fresh-map --cycles <N>` builds a 3x2 limited natural pond with a pump and draws it down
  (each cycle 250 ticks; recession is outside-in, middle cell last). Then read cell terrains for RM_WaterThin; `liquid_checks.py --only L8 --l8-pond x,z` is the
  existing proof of "shallows before mud" (written, never run live). No tool freezes the pond at the thin stage for the camera: pause when a cell reads RM_WaterThin, frame it.
  Keeper: `RM_fw_walk_thinwater_20261017` (via `review_map.py --save --name ...`, or a bridge save under that name).

## (c) Joined weir run, four looks, across a LIVE river
- Live river: `python.exe src/RimMandrake/FlowWorks/northstar/river_site.py` (founds a colony on a mild tile with a river), then
  `python.exe src/RimMandrake/FlowWorks/review_map.py --rivers --build --save` (map R; station r_weir builds ONE `RM_BankWeir`, style None).
- Looks: `RM_BankWeir_Scrapper|Industrial|Modern|Futuristic` (ThingStyleDefs; textures exist, 9 pngs each under `Textures/RimMandrake/FlowWorks/Weir/<Look>`).
  Style per thing = `jawa/set_thing_props style=` (same as above).
- **No tool builds a joined run** (adjacent weirs along the bank, per look). The `river_works_looks` station is a single weir on a painted river with NO current.
  Plan: four runs of N adjacent `RM_BankWeir` via `jawa/build_batch` (rot from review_map_rivers.ROT), one run per look, each followed by a style call; then unpause
  a few hours so the slack pool forms. Keeper: `RM_fw_walk_weirs_20261017`. Existing saved river site: `RM_TestSite_river_v1` (load it instead of founding, if FOUNDRY agrees; loading is not writing).

## (d) Venomvine (tall renders) on a Scrub map
- Existing: `src/RimMandrake/LeaningScrub/prep_site.py` / `python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load leaningscrub` loads the saved site
  `RM_TestSite_leaningscrub_v1` (exists in Saves). It predates this deploy's new textures/GenStep (RM_VenomvineIslands_GenStep, tall variants _c/_d, RM_VenomvineThicket_a), but
  PLANTS already placed keep their def, so the new art shows after the restart.
- New-island gen step only fires on a freshly generated Scrub map: `world_tile_map_generate` on a Scrub tile (note the black-map/stale-render caveats in rimworld-live-review:
  call `jawa/map_commit`, spawn living colonists). No tool does the whole thing; fallback: `rimworld/spawn_thing` of each `RM_*Venomvine` def on the loaded site, camera via stage_review `--frame`.
- Keeper: `RM_fw_walk_venomvine_20261017`.

## (e) Facings: one of each changed creature, beside a human
Defs (all measured by grep of `src/**/*.xml`): RSW_Blarth, RSW_BloodletterPetrel, RSW_Bolotaur, RSW_CanCell, RSW_ColoClawFish, RSW_Faa, RSW_Gorg (also RSW_FrilledGorg /
RSW_LongtailGorg exist; RM_ShaleGorger is NOT the Gorg), RSW_Grazer (RSW_FeralGrazer exists), RSW_Hssiss, RSW_Kreetle, RSW_Narglatch, RSW_Nexu, RSW_Porg, RSW_Stintaril, RSW_Tukata,
RSW_Vornskyr, RSW_Wampa, RSW_Varactyl, RSW_OpeeSeaKiller, RSW_Yobshrimp. ColoClawFish / OpeeSeaKiller / Yobshrimp are sea creatures: they need water cells (or a sea map), not grass.
- Tool: `python.exe src/RimMandrake/Utils/stage_review.py --map <id> --kill-hostiles --clear chunks,filth --spawn "RSW_Blarth:1,RSW_BloodletterPetrel:1,..." --at X,Z --spread 3 --layout grid --face south --frame X,Z,W,H --shot facings_south --save RM_fw_walk_facings_20261017`
  (`--face` locks ALL spawned pawns to one facing, so rerun with --face east/north/west for each facing; wild spawn, grid layout, never cluster).
- **No flag puts a human beside them.** Add by bridge: `jawa/spawn_pawn {kindDef:"Colonist", x, z, count:1, faction:"PlayerColony"}` at the line's start (a living colonist also keeps the map from being culled). Pause (set_time_speed 0) before shooting.
- Sea trio: second call with `--terrain` water or hand-place; flyers (none in this list are flight-tested live: owner ruling, never live-test flight without him).
- True-scale sheets for the same set already exist (`rimworld-review-sheets`); the walk is the in-game complement.

## Update (same day)
- Mod list: `modset.md` + `walk_modlist.py` (last step of `deploy_all.sh`). Thin water: art installed provisionally and the def edited (commit in the log); deploy FlowWorks with `deploy_all.sh`.
- `stage_extra.py sprinklers|weirs|human` replaces the "no tool" lines for (a), (c) joined runs and (e) human; its docstring lists every bridge call and where it already runs. Never run live.
