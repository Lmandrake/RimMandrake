# WEIR_WASH A2 proof hook — progress (BENCH builder, 2026-10-15)

Item: `WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST` · A2 (L2): "live breach with no placeable strand room leaves the
held catch spawned on the map, not lost". A1 (L1, offline WashHeld with fake things) passed 2026-10-11.

## Why A2 is unmeasurable today
`RM_Building_BankWeir.WashCatch` despawns each held stack, then `GenPlace.TryPlaceThing(.., strand, Near)`; on
failure `RM_RiverMath.WashHeld` respawns it at its old cell. The engine's Near search (rimsage `GenPlace.TryFindPlaceSpotNear`)
scans `NumCellsInRadius(12.9)` cells and only fails when EVERY cell is Unusable. The stack's own old cell is
emptied by the despawn and lies within a few cells of the strand, so a real "no room" cannot be staged on a map:
the old cell always accepts it. The existing `ProofBreach` only reads "heldAfter < heldBefore" (the happy path).

## Hook design
- Seam: `internal static Predicate<IntVec3> washPlaceValidator` on `RM_Building_BankWeir`, passed as the
  `extraValidator` of the wash's `TryPlaceThing`. Null in play (identical behaviour). With `c => false`,
  `TryFindPlaceSpotNear` returns false and `TryPlaceThing` returns false with no Log.Error, the exact engine
  outcome of no room.
- Probe: `RM_RiverWorksProofWorks.ProofBreachNoRoom` spawns a weir + 10 potatoes on its bank, snapshots
  `HeldCatch()` (positions, units), sets the validator (counting calls) around one `Breach()`, clears it in a
  finally, then reads every held thing back.
  `NOROOM asked=Q held=N spawned=S atOld=A unitsBefore=U unitsAfter=V breaching=B at=C`.
  `asked=0` (no strand found, nothing despawned) returns an UNMEASURED line, never a pass.

## Changes (cc964dd4a4)
- `src/RimMandrake/FlowWorks/Source/Rivers/RM_Weir.cs` — the seam (+6 lines, one call-site arg).
- `src/RimMandrake/FlowWorks/Source/Rivers/RM_RiverWorksProofWorks.cs` — `ProofBreachNoRoom`.
- `src/RimMandrake/FlowWorks/northstar/extensions_rivers.py` — row `works/breach_wash_no_room_keeps_catch`
  (toggle breachWashesCatch) with PROVE/EXPECT/LIES comment.
- DLL + .srchash rebuilt (winbuild 0 warnings 0 errors).

## Build / selftests / review
- `run_selftests.py --only` selftest_flowworks_stock.py, selftest_flowworks_rivers.py, northstar/selftest_extensions.py: 3/3 PASS.
- `extension_proof.py --list` shows the new row under `works`.
- Full-file review of all three files: nothing found; mark-clean at cc964dd4a4.
- NOT done: `src/RimMandrake/Utils/modcheck/required_checks.json` was already stale before this change (GSS
  M20a-d checkout rows, FlowWorks tank_loop_pour_in, several script_shas); a rebuild would also have baked in
  Pyrelands' uncommitted validation.py (another builder's in-flight work), so it was left as committed. The next
  rebuild picks up `works/breach_wash_no_room_keeps_catch`.

## Live proof owed
Bridge held, FlowWorks DLL deployed, a `river_site.py` map:
`python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river --chains works | tr -d '\r'`
or the single call `jawa/static_call type=RimMandrake.FlowWorks.Rivers.RM_RiverWorksProofWorks method=ProofBreachNoRoom args=-`.
PASS bar: asked>0, spawned = atOld = held > 0, unitsAfter = unitsBefore, breaching=True.
Can-fail: deleting the respawn branch in `WashHeld` leaves the stacks unspawned, so spawned=0 and the row FAILs.
