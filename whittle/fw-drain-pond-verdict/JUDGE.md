# JUDGE — POND_DEPTH_VERDICT_FIX_DEEP_COUNTS_PARTIAL

Independent judge, fresh context. Scope: the offline acceptance-instrument repair to `pond_depth_verdict` only. This report does not establish anything about how a lake actually looks in game.

## Evidence inspected (read-only tools; no shell, bridge, game or external service)
- `whittle/fw-drain-pond-verdict/STATEMENT.md` (three bullets); `NOTES.md` (only the header "# Owner rulings", no rulings in it).
- `src/RimMandrake/FlowWorks/northstar/liquid_checks.py:360-405` (`parse_pond`, `pond_depth_verdict`) as it is now.
- `src/RimMandrake/FlowWorks/northstar/selftest_liquid_checks.py`: the `case` harness (lines 14-15), the L8 block (105-155) and the exit logic (171-175, `sys.exit(1 if bad else 0)`).
- Evidence files: `resume.patch`, `old_pond_depth_verdict.py`, `verify_resume.py`, `resume_verification.json`, `resume_verdict_comparison.json` (all 20 rows), `resume_integrity.json`, `resume_selftest.txt`.
- I did not read DONE.md, BROADEN.md, FINDINGS.md, pre_resume/, any earlier JUDGE report or any builder commentary.

## Production change
- `resume.patch` changes one line in `liquid_checks.py` (line 403): `+ c.get("deep", 0)` is removed from the partial-stage sum. Nothing else in the production file changes.
- I compared `old_pond_depth_verdict.py` line by line with the current function. They are identical apart from that line, docstring included.
- The current docstring already said part-depth stages are "(chest/shallow/thin) instead of only full original water". The fix brings the code into line with its own contract.
- `resume_integrity.json` records `git status` showing only the two source files modified, plus the untracked whittle directory.
- **Conclusion:** the change is limited to removing `deep` from the partial-stage sum.

## Replay fidelity (`verify_resume.py`)
- **Where the old function comes from:** `git show 4ca1fc48…:liquid_checks.py`. The script parses it with `ast`, pulls out the `pond_depth_verdict` node and asserts it is byte-identical to `old_pond_depth_verdict.py`. It then compiles and runs that same node. So the original production function is executed, not a hand-copied version. The function uses no module globals, so running the node alone is sound.
- **Current function:** imported from the working-tree file.
- **Fixtures:** the script pulls `_P` and `_pond_cases` out of the final selftest via `ast` and runs them with `LC` bound to the current module. The fixtures are therefore the same `parse_pond`-parsed dicts the selftest uses. Each function gets its own deep copy of identical inputs.
- **Assertions:**
  - The current function meets all 20 expectations.
  - Exactly 3 cases differ under the old function, and each goes from old `PASS/MOD` to current `FAIL/MOD`.
  - Source hashes match before, during and after the run, and match the selftest receipt.
- **Recorded result** (`resume_verification.json`): `total_pond_cases` 20, `current_failures` 0, `old_failures` = deep-only at s=1; earlier-partials-plus-filtered-read with a deep-only final census; deep-only at s=2. `fresh_results_equal_original_recorded_results: true`.
- I checked the comparison rows by hand against both function bodies. Every old and current verdict shown is what the code would return.

## Per-bullet verdicts
1. **Deep-only census with a falling surface returns FAIL/MOD — SUPPORTED.**
   - The current line 403 fails whenever `s >= 1` and chest+shallow+thin == 0.
   - Cases cover deep-only at s=1 and at s=2, and a deep-only final census after earlier partial reads and a filtered `None`. All give FAIL/MOD now. The old function gave PASS/MOD on all three, which was the false-safe behaviour.
   - Precedence is right: nonapplicable and no-movement reads still return UNMEASURED/SITE first, and both have cases.
2. **Genuine partial stages still pass; a mixed census is valid — SUPPORTED.**
   - chest-only, shallow-only and thin-only each PASS at s=1, and shallow-only passes at s=2.
   - Mixed censuses pass: deep 99 + thin 1, and deep 4 + thin 1 with repeated brim reads (the stable-wet boundary).
   - The stable-wet guard still comes first: an intermediate shrink from 100 to 99 at s=1 FAILs even though partial stages show later.
3. **Existing classifications intact; regression checks run production and fail against the original — SUPPORTED.**
   - The earlier gates (fewer than two reads → HARNESS, nonapplicable → SITE, no movement → SITE, shrink → FAIL) are untouched in code.
   - Every original L8 case is kept. Several are now stricter, checking `[:2]` instead of only `[0]` or `[1]`.
   - New cases add: no reads, filtered reads not producing a second reading, and the precedence cases above.
   - The selftest calls `LC.pond_depth_verdict` from the production module, and `case` failures exit nonzero. The replay shows three of these cases fail against the original function.

## Defects
None material found.

Minor observations, not blocking:
- The selftest run log (`resume_selftest.txt`) shows only the file-level PASS. The per-case `N/N` line isn't captured. A passing result still follows from returncode 0 together with `sys.exit(1 if bad else 0)`.
- The old pre-existing case "s fell but no part-depth square" uses `own=100`, so it never exercised the `deep` bug. The new deep-only cases close that gap.

## Exact limits
- **I did not rerun any tests or scripts.** No shell was used; I did not run the selftest, `verify_resume.py` or `git`.
- I did not independently confirm:
  - that the `4ca1fc48…` blob really contains the extracted function;
  - any SHA-256 value;
  - the HEAD SHA (`a4ac5845…`).

  I rely on the recorded receipts for these, and on the internal consistency I checked by reading. Specifically: the patch's `-` line equals the old function's line; the current file matches the patch's `+` side; the comparison rows agree with both code bodies.
- `resume.patch` is a diff against HEAD (`a4ac5845…`), not against the original SHA (`4ca1fc48…`). Changes elsewhere in `liquid_checks.py` between those commits were not reviewed. The `pond_depth_verdict` function itself is identical to the original apart from the one fixed line.
- This is offline instrument logic only. Nothing here shows that the game produces partial-depth censuses or that any lake shallows.

would show: yes
