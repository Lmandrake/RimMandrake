Fresh read-only Opus call; provenance evidence/broaden_call.json, exact input evidence/broaden_input.txt, envelope evidence/broaden_raw.json.

I found no stale-route path in the production default, but the regression coverage is thinner than the repair. The null-lay drop has no test, and none of the behavioural tests is a drop where the dropped hose actually crossed another. This is not an acceptance verdict.

Paths are relative to `/home/mandrake/rm/scratch/BENCH/fw-drain/src/RimMandrake/FlowWorks/Source/`.

## What production does (LegacyFrame off)

- **Default.** `LegacyFrame` is a plain static that starts `false`. The only thing that sets it is the `FrameLegacy("1"/"0")` static-call hook (`Hose/RM_MapComponent_Hoses.cs:100-106`), and no settings or other code set it.
- **Three drops in DrawAll**, all written as `!LegacyFrame && meshes.ContainsKey(r)`:
  - Carried with a trail: drop before `DrawCarrying` (`:1636`).
  - No lay (`lay == null`: instant or automatic reel-in, stored, or carried with an empty trail): drop (`:1646`).
  - Retracting: drop after `EnsureLay`, before the cache lookup (`:1670`).
- **DropMeshes clears the index.** It removes the cached meshes, calls `crossIndex.Drop` and destroys the stub mesh (`:1794`). `Drop` then marks every strand whose box meets the dropped one as dirty (`HoseCrossShadows.cs:108-113,123-131`).
- **A retracting hose never re-caches.** Its key is forced to null (`:1721`), so nothing is written back to the cache (`:1741`). Nothing on the mated-end path writes the cache either, since that path only fills in key and points (`:2483-2507`).
- **Ungated drops.** A re-lay landing (`:1070`), `Deregister` (`:183`) and `MapRemoved` (`:164-165`) drop whatever `LegacyFrame` is. The index is filled at mesh build (`:1745`) and in DrawCrossShadow (`:1875`) whatever `LegacyFrame` is, and so is the rank marking (`:2089`).
- **What the index keeps in line.** At the end of each production frame the index's strand ids equal the cache's keys. Every cached entry belongs to a laid hose that is drawn with a cache key: not carried with a trail, not retracting, not without a lay.

## Revealing scenarios

1. **The finding's own case, carried.** An older lower hose L crosses a newer upper hose U. Pick L up and walk away. *Expected:* L's cache and index entry are dropped on L's first draw visit, U becomes dirty, U's spans no longer include L, and U's crossing shadow mesh is rebuilt empty. Only row7 covers this, as a text check.
2. **Instant or automatic reel-in.** `ReelIn` and `Retract` null the lay (`Hose/CompHoseReel.cs:765-775`). This also covers a retracting hose with no winder, which reels in immediately (`:693`). This runs through the null-lay drop at `:1646`, which **no selftest anchors**. Row7's helper looks for the same drop text, but only the first copy after the carry branch, so deleting `:1646` passes rows 7, 8 and 9.
3. **Retracting lower.** U stops shadowing L for the whole wind. This is a deliberate loss of a real shadow, stated in the comment at `:1666-1669`. The remaining part of L gets no shadow either. Treat it as an accepted behaviour change, not a regression. A retracting hose *as the upper* casting no crossing shadow is older behaviour: the null key already skipped DrawCrossShadow at `:1760`.
4. **Active lower kept (the positive case).** U crosses an active lower A and also L. Carry L. *Expected:* U's spans equal the all-pairs spans against {A}, which is not empty. Nothing tests "drop one lower, keep the other".
5. **Ranks shift because L left the layering.** L's lay goes null, which changes the layering key (`:2083`), which calls `RanksMoved` and changes U's or A's rank. If A's end fitting rested on L (rule 3), A's rank relative to U can flip, so U's shadow on A should appear or disappear. HX3 swaps ranks but never at the same time as a drop.
6. **Carry and set down again at the same place.** After the re-lay lands, L gets a new build serial, so U's shadow comes back next frame. Row9 covers legacy keying; HX3 covers index re-lays. Nothing covers drop followed by a fresh Set.
7. **Order within a frame (one-frame limit).** The draw walk rotates (`:1619`). If U is visited before L in the pickup frame, U's check still sees L: one stale frame. U is marked dirty by the drop and rescans next frame. A re-laid L has the mirror case: one frame with its shadow missing. Nothing documents or tests this.
8. **Deferred crossing budget.** After the drop, U is pending, but if `crossSpent` is over budget, U keeps drawing its **old** shadow mesh with L's phantom (`:1878-1882,1909-1910`). The probe read of U's crossing spans (`CrossSpansOf`, `:123`) also still reports L's spans. Rotation plus "always at least one scan" bounds the lag. HX5 proves Pending is exact and the queue drains, but only for a re-lay wave, never for a drop.
9. **Turning LegacyFrame on and off.**
   - On, then carry L: the phantom shadow appears. That is the intended pre-fix comparison, because the legacy path walks every cached hose (`:1899-1906`).
   - Then off: the first production frame drops L, with the scenario 7 order lag.
   - This recovery only works because index filling and rank marking are ungated. HX4 checks rank marking is ungated, but **not** that the index Set at `:1745` stays ungated.
