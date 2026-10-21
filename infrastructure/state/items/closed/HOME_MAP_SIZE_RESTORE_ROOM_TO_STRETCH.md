# HOME_MAP_SIZE_RESTORE_ROOM_TO_STRETCH

Owner, by card 2026-10-20: "Starting map is 250x250, old world 325x325: which size?" -> "Back to 325".

## Where the size lives (read 2026-10-20)
- Every home map generated after game start (gravship landing `GravshipUtility`, settling, `GetOrGenerateMap`) uses the
  SCRIBED `WorldInfo.initialMapSize` (RimSage). `GameInitData.mapSize` (default 250, Dialog_AdvancedGameConfig sizes
  200..325) only sizes a NEW game's first map — players never start one.
- `CANONICAL_ASHKARR_START_2026-09-12.rws`: `initialMapSize` (325,1,325) — the "old world". Every
  `ASHKARR_DEV_*_2026-10-20.rws` (START, _LOCKED, SHIP, LANDED, FOUNDERS): (250,1,250), and their one map is 250x250.
- No def, scenario or Mod Setting of ours sets it; no `.rws` in Saves/, Saves_archive or the FOUNDRY/northstar backups
  has a 325 map. The route is world data on the live world, then an in-game save — no hand-edited .rws.
- Built: `jawa/world_info_set initialMapSize=<200..325>` (JawaBench, 3742c2b6bc29), compiled, NOT deployed. ⚠️ build.py's
  plan says the deployed companion has tools the repo source lacks (jawa/animal_bond, difficulty_tune, fire_raid, …):
  find which build carries them before `--apply`, or the deploy removes them.

## Runbook (game down for the companion, then bridge)
1. Resolve the LOSES list above, then `python3 src/RimMandrake/bridgetools/build.py --apply` with the game DOWN.
2. Load the dev save the world remake treats as current (the LOCKED one unless `TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` says otherwise).
3. `jawa/world_info_set initialMapSize=325`; `jawa/world_info` reads initialMapSize 325.
4. Save in game under a new name; confirm `<initialMapSize>(325, 1, 325)</initialMapSize>` in the file.
5. The existing 250x250 home map keeps its size; the next landing/settle makes a 325 map. If the shipped start must itself be
   325, the LANDED/FOUNDERS step is redone after step 4.

NEXT: settle which companion build owns the missing tools, deploy the companion with the game down, then run steps 2-4 on the dev save.
