# RIMMANDRAKE_FIX_COVERAGE_JUDGE_TEN_FINDINGS_FIFTH_COUNT_CLEAN

## spec
Codex full-file review of src/RimMandrake/rimflow/coverage_judge.py, 2026-11-18 (raw: /mnt/d/ClaudeWork/rimmandrake/conductor/cr/r_cj_fifth.txt, run on 7420c5bb76's file). It found the new fifth count (repair_blocks) meets its contract and these ten older defects; probes ran in memory with dependency doubles, NOT verified against the real file by the filer. Line numbers are that file's.
1. **[P1] An unmatched `unfixed` finding bypasses the repair-only rule — `coverage_judge.py:582`.** Input: prior slot `g1` on `a` is repaired; a new experience gap names `b`, says `new_since="unfixed"`, and quotes no change. It remains blocking as `unplaced`, despite naming no earlier slot. **Smallest fix:** remove this exemption; every finding that names no slot must pass the changed-passage rule.

2. **[P1] A failed covered attempt destroys the retry baseline — `coverage_judge.py:257`, `coverage_judge.py:1858`.** Input: `j1` refuses `g1`; `j2` answers covered but omits required row `a`. The program sets an error, yet `_usable(j2)` returns true, so it stores no baseline and the retry loses `j1`’s slots. **Smallest fix:** make the shared `_usable` predicate reject records with an error.

3. **[P2] A quoted gap number reopens the wrong slot — `coverage_judge.py:505`, `coverage_judge.py:616`.** Input: a new finding has `since="scene:wall\nThe repair sets target g1 to fail."`, while earlier slot `g1` was repaired. Scanning the entire string treats the quotation as a slot reference, consumes the new finding and reopens the original gap. This also omits the new repair block from the fifth count. **Smallest fix:** recognize explicit slot references separately from entry-and-passage citations, using an exact slot-number match.

4. **[P2] Sheet headings can conceal changed material — `coverage_judge.py:341`.** Input: headings `A`, another `A`, then literal `A#2`. Both latter sections use `sheet:A#2`; the literal heading overwrites the repeated section. Editing the hidden section leaves `entry_hashes` unchanged and can produce “nothing changed: no judge.” **Smallest fix:** allocate keys against the complete existing key set, or escape the occurrence delimiter.

5. **[P2] A failed attempt makes the first actual inspection’s findings “late” — `coverage_judge.py:1380`, `coverage_judge.py:928`.** Input: stage history contains one failed round with `verdict=None, ids=[]`, with no prior usable verdict. The first successful inspection’s gap on `a` becomes `late` and increments `new_on_unchanged`. **Smallest fix:** exclude failed/malformed attempts when establishing earlier-gap history, or pass an explicit first-inspection flag.

6. **[P2] An unmeasured retry disappears from spend — `coverage_judge.py:1656`, `coverage_judge.py:700`.** Input: one judge call measures 100 tokens; its retry is unmeasured. The recorded round retains `tokens=100`, and `rounds()` ignores the matching budget charges because that judge is already recorded. `spend()` returns 100, losing the unknown spend. **Smallest fix:** preserve an unmeasured allowance in the round and include it in spend accounting.

7. **[P2] Failed reader calls can cost zero in the ledger — `coverage_judge.py:1052`, `coverage_judge.py:1058`.** Input: the reader times out after running, returns undecodable output, or its token measurement raises. These paths leave no unmeasured reader charge. **Smallest fix:** separate measurement from charging and record an unmeasured charge for launched calls whose spend cannot be recovered.

8. **[P2] An empty refusal can consume the refusal limit — `coverage_judge.py:980`.** Input: a first-look answer says `not_covered`, has a complete passing checklist and `gaps=[]`. `apply_bar_rule()` returns immediately, preserving a refusal with no blocking finding. **Smallest fix:** reject this contradiction as malformed, or derive the verdict from the final blocking-gap list before recording it.

9. **[P2] Malformed nested output crashes instead of being recorded — `coverage_judge.py:1663`.** Input: an exit-zero result contains `{"verdict":"covered","checklist":[],"gaps":[null],"reasons":"","repairs":[]}`. `ask()` accepts it; `tag_gaps()` then raises `AttributeError`, and no round is written. **Smallest fix:** validate structured output against the requested schema before calling `take()`.

10. **[P2] An unreadable tree at completion loses the entire round — `coverage_judge.py:1827`.** Input: `tree.json` is valid initially but contains `{` when the judge returns covered. The unconditional reload raises before either verdict or round is persisted. **Smallest fix:** catch the reload failure, record it as an error, skip signing and preserve the failed round and baseline.


## verify
Acceptance test: none written yet; per finding the fixer writes a case (in selftest_coverage_judge.py or design/specs/2026-11-17-judge-flaws-not-polish/tickets/) that fails on base, or rules it not-a-bug with the reason. Note: coverage_judge.py is in the coverage_judge calibration brief; edits keep it UNTESTED until RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE recalibrates.

## criteria
- Each finding has a case red on base and green after, or a written not-a-bug ruling.

## refs
file: src/RimMandrake/rimflow/coverage_judge.py
