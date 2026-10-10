# BACTA_TANK_ART_1 — Bacta tank art from the ESB canon image

Replaces the procedural PIL placeholders in `src/RimStarWars/Bacta/Textures/` (each folder's `PLACEHOLDER.md`
lists every file and the constraints the real art must keep — two layers, a clear middle for the fluid column,
drawSize×128 canvases, no `_west`).

## state 2026-10-10 (FOUNDRY)
- Six artpipe jobs filed (`Transient/bacta_tank_art_jobs_20261010.json`, priority 50): tank body north/south
  (128×256), east (256×128), medical droid, bacta canister, bacta spray. Each carries `install_to` at the exact
  texPath (art binds by texPath).
- `RSW_BactaPatch` already has two finished renders (`phfix_RSW_BactaPatch_a/_b`, 2026-10-08) awaiting a sheet ruling.
- NOT filed: `RSW_BactaTankShell_*` (the glass over the occupant). It must be mostly transparent with a clear
  middle, which an image model will not hold; keep the procedural shell unless a render proves otherwise.
- No ESB reference image is on disk and no canon-library entry exists for the bacta tank; the prompt describes it.

## NEXT
Renders land in `D:\Luke\dev\_artpipe\done`; put them on an owner review sheet, then `art.py install`/`enact` what he keeps.
