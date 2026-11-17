# Recording the pin commit

> **Status: Codex draft (gpt-6.1-sol), 2026-11-17, read by the Conductor, NOT approved by the owner.** Nothing is built from this until he answers the open questions. Acceptance tests listed are proposed and unrun.


## 1. Problem

[measured] `input_changes` finds every historical occurrence of the pinned hash, then uses `at[-1]`. After A → B → A → C, this selects the restored A and returns only C. Both automatic source collection and the re-pin checker use this result. The decisive expression is `"i > at[-1]"` in `src/RimMandrake/rimflow/designer_stage.py:2244`, called at lines 2324 and 2436.

[measured] Accepted results currently store `"inputs": inputs(d, st, repo)` at `designer_stage.py:2030`. Re-pin updates selected hashes at line 2460. Neither write records a commit identifying the pin.

## 2. Why the attempts failed

- [measured] **Merge attribution.** The reviews found skipped side-branch changes, unnecessary merge citations, discarded edits charged to re-pin, and round trips hidden by unchanged merges.
- [measured] **Incomplete history.** A shallow boundary could become a false recorder.
- [measured] **Unreadable evidence.** A failed blob read could move the inferred anchor forward.
- [measured] **Split landings.** State and accepted artifacts could arrive in separate commits. An assumed exemption also accepted a mismatched recorder.
- [measured] **Branch ancestry.** A pin joining main from another branch could incorrectly inherit main’s earlier changes.
- [measured] **Renames.** Moving the concept folder could become a false recorder.
- [measured] **Timeouts.** One timeout escaped the CLI. Another implementation repeated the same timed-out lookup fourteen times.
- [measured] **Scope.** The final review identified the recursive walker and expanded implementation as exceeding the requested small fix.

## 3. Design

[guess ~85%] Touch only `src/RimMandrake/rimflow/designer_stage.py` and the existing `selftest_designer_stage.py`, `selftest_designer_repin.py`, and `selftest_designer_stage_land.py` in that directory. The following fields are **proposed additions**.

### Persist each input’s anchor

[guess ~90%] Add `pins` to each accepted result in `stage.json`. It maps each file dependency to a record containing `commit`, `hash`, and `path`. These hold the full commit SHA, the existing semantic input hash, and the repository-relative input path. Separate entries preserve the different boundaries created by partial re-pins.

[guess ~85%] `close_run`, beside the accepted-result construction at line 2030, writes these records for `done` results. Capture the concept clone’s HEAD with a bounded lookup and verify its input hashes. If an accepted artifact awaits landing, write `commit: null`. This explicitly represents an unfinished anchor.

[measured] `land_state` already receives `"PUBLISHED <sha>"` from the landing operation at lines 2137–2140. Its existing landing includes changed concept artifacts through `state_paths`, lines 2090–2105.

[guess ~80%] For unfinished anchors, `land_state` verifies the accepted hashes in that returned commit, fills `commit`, atomically writes `stage.json`, then publishes that metadata with one further bounded landing. The first published commit supplies the anchor. This handles split landings without a self-reference. Persist the returned SHA before the metadata landing so retries retain it. A lost publication receipt leaves the anchor unfinished and produces `UNMEASURED`.

[guess ~90%] In `repin`, beside lines 2460–2463, replace the anchor only for each successfully updated input. Use the verified committed snapshot already checked by re-pin. Preserve anchors for unchanged inputs and the exam inputs left stale.

### Read the recorded boundary

[guess ~85%] Extend `input_changes` to receive the input’s pin record and a transient plan context. The context contains `deadline` and `cache`. For recorded pins, issue **one bounded Git history call per distinct anchor and input path**, including the anchor, original parent relationships, commit messages, and complete input differences. Reuse its result throughout source collection and the dry checker.

[guess ~80%] Compute semantic transitions using the existing `input_hash` rules. The batch must supply complete file content through full-context differences, avoiding per-commit blob subprocesses. Bound collection and parsing by time, commit count, and output bytes. Incomplete output returns `UNMEASURED`.

[guess ~80%] Evaluate merges from the supplied parent graph. Follow post-pin parents whose input equals the merged input, including matching sides containing A → B → A. Discard a differing side when the merge keeps another parent’s input. Require a merge citation when it introduces an input value without a traced post-pin source. A pin arriving through a branch establishes its own ancestry boundary. Earlier changes on main stay before that boundary. Ambiguous attribution returns `UNMEASURED`.

[guess ~90%] An entirely absent `pins` field selects today’s legacy algorithm until the next successful pin. A present but missing, malformed, unfinished, or unreachable anchor returns a named `UNMEASURED` cause. A changed concept path also returns `UNMEASURED` until a deliberate new pin records its location.

### Bound Dispatch work

