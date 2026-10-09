# LIVE_ROUND2_FIXES_PROOF_1 — prove the three live-round-2 fixes in game

Filed by the FOUNDRY worker that fixed them offline (progress: `Transient/FOUNDRY_LIVE2_DEFECTS_PROGRESS_2026-10-01.md`).
Deploy first (`deploy_custom_mods.py --apply`, plus the composed `mandrake.rm.biomes`). One Stillsand quicktest covers all three.

## 1. MUURROK_BEAM_NO_DAMAGE_1 (fixed `f591714e5`, closed)
The warmup is now held by a `UseVerbOnThingStatic` job. On Stillsand, Clear weather, daytime: down a muffalo 8-15 cells from
a surfaced RM_Muurrok, then `jawa/pawn_use_verb action=cast verb="mirror crest"`. The readBack `currentJob` must be
`UseVerbOnThingStatic`; after ~250 ticks `jawa/list_pawns includeHealth` must show `Burn` on the target (it hits the target
cell on about 2 of 3 bursts, so cast 3 times before calling it a miss). Also fire `RM_MuurrokEmergence` and let the visit run:
a hunted pawn should gain `Burn` before the strike. No exception naming `RM_Verb_MirrorBeam` in Player.log.

## 2. SOORRAK_INSTANT_JOB_LOOP_1 (diagnostic only, still open)
Spawn 6 wild RM_Soorrak on a Stillsand quicktest, run 2,500+ ticks (state reads only; never watch or screenshot flight).
The deciding Player.log line is `[RM CreatureBehaviors] instant job loop: RM_Soorrak` — it names the looping JobDef, its
giver class, think tree and targets. Paste that line into SOORRAK_INSTANT_JOB_LOOP_1; the fix follows from it.
If no such line appears and a soorrak still reads `Wait_MaintainPosture` at every sample, the loop is not a same-tick
Succeeded end, and the item's premise is wrong.

## 3. RIMPLACE_STUFFLESS_THING_ROWS_1 (fixed, closed)
`jawa/run_genstep RSW_GenStep_WhisperSarlaccSign`, then one `world_tile_map_generate` Settlement map. Player.log must have 0 of
`MakeThing error: SculptureSmall is madeFromStuff but stuff=null` and 0 of `MakeThing error: Bedroll is madeFromStuff but stuff=null`.

## criteria
- Bars 1 and 3 read as above; bar 2's line is captured into SOORRAK_INSTANT_JOB_LOOP_1.

## verify

### Exact checks 2026-10-09 (acceptance sitting)
- A3 CHECK: Named in the item: `jawa/run_genstep genStepDef=RSW_GenStep_WhisperSarlaccSign` (WARNING: high risk, irreversible, runs on the live map; only on a throwaway quicktest map; GenStep defined in `RimStarWars/StructureInjectionsSW/Defs/GenStepDefs_Whisper_Batch1.xml`). Before it, record the line count of Player.log (WSL `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log`); after it, `jawa/drain_log limit=400 contains="stuff"` and regex the new log tail for `madeFromStuff but stuff=null|MakeThing.*stuff=null`. PASS: run_genstep success=true and the log tail since the call holds zero `stuff=null` lines (control: the same regex on the pre-fix log in `Transient/` finds the old errors, if a copy exists). FAIL: any `stuff=null` line after the call, or run_genstep success=false / null-elevation no-op (UNMEASURED: the step did not place anything; confirm with `jawa/list_things` for the sign).
