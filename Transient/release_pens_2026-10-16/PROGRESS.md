# REVIEW_SAVE_RELEASE_PENS — progress (BENCH helper, 2026-10-16)

## 1. Ledger item
None existed. Filed `PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK` (BENCH, needs deploy); prose + live verify list in `infrastructure/state/items/PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK.md`.

## 2. Mechanism (why pen animals are pinned)
`jawa/artboard_stage` pawn ops: `StartJob(MakeJob(JobDefOf.Wait, 60000), InterruptForced)` then set rotation (`JawaBenchArtboardTools.cs`). Nothing re-applies it; ending the job is enough. FlowWorks `review_map.py` uses `jawa/spawn_pawn` (no pin): not touched.

## 3. Companion tool
`JawaBenchPenTools.cs`: `jawa/pen_release(rects|pawns|allMap, includeHumanlike)` and `jawa/pen_pin(rects|pawns|allMap, restore=true, ticks=60000, includeHumanlike)`. Counts selected/released/notReleased/pinned/returnedHome, skipped[] with reasons, job histograms before/after; release stash is in memory only.

## 4. Build
`build.py --gm` (plan only, no --apply): 0 warnings 0 errors; DLL tool table 402 tools incl. both; `selftest_tool_metadata.py` PASS. NOT deployed (game running). Note the build includes the foreign uncommitted edit in `JawaBenchPawnKitTools.cs`; a deploy from HEAD needs that resolved or `git archive` export (build.py --apply does this).

## 5. Review-map wiring (--release-pens)
`src/RimMandrake/Pyrelands/human_review.py`: `pen_stations`/`pen_rects`, `Review.pens()`, flags `--release-pens` / `--pin-pens` (mutually exclusive, argparse error).

## 6. Selftests
`selftest_pyre_review_map.py` section 11 (pen rects cover every specimen; routing via fake bridge; refusal noted; both-flags refused): ALL PASS. run_selftests --only: GREEN 2/2.

## 7. What the live check must prove
See the item's `## verify`: released == specimen count with no Wait after; animals move but stay inside pens when unpaused; pin returns them home with S/E/N/W read back; second release selects 0 and says so.

## 8. Commits
(pending)
