# WARCASKET_FIRST_SCRIPT_1 worker note

Files: `src/RimMandrake/Warcasket/validation.py`, `northstar_plan.py`, `northstar_site.py`; walk `design/validation_walks/RimMandrake/Warcasket.md`.
Offline proof: `northstar_driver/cli.py run --mock --mod Warcasket --plan ... --mock-skip-site` runs to completion (NOT GREEN under mock by design: the mock lacks pawn_gear etc.); `lint_calls.py`: 35 literal calls, 0 undeclared, 1 UNCHECKED (`jawa/pawn_gear` via `**{"def":...}`, `def` is a Python keyword); `modcheck lint` clean for the walk; `floor --all`: Warcasket "no bar" (DRAFT walk, no owner bars, so "bar met" cannot apply); every toggle (6) has a covering component.

## Two MOD DEFECTS fixed offline (XML only, no DLL change)
1. `RM_Warcasket` had no `<tickerType>`: apparel defaults to Never, `Thing.DoTick` (RimSage) never calls TickRare, so `RM_CompWarcasketIntegrity` never ran. Added `Rare`. Guard: `compound_failure_fires`.
2. `ToxicEnvironmentResistance 0.9` was in `statBases`; vanilla masks use `equippedStatOffsets`. Moved. Guards: `toxin_cover`, `warcasket_wearer_resists_core_dose`.
Neither was seen red live; a green first run is the fix working. Sibling check owed: `RM_ScaldGear.xml` (TerminalBiomes) was the pattern copied for stats; same statBases trap possible.

## Bars: 38 components in 6 chains (defs_and_load 4, suit_stats 7, compound_failure 6, terrain_immersion 8, sarcophagus 5, core_and_cask_bay 10 incl. site rows)
Tier: `warcasket` (exists; 10 mods, all DLCs).

## How each check is proven able to FAIL
- defs_resolve: control `absent_def_is_refused`. comps_wired: base suit must NOT carry the seal. no_warcasket_log_errors: UNMEASURED if buffer full.
- suit_stats: the naked reading of the same pawn is the control (zero delta if the suit applied nothing). To break: delete `<VacuumResistance>` from the def.
- compound_failure: ON arm must breach; heat-only room is the control; OFF arms (compoundFailureEnabled, masterEnabled) must read zero. To break: remove `<tickerType>` (fires red).
- terrain_immersion: naked vs suited vs ford; toggle arms use the severity delta. To break: set `RM_HazardousTerrainProtection` to 0 (suit arm goes red).
- sarcophagus: Junker corpse must yield suit+core+Steel 25+ComponentIndustrial 2; ordinary suit corpse is the control. To break: remove the extension from the Junker def.
- core: loose core doses; far pawn clean; core on bay cell clean; toggles flip inspect text and dose.

## Unmeasured / UNCOVERED (named in the walk)
vacuum as a hazard (no room_vacuum tool); corpse seal state / strip (no tool); wastepack dissolution (no comp-field reader); gravship substructure placement; art.
Statistics: compound ON arm ~7 expected breaches (false-red ~0.1%), OFF arms ~4.8 (~0.8% false-green). Rerun before filing a lone red there.
Unmeasured shapes to watch on the first run: make_empty_room leaves a random DOOR (heat re-set every 500 ticks); ordered_job with a Corpse targetAId; spawn_pawn on a pad turned to deep water; Soil pollutable (`cellsEverPollutable`); `storage_settings` read returns `allowedSample` as strings or dicts (both handled).

## LIVE-RUN SHEET
1. Bridge: `python3 src/RimMandrake/rimflow/cli.py bridge take --for "Warcasket first script"`.
2. Tier: kill game first (modset_builder refuses within 3 min of Player.log activity), `python3 src/RimMandrake/Utils/modset_builder.py --tier warcasket --apply` (check `--help` for exact flag), launch via Steam, wait for `Bridge token:` (cold load of 10 mods: minutes, not 15). Deploy the mod folder first (`deploy_custom_mods.py --mod Warcasket --apply`): the XML fixes live in the repo only.
3. Quicktest map >= 150x150 (`rimworld/start_debug_game_ready`), bridge up, all five DLCs.
4. Driver: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Warcasket --plan src/RimMandrake/Warcasket/northstar_plan.py` (cd to repo root, relative paths). Results `Transient/northstar/Warcasket_*.json`.
5. Tick budget: ~6000 + 2x4000 (compound) + 3000 (immersion) + 3800 (sarcophagus) + 4x2500 (core) + short waits = ~31000 ticks at ~53 ticks/s = ~10 min wall (compound chain alone ~5 min).
6. Site: no god mode needed; the suite clears its own pads; settings must be at defaults (preflight checks).
PASS/FAIL: see each component's name in the walk's arrows. A FAIL starting `UNMEASURED:` is a harness/site matter (died pawns, rolled log buffer, unpollutable floor); `toxin_cover` / `compound_failure_fires` red = the offline fixes did not take or were not deployed.
