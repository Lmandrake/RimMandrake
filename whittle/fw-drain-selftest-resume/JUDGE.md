# JUDGE — FLOWWORKS_SELFTEST_FIX_TWO_STRAY_REDS (selftest-resume)

I based this review on the actual source at HEAD `2c50b03192750395ce1f265208842d4d3284f305` plus its five uncommitted SelfTest edits, the history, and the raw run evidence. I did not use builder DONE/PAIRINGS conclusions as a basis.

## 1. Frozen statement bullets

**Bullet 1: the two original cases pass on current production source, keeping the pond unit-times-beds checks and the shared westward strip rim check. TRUE.**
- Raw output `evidence/final/csharp_stdout.txt:521` shows `ok    Pond_capacity_dug_out_and_back_in_any_order`, and `:769` shows `ok    PipeTankRiser_wiring_link_stops_layer_prints_flange_follows`.
- The published repair `4e9da327df` is an ancestor of HEAD and origin/main (`verification.json` `original_repair_ancestor`, `history.json` `repair_is_ancestor: true`). Neither guard file is in this run's diff (`source_diff.patch` changes only five other SelfTest files).
- **Pond check.** `DeepBedChecks.cs` still requires `Regex.Matches(st, "body.capacity = RM_BedMath.CapacityForBeds(unit, BedSum(body, owner));").Count == 3`. Current `RM_LiquidStock.cs` has exactly three such statements, at :455, :497 and :524.
  - What this pins: exactly three textual occurrences of that one resizing statement in that file.
  - What it does not pin: which methods they sit in (detach, reattach or ReleaseRect), method identity, or any capacity assignment written another way. The case also keeps its `levelUnit` and far-cell `owned.capacity += add` checks.
- **Westward strip check.** `ReelRiserShadowChecks.cs:265-266` requires both `return PrintStrip(this, sm, plan.Path, yTile + 0.001f);` and `if (LiquidJoinRule.TravelsWest(path)) { float sw = vr; vr = vl; vl = sw; }`. These match `Machinery/RM_LiquidJoins.cs:528` and `:540`, inside the shared `PrintStrip` at :534. Line :239 separately executes the production-linked `LiquidJoinRule.TravelsWest(plan.Path) == (dx < 0)`.

**Bullet 2: the five further guards are resolved against intended current behaviour with meaningful negative controls, and the complete relevant FlowWorks C# run passes. TRUE.** Two qualifications follow in §2.
- All five previously failing cases show `ok`:
  - `RiverSwitchFlip_weirWhiteWater` (:292)
  - `PitCapture_follows_a_held_pawn_that_moves` (:402)
  - `PipePole_P3_sag_at_the_slider_extremes` (:1128)
  - `LW1 … TakeLayWorld uses World(LayWorldMaxAge)` (:1201)
  - `Thirst_small_pond_drink_admitted` (:1271)
- Totals: `1238/1238 passed` (:1468), `hose: 188/188 checks passed` (:1473) and `hose: 455/455 assertions passed` (:1507). There are no FAIL lines and no unmeasured phrase.
- The wrapper reports `PASS 1/1 FAIL 0/1 UNMEASURED 0/1 CRASH 0/1`, `RESULT: GREEN` (`final/selftest_stdout.txt:8-9`), with receipt `returncode: 0`.
- Each change follows a real production refactor and adds can-fail text mutations (§2). The qualifications: the PipePole numeric checks run on copied math only, and two hose positive pins have no paired negative control.

**Bullet 3: the evidence identifies the original repair, the reason for each guard change, the exact tested sources and the actual output, and shipping behaviour and the approved GSS cord look are preserved. TRUE at source level; no fresh rendered proof (not required, since nothing rendered changed).**
- **Original repair.** `history.json` carries `4e9da327df` with its full diff.
- **Reasons for each guard change** (from `history.json`):

  | Guard | Production commit |
  | --- | --- |
  | Weir | `4a0f8616b7` WEIR_SPILL_REDRAW_ANIMATED_NOT_PAINTED |
  | Pit capture | `6d07391d3b` PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP |
  | GSS curve | `b05e9ce45d` "owner-approved cord look" |
  | Hose | `377557044b` (corridor versions) and `12c138bd76` HOSE_DIRTY_LIST_WIDEN_NO_OVERFLOW_REBUILD |
  | Thirst | `8fb9f7f2b6` (Pyrelands landing that introduced `Consider`) |