10. **Hose drawing skipped** (settings disabled, world map showing). The cache persists, and changes of state happen without any draw. On the first frame back the drops catch up (lay null, carry or retract). Low risk; same order limit.

## Existing coverage

**Strengths**
- Rows 7 and 8 (`SelfTest/HoseCarryChecks.cs:235-285`) pin the carry and retract drop lines in position, with tests that are shown to fail when the line is removed.
- Row9 (`:287-314`) pins legacy crossing keys to build serials.
- HX4 (`SelfTest/HoseCrossShadowChecks.cs:281-293`) pins DropMeshes→`crossIndex.Drop`, Clear on map removal, and ungated rank marking.
- HX1, HX2 and HX3 show the index spans equal the all-pairs spans across lays, rank swaps and one Drop. HX5 covers Pending and draining under the budget.

**Gaps**
- Rows 7 and 8 only check source text. They don't check how the cache behaves.
- No check on the null-lay drop at `:1646` (scenario 2).
- HX3's drop tail (`:212-223`) drops `ids[0]` without asserting it was anyone's lower. It may test nothing, and it would not reject a `Drop` that skips `MarkNear`.
- No check that a drop clears an upper's spans while keeping a still-active lower's shadow (scenario 4).
- No test of a drop combined with a rank move (scenario 5), with the order lag (scenario 7), or with budget deferral (scenario 8).
- No pin that `crossIndex.Set` at mesh build stays ungated (scenario 9).
- The frame-level match between index and cache is never checked offline; the DrawAll loop needs Unity and Verse.

## Smallest useful controls

1. **Null-lay row (text check).** Inside DrawAll, anchor the gated `DropMeshes` between `if (lay == null)` and `lastDraw[r] = "none"`. Add a failing variant that deletes it. Anchor on `lay == null` so row7's matching string can't satisfy it.
2. **Index drop test (Verse-free).** Strands L (rank 0) and A (rank 1) both cross U (rank 2).
   - Check U: spans are not empty and cover both crossings.
   - `Drop(L)`: assert `Pending(U,2)` is true, the next Check returns true, and the spans equal the all-pairs spans against {A}, not empty and different from before.
   - Failing variant: skip the Drop, and the spans still differ from the all-pairs result.
3. **Drop and rank move.** Same fixture, plus compacted ranks after the drop and `RankMoved` on the ids that moved. Assert U's spans equal the all-pairs spans with fresh ranks. Add one variant where A's rank flips above U.
4. **Order lag.** Within one simulated frame, Check U and then `Drop(L)`. Assert U is stale that frame, `Pending` is true, and U is clean the next frame. Lag ≤ 1 frame.
5. **Drop under budget.** Same as HX5, but with Drops instead of Sets and one scan per frame. Assert stale spans persist only while Pending stays true, and that it drains to the all-pairs spans.
6. **Re-lay after drop.** `Drop(L)` then `Set(L, sameRoute)` restores U's spans. `Set(L, movedRoute)` makes them follow the new route.
7. **Toggle pin (text check).** All three DrawAll drops are gated identically on `!LegacyFrame`, and the `crossIndex.Set` at mesh build is *not* gated.

## Limits to keep explicit

- **LegacyFrame on** deliberately reproduces the pre-fix phantom shadows. Don't count that as a production regression.
- **Accepted limits:** one stale frame from walk order, a stale mesh lasting several frames under the crossing budget, and no shadow on a hose while it winds.
- **Live, still unverified:** the shadow actually disappearing in a running game, and the cache and index matching at the end of each frame.

Maker action: add complete production draw/drop/cross-method extraction against explicit engine boundaries, with both visit orders for carry/null-lay/retract, nonempty surviving active lower oracle, destroyed meshes and index state, dirty budget recovery, rank/toggle and same-key relay. Preserve order/budget lag as explicit limits. These tests exceed source-only guards without modifying shipping logic. Staged original-behavior and index mutation controls will prove sensitivity before final standard runner.

Observed: focused3 passed 10 Cases (nine production-body HS scenarios plus HX4) and HoseCarryChecks41/41. All eight staged controls compiled and failed behavioral assertions; originals were restored byte-exact. Final stock runner ran fresh, PASS1/1; main1287/1287, hose188/188 checks and457/457 assertions. Full independent content readback is evidence/verification.json. Order/budget lag and retraction omission remain explicit; no shipping fix was needed.
