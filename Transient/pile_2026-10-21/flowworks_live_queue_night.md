# FlowWorks live queue — BENCH helper, night 2026-10-21/22

Bridge: taken by BENCH (FlowWorks live queue: fallen cord, pit cover, pitfall). Game: DOWN at start.

## 1. FALLEN_CORD_BUILD_RUBBLE_IS_NO_SHIELD
- mechanism: (pending)
- class: (pending)
- fix: (pending)
- live: (pending)

## 2. FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED
- (pending)

## 3. FLOWWORKS_PITFALL_FIX_HISTORY_NOT_SAVED
- (pending)

## Tier / ModsConfig
- (pending)

## Log
- 03:40Z item 1 fix written (LandWreck lays rubble, not the impassable wreck, on a square whose cord fell: RM_MapComponent_FallenCords.CordFellAt); lines_proof row no longer clears wreck (wreck on cord square = row FAIL; mock fault wreck_shields). FlowWorks built + deployed (with items 2/3 offline fixes already in source). Tier fw_gss_sitting applied, game UP.
- 03:45Z PRIORITY CHANGE (coordinator, owner 8:40 PM "I'd really like to do the live walk ASAP"): queue PARKED after deploy. Staging owner_review_stage on a debug quicktest (250x250, RM_TheRot), origin 10,100 so bars (x160..222) fit.
- 03:47Z stage 1 (ladders,spikes,gates,shallows,sprinklers,hoses) rc=0; one hose lay refused (81,161)->(91,161) no room for lead-out. Stage 2 (bars) running.
- 03:52Z owner walk STAGED. Save FLOWWORKS_OWNER_REVIEW_20261021_2043 (15.4 MB, save_guard: no keeper changed). Debug quicktest 250x250 RM_TheRot, origin 10,100.
  Areas: main rows rect (7,94,64,70): ladders, spikes, gates (sluice + grate), shallows, sprinklers; hoses rect (74,94,84,76); bars rect (160,94,62,76): bars_joint/dry/trench/access/bridges/bridge_kinds.
  Failures: hose lay (81,161)->(91,161) refused (no room for lead-out; pipe_beside_hose_6 scene); bars_trench ProofTrenchCover refused x2 (shooter has no ranged verb) - pawns staged, cover numbers not read. Stage-1 overview.png overwritten by stage-2's.
  Camera framed on (7,94,216,77); hour ~10.5, Clear locked, hostiles killed. Game UP, bridge HELD for the owner walk. Player.log: no exceptions storm (harvest --stale-ok: 6 cross-refs + 1 texture path on the 14-mod tier).
- 03:58Z owner: staged map unusable (no labels). Rebuilding with review_map.py: --plan, then --build --fresh-map --only visuals first.
- 04:30Z review map visuals block (39/39) built, labels 461 pinned, saved RM_fw_review_20261021; owner finished walk. Gallery not built. Resuming queue.
- 04:35Z sluice fix committed with clean-clone DLL c922fd3a3f00 (not yet deployed). Running lines_proof live (loaded DLL = f76aafe build with item fixes).
- 04:45Z ITEM 1 CLOSED f76aafe3ac76 (live PASS, wreck not cleared). LADDER_HOSE FAIL once in full run, PASS alone -> filed LADDER_HOSE_DIAGNOSE_RETRACTS_ON_A_WHIM. Next: items 2/3 rows (pit cover kill, pitfall save round trip).
- 05:05Z FlowWorks c922+proof-surface DLL deployed, game relaunched. Running COVER_BREAK_DROPS_RIDER + PITFALL_SAVED_ARRIVAL_FALLS (new lines_proof rows).
- 05:15Z COVER_BREAK_DROPS_RIDER live PASS (lines_pit_run1.json). PITFALL row UNMEASURED/HARNESS: load_game_ready answered mid-load; row now waits for Playing + polls ProofTrap. Rerunning.
- 05:30Z PITFALL row FAIL/MOD live: FinalizeInit called superdeepTrap.ResetDetector() after every load, wiping the scribed lastCell. Fix: removed. Built (clean clone), deploy at next restart. Meanwhile staging gates+hoses on current game for sluice look + joins close-ups.
- 05:50Z SLUICE closed c922fd3a3f00 (north rim black live). 15 join close-ups in joins_live/ (pinned; camera floor is rootSize 8, so crops of full-res shots at ~114 px/cell). Restarting for the ResetDetector fix.
- 06:05Z COVER_BREAK_DROPS_RIDER + PITFALL_SAVED_ARRIVAL_FALLS both live PASS (lines_pit_run3.json) on the ResetDetector fix.
