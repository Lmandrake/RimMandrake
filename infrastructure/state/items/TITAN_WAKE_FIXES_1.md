# TITAN_WAKE_FIXES_1 — Titan wake step fixes

Filed 2026-10-07 by BENCH from `HUGE_THINGS_GPT_REVIEW_1` (full GPT review of the merged Huge Things, `c954ccdca`). Mod: `src/RimMandrake/HugeThings`. Do not deploy as part of filing.

## spec
Verified fix-now findings from `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md` (gone from disk; last copy in git at e2e47abef7) (triage `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW_TRIAGE.md` (gone from disk; last copy in git at c6b6033633)), checked on code and on 1.6 (RimSage).

- **B3.6**: `TitanicWakeProcessor.ProcessCell` (`:31-37`, `:110-140`) damages per cell. In 1.6, `ThingGrid.Register` registers a multi-cell thing in every cell, so a 2×2 under a 4×4 step takes 4 blows. Fix: collect unique targets per step, then damage once.
- **B3.7**: in 1.6 the `Thing.Position` setter returns early when the value is equal, but `Patch_Thing_Position_Wake.Postfix` (`:28-33`) still fires. Fix: prefix-capture the old position and map; act only on a real change on the same map.
- **B3.8**: `CompTitanicWake.Notify_EnteredCell` (`:160-173`) and `ProcessFootprint` never check `Pawn.Flying` (1.6 `Pawn.cs:1515`). Fix: no ground wake while airborne.
- **B2.4**: the Postfix calls `TryGetComp` on every pawn move before reading `WakeActive`. Fix: read the gate first.
- **B3.18 / C3.4**: `DefQualifies` tests `baseBodySize >= t1` only (`RM_TitanicKernel.cs:29-34`). In 1.6 `Pawn.BodySize = CurLifeStage.bodySizeFactor * baseBodySize`, so a race with a life-stage factor above 1 is tiered at runtime without the wake comp. The comment at `TitanicTierUtility.cs:231-237` claims to handle this and does not. Fix: qualify on base × max life-stage factor. Fuzz base and factor independently.

## verify
The titan fuzz family has new cases (multi-cell dedup, life-stage qualification) that fail on revert. Lints pass.

## criteria
A1: the five bullets are fixed. A2: the regression cases exist.

## current state — 2026-11-11
All five fixes are present in current source; the implementation is already recorded at 88c73d3ebe58. The original findings above describe the pre-fix defects. The authoritative remaining ledger criterion is A1 L2: live, a T3 titan stepping over a 2x2 crushable deals one blow per step; a flying titan leaves no wake; a stationary Position re-set fires no wake. Offline source/fuzz checks alone do not discharge that criterion.

NEXT: run the ground-only one-blow/reset checks on a disposable site; park the live flight portion for an owner-present test. Exact reserved question and evidence pointers: /home/mandrake/codex-steve/ht-loop/OWNER_QUESTIONS.md. No fresh acceptance or flight was run by this drain round; no criterion was removed.
