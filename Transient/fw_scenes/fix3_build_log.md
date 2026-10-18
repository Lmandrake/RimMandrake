# fix3 build log — FOUNDRY offline (scratch clone /home/mandrake/rm/scratch/FOUNDRY/fix3), 2026-10-18

Items: SWIM_DUG_RESERVOIR_FIX_PAWNS_CANT_ENTER, SWEEP_PRISONER_FIX_NEVER_RETURNS, HOSE_LEFTOVER_FIX_FULL_CANAL_LOSS.
Source: `Transient/fw_scenes/live_day3_report.md` bugs 1-3. No bridge, no game.

- [x] 0 clone (origin e23ef031a), root causes read
- [x] 1 SWIM dug reservoir: fix + SelfTest
- [x] 2 SWEEP prisoner: fix + SelfTest + returns_home row
- [x] 3 HOSE leftover: fix + SelfTest
- [ ] 4 SelfTest / oracle 3000 all modes / vv_shipped_matrix / run_selftests --only
- [ ] 5 commit, fetch, winbuild, publish

## Stages
- 0 root causes:
  - SWIM: the climb rule (pocket grid, cliff masks, RelativeVeto, step cost) reads `ClimbDepthAt` = the HOLE depth and
    never the water in it, so a brim-full 3 m reservoir (6 notches) is a sheer 6-notch drop for a person (K=2): masks
    close the lip, RelativeVeto says CanReach false. The swim path cost and the deep-swim set (`IsSwimTerrain`) read
    natural deep TERRAIN only, so a dug cell reads `deepCell=False`, and its cost is the wet-pit planning cost 300.
  - SWEEP prisoner: not the river. Vanilla `JobGiver_PrisonerEscape`: a prisoner whose district touches the map edge
    escapes; standing ON the edge it exits at once (`Pawn.ExitMap` -> PassToWorld, status left Prisoner, unbooked).
    Live: gone at tick 250 (the river took the others at 500), still Prisoner, off map, book 2 for 3.
  - HOSE: the drain lands on the full canal square; `PlaceInWater` and `PlaceNearby` (6.9 squares) find no room (canal
    full, intake pond farther), no filth lies on water, so the rest is the announced loss.
- 1 SWIM fix (source): `RM_SwimMath.DugSwimClimbDepth` / `ClimbDepthWithSwim` (Verse-free); Excavation keeps a derived
  dug-swim set (`RefreshDugSwim`, every 60 ticks + on the swim master's Reapply): `ClimbDepthAt` and `CopyClimbDepth` read
  a swim square at its water surface (pocket grid, cliff masks, RelativeVeto, falls, step cost); a change bumps the climb
  generation + swim grids, re-reads those path costs, clears reachability. `IsDeepSwimCell` and the swim offset grids
  include dug swim squares; the wet-pit planning prefix prices them at `swimPathCost`; RM_PitStepCost reads ClimbDepthAt.
  SelfTest case `SWIM_DUG_reservoir_swimmable_pits_keep_their_rules` (can-fail = live shape) ok; SelfTest 564/564.
  PondReturnChecks' two seam pins re-pointed (the seam starts from HollowDepthAt; only a swim square reads its surface).
- 2 SWEEP fix (source): Harmony prefix `RM_Patch_EscapeIntoCurrentIsSwept` on `Pawn.ExitMap`: a prisoner/slave of the
  player, not released, leaving from a cell the current carries pawns on (HasCurrent + IsCarried, current running,
  washOffMapEdge on), not caravan/teleport -> `RM_TakenByLand.Take(p, "river")` (held, booked, letter, walked home as
  captured), vanilla exit skipped only when taken. Rule: `RM_TakenByLandKernel.ExitIntoCurrentIsSwept`. No new setting:
  washOffMapEdge off = vanilla escape (PatchFeature label-only so a failed patch never turns edge washing off).
  SelfTest `SWEEP_PRISONER_escape_into_the_current_is_a_sweep` (prisoner + slave; can-fail = pre-fix unbooked exit).
  extensions_rivers.py returns_home stages a Prisoner and a Slave on the last two edge cells; each that leaves must be back
  on the map, same pawn/faction, guest status read back. selftest_extensions PASS (+3 fake shapes: back PASS, never back
  FAIL, back as Guest FAIL).
- 3 HOSE fix (source): `RM_LiquidSpill.PlaceAnywhere` after PlaceNearby, before the announced loss: every dug square and
  every pond body of the liquid's kind on the map, nearest first (Verse-free `RM_LevelPour.PlaceNearestFirst`); the
  intake pond is the common home. Truly nowhere (no room anywhere) stays the announced loss in litres. Dry-ground filth
  order unchanged (owner question open on HOSE_LEFTOVER_FIX_NO_VANISHING_LITRES). Not changed: the pump still lifts a
  level into the hose over a full canal (now conserved on drain). SelfTest `HOSE_LEFTOVER_full_canal_goes_to_the_nearest_home_with_room`.
- SelfTest 566/566; winbuild FlowWorks compiles 0 warn 0 err (dirty tree, not committed). Running oracle 3000 next.
- oracle 3000: 9 modes PASS 3000/3000, 0 FAIL. Running vv_shipped_matrix --skip-ep.
- vv_shipped_matrix --skip-ep: VERDICT PASS; SHIPPED kernel_fuzz 0/10000, fills 0/10000, surface 0/1000, seq_* 0, hose 0/2798, trail 0/1500; OFF_edgeSinks kernel_fuzz 142/2000 (known); control 194/2000. SHIPPED-hook suite 23 authored-tuple kernel cases (none of mine).
- run_selftests --only (22 FlowWorks python + settings): 20/22; reds not mine: selftest_review_map (evidence precondition: flow_spreads now 'partly'), selftest_settings_screens SWBestiary#BeastMechanics (known, not FlowWorks). Committing source.
- merged on origin 33461177a -> source 47b1a5045; winbuild there 0 warn 0 err; SelfTest 566/566 passed on the merged tree. Committing DLL + push.
