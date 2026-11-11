# JUDGE — POND_DEPTH_VERDICT_FIX_DEEP_COUNTS_PARTIAL

Independent judge. I had no part in building this. I did not read DONE.md, BROADEN.md, FINDINGS.md or any builder commentary. Scope: the offline acceptance instrument `pond_depth_verdict` only. Nothing here shows that a lake actually looks right in game.

## Evidence inspected
- `whittle/fw-drain-pond-verdict/STATEMENT.md` and `NOTES.md` (NOTES contains only the heading "# Owner rulings", with no rulings).
- `src/RimMandrake/FlowWorks/northstar/liquid_checks.py:360-405` (`parse_pond`, `pond_depth_verdict`).
- `src/RimMandrake/FlowWorks/northstar/selftest_liquid_checks.py:1-175`, including the L8 block at lines 105-155 and the exit logic at lines 173-175 (`sys.exit(1 if bad else 0)`).
- Evidence files: `selftest_stdout.txt`, `selftest_stderr.txt`, `verification.json`, `verdict_comparison.json` (all 20 rows), `old_pond_depth_verdict.py`, `production.patch`, `verify.py`.
- Context: `src/RimMandrake/FlowWorks/Source/RM_PromotionProofs.cs:295-328`, the `ProofPondDepth` census emitter, to check what `deep` means.

## Replay integrity
- **Is the old function really the original production function?** `verify.py` gets it with `git show 4ca1fc48…:liquid_checks.py`, parses it with AST, compiles the `pond_depth_verdict` node and execs it. The saved `old_pond_depth_verdict.py` matches the current function line for line except for one line: the partial-stage sum at current line 403. The old line has `+ c.get("deep", 0)` and the new line does not. The recorded `original_git_sha` and `current_git_sha` are both `4ca1fc48…`, so the fix is an uncommitted working-tree change against HEAD. That makes HEAD the right "original" revision.
- **Are the fixtures identical for both functions?** `verify.py` uses AST to pull `_P` and `_pond_cases` out of the final selftest file and execs them with `LC` set to the current module. Every fixture therefore goes through production `parse_pond`. Each function gets its own `copy.deepcopy` of the same parsed reads. `parse_pond` is not touched by the patch, so parsing the fixtures with the current parser is equivalent to parsing them with the old one. `verdict_comparison.json` records the parsed inputs. I checked them by hand against the fixture definitions; they match, including the `None` entries for filtered reads.
- **Does the current function match expectations?** For each row, `verify.py` asserts `current_result[:2] == expected`. It also requires exactly 3 regressions where the old function returns `PASS/MOD` and the current one returns `FAIL/MOD`. It hashes both source files before and after the run.
- **Did the selftest pass?** The recorded run was `run_selftests.py --only selftest_liquid_checks.py`. It shows `PASS 1/1`, `RESULT: GREEN`, returncode 0, and an empty-of-errors stderr. The run was not served from cache: stdout says "1 ran … an input changed".
- **Can the selftest go red?** Yes. The selftest exits 1 on any mismatch. The 3 deep-only rows expect `FAIL/MOD`, and the old function returns `PASS/MOD` on them, so the selftest would fail against the original predicate.

## Production change scope
- `production.patch` has a single hunk. It removes `+ c.get("deep", 0)` from the part-depth sum at `liquid_checks.py:403` and nothing else. The current source agrees with the patch. The docstring was already worded correctly ("chest/shallow/thin … instead of only full original water") and is unchanged.
- I could not independently confirm that no other part of `liquid_checks.py` differs from HEAD, because I did not use a shell or git. The single-hunk patch and my comparison of the old function with the current one are consistent with a change confined to that line.

## Verdict per statement bullet
1. **"When the surface falls and the census still contains only deep water, the verdict is FAIL/MOD rather than accepting a partial-depth stage." — SUPPORTED.**
   - Rows covering this: deep-only at s=1, deep-only at s=2, and a deep-only final census after earlier partial stages with a filtered `None` read.
   - Old function: `PASS/MOD` on all three. Current function: `FAIL/MOD` with the reason "no square shows a part-depth stage".
   - This matches the C# emitter. There, `deep` counts `WaterDeep` cells that are not the cell's original terrain. That is full-depth water, not a part-depth stage.
2. **"Chest, shallow and thin stages stay acceptable when the stable-wet-count and falling-surface conditions hold; a mixed deep/partial census is also valid." — SUPPORTED.**
   - Rows covering this: chest-only, shallow-only and thin-only at s=1; shallow at s=2; mixed deep=99 with thin=1; the original chest/thin case; deep=4 with thin=1 after repeated brim reads.
   - All of these return `PASS/MOD` from both the old and the current function.
   - The stable-wet-count condition still holds a partial-stage census to FAIL: the case with an intermediate shrink (wet 99 at s=1) returns `FAIL/MOD` from both.
3. **"No-pump, nonapplicable-body, insufficient-reading and shrink-from-the-rim classifications stay intact, and focused checks run the production predicate and fail against the original false-safe implementation." — SUPPORTED.**
   - No-pump: SITE in both functions, including when the final census is deep-only.
   - Nonapplicable body: SITE in both functions, including a nonapplicable early read followed by a deep-only final census.
   - Fewer than two reads (0 reads, 1 read, and filtered `None` reads): HARNESS in both functions.
   - Shrink from the rim: `FAIL/MOD` with the shrink reason in both functions.
   - The selftest imports and calls production `LC.pond_depth_verdict`. The replay shows 3 of the 20 cases would fail against the original implementation.

## Defects
None found that are material to the statement.

## Limits
- **I did not rerun anything.** No tests, no `verify.py`, no git. That follows the no-shell instruction. My conclusions rest on reading the recorded outputs, the code and the evidence files. I did not verify the SHA-256 hashes or the git revision myself.
- **The selftest file is not covered by the patch.** `production.patch` covers only `liquid_checks.py`, and I did not see a diff of the selftest file against HEAD. I judged the final L8 block as it stands now.
- **The fix assumes `deep` is never a partial stage.** It treats deep water that is not the cell's original terrain (for example, deep over a former abyss cell) as not a part-depth stage. That matches the docstring and the statement. No owner ruling in NOTES.md addresses it either way.
- **Only the final census is judged.** The partial-stage check looks at the last read alone. The stable-wet check looks only at reads with s == 1 and r == 0. Both are pre-existing behaviour, the statement calls them "existing" conditions, and the fix leaves them unchanged.
- **This is offline only.** The run used no bridge and no game. Nothing here establishes how real ponds behave or look.

would show: yes
