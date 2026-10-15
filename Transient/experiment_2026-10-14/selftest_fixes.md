# Selftest fixes — nightly 427/435, four persistent failures (2026-10-15, BENCH)

Code commit: 06faddba44. Reruns via `run_selftests.py --only <test>`.

## 1. selftest_lint_harmony_targets.py — FIXED, 1/1
- cause: `RM_Patch_ConnectivitySource_Allocate` and `RM_Patch_PathFinderMapData_Dispose` in
  `src/RimMandrake/FlowWorks/Source/Superdeep/RM_CliffMask.cs` had no [PatchFeature] on purpose ("the masks must exist
  for every map"). The lint requires one on every PatchApplier class (all 3 asserts failed from these two classes).
- fix: label-only `[PatchFeature("Superdeep pits trap: cliff-mask bookkeeping")]`, the constructor PatchApplier
  offers for this case (it reports the failure and switches nothing off, like PipeLook's). No settings field: gating
  it on `superdeepCaptureEnabled` would be wrong, because the lifecycle must run while the feature is off. If Allocate fails,
  Swap finds no masks and hands out vanilla's array.
- rebuilt with winbuild.py FlowWorks (0 warnings); DLL + .srchash committed. Not deployed.

## 2. northstar_driver/selftest_lint_calls.py — FIXED, 1/1
- cause: the snapshot was stale. `jawa/health`, `jawa/health_profile` (JawaBenchHealthTools.cs) and `jawa/storyteller_comps`
  (JawaBenchStorytellerCompsTools.cs) are real committed [Tool]s.
- fix: regenerated with its own tool, offline: `tool_schemas.py --supplement-only ../../bridgetools/JawaBench.BridgeTools`
  (532 tools). The snapshot is not hand-edited. A `--live` refresh is still the better refresh when a bridge holder has one.

## 3. art/selftest_subject.py — FIXED (the test was provably wrong), 1/1
- cause: the live probe expected the render family `bluedesert_dorrak` as a column ref. Dorrak's renders (_south/_north/_east)
  are now installed in the art ledger at `Things/Pawn/Animal/RM_Dorrak/RM_Dorrak`, so resolve_art binds them as 3 `ledger`
  columns. By design (`bound_fams`, subject.py) a family already bound through the ledger is not repeated as a name-matched
  `render` column. The resolver is correct, and the probe predated the install.
- fix: the probe accepts the family from render/job refs OR from the ledger columns' jobs (FAM_RE-stripped). It still fails
  if no Dorrak art is found: an exact match, and `bluedesert_dorrak_dessicated` alone would not satisfy it.

## 4. rimflow/selftest_reader_invariant.py — KNOWN, filed: READER_BASELINE_REPAIR_OLD_ORDER_TRIPS (proposed, BENCH)
- re-measured 2026-10-15: the only diff is still old-order 8 errors vs new 7. The old order produces a spurious
  `BENCH may not lease PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` refusal. Bridge and game agree.
- not fixed: the fix changes the test's historical baseline order (cross-shard same-second causal pairs), which is a
  design choice and not a small, obvious fix. A note was added to the item.

## Commits / review
- 06faddba44 code. A ledger + review-record commit follows.
- CLEAN: RM_CliffMask.cs (full-file review, nothing found), selftest_subject.py (full review; one cosmetic rename,
  shadowed `fams` -> `found`, done before the mark).
- tool_schemas.json is generated data and was not reviewed.
- C5 still RED until READER_BASELINE_REPAIR_OLD_ORDER_TRIPS lands (selftest_handoff.py passed on the r6 rerun).
