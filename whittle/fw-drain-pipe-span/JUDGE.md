# Independent judge report: PIPE_SPAN_SELFTEST_FIX_COLLAPSED_WHITESPACE

**Verdict: the repair is sound and the frozen bullets hold at offline scope.** I found no material failure, no misleading claim and no missing control that would discriminate. I worked only from the actual source and raw evidence, not from the builder's narratives.

## Q1. Does the guard accept the real callback and reject the counter-only one?
`CallbackBumpsNet` (`PipeSpanNetChecks.cs:60-69`) works in four steps:
1. It strips comments with `TransferChecks.StripComments` (`TransferChecks.cs:693-718`, which leaves string contents alone).
2. It collapses whitespace with `RiverSwitchFlipChecks.Flat`. This is the exact normaliser `Src` now calls (`RiverSwitchFlipChecks.cs:44,47`). The diff confirms it is a pure extraction of the old inline `Regex.Replace(..., @"\s+", " ")`.
3. It requires exactly one header matching `internal static void OnSpansChanged(Map map) {`, with the opening brace.
4. Using `DrawbridgeChecks.Body` (`DrawbridgeChecks.cs:23-35`, brace-depth walk), it requires the body to contain `if (RM_PipeSpanNetMath.Changed(…)) { NetBumps++; RM_LiquidNet.Bump(map);`.

**The real callback is accepted.** The flattened `RM_PipePoles.cs:70-93` matches: the `Changed(` arguments are about 59 characters, under the `{0,120}` limit, and are followed by `))`.

**Counter-only callbacks are rejected.** All five counter-only mutants (`:204-211`) are rejected after `Flat(StripComments(...))`:
- CRLF/tab block body
- odd spacing
- `internal` expression body
- the exact historical `private static void OnSpansChanged(Map map) => SpansChangedCount++;` (history.txt line 470, commit 1e681b9)
- `{ SpansChangedCount++; return; }`

The test also asserts that the flattened text contains no `\n` or `\t` (`:216`).

**Each mutant must really change the source.** Every mutant goes through `raw.Replace(callback, …)`, and `Assert(mutant != raw)` is checked at `:214` and `:245`. A sub-replacement that silently fails to match makes the case fail; it cannot pass vacuously.

**Positive controls separate real rejections from an always-false predicate.** The current callback is accepted both raw and normalised (`:220`), with CRLF/tab re-indentation (`:221`), and with decoys wrapped around it (`:251`). A predicate that always rejects would fail these; one that always accepts would fail the mutant assertions.

## Q2. Coverage and remaining limits
Every category you listed is covered, in `:231-251`:

| Category | Control |
|---|---|
| Expression body borrowing the next brace | `=> …; private static void Decoy(Map map) {block}`. Only the brace-in-header requirement rejects this; without it, `Body` would open on Decoy's `{` and accept. |
| Moved bump code | block-bodied counter followed by a Decoy method holding the real block |
| Missing / renamed callback | `""` and `UnusedCallback` |
| Commented-out bump | `/* block */` inside a counter-only body. This is rejected only because comments are stripped. |
| Deleted parts | `NetBumps++` removed; `Bump(map)` removed; `Changed(...)` replaced with `true`; `!Changed` |
| Comment spoofing | a commented-out counter-only header added before and after the file. It must stay accepted, which only works if stripping keeps the header count at 1. |
| Unrelated counter text | a `Probe()` method and a string literal |
| Whitespace variation | `:207`, `:221` |

**Use of existing helpers is proportionate.** The change adds one internal `Flat` helper, reuses existing `internal` helpers, and touches no production code.

**Remaining source-shape limits.** None of these defeat this narrow item:
- **False alarms (fail safe):** the guard is tied to the `internal` modifier and the `map` parameter name. Changing either turns it red.
- **Accepted although unreachable:** a dominating `return;` or `if (false)` wrapper around a correct bump block would still pass.
- **Brace confusion:** braces inside string literals in the callback would confuse `Body`. There are none today.
- **Minor gap:** `:221` does not assert that its whitespace rewrite changed the text.

## Q3. Are the existing checks kept, and do the math cases still run?
Yes. `:186-196` still carries:
- the three `RM_LiquidNet.cs` wiring patterns
- registration via `new Action<Map>(OnSpansChanged)` (matches `RM_PipePoles.cs:184`)
- the join-order `IndexOf` check (matches `:105`, then `:112`)

