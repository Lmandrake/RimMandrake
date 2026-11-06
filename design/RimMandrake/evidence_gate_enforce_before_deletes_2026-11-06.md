# What enforces a close once a guard dies (EVIDENCE_GATE_DESIGN_ENFORCE_BEFORE_DELETES)

Written 2026-11-06 by Relentless. Readings taken about 22:30Z. Corrects RIMFLOW_DELETE_CLOSE_GUARDS_ONE_PER_LANDING (WP-09c).

## The answer

- **Two things get deleted: the warn-only hook and its lint.** Neither ever refused a close.
- **Every `_close_gate` check is kept.** The evidence record cannot stand in for them. It holds two entry kinds,
  `run` and `marker` (`evidence.KINDS`), and lives in the Relentless store, outside the repo. The checks read criteria,
  guards and paths, cover hand closes, and must replay from the ledger alone.
- **`relentless_wall.py` GAP parsing is kept.** Deleting it reverses the owner's card "Narrow it now". Only he can do that.
- **The enforce flip is step 1 and is fully specified below, but it cannot land yet.** It adds a refusal, and the freeze
  bars that until the 3-day check is read. Today it would also wrongly refuse 4 of 74 supervisor closes.
- **No deletion below depends on the flip.** The item assumed the deletions remove refusals. They do not, so the flip
  is no longer what makes them safe. It stays first for any later deletion of a refusing check.

## What was measured

| Question | Reading | How |
|---|---|---|
| Who closes | Of 166 closes since 13:47Z, 149 are the supervisor's | ledger shards at origin/main, `close` events, `why` exactly `relentless: blind check passed` |
| Closes that never reach the shadow | 3 of 166, all hand or owner, none held by the store | the same events joined to `evidence_shadow.jsonl` on item and sha |
| Predicate against supervisor closes since 18:00Z | 70 accepted, 4 rejected | the same join |
| Predicate against the other closes since 18:00Z | 12 of 13 rejected, 1 has no row | the same join |
| What the gate refused | `unchecked` 5, `guard` 3, of 183 rows | `gate_reasons` in the log; the predicate's reasons never name either |
| WEAK verdicts narrowed to PASS | 222 of 302 WEAK verdict rows since 2026-11-02 | store `shadow.jsonl`, rule `narrow_weak_1` |
| Are narrowed closes false | 16 of 16 audited HOLDS | `infrastructure/state/close_audits.jsonl`, stratum `narrow_weak` |
| Closes naming debt the hook looks for | 0 of 1003 code closes since 2026-11-03 (113 not the supervisor's, 890 the supervisor's) | each close's commit body against `live_proof_lint.PHRASES` |

Sanity probes for the zero: `git log -i -E --grep` over the same phrases agrees (0 commits since 2026-11-03). The same
regex does find the phrase in f9163831e0, the commit of a close the sweep lists, and the newest commit using a phrase
is 0360959f8a, 2026-11-01.

The four supervisor closes the predicate rejected since 18:00Z are the predicate's own faults, not false closes:

| Item | Predicate said | What happened |
|---|---|---|
| RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN | run not green, no marker | Closed at work sha 88360b38, whose record holds an old red run. The candidate 0a0e109a is green with a PASS. `_record_for` takes the sha's own record first. |
| RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN | no record | Closed at work sha e8c7158e. The candidate 0a387e4e is green with a PASS. `_same_work` says no because another item's landing also changed `relentless.py`. |
| EXAM_SETTER_FIX_DEMANDS_ITS_OWN_MECHANISM | marker WEAK | A GAP:OTHER WEAK, which the live rule reads as PASS. |
| OPS_CHURN_DIAGNOSE_RELENTLESS_BBZJ_VGUX | run not green | The box run was `unrunnable`; the Marker said PASS. EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO decides this case. |

A refusal is not cheap. `has not earned its close` sends the supervisor to `fail(..., "close_refused", ...)`, so each
wrong refusal costs an attempt on finished work.

## Step 1: the enforce flip

**Tracked by** EVIDENCE_GATE_FLIP_ENFORCE_AFTER_NOV9, blocked on the 3-day check. Before this note, no work package named it.

**The change.** Add `evidence_gate.ENFORCE = False`, a module constant shaped like `model.MARKER_FAIL_LOCKS`. It is not a
key in `relentless_rules.json`, which the freeze bars. The flip is one commit setting it to `True`.

**Where it acts.** In `cmd_close`, at the `_evidence_shadow(args, sha, no_code, [], line)` call after `_live_gate`, so
`live` is a checked line. `_evidence_shadow` returns the row. When `ENFORCE` is on and the close is in scope, a row with
`predicate` reject calls `die`, and the text keeps the words `has not earned its close`, which is how the supervisor
recognises a refusal.