- **Exact tested sources.**
  - `final/integrity_before.json` and the receipt's `sha256_after` cover FlowWorks, GSS and shared sources, the runner scripts and the reference file. The receipt reports `source_test_hashes_unchanged: true`.
  - `pre_judge_integrity.json` reports `matches_proof_inputs: true`, `matches_tested_HEAD: true` and `changed_production_paths: []`.
  - `final/BUILD_SOURCE.json` shows `ev_start` and `ev_end` with the same SHA, the same five dirty SelfTest paths and the same token.
- **Shipping and GSS preservation.**
  - No production or GSS file is in the diff or among the dirty paths.
  - `GimmeSomeSlack/Source/Aerial/AerialMath.cs` is hashed at `019a9278…` and unchanged.
  - The only GSS-touching edit is a test-side read of the existing curve. The approved cord look's source is therefore byte-preserved, and no re-shoot is triggered.
  - This is source-identity proof, not a fresh pixel comparison.

## 2. The five guard/production pairings

**(a) Weir white water: `RiverSwitchFlipChecks.cs` vs `Rivers/RM_Weir.cs:705-710`. Change warranted.**
- Production now has `bool animate = RM_RiversSettings.weirWhiteWater; DrawSpill(map, animate ? frame : 0); if (animate) { DrawWhiteWater(...); }`. The doc comment at :686-687 states the intended off-state: no white water, and the crest frozen on frame 0.
- The guard scopes to the `DrawAt` body, requires exactly one `DrawWhiteWater(` and one `DrawSpill(`, and checks the exact gated sequence.
- Its four mutations are meaningful and each one is caught:
  1. ignoring the switch (`animate = true`)
  2. an unconditional `if (true)`
  3. an animated crest while off (`frame` instead of `animate ? frame : 0`)
  4. an extra unconditional white-water draw
- Limitation: this is a source-text check only. No drawing runs offline.

**(b) Pit capture pin: `RelativeRulesChecks.cs` vs `Superdeep/RM_PitRooms.cs:756-801` and `:817-860`. Change warranted.**
- The old `PawnUtility.ForceWait` pin was replaced by a dedicated `JobDriver_CaptureDownPinned.Pin`, because vanilla Wait auto-melees the warden standing at the lip (comment at :812-816). The JobDef exists (`FlowWorks_JobDefs.xml:46`, `RimMandrakeFlowWorks_DefOf.cs:33`).
- The guard is scoped to the `JobDriver_CaptureDown` class text. In both the reach toil and the hold refresh, it requires the Pin call inside the `Hold:` arm, before `Repath:`, exactly once.
- Mutations that are caught:
  - removing either pin call
  - moving the refresh into `Repath`
  - a helper that never calls `StartJob`
  - `expiryInterval = 1`
  - removing the already-pinned early return, the `FailOn` warden-job release, `StopDead` or `ToilCompleteMode.Never`
- These discriminate the real regression: reverting to a ForceWait pin would delete the Pin call and be caught.
- Unchecked: the downed/asleep `ForceWait` fallback branch at :829-835. The step logic itself (`RM_PitRoomMath.CaptureDownNext`) is production-linked math and still executes.

**(c) PipePole sag vs GSS curve: `PipePoleChecks.cs` vs `GimmeSomeSlack/Source/Aerial/AerialMath.cs:147-192`. Change warranted.**
- GSS replaced the `4t(1-t)` parabola with the flat-ended `Droop(t) = sin²(πt)` plus `SpanEndSamples`. This landed with the owner-approved cord look (`b05e9ce45d`), and the doc comment at :164-168 gives the kink rationale.
- The guard pins all of the following from whitespace-collapsed GSS source:
  - the exact `Droop` body
  - the `SpanTs` end-sample insertion and sort
  - the `SpanCurve` length-scaled sag
  - the per-sample `sag * Droop(t)`
  - the end clamps
