Full-file review found five blocking issues:

1. **Incomplete passing verdicts count as calibrated passes.** `coverage_calibration.py:425` never checks `CJ.missing_rows()`. A schema-valid `covered` answer with an empty checklist passes calibration; production re-asks and ultimately refuses to sign if required rows remain missing.

2. **Refusals bypass production validation and routing requirements.** `coverage_calibration.py:456` second-reads gaps without production’s refusal-contract checks and correction handling. Invalid evidence or malformed refusal records can therefore count as successful planted refusals. Separately, line **469** returns `"refuse"` for `not_covered` with no gaps, bypassing `outcome()` entirely—even `bad_conflict_routing` passes without identifying or routing the conflicting criterion.

3. **Delta findings disappear only in calibration.** After `CJ.delta_merge()` at `coverage_calibration.py:437`, production restores dropped findings that name no slot before applying `classify_new()`; calibration omits that step. For example, an out-of-scope finding tagged `late`, with a valid changed-passage quote but no `late_why`, gets dropped here. Production restores it and can block after serious confirmation; calibration can report a pass.

4. **An unmatched `unfixed` finding bypasses the same-problem rule.** The shared `CJ.classify_new()` called at `coverage_calibration.py:440` preserves such findings as `unplaced` blockers. With prior slot g1 concerning `light`, a finding tagged `unfixed` concerning only `oil_out` names no earlier slot, yet can block without a changed-passage quote or serious confirmation. Under the stated rule, it is new and must satisfy rule 4. This affects both calibration and production.

5. **`good_one_kind_enough` narrows its owner’s promise.** `coverage_calibration.py:280` promises beasts stay away **from the room**, but line **297** checks only that the wolf stays outside the lantern’s two-cell radius. In the seven-by-seven room, a wolf can enter the outer room cells and still pass. A sound brief can refuse this specific coverage hole without demanding another roster kind. Align the promise and tested boundary while retaining the single wolf.

Advice: move the selftest’s expected-prior-judge and delta-baseline assertions into replay staging. The supplied contents do not establish that the specified commit is wrong.

VERDICT: FIX_FIRST