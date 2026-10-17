# RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS build log (FOUNDRY offline, scratch clone)

- [ ] 1 root cause
- [ ] 2 fix (C#)
- [ ] 3 offline tests (SelfTest + kernel mock)
- [ ] 4 extensions_rivers.py returns_home asserts
- [ ] 5 SelfTest / oracle 3000 / vv_shipped_matrix / run_selftests --only
- [ ] 6 commit, fetch, winbuild, publish

## Stages
- 1 ROOT CAUSE (RimSage, vanilla 1.6): RM_TakenByLand.Take -> policy.Remove -> WorldPawns.PassToWorld -> AddPawn ->
  Pawn.Notify_PassedToWorld: a pawn of the PLAYER faction (or factionless humanlike) whose WorldPawns.GetSituation is
  Free gets SetFaction(random non-colony humanlike faction). KeepForever does not change the situation (still Free).
  So every held colonist (and tamed animal, and slave) was handed to TradersGuild/Pirate/Outlander on the way OUT; the
  return spawned the same pawn object with the NPC faction. Also: Free world pawns are redress candidates (PawnGenerator).
- 2 FIX written: RM_TakenByLand.Take holds the pawn id (RM_TakenHoldSet) BEFORE policy.Remove; Harmony postfix
  RM_Patch_TakenPawnNotFree turns a held pawn's Free situation into ReservedByQuest (no faction swap, no redress, no
  quest picks); record captures faction/host/guestStatus; Return releases, restores (Restore) before spawn; old records
  with no capture and wasPlayer -> SetFaction(OfPlayer). Covers the gale too (same service).
- 3/4 tests written: SelfTest TakenIdentityChecks.cs (mock take/return, can-fail = live result); selftest_river_site.py
  returned_same_pawn checks (0 failures); extensions_rivers.py returns_home asserts identity+faction+gear per swept pawn.
- 5 running SelfTest (selftest_flowworks_stock.py) 15:27
- 5 SelfTest 533/533 (4 new RIVER_SWEEP cases ok); winbuild compile check 15:30
- 5 winbuild OK (0 warn 0 err); oracle 3000 all modes 15:30
- 5 oracle 3000: 8 modes PASS, 0 FAIL; vv_shipped_matrix --quick? no: full shipped 15:32
- 5 vv_shipped_matrix --skip-ep: SHIPPED all families 0 (kernel_fuzz 0/10000, fills 0/10000, hose 0/2798...), control 194/2000; VERDICT FAIL only on known AUTHORED Thirst_slime_last_resort_ruled; OFF_edgeSinks kernel_fuzz 142/2000 known. run_selftests --only 15:40
- 5 run_selftests --only river_site/extensions/flowworks_stock: see commit msg (fixed extensions fakes to answer pawn_get; new turns_npc can-fail -> FAIL) 15:43
- 6 committed source d21e7ab33, rebased onto origin 0fe44a6ea -> bf1e344d1; SelfTest on merged tree 15:44
- 6 merged tree green (3/3 --only); fetch: origin unmoved; winbuild on bf1e344d1 OK; committing DLL + pushing 15:46