- Seven replace-with-"0" mutations, plus restoring the old parabola, are all caught.
- **Flag: the numeric checks run on copied math only.** `CurveZ` re-implements sin² in the test. The 101-point symmetry/bound loop, the mid-span depth and the `endSlope < 1e-4` check therefore never call GSS code (AerialMath is not compiled into `RimMandrakeFlowWorks.SelfTest.csproj`).
  - `4 * SagMax > 0.2` only checks a constant.
  - The real link to production is the exact-text pin of `Droop`, which is strict. The slider math (`RM_PipePoleMath.SagDepth/ClampSag`) is production-linked.

**(d) Hose swim invalidation: `HoseMateEndQueueChecks.cs` vs `Hose/RM_MapComponent_Hoses.cs:248-263`, `:405-427` and `HoseWorldPatch.cs`. Change warranted.**
- The old bool `MarkDirty` with a `MapChanged()` fallback is gone. `HoseDirtyList` now holds the whole map (`HoseWorldPatch.cs:23,39`). `SwimCellsPublished` touches corridor versions unconditionally, returns if there is no current snapshot (the next read rebuilds whole), and otherwise marks each cell.
- The guard pins the touch loop, the snapshot early return and the mark loop as exact text. Removing either the `cv.Touch` or the `MarkDirty` statement is caught.
- **Flag:** the `MarkDirty` body (`dirty.Ensure…; dirty.MarkRect…`) and the `PatchWorld` check (`HoseWorldPatch.Patch(world, dirty, liveRule, maxCells)` plus `worldSerial++`) are positive pins with no paired negative control.
- Substantive backing comes from production-linked cases: `HoseWorldPatch.cs` is compiled into the SelfTest (csproj :192), and `HOSEPATCH_EQUALS_FULL_REBUILD_RANDOM_SPAWNS`, `…_DIRTY_HOLDS_WHOLE_MAP_NO_OVERFLOW` and `…_BOUNDED_BATCHES_EQUAL_FULL` pass (`final/csharp_stdout.txt:379-383`). The component wiring is still text-only.

**(e) Thirst small pond: `ThirstChecks.cs:80-110` vs `Thirst/RM_ThirstUtility.cs:480-580`. Change warranted.**
- Inside local `bool Consider(IntVec3 c)`, `return true` means "skip this cell, keep walking". Both loops (:552 and :575) `break` only on `!Consider(c)`. The affordability gate (:532-535) sits before the reach/forbidden test (:536) and before admission (`bestCell = c;` :540). So the original `continue` semantics are preserved.
- The guard is scoped to the 6-argument overload's body, then to `Consider`. It requires: the next statement after the gate starts `return true;`; the gate comes before `IsForbidden` and `bestCell = c;`; `ex` is declared before `Consider`; and exactly two `if (!Consider(c)) { break;`.
- Mutations that are caught:
  - no refusal at all
  - `return false` (premature search end)
  - admission before the gate
  - an inverted callback test
  - the gate moved after the reach check, where it would count toward the 40-reach-failure cap
- The economics are production-linked: `RM_ContainerMaterialMath.BodyAffords` and `RM_StockMath.CanDebit` are swept, and the `CanDebitTerrain` statement sequence is pinned.

