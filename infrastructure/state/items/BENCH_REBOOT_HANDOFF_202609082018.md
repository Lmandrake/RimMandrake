# BENCH reboot handoff — 2026-09-08 evening

## Start here
1. Read `observed/LIVE.md` top section — the MODERN GAME baseline (owner-ruled today).
2. The sitting to open: **worldmap modification WITH the owner** — bridge work.
   `rimflow bridge take` first (it is FREE). ⚠️ The running game currently has the
   GRAVSHIP save loaded (last migration test) — load
   `WORLDMAP_V24_consolidated_names_2026-09-09` before world edits.
   Skills: rimworld-world-editing + rimbridge. Memory: biome-sheets loop
   (one biome at a time, with him — don't audit his map at him).

## What this sitting finished (all pushed through 1a6feb62)
Consolidation sprint repo-side + proof load (590 clean) · save migrations
(V24 world + gravship f, live-proven, canonically re-saved) · saves pruned
to 4 keepers (deleted-unverified until next-launch count) · Pyrelands is a
real self-contained biome (built, undeployed) · Chronicle-Ninefold
decoupled (built, undeployed) · dunes design v2 ruled build-ready
(MOVING_DUNES_BUILD_1 gated on shader quicktest) · maturity dashboard:
new layout + 58-system refresh, republished · Graffiti generic marks
sheet awaiting owner review (Transient/art_review_generic_marks/) ·
Sand People mod evaluated → owner unsubscribes (capture committed).

## In flight at handoff
- Desert wraps art candidates agent (opus) — output lands in
  `Transient/art_review_desert_wraps/` + contact sheet; if the folder has
  a sheet, bring it to the owner (DESERT_WRAPS_ART_COMMISSION_1).

## Traps rediscovered today (cost time, will again)
- `rimworld/load_game_ready` is a does-save-exist checker, NOT load
  progress; probe game content on fresh connections instead.
- python.exe cannot see /tmp — bridge scripts live in Transient/.
- ModsConfig id-merge dedupe: destination keeps its OWN slot (lesson filed).
- git add: one bad path kills the whole add; never 2>/dev/null it.
- The dump's count-fingerprint FALSELY passes right now (set differs by
  sandcastles/seaswaterline at same count) — retake dump on next load.

## Owed next windows
Shutdown window: deploy Pyrelands + Chronicle DLLs together with their
quicktests. Pre-freeze: rid/xtp regen (build_salvation_rid.py), Ashkarr
tile switch to RM_FE_Pyrelands (PYRELANDS_WORLD_SWITCH_1). FOUNDRY queue
carries its notices (swept WIP, smelt config, About XML `--` lesson).
