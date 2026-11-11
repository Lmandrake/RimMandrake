# JUDGE: fw-drain-underpass

Scope: I read STATEMENT.md, the production row `raise_spares_underpass` and the new helper `_underpass_injuries`
(`src/RimMandrake/FlowWorks/northstar/drawbridge_proof.py:513-587`), the old row
(`evidence/old_drawbridge_proof.py:512-540`), the list_pawns producer (`JawaBenchTerrainTools.cs:1162-1178`),
`validation_core` require/scope semantics, the focused selftest (`src/RimMandrake/Utils/selftest_drawbridge_underpass.py`),
the existing `selftest_drawbridge_proof.py`, and the raw evidence (focused/regression/existing logs, `focused_rows.json`,
`regression_old_rows.json`, `verdict_comparison.json`, `verification.json`). I did not read DONE.md or NOTES.md.
I had no shell, so I did not re-run the tests myself. The run results below come from the recorded logs, checked against the code.

## Bullet 1: safe only when the pawn stays in the same cell and its injuries are unchanged — TRUE
- `same = at(u0) == at(u1) and h0 is not None and h1 is not None and h0 == h1` (line 540). A PASS also requires `good`,
  which includes `same`.
- The cells must be real ints: `type(p.get(k)) is int` for x and z on both reads, or the row gets a HARNESS require
  (lines 538-539). This rejects bools and missing values. The old row PASSed "unread cells" because `(None, None) == (None, None)`.
  The new row reads UNMEASURED/HARNESS (verdict_comparison).
- `u0`/`u1` are deep copies taken at read time (lines 528, 536). The "shared mutable pawn payload" case shows this
  matters: old = PASS, new = FAIL.
- The comparison covers every field of every hediff record, as a sorted multiset of canonical JSON strings. Order doesn't
  matter, but duplicates and every field do.

## Bullet 2: worse severity, replacement injuries and changed parts can't pass on equal count — TRUE
- The old bar was `len(after) == len(before)`. The new bar is equality of the full records (`def`, `label`, `severity`,
  `part`, `partLabel`, `lastInjury`, plus any extra keys).
- Recorded verdicts, old to new:
  - worsened equal count: PASS to FAIL
  - tiny severity drift (2.5 to 2.500001): PASS to FAIL
  - replaced equal count (Cut to Burn): PASS to FAIL
  - part changed: PASS to FAIL
  - side label changed: PASS to FAIL
  - last injury changed: PASS to FAIL
  - duplicate multiplicity replaced: PASS to FAIL
  - large distinct severity (2**54 vs 2**54+1, exact because ints are kept as ints): PASS to FAIL
- Integral floats are normalised (`1` == `1.0`) without losing precision for other values. Because of this, the
  intended equal cases still PASS.

## Bullet 3: missing or malformed health is a harness failure, not an empty healthy list — TRUE
- `_underpass_injuries` requires `health` to be a dict and `health.hediffs` to be a list (an empty list is valid). It also
  requires every record to be a dict with all six fields the producer emits.
- It then type-checks each field:
  - `def` must be a non-empty str and `label` must be a str.
  - `severity` must be a finite, non-negative int or float. Bools are rejected, and 10**400 is caught through OverflowError.
  - `part`, `partLabel` and `lastInjury` must be null or a non-empty str.
  - `part` and `partLabel` must be null together.
- Any failure calls `V.require(..., cls="HARNESS")` and the helper returns None. Inside the row's scope this withholds
  the verdict, so the row reads UNMEASURED/HARNESS.
- The field set matches the real producer, `JawaBenchTerrainTools.cs:1166-1178`: def, label, severity, part, partLabel and
  lastInjury, with nulls for whole-body hediffs. So a well-formed live reading is accepted.
- Recorded cases where the old row scored a PASS and the new one reads UNMEASURED/HARNESS:
  - `hediffs` absent, null, False, 0, a string or a dict, on both sides
  - null or string records
  - incomplete records
  - records missing each of the six keys
  - bad severities (True, '2.5', None, nan, inf, -1, 10**400)
  - bad part/label types
  - part None with a partLabel set
- Each case is recorded for the before, after and both sides. When the bad reading was on one side only, the old row
  usually reported a mod FAIL.
- The shared `_health` helper is unchanged for its other callers. `test_shared_health_helper_unchanged` pins this.

## Bullet 4: focused offline checks run the production row; unchanged health passes, false-safe cases fail — TRUE
- The selftest loads `drawbridge_proof.py` by path. `focused_rows.json` shows `"source"` as the production file. It calls
  `DP.raise_spares_underpass(ctx)` under the real `DP.V.scope` and `DP.V.PRE.judge`. Only bridge I/O is stubbed: proofs,
  pawns, counters and ticks.
- focused.stdout.log: PASS 1/1, GREEN. focused_rows.json: failures=0, errors=0.
- These cases PASS/MOD:
  - unchanged existing injury
  - real empty lists
  - reordered list
  - whole-body null parts
  - 1 vs 1.0
  - capacity-only change
  - injury-fields-only health block
- Every false-safe case reads FAIL/MOD, and every malformed reading reads UNMEASURED/HARNESS.
- Regression replay against the old source (`DRAWBRIDGE_UNDERPASS_MODULE=old_drawbridge_proof.py`) gives RED with 115
  failures. The old verdicts in regression_old_rows.json are PASS on the equal-count harm cases, so the checks can fail.
- The existing `selftest_drawbridge_proof.py` (FakeBridge mock, including the `underpass_tipped` can-fail) still runs
  GREEN. FakeBridge's under-pawn has an empty hediff list, so its minimal `{"def": ..}` record shape doesn't trip the new
  strict reader.

## Residual notes (none of them falsify a bullet)
- Strict equality over a 10-tick raise could give a false FAIL if a pre-existing hediff's severity drifts on its own
  (SeverityPerDay comps tick every 200 ticks). This errs toward failing, not toward a false safe.
- If the pawn is gone from the list_pawns read after the raise (for example, killed), the row reads UNMEASURED/HARNESS
  rather than FAIL. That is not a false safe either.
- I couldn't check the recorded SHA-256 (production_sha256_after) against the current file without a shell.
- No live game run is claimed. All the evidence is offline, which is what bullet 4 asks for.

All four bullets are true.

would show: yes
