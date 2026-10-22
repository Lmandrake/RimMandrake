# drawbridge pair night — 2026-10-21 (BENCH helper)

## 1. WINCH_REACH_DIAGNOSE_CANREACH_FIBS
- status: starting

## 2. DRAWBRIDGE_RAID_DIAGNOSE_LOITERING_AT_MOAT
- status: pending

## 3. hostile-arrival tick-stop interference item
- status: pending

## bridge / tier / ModsConfig
- pending

### item 1 progress
- claimed; FindPathNow(Touch, Deadly) gate added in JobOnThing after reserve checks; built; deployed (md5 132d2f8d both); committed 93cdbdc40a (pre-publish sha). Next: live LOWER_ONLY_FROM_WINCH.
- live 1 (fresh map): UNMEASURED/SITE — path precondition found=True. Probe: staged+read while PAUSED, the 1.6 pathfinder had not seen the new walls/depth; after 10 ticks found=False and farLower job=False (fix). HARNESS fix: ctx ticks(10) after build and after DevSet raise. Lesson filed.
- live 2: LOWER_ONLY_FROM_WINCH PASS (farLower job=False why=refused_at_winch,refused_at_far; winchLower job=True; farRaise job=True). Transient/pile_2026-10-21/drawbridge_winch_reach2.json
- item 1 CLOSED at 93cdbdc40ac1 (harness 7e904f09852e). Full drawbridge run after fix: 11/12 PASS, RAID_UP separate (Transient/pile_2026-10-21/drawbridge_all_after_fix.json).

## 2. RAID_UP progress
- run1: SITE — sapper island (dx=-60) outside the prepared rect, its steel bridge refused; gunners chased start colonists + a wild RM_Ssurr. (One attempt also hit GovernorStop threat_structure: dormant Hive on the fresh map.)
- fix: per-variant ProofResetRect+prepare_site, vanish every non-island non-hostile pawn, tick 10 settle, teardown (kill hostiles, destroy buildings) after each variant.
- run2: sapper lord went 60 cells to the assault island (bridged by plank+ladder) = contamination -> teardown added.
- run3 (clean sites): assault OK (RM_RaiderSetLadder seen, reached ring). sapper FAIL: WinchJobs 0; trash/AISapper-style AttackMelee on anchor/deck, CrossTrench ladder jobs. Instrumenting ProofDecision + NearestRaisedWinch per raider.
- run4: ProofDecision showed moat uncrossable + NearestRaisedWinch found, yet WinchJobs 0 -> vanilla gives Sapper duty only to IsGoodSapper pawns; Mercenary_Gunner never qualifies (HARNESS). Fix: Grenadier_Destructive, Mining 20, frag grenades if needed, IsGoodSapper SITE check; refusals of left-map raiders / disabled mining marked _answer.
- run7 --only RAID_UP: PASS (assault ladder+plank, PlanksLaid 1; sapper WinchJobs 12, AttackStatic on winch). Full run: RAID_UP FAIL from other rows' buildings being trashed -> clear origin-plot buildings before each variant. Final full run 12/12 PASS (Transient/pile_2026-10-21/drawbridge_all_final2.json). Item CLOSED at d722e97f1170.
- Note: one full run had WINCH_LOST_CRASHES UNMEASURED/HARNESS ("no health block" after the crash: victim likely killed, list read lacks health); passed on the rerun. Not fixed.

## 3. interference item
- Filed TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM (lines/drawbridge preflights never call validation_core.site_calm; Trispike at arm 02:49Z, dormant Hive at arm 03:04Z). Earlier hive/arrival items are closed and covered other scripts.

## bridge / tier / ModsConfig
- game closed (PID 24308), stamped down; ModsConfig restored 325 mods md5 3ad3f33d; bridge released. Player.log 0 exceptions (copy drawbridge_pair_Player.log).
