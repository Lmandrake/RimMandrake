Eight findings below. These are source findings; the suggested checks have **not** been run. Locations use exact code-line anchors, as permitted, rather than uncertain line numbers. Paths are relative to `Source/Hose/`.

**F1 — MEDIUM — Missing length-version key is treated as the current version**

- **Where:** `RM_HoseSettings.cs`, `ExposeData()`:
  `Scribe_Values.Look(ref maxLengthDefaults, "hose_maxLengthDefaults", HoseMath.MaxLengthDefaultsVersion);`
- **What happens:** The documented legacy value is **0**, but an absent version key receives the current version before `MigrateMaxLength` runs. A legacy configuration containing length 30 and no version marker therefore loses the information needed to distinguish the old default from an intentional setting.
- **Repro:** Load a settings fixture containing `hose_maxLength=30` without `hose_maxLengthDefaults`.
- **Suggested check — offline:** Deserialize that fixture and assert migration to 40; separately verify that a current-version intentional 30 remains 30. Use the actual `MigrateMaxLength` implementation.
- **Confidence:** **Medium**; the incorrect missing-key default is visible, but the migration helper and legacy importer are outside this slice.

**F2 — HIGH — Disabling automatic resume also disables fresh gizmo orders on dropped hoses**

- **Where:** `HoseCarry.cs`, `HoseOrderRules.MayResume()`:
  `pending != HosePendingOrder.None && (carry != HoseCarryState.Dropped || forced || autoResumeDropped);`
  `CompHoseReel.cs`, `OrderMove()`:
  `pending = HosePendingOrder.Move;`
- **What happens:** A fresh order does not distinguish itself from an interrupted order. `OrderMove` and `OrderRetract` leave a dropped hose in `Dropped`, so ordinary hauling rejects the newly requested work whenever automatic resume is off. The setting promises that the end waits until the player orders it, but the reel’s own order buttons cannot restart it. Forced float-menu jobs bypass the problem.
- **Repro:** Disable automatic resume, interrupt a deployment, then use the reel’s **Move hose end** or **Retract hose** gizmo.
- **Suggested check — offline:** Exercise fresh Move and Retract orders from `Dropped` with automatic resume disabled. Assert that fresh orders are eligible while an untouched interrupted order remains suspended.
- **Confidence:** **High**.

**F3 — HIGH — An accessible loose end cannot be ordered moved when its reel is inaccessible**

- **Where:** `Jobs/FloatMenuOptionProvider_Hose.cs`, `Blocked()`:
  `if (!p.CanReach(reel, PathEndMode.Touch, Danger.Deadly)) return "no path";`
  Both pickup menu paths call `Blocked(...)` before `EndBlocked(...)`.
- **What happens:** Moving a laid end requires reaching the end and destination, but the float menu additionally requires reaching the reel. This contradicts `WorkGiver_HoseOrders.JobFor`, whose laid/dropped branch correctly checks the loose end instead. A wall, locked access, or depth separation around the reel disables an otherwise executable forced pickup.
- **Repro:** Deploy a hose outside a room, seal access to the reel, and right-click the accessible loose end with a pawn outside.
- **Suggested check — cheap live read:** Read reachability to reel, end and destination; then compare `JobFor(..., true, ...)` with the menu’s blocked reason. Expected fixture: reel unreachable, end/destination reachable.
- **Confidence:** **High**.

**F4 — MEDIUM — Destination validation uses a different arrival mode from execution**

- **Where:** `Jobs/WorkGiver_HoseOrders.cs`, `JobFor()`:
  `if (!pawn.CanReach(dest, PathEndMode.Touch, d)) ...`
  `Jobs/JobDriver_CarryHoseEnd.cs`, `WalkEndMode()`:
  `return Dest.Standable(pawn.Map) ? PathEndMode.OnCell : PathEndMode.Touch;`
- **What happens:** The order accepts adjacency reachability, then requires entry onto a standable destination. Wherever touching a cell is possible but entering it is forbidden, the pawn can collect the hose before the actual walk fails. `OnFinish` then drops the end and cancels the order. This is especially relevant to the mod’s depth-boundary restrictions.
- **Repro:** Order deployment onto a standable cell across an entry restriction that permits reaching its edge.
- **Suggested check — cheap live read:** First establish a fixture where `CanReach(dest, Touch)` is true and `CanReach(dest, OnCell)` is false. Confirm that `JobFor` currently accepts it. Validation should use the same arrival-mode decision as the driver.
- **Confidence:** **Medium**; the mismatch is definite, but the particular depth fixture needs confirmation against the unseen reachability patches.

**F5 — MEDIUM — Failed forced-job submission leaves the new shared order queued**

- **Where:** `Jobs/FloatMenuOptionProvider_Hose.cs`, `TargetThen()`:
  `HoseJobs.GiveForced(p, j);`
  The retract callback likewise ignores its result. `HoseJobs.GiveForced()` returns:
  `return p.jobs.TryTakeOrderedJob(j, JobTag.Misc);`