The production net-bump check is kept and tightened: what used to be a whole-file `Has` (diff line 37) is now scoped to the callback body (`:191`). Only the vacuous `!poles.Contains("SpansChangedCount++;\n\t\t}")` was removed. The production edge/net/signature cases at `:75-182` are unchanged and executed.

## Q4. Raw output and identities
**csharp_stdout.txt:**
- Lines 1133-1140 show all eight PipeSpan cases as `ok`. The names match the source exactly, including the two new ones: `PipeSpan_P3_callback_guard_rejects_normalized_counter_only` and `PipeSpan_P3_callback_guard_scopes_changed_bump`.
- Line 1470: `1240/1240 passed`. Line 1509: hose `455/455`.
- There are no `FAIL` lines (the runner prints `FAIL  name`, `Program.cs:101`). Lines 1-35 are build warnings only, and csharp_stderr.txt is empty.

**Wrapper:**
- `Program.cs:2281` returns 1 on any failure, and the wrapper exits with that code (`selftest_flowworks_stock.py:131`).
- The receipt has `returncode: 0`. selftest_stdout.txt shows `PASS 1/1 FAIL 0 UNMEASURED 0 CRASH 0 SKIPPED 0` and `0 CACHED PASS`.

**The "not recordable … changed during the run" line** is about cache recording, not the verdict. The raw refusal row lists `/etc` and `/home/mandrake` folder moves, a wall-clock read and `/mnt/c` dotnet reads. selftest_flowworks_stock.py has the same hash (`1c4bc152…`) before, during and after the run.

**Identities:**
- `stage_identity.json` reports `all_inputs_match: true`, and the staged hashes equal the expected ones. Examples: PipeSpanNetChecks `66e32015…`, RiverSwitchFlipChecks `c502478a…`, RM_PipePoles `df06e2bc…`, DrawbridgeChecks `47d88484…`, TransferChecks `3b585359…`, RM_PipeSpanNetMath `e0d02bdb…`.
- The test exe mtime (1794390113) is after the run started (1794389988), so it was built from this stage.
- BUILD_SOURCE shows HEAD `b24bb1ca…`, dirty only in the two SelfTest files, both at start and at end.
- `pre_judge_integrity.json` reports `matches_proof_inputs: true`, `matches_tested_HEAD: true` and `changed_production_paths: []`.
- The reference identity (Pawn_NeedsTracker) matches across both readbacks. It isn't related to this item.

## Q5. Reconciling the triage note
- **What production actually does.** Commit 5f54729 replaced the counter-only expression body with a callback that counts every call, then bumps the liquid net only when `RM_PipeSpanNetMath.Changed` reports a new span signature (`RM_PipePoles.cs:70-93`).
- **What the original guard meant.** Its message was "the callback is no longer only a counter". Its intent was to fail if the callback reverts to counter-only.
- **The 2026-10-29 done-condition is inverted.** It says "fails when the callback body gains a statement". The working callback already has many more statements than the counter, so a guard written to that condition would fail the shipped code. The owner's quoted words ("Please assess those ancient queue items … do they REALLY need the owner?") ask for triage only and give no instruction about guard semantics.
- **The proper intent** is to fail when the changed-set bump is lost (counter-only, missing, moved or neutralised) and to accept the working callback. The new guard implements exactly that.
- **The old needle was vacuous twice over.** Apart from the whitespace collapse, `SpansChangedCount++;\n\t\t}` would not match the historical expression-bodied form even in raw text. `original_guard_reproduction.json` records `old_guard_accepts_retired_callback: true`.
- **Agreement:** `evidence/scope_reconciliation.md` reaches the same conclusion I derived independently.
- **Red-first:** this is shown inside the test by mutants applied to the real source, not by a separate red run of the suite. That is adequate at offline scope.

## Q6. Scope and gaps for the parent
- The diff touches only `PipeSpanNetChecks.cs` and `RiverSwitchFlipChecks.cs`. There are no production, Defs or GimmeSomeSlack changes, so shipping behaviour and the approved GSS cord appearance are untouched.
- **Gaps for the parent:**
  - NOTES.md contains only a heading. The reconciliation lives in `evidence/scope_reconciliation.md`, and the ledger note correcting the inverted done-condition is the parent's to write.
  - There is no live-game proof, and this item doesn't require one.
  - The source-shape limits listed under Q2 remain.

would show: yes