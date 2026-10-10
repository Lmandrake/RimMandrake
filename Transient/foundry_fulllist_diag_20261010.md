# FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO — progress log (FOUNDRY, 2026-10-10)

## Status
- started; claiming ticket

## Diagnosis

## Fix

## Cold-load proof
- 18:00Z wrote src/RimMandrake/Utils/costlist_resolve_check.py (patched-def-tree costList resolver); running on FULL.LATEST
- 18:13Z suspect: today's CANON_MATERIALS patches remove KOTOR_AlloyDurasteel/Bronzium (RSW_DurasteelConvert only rewrites counts 1..30; KotORDroids uses 80/100/120). Waiting on resolver.
- 18:13Z resolver still running (lxml full-tree patch sim, ~10+ min)
- 18:23Z resolver still running
- 18:24Z resolver v2 (defName index) running; 55946 defs combined
- 18:36Z coordinator: run build.py --gm --apply (companion 1955bd4b6) before the full-list cold load; check awareness init line + jawa/awareness status after
- 18:44Z resolver at 10000 ops
- 18:53Z resolver: .. 10000 ops, at mandrake.rut.pawnflavor
- 18:54Z resolver v2 crawled (index rebuilt on every in-def Add); fixed invalidation, rerun v3
- 19:10Z v3: .. 6000 ops, at mandrake.rut.patches
- 19:22Z v4 (incremental index):    slow op 25.8s mandrake.rut.patches /Defs/PawnKindDef//texPath[text()="Things/Pawn/Animal/AA_Rapto
- 19:25Z ROOT CAUSE: resolver v5 (FULL.LATEST, 10959 ops) -> OuterRim_Durasteel missing in 6 neronix17.outerrim.furnitureanddecor DOORS (Minify Mass path) + beds/tables/dressers. RSW_DurasteelConvert_OuterRim.xml (0f32b77b8, today) removes the def but its count Replaces only cover OuterRim.Core counts. Fix: SetName catch-all in both durasteel convert patches. Owner/coordinator: no deploy, no bridge, no launch this pass. Proving offline with override.
- PROVEN OFFLINE: resolver with the patched Armoury (override) -> 0 OuterRim_Durasteel misses, 0 MINIFY MASS PATH hits
  (11 remaining misses are pre-existing apparel / van.dacrypts entries off the Mass path; Meat_Human is implied).
  Armoury validation durasteel_convert_static / durasteel_outerrim_static [] and selftest_armoury pass.

## Launch steps owed (NOT run: owner ruling via coordinator, bridge-system review first)
1. deploy: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Armoury` (read plan) then `--apply`
2. `rimflow bridge who` -> `rimflow bridge take --for "full-list load proof"`
3. kill RimWorld by PID (tasklist), then restore FULL.LATEST: `python3 src/RimMandrake/Utils/modlist_swap.py --restore` (551)
4. (companion DLL 1955bd4b6 if still wanted: `build.py --gm --apply` while game is down)
5. launch via Steam (launch_and_wait.sh, rimbridge skill); `belt_watchdog.py` every 5 min
6. pass = `Bridge token:` in Player.log, no 'Resetting mods config'; TPS record autostart line; release bridge
