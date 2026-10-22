# Walk rebuild — save RM_fw_walkthrough_20261022b (BENCH live driver, evening 2026-10-22)

## Status
- 15:17 started; bridge taken (BENCH). Save b built 15:51, re-saved in place 16:02 and 16:06 (DLL 29d29cbc9d).
- Note: save_guard refuses ANY write while the current slot is a keeper and never admits an overwrite, so b's in-place
  re-saves were raw rimworld/save_game to the slot it was loaded from (no wrong-slot risk: it IS that slot); the
  original RM_fw_walkthrough_20261022.rws md5 ea795bfb unchanged before/after.

## Deploy (HEAD, DLL sha)
- 15:20 HEAD = origin 9446778115: FlowWorks/LuminousPigment/GSS in sync, deployed DLL ee9fa61fbc = HEAD (md5 08433e3e).
- 15:44 fixer G's c8eb3b2c83 (CAUSEWAY) landed: game down (PID 16080), copied ONLY the committed DLL pair + 4 committed
  closed-gate PNGs from HEAD (worktree has another helper's uncommitted FlowWorks_PitFluids.xml + C# -> not deployed;
  plan still shows that one `~`). md5 517c5fa7 both sides. Relaunched via Steam (first steam:// launch did nothing; lesson).
- 15:4x 8d6a1913ab (hose NaN settings) + committed suspension-bridge def/patch deployed the same way (md5 c2823f28).
- 16:03 29d29cbc9d (spill fuel numbers; glow tank fix ab9c0eae13 inside) + now-committed FlowWorks_PitFluids.xml deployed
  (md5 acffbd1a); FlowWorks plan clean afterwards. Player.log after reload: 177 lines, no error/exception lines.

## Map C build
- 15:46 `--build --fresh-map`: 10/10 as staged, DB row built (no DB note), 38 sign books, 425 s. Soak movers: C4 (16 dug
  cells, the fluid_moves plot, fixer B intended) and C12 (a staged kennel Thrumbo wandered; later absent from the pawn list).
- Cleaned after: vanished a wild boar inside C3 and a wild muffalo; destroyed plants over every plot +6 and the DB row
  (giant RM_TheRot mushrooms hid the drawbridges; a paused destroy needs jawa/map_commit before the picture changes) and
  along z 0..12 (mushrooms over C3's dropped carry and C12's pits).

## Map R build
- 15:50 `--river --build --fresh-map`: tile 6758, map 9 (map C = 0); C1 at (161,87) FAIL only on RM_BankWeir (a
  Plant_Reeds at 171,127 refused wipeExisting=false) -> hand-built with wipeExisting=true + Scrapper style; C11 8/8;
  13/13 sign books. Vanished one wild muffalo near R1. map_r_placed.json committed (84cf60fdbf).
- CLOCK: the tiles are 94 deg of longitude apart (6.3 h). At map C 10:00 map R is 03:42 = black frames. Save b is pinned
  at map C 16:00 / map R 09:42 (both lit; captures checked).

## Stop 6 premise fix (storage tanks do not level; ponds + hose)
- C7 restaged (2ed874c986): two 4x4 dug ponds 2 m deep (HIGH full, LOW 1 notch) west of the plot, two Modern reels joined by
  a pipe (x=11), a hose from each onto its pond's lip; HIGH end Outflow, LOW end Capped (idle-stable). Three ground tanks
  stay as a SIZE look, not joined.
- Live (fresh map, C7 only): opening LOW (role Outflow) -> both reels read "Levelling: flowing", 10,000 dL per 250-tick
  cycle (HIGH 640000 -> 620000, LOW 160000 -> 180000 in 500 ticks). Full level at ~6,000 ticks (~2.4 in-game h).
- Traps: a hose needs >4 squares of straight lead-out ("no room for the straight lead-out from the nozzle" at 4); the
  scenario hose tuple's 5th field is the END LOOK (cap/nozzle), not the role; roles go through RM_LineProofs.ProofHoseRole.
- UX finding (for his eye): while levelling flows, the Outflow end still reads "Nothing drains here: needs a pump or a tank
  set to Dump" and the HIGH end flips from "beside deep water" to "lying free".

## Walk preview (one capture per stop)
- Script: Transient/pile_2026-10-22/walk_preview.py (runs each stop's goto, sizes the zoom to the rect, screenshot_cell_rect).
  19 captures in Transient/pile_2026-10-22/walk_preview/ (stopNN_*.png), all looked at on 29d29cbc9d.
- 11/11 stops land on their subject, lit, unfogged, nothing dead; hostiles = the two staged prisoners only (C7, C12).
- Stop 4: the TIMBER RAISED leaf draws nothing (ProofLeaf raised 3/3, no winch) -> filed TIMBER_LEAF_DIAGNOSE_UP_AND_INVISIBLE.
- Stop 6 re-proven on 29d29cbc9d: opening LOW -> 20,000 dL moved in 500 ticks, reels "Levelling: flowing"; then save b
  reloaded so the ponds stand unpoked (HIGH 640000 / LOW 160000 dL).

## Overflow toggle
- Global Mod Setting (not per map). Left OFF in save b and Mod Settings (read back False). Stop 11 turns it ON on map R
  and OFF after; commands in walk_tonight.md. Toggle proven live: set True -> get True -> set False -> get False.

## Redeploys after fixer commits
- c8eb3b2c83 (15:44), 8d6a1913ab (15:5x), 29d29cbc9d (16:03). Fixer G's asks on c8eb3b2c83: deep_lake_proof refill PASS
  (noted on DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE); raid_trench depth 8 RAID_FILL_CAUSEWAY FAIL but SITE-disturbed (Mechanoid
  lord, colonists shot across) -> noted on CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP, calm rerun owed.
- 16:13 d84d296f3d, 16:26 195c2fe9bc: Transient/pile_2026-10-22/walk_redeploy.sh (committed DLL pair from origin/main only,
  relaunch, reload b, Player.log scan): 0 error lines each; stops 1 + 6 re-checked (ponds unpoked 640000/160000); b re-saved
  in place 16:15 and 16:27 (original md5 unchanged).
- 16:29 4d833ad1bd (sheet/glow/fire review fixes): redeployed, 0 log errors; stop 11 REHEARSED on it: the staged plot never
  spills by itself (S0 held open 1 h, ledger in=0) -> stop 11 now spills 40,000 dL via ProofSheetSpill (29 wet squares);
  overflow set back OFF (read back False), b reloaded and re-saved 16:31.

## Final state
- (see the last lines of this file)