[guess ~85%] Give each re-pin plan one shared five-second measurement budget, including legacy tracing, source lookups, and dry validation. Every subprocess receives the remaining time. Cache completed lookups and abort the plan on its first timeout. Permit one later fresh measurement during application.

[guess ~90%] Dispatch may invoke these bounded checks and its existing landing route. Every added scan, Git traversal, parser, and subprocess must consume that budget. Automatic fetches, deepening, recorder reconstruction, and same-plan timeout retries are excluded from the design.

## 4. The four outcomes

[guess ~90%] Preserve the public tuple and exception shapes, with explicit reasons throughout the touched measurement paths.

| Outcome | Return and meaning |
|---|---|
| Could not look | [guess ~90%] `input_changes` returns `(None, "UNMEASURED <cause> ...")`. Examples include `git_timeout`, `history_incomplete`, `anchor_unreachable`, `pin_pending`, and `path_changed`. |
| Failed | [guess ~90%] A completed check finds an uncited change or invalid source. Return the existing refusal record with a `FAIL` reason, or raise `Refused` carrying it. |
| Zero | [guess ~90%] A numeric measurement may equal `0`, including a subprocess return code. Test it explicitly. Success also requires complete, valid output. |
| Empty set | [guess ~90%] `([], "")` means a completed trace found zero relevant commits. An empty source list still passes through the existing re-pin eligibility checks. |

[guess ~90%] `repin_sources` propagates measurement causes through its existing refusal fields. CLI and application paths catch `TimeoutExpired` and preserve `UNMEASURED`. Successful empty output, absent files, and failed reads receive separate handling. Failed reads never become empty bytes through `or b""`.

## 5. Alternatives considered

- [measured] **Reconstruct the recorder from history.** Three reviews found further failures involving ancestry, shallow boundaries, missing blobs, and renames.
- [guess ~95%] **Use the first matching hash or a commit date.** Repeated content and independently edited timestamps cannot identify the acceptance operation.
- [guess ~90%] **Store one SHA per stage.** A partial re-pin would advance the boundary for inputs whose earlier changes still require accounting.

## 6. Tickets

[guess ~90%] Each ticket adds its stated regression to the named existing selftest. Run that augmented selftest against today’s production code to demonstrate red, then against the change to demonstrate green. These proposed regressions have not been run.

| Ticket, one change each | Runnable acceptance command |
|---|---|
| [guess ~85%] Record initial anchors, including split landing and failed metadata publication. | `python3 src/RimMandrake/rimflow/selftest_designer_stage_land.py` |
| [guess ~90%] Update only successfully re-pinned input anchors. | `python3 src/RimMandrake/rimflow/selftest_designer_repin.py` |
| [guess ~95%] Replace hash reconstruction for recorded pins. A → B → A → C must require B’s source. | `python3 src/RimMandrake/rimflow/selftest_designer_repin.py` |
| [guess ~80%] Implement merge attribution, including branch-recorded pins and discarded sides. | `python3 src/RimMandrake/rimflow/selftest_designer_repin.py` |
| [guess ~90%] Keep absent-field legacy behavior and adopt anchors at the next pin. | `python3 src/RimMandrake/rimflow/selftest_designer_stage.py` |
| [guess ~90%] Preserve the four measurement outcomes through automatic and CLI entry points. | `python3 src/RimMandrake/rimflow/selftest_designer_repin.py` |
| [guess ~90%] Refuse incomplete ancestry, including shallow clones and missing anchor objects. | `python3 src/RimMandrake/rimflow/selftest_designer_repin.py` |
| [guess ~90%] Detect recorded-path changes and sparse omissions. Sparse-present inputs must work. | `python3 src/RimMandrake/rimflow/selftest_designer_repin.py` |
| [guess ~90%] Enforce the shared deadline. Fourteen stale pairs must stop after the first mocked timeout. | `python3 src/RimMandrake/rimflow/selftest_designer_repin.py` |

[measured] The supplied ticket additionally requires the integration command below. I read the implementation and tests, without running this suite or changing repository files.

```sh
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land
```

## 7. Open questions for the owner

- **Conductor's note:** the merge-attribution ticket in section 6 rebuilds the git-graph reasoning that three attempts failed on. The smaller option is to return `UNMEASURED` for any merge inside the range and require a deliberate new pin.

- [guess ~85%] **Accept the extra metadata landing for split pins?** Recommend yes. It provides a verified artifact commit while preserving the existing split-landing workflow. An interrupted receipt remains visibly unfinished.
- [guess ~85%] **Support automatic tracing across concept-folder renames now?** Recommend a named `UNMEASURED` refusal and a deliberate new pin. Rename reconstruction would expand this build.
- [guess ~80%] **Approve a five-second measurement budget per plan?** Recommend five seconds initially. Timeout refusals will expose whether it needs adjustment.