- **What happens:** The targeter saves and restores the previous order when `JobFor` rejects construction, but does not restore it when actual submission returns false. A failed instruction to one selected pawn can therefore become an autonomous order for another colonist, and an existing order has already been overwritten.
- **Repro:** Start the targeter, make the selected pawn unable to accept the ordered job before committing the target, then click. The relevant failure is `TryTakeOrderedJob` returning false.
- **Suggested check — offline:** Extract the submission transaction behind an injectable issuer. Return false and assert restoration of both `pending` and `pendingAt`; cover carry and retract callbacks.
- **Confidence:** **High** for the unchecked failure path; **medium** for its frequency during ordinary play.

**F6 — MEDIUM — Interrupting winding reels in more hose than the pawn actually wound**

- **Where:** `HoseCarry.cs`, `HoseTrail.ShortenBy()`:
  `while (Cells.Count > 1 && PulledLength(w) > target + 1e-9) Cells.RemoveAt(Cells.Count - 1);`
  `CompHoseReel.cs`, `StopWind()`:
  `t.ShortenBy(wound, w);`
- **What happens:** Winding progresses fractionally, but interruption removes whole trailing cells until the length falls below the target. It discards the unwound remainder of the final segment. Repeated cancellation and restart therefore retracts faster than the configured winding rate, particularly at low speed or low Manipulation.
- **Repro:** Begin retracting a straight hose at low winding speed, cancel immediately after one winding update, and repeat.
- **Suggested check — offline SelfTest:** On a straight trail, call `ShortenBy(0.1, w)` where the final segment is one cell. Assert that the remaining length decreases by 0.1, rather than a whole cell. Preserving a fractional endpoint or winding remainder would avoid the excess.
- **Confidence:** **High**.

**F7 — MEDIUM — A short visible hose can retain a large trail and cause quadratic interruption work**

- **Where:** `HoseCarry.cs`, `Step()`:
  `Cells.Add(c);`
  Length acceptance uses `PulledLength(w)`, rather than bounding retained history. `ShortenBy()` repeatedly recomputes that length while deleting cells.
- **What happens:** In open ground, pulling taut reduces a long walked trail to approximately mouth-to-end distance, but the original cells remain stored. Repeated moves through distinct nearby cells can accumulate hundreds or thousands of entries within a 40-cell hose’s radius. Carry steps repeatedly copy/scan that history; interrupting winding can perform quadratic work when many trailing cells must be removed.
- **Repro:** Move the same end through a non-self-intersecting serpentine route inside a nearby open square, then retract and interrupt it.
- **Suggested check — offline SelfTest/perf:** Build a serpentine trail whose taut length remains below 40; compare 100, 400 and 1,600 cells. Measure retained count and `ShortenBy` work. Include a route ending near the mouth so shortening removes most of its history.
- **Confidence:** **High**.

**F8 — MEDIUM — Coupling to native equipment gets the plain set-down time**

- **Where:** `Jobs/JobDriver_CarryHoseEnd.cs`, `SetDownTicks()`:
  `bool couples = comp != null && Dest.IsValid && comp.RelayAt(r, new RimMandrake.Shared.Slack.Cell(Dest.x, Dest.z)) != null;`
  `return couples ? HoseJobTuning.coupleTicks : HoseJobTuning.setDownTicks;`
- **What happens:** Only another reel qualifies as a coupling. A native tank, pipe or machine connection takes the plain 30-tick set-down time instead of the advertised 90-tick coupling time. The handling-setting tooltip explicitly describes the latter as time spent screwing the end on.
- **Repro:** Compare deployment onto a relay intake with deployment onto a native tank/pipe coupling at handling time 1.
- **Suggested check — cheap live read:** Read the destination’s resolved port and the set-down toil’s `defaultDuration`; expect 90 for both actual couplings and 30 for a loose end.
- **Confidence:** **High** for the timing difference; **medium** for the intended native-coupling timing interpretation.

## Outside this slice

The following were referenced but not supplied:

- `RM_MapComponent_Hoses`, including registration, holder scheduling, geometry rebuilding, relay caches and `RelayVersion` consumers.
- `RM_HoseLinks`, `RM_LiquidNet`, its kernel, topology invalidation and route revalidation.
- `RM_LiquidSpill`, `RM_HoseHold` and committed-transfer callers. Consequently, liquid conservation during winding, dropping, disabling hoses or removing maps cannot be established here.
- `HoseMath`, `HoseLive.CacheFresh`, geometry/world helpers, `HoseStateMachine` and tint continuity logic.
- `RM_HoseLegacy`, the enclosing settings lifecycle, Harmony patches, hose/job/workgiver XML and multiplayer synchronization registration.

No definite cross-save static-table leak or liquid-loss finding is established by these files alone. All supplied file blocks appear complete; `known_behaviours.md` explicitly contains truncated ledger heads, rather than unexpectedly truncated source.