**What it covers.**
- Only closes whose `--why` is exactly `relentless: blind check passed`. `RELENTLESS_WHY` is a substring test and would
  catch a Conductor's words, so it is not used.
- Hand, owner and behind-the-gate closes stay with `_close_gate` and `_fold_close_gate`. Of the 13 other closes since
  18:00Z, 12 would be refused if the predicate covered them.
- `implemented` and `verify` reach done without passing `cmd_close`, so the flip does not cover them. `run_refusals` in
  the fold (`_apply_implemented`, the `verify` path) is what holds those, which is one more reason it stays.

**On a blind predicate.** In scope, a `None` row (`judge` found no state, or `shadow` hit an exception) refuses. Silence
must not pass as green on the one route the flip claims.

**Preconditions, each its own landing before the flip.**
1. EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO is closed: a declared window, scope on each row, `unrunnable` decided.
2. EVIDENCE_GATE_FIX_WORK_SHA_HIDES_CANDIDATE is closed: the two record-selection faults above.
3. `green()` reads the word the supervisor acted on, inside the flip item. `evidence.append_marker` keeps only
   `reasons_sha256`, so the predicate cannot run `acted_weak` itself. `marker_receipt` and `harvest` record an `acted`
   field from `relentless_wall.read_as`; an old entry without it keeps today's reading. New cases in
   `selftest_evidence_gate.py`: a GAP:OTHER WEAK accepts, a GAP:DIFF WEAK rejects, an untagged WEAK rejects. The corpus
   rows whose tag reads PASS leave the false class, named in that commit, because the card and the 16 of 16 audit say
   they are not false closes.
4. RELENTLESS_MEASURE_THREE_DAY_CHECK_NOV9 has been read, which ends the freeze (`standing_rulings.md`, Relentless: subtract).

**The reading that licenses it.** `evidence_gate.py report` on a window opening after preconditions 2 and 3 land: at
least 30 supervisor closes, 0 gate-accept/record-reject disagreements, and `corpus check` OK. Agreement here licenses
the flip only. It says the predicate would not hold good work. It cannot show the predicate does the gate's job, so it
licenses no deletion.

**The revert.** `git revert <flip sha>`, then `./publish`. That puts `ENFORCE` back to `False` and leaves the log
running. Do it on the first `close_refused` whose candidate record holds a green run and the Marker's PASS.

**If the read says no.** Nothing below waits on it. The predicate then logs and decides nothing, and deleting
`evidence_gate.py` becomes the natural next subtraction, for the Conductor to file.

## The four guards

| Guard | Verdict | What replaces it | Test | Reading that licenses deletion |
|---|---|---|---|---|
| `cli.py` close guards | **Kept**, check by check below | Nothing | See below | None |
| `relentless_wall.py` GAP parsing (`narrow_word`, `acted_weak`, `names_strong`, read by `read_as`, `weak_reads_pass`) | **Kept** | Nothing. Redesign section 2.3 assumes a supervisor hunk-revert field; `evidence.KINDS` has none, and adding one is new machinery | `selftest_relentless.py`, `selftest_relentless_codex_seven.py` | Not a reading: an owner card |
| `.claude/hooks/warn_close_live_proof_owed.py` | **Deleted**, landing D1 | Nothing for hand closes. On the supervisor's route the hook never ran, and the contract's live clause is the record there (`live owed` in `green()`) | `rules()` in `selftest_evidence_gate.py` | 0 hand closes naming a phrase since 2026-11-03, re-read at landing |
| `src/RimMandrake/rimflow/live_proof_lint.py` | **Deleted**, landing D2 | Nothing: its only consumer is the hook, and its sweep's 40 old rows are read by nobody | None left | D1 landed, and `entrypoint_inventory.py` shows no other entry point |

**The hook meant is this one.** The item called that an inference. `redesign.md` section 2.3 names it: "`warn_close_live_proof_owed` hook + `live_proof_lint.py`".

**The hook only ever saw hand closes.** It is a PreToolUse/Bash hook in a Claude session, and the supervisor closes by
subprocess. Warn-only by its own spec, it never refused a close, so no shadow reading says anything about it. This is
the one case where the licence is a direct count rather than a predicate.

**Why GAP parsing is not read as covered by the Subtract card.** That card says "do the redesign's filed deletions",
which lists this row, but it did not put the trade to him. Deleting the parsing with no replacement returns every
GAP:OTHER WEAK to a hold: 222 of 302 WEAK rows, with 16 of 16 audited ones holding. That reverses "Narrow it now" (card,
2026-11-04 07:02Z, RELENTLESS_WEAK_MEASURE_PASS_COLLAPSE), and changing his ruling is his (`delegation_policy.md`
section 2). If the Conductor wants it, it is a card with those numbers. The pattern redesign feared, a GAP:OTHER on a
lesson-only candidate, stays rejected when it closes `--no-code` (`empty diff` in `green()`).

