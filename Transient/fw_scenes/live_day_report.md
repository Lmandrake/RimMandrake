# FlowWorks live day report — 2026-10-17 (FOUNDRY live-driver helper)

## 1. Deploy of fe309aefe (level-water fix)
DONE 17:57Z. Live list was already the 11-mod flowworks list (modlist_swap --status: UNRECOGNISED, 11 active;
harmony, core + 5 DLC, rimbridgeserver, simplecamerasetting, gimmesomeslack, flowworks), so no swap was needed.
Game closed (Stop-Process), `deploy_custom_mods.py --mod FlowWorks --apply` (65 files, VERIFIED in sync; the
deployed copy was also behind on 56 weir/bank textures and defs, all committed), relaunched via `steam.exe -applaunch 294100`.
Deployed DLL sha256 ee95273... = repo DLL = the `# dll:` header of the committed `.srchash`; deployed `.srchash`
byte-identical to the repo's; RM_FlowKernel.cs hash in the srchash (080c9580...) = the committed file. Previously
deployed DLL was 82f3943b... (stale).

## 2. water_scenes_walk.py crash fix
_pending_

## 3. S1..S6 rerun at shipped settings
_pending_

### Pond fill grids S2/S5/S6
_pending_

### S3 mass difference
_pending_

## 4. PIT_CLIMB live proof
_pending_

## 5. Bridge permission file
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\companion_profile.json`:
expiresUtc changed 2026-10-17T20:30:00Z -> 2026-10-18T02:00:00Z at 17:58Z. Nothing else in the file was touched.

## 6. Left over
_pending_
