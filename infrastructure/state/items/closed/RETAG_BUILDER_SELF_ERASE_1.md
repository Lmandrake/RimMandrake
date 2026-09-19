## spec
Filed by BENCH: `build_retag_patches.py` diffs the frozen manifest against a
pinned pre-retag capture to decide which fields need patching. Two related
defects:
1. **Self-erasure**: if `CAP` ever points at a capture taken AFTER the retag
   is deployed, every one of the 269 real ops reads as "already correct" and
   a regeneration silently drops them all (measured: 269 → 33 defs, 5745
   deletions). `CAP` was only pinned by convention/comment, not enforced.
2. **Unmeasurable rows silently skipped**: a manifest row absent from the
   pinned capture entirely (e.g. a def authored after the capture was taken
   — `RUT_Antiq_*`, built the same night by `ANTIQUITIES_TREE_BUILD_1`) hit
   `dn not in live: continue` and was never emitted at all, which is why
   `RUT_ResearchRetag_Supplement.xml` had to be hand-written for 13 rows (10
   revived `DP_RGive*` + 3 `RUT_Antiq_*`).

## what changed
`design/Jawa/research_review/build_retag_patches.py`:
- **Hard guard**: `_assert_capture_is_pre_retag()` reads the capture's own
  `manifest.json` (`mods[].packageId`) and refuses (`SystemExit`) if
  `mandrake.rut.researchretag` is active in it — makes the "pinned on
  purpose" comment unbypassable instead of a convention. Live-tested against
  a real post-retag capture (`2026-09-04T23-46-09Z`) — correctly refuses.
- **Unmeasured-row folding**: a manifest row absent from the capture no
  longer gets skipped. It now emits techLevel/baseCost/prerequisites
  manifest-authoritatively (no live baseline to diff against, so
  unconditional emission is the only sound choice) — the same shape
  `field_patch()` already produces for measured rows, which is inherently
  idempotent (Replace-if-present/Add-if-absent), so these rows are safe to
  regenerate repeatedly regardless of capture state. Unit-simulated against
  the supplement's own `RUT_Antiq_Religion` row (T1→Industrial, cost 1200,
  prereq `RUT_Antiq_Language`) — produces the identical 3 ops.
- Measured rows' existing diff-against-capture logic (the "only touch
  techLevel when outside the tier's allowed set" nuance) is UNCHANGED —
  that flexibility is deliberate design, not a bug, and the fix does not
  touch it.

`src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag_Supplement.xml`:
header updated to record the fix and explain why it is NOT yet folded in
and deleted (see below).

## verify
- Guard tested live against a real post-retag capture (`2026-09-04T23-46-09Z`)
  — correctly raises `SystemExit` naming the reason.
- Unmeasured-row folding unit-simulated against a real supplement row — byte-
  identical shape to the hand-written entry.
- `python3 -m py_compile` clean.
- **NOT run end-to-end**: every capture currently on disk is post-retag (the
  originally-pinned `2026-09-04T02-23-44Z` capture no longer exists at all —
  captures get cleaned up over time), so there is no valid baseline left to
  actually regenerate `RUT_ResearchRetag.xml` against and prove the merge
  live, or to fold the supplement's 13 rows in and delete the file. This is
  an honest limitation, not skipped work — the fix is real and independently
  tested piece by piece, but the full generator run needs a genuinely
  pre-retag capture (or a scratch mod list with researchretag disabled,
  captured fresh) that doesn't exist right now.

## criteria
- Repointing `CAP` at a post-retag capture fails loudly, not silently.
- A manifest row with no live baseline (future Antiquities-style additions)
  gets real ops instead of being silently dropped.
- Measured rows' existing "outside allowed set" flexibility is preserved.
- Next real regeneration (whenever a valid pre-retag-equivalent capture
  exists) should produce `RUT_ResearchRetag.xml` output that supersedes
  `RUT_ResearchRetag_Supplement.xml` entirely — at which point that file
  gets folded in and deleted, per its own updated header.
