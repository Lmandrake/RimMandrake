# Different-model broaden

Caller: `whittle/fw-drain-underpass/evidence/call_broaden.py`.
Bounded request: `evidence/broaden_prompt.txt` (six adversarial cases maximum; no tools, edits, live game or bridge).
Raw response: `evidence/broaden_raw.json`; process metadata: `evidence/broaden_call.json`; stderr: `evidence/broaden_stderr.txt`.
The independent call returned successfully in session `3452e92f-83e0-43fd-b47f-0ccc1144fd49`; the raw model usage identifies `claude-opus-5-5`. It was not a fork and had no builder conversation history.

Opus suggested duplicate multiplicity, malformed shapes on either side, explicit null versus absent keys, boolean/nonfinite severity, exact equality decisions, mutable before/after aliasing, and identity/cell edge cases. See the raw answer for its full wording.

Acted on these revealing cases in `src/RimMandrake/Utils/selftest_drawbridge_underpass.py`, exercising the production scene with real precondition scope/judge:

- A shared mutable pawn payload is changed during the raise call. Capturing the before pawn deeply before the call preserves both the injury comparison and raw evidence. The corrected row fails this harm case; the isolated old source passes it.
- Duplicate injuries are reordered, removed, and redistributed with the total count unchanged. Multiset comparison ignores order but preserves multiplicity. The equal-count redistribution fails with the fix and passes with the old count comparison.
- Missing/null/malformed health and list entries are tried before, after, and on both sides, including incomplete producer records, booleans, NaN, infinity, and an oversized integer severity. Each corrected result is UNMEASURED/HARNESS with a concrete reason, while a real empty list remains PASS.
- Side changes within the same body-part definition are caught through `partLabel`; whole-body explicit null fields pass. Missing coordinates with valid injuries are HARNESS; moved cells fail.

Raw results: `evidence/focused_rows.json` and `evidence/regression_old_rows.json`; side-by-side verdicts: `evidence/verdict_comparison.json`. The required runner calls, exact exit codes, source hashes, and filesystem type are in `evidence/verification.json` and its named stdout/stderr logs.

Decisions: the frozen statement requires unchanged measured injuries, so even tiny severity drift fails; there is no tolerance. Every producer injury field participates, including labels and lastInjury, while list order and numeric equivalents 1/1.0 do not change the injury snapshot. Raw capacities/pain/bleed readings are retained but are not injury equality inputs. Null part fields are valid; missing fields are not. Other `_health` callers retain their original behavior, explicitly checked by the focused test and the existing drawbridge selftest. The pawn is read by the same spawned pawn ID on both sides. Broader map/death instrumentation and stopping staging immediately after a precondition failure were not added to this narrow repair; the existing scoped harness withholds the verdict on failed reads. No live claim is made.