## Each `_close_gate` check

None has a record entry, so each row reads "kept". The last column says what would have to change first.

| Check | What it protects | Why the record cannot replace it | Test | Reading that would license deletion |
|---|---|---|---|---|
| `close_refusals` owed | Ledger criteria still owed, or passed on another sha | No criterion entry kind; the predicate's `live owed` covers the contract's live clause, not L1/L2 criteria | `selftest_close_gate.py` | None: needs a criterion entry kind, new machinery |
| `close_refusals` unchecked (`run_refusals`) | A level-tagged pass on this sha | The supervisor writes its own L0 pass just before closing, so this bites only hand closes, which the predicate does not cover; the fold needs it too | `selftest_close_gate.py` | None while hand closes exist |
| `close_refusals` fail (`run_refusals`) | Newest deciding run is a fail | Same; also the shared half of `implemented` and `verify` | `selftest_close_gate.py` | None while those routes exist |
| `close_refusals` guard (`guard_owed`) | A fix that died owes a class guard | `NOT_JUDGED = {"guard"}`; the record does not know a fix died | `selftest_repeat_guard.py` | None: needs a guard entry kind |
| `_sha_refusals` | The sha resolves, is more than the ledger, touches the cited paths | The predicate only looks up a record by sha | `selftest_relentless_nocode_close.py`, `selftest_relentless_stale_nocode.py` for the ledger-only half; no selftest quotes the cited-paths refusal | None: redesign section 3.4 keeps the literal sha |
| `_guard_refusals` | The guard is the test shown red, committed, and green now | The predicate runs nothing | `fixture_guard_gate.py`, `selftest_repeat_guard.py` | None: needs a guard entry kind |
| `marker_lock` | Prints a Marker FAIL at a hand close; the lock is off | On the supervisor's route a FAIL never reaches a close, so only the hand route sees it, where the predicate is silent | `s7_marker_fail` in `selftest_close_gate.py` | His bar for the trust rerun (`operations_design_2026-11-01.md` section 9 step 6) decides lock or removal |
| `_fold_close_gate` | A close from a clone behind the gate; every replay | The fold is a pure function of the ledger, and the store is not in the repo or on other clones | `selftest_close_gate.py` | None, permanently |
| `_live_gate` (beside the gate) | A promise holds right now (owner, 2026-10-31) | The predicate reads the line it checks | `selftest_live_gate.py` | None: the predicate depends on it |

## Kept around the record (redesign section 3.4, unchanged)

| Kept | Where | Test |
|---|---|---|
| lease fence | `fence_check` in `relentless.py` | `selftest_relentless.py`, `selftest_relentless_trailing_land.py` |
| literal sha | `cmd_close` requires `--sha` or `--no-code`; `_unpublished_commit` | `selftest_cli.py` |
| landing | `unlanded_owed` in `relentless.py` | `selftest_relentless_revert_landing.py` |
| provenance flags | `--owner-said`, `--by-card`, `--per-ruling`, `--why` | `selftest_close_gate.py` |
| diagnose and warrant | `diagnose_owed`, `warrant_owed` in `relentless.py` | `selftest_relentless_explain.py`, `selftest_relentless_breakers.py` |
| independent audit | `close_audit.py` (redesign G20) | `selftest_close_gate.py --au4` |

## The order

| Step | Landing | Waits for | Revert |
|---|---|---|---|
| 1 | The enforce flip | Its four preconditions and its reading | `git revert <flip sha>`, `./publish` |
| D1 | Delete the hook: `.claude/settings.json` entry, `warn_close_live_proof_owed.py`, `selftest_warn_close_live_proof_owed.py`. Move `hook=warn_close_live_proof_owed.py` from `live_baseline.txt` to `live_retired.txt`, or `deadman_check.py` files `LIVE_RESTORE_*`. Fix the references in `folded_into_operations.md`, `rimflow_system_and_stuck_state_2026-10-07.md`, `git_workflow_plan_2026-10-01.md`. | Its count re-read at 0. Nothing from step 1: a warn refused nothing | `git revert <D1 sha>` |
| D2 | Delete `live_proof_lint.py`; fix `rimflow/docs/README.md` | D1 landed; `entrypoint_inventory.py` shows no other entry point | `git revert <D2 sha>` |

A touch of `.claude/settings.json` or a hook needs a live line, so D1's contract carries `--live "once: ..."`.

Any later deletion of a refusing check goes after step 1, with a record entry and test named here first. A shadow
agreement count alone does not license one, because agreement cannot show equivalence.