**Reference recovery (Thirst_harmony_target_and_call_sites): warranted and in scope.**
- The first attempt printed `…decompiled Pawn_NeedsTracker.cs not on disk (D:\Luke\dev\reference\…) - the ShouldHaveNeed signature check was NOT run; UNMEASURED` (`evidence/csharp_stdout.txt:1288`). The wrapper then reported `UNMEASURED 1/1` (`evidence/selftest_stdout.txt:48-49`). That failure is preserved.
- The new `RIMWORLD_DECOMPILED` lookup (`ThirstChecks.cs:520-523`):
  - keeps the legacy `/mnt/d` default and the `D:\` fallback when the variable is unset;
  - does not fall back once the variable is set;
  - keeps the explicit UNMEASURED message whenever the file is absent (:528-532).
- `reference_provenance.json` shows `ilspycmd -t RimWorld.Pawn_NeedsTracker` run against the installed Steam `Assembly-CSharp.dll` (sha `5cf1b5be…`) and output sha `fa588681…`. The decompiled file contains `private bool ShouldHaveNeed(NeedDef nd)` (`reference/RimWorld/Pawn_NeedsTracker.cs:198`).
- `reference_windows_readback.json` shows Windows Python resolving the UNC path via WSLENV, `exists: true`, with the same sha.
- The final receipt records the same `RIMWORLD_DECOMPILED`/`WSLENV` and hashes the reference before and after (`fa588681…`).
- The final output has `ok Thirst_harmony_target_and_call_sites` (:1288) with no unmeasured line. Given the code, that means `File.Exists` was true and the `Contains` assertion executed and passed.
- The reference is evidence-local and deliberately unstaged (`expected_stage_exclusions`). I could not independently re-run the decompile.

## 3. Did the full relevant wrapper run on the stated sources?

Yes, for the offline FlowWorks stock C# suite.
- **Command:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_flowworks_stock.py --workers 1`, under strace.
  - Return code 0, elapsed 472 s, `tested_HEAD` `2c50b031…`.
  - Raw output was decoded from wrapper PID 109316 (`output_extraction.json`). The process samples show that PID as `selftest_flowworks_stock.py`, running git status and the stage rsync.
  - The `1238/1238 passed` and `455/455` writes appear in `selftest_output_writes.strace`, and the stdout sha matches `verification.json` `raw_output_sha256`.
- **Stage identity** (`final/stage_identity.json`):
  - `all_inputs_match: true`.
  - Staged `ThirstChecks.cs` is `b017c303…`, the post-change hash; the first attempt staged `95770c75…`.
  - The SelfTest DLL/exe/pdb mtimes (≈1794388173.9) fall inside the run window (1794388076 to ≈1794388548), so the binary was rebuilt from the final sources.
  - The only exclusions are `Preview.png` and the evidence reference. The first attempt's audit failure on `Preview.png` is preserved alongside the explicit exclusion in `stage_identity_verified.json`.
- **The `not recordable … changed during the run: selftest_flowworks_stock.py` line** (`final/selftest_stdout.txt:5`) is a cache-record refusal, not a test result.
  - `cache_record_refusal.json` rows cite `/etc`, `/home/mandrake` and `__pycache__` folder changes, a wall-clock read and external `/mnt/c` .dotnet paths.
  - The script's own hash (`1c4bc152…`) is identical before and after the run.
- **Not executed in this run, and not counted as fresh passes:**
  - GSS `AerialSelfTest`/`SittingChecks` (curve and end sampling)
  - the separate FlowWorks Replay project (`ReplayTick.cs`, `Replay.Sources.props`, `baseline.txt`)
  - any live game, map, job or pixel behaviour

  `verification.json` `supporting_tests_not_executed` says the same.

## 4. Issues and limitations

**Issues requiring repair before parent inspection:** none blocking.

**Non-blocking weaknesses the parent should know about:**
- The PipePole numeric curve properties run on a test-local copy of sin² (copied-math-only). Production fidelity rests on the exact `Droop`/`SpanCurve`/`SpanTs` text pins.
- The hose `MarkDirty` and `PatchWorld` assertions have no paired can-fail mutation. Behavioural backing comes from the HOSEPATCH production-linked cases, not from the component wiring.
- The weir, pit-capture, hose-wiring and thirst-search guards are source-structure pins. They catch the listed mutations but do not execute RimWorld jobs, drawing or search.
- The downed/asleep `ForceWait` fallback in `Pin` is unguarded.

**Remaining limitations:**
- The pond count pins three occurrences of one statement form in `RM_LiquidStock.cs`. It does not establish method identity or every capacity assignment.
- The GSS/shipping preservation claim rests on source identity: no production, GSS, art, deploy or ModsConfig file changed. There is no fresh rendered-pixel comparison to the approved crops, and none is triggered, since the look's source is byte-unchanged.
- GSS selftests, the Replay project and live play were not run here.
- The reference decompile provenance comes from receipts. I did not re-run it.
- Nothing is committed, published or closed. This review does not mark the code CLEAN; the parent alone publishes and closes.

would show: yes