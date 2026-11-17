# Landing checks in the builder’s gate

> **Status: Codex draft (gpt-6.1-sol), 2026-11-17, read by the Conductor, NOT approved by the owner.** Nothing is built from this until he answers the open questions. Acceptance tests listed are proposed and unrun.


## 1. Problem

[measured] The common landing door is `./publish`. Its `_publish()` runs `tree_checks()` and `pipeline_checks()` before calling `land()`. Those checks have no test-table selection today. Inside `land()`, a rebase and possible DLL rebuild precede the push, so the final candidate can differ from the earlier checked commit. [publish.py:801](/home/mandrake/rm/bench/src/RimMandrake/Utils/publish.py:801) [publish.py:541](/home/mandrake/rm/bench/src/RimMandrake/Utils/publish.py:541)

[measured] GSS’s `offline_gate()` runs a fixed list and returns `"red"` and `"steps"`. Its list omits `T_STUB_ART_CENSUS`, which the table maker describes as checking “every texture under Textures/”. The existing generic runner also treats timeouts as “UNMEASURED, not refused”. [proof_all.py:218](/home/mandrake/rm/bench/src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py:218) [make_test_table.py:54](/home/mandrake/rm/bench/design/concepts/GimmeSomeSlack/version/make_test_table.py:54) [publish.py:768](/home/mandrake/rm/bench/src/RimMandrake/Utils/publish.py:768)

## 2. Why the attempts failed

[measured] The two supplied reviews report these finding classes.

- **Containment**. Internal timeout and caller cancellation left descendants running.
- **Initial publication**. An unconditional comparison with `origin/main` refused an empty remote.
- **Selection**. Table definitions, declared inputs and cross-mod changes escaped verification.
- **Coverage**. The first implementation hard-wired GSS.
- **Cost**. A metadata edit selected 82 commands with 66 minutes of recorded runtime.
- **Evidence publication**. Recording a red result triggered the red check again and blocked publication.
- **Sparse checkout**. Missing tooling either bypassed enforcement or broke unrelated publication.
- **Verdicts**. Exit zero carrying `UNMEASURED` was accepted.
- **Validation coverage**. Passing fixture selftests left production and Windows-backed landing unverified.

## 3. Design

[guess ~90%] Extend the existing **publisher-side offline gate** with a dedicated landing-check phase. Insert it in `land()` immediately after the “nothing local left to push” branch at line 549, before `before_push()` and the push. Run it against the exact `head` being submitted, including `Stranded.tip`. Each rebase retry checks its resulting candidate. GSS’s `offline_gate()` calls the same landing runner before its return at line 251.

[guess ~90%] Add these **proposed configuration fields** to existing `publish_tree_checks.json`.

| Field | Writer and reader |
|---|---|
| `landing_deciders` | Reviewed registration map, keyed by mod. Read by the new landing phase and GSS gate. |
| `landing_deciders.<mod>.source_roots` | Explicit repository directory paths. Read during changed-path selection. |
| `landing_deciders.<mod>.tests` | Explicit existing test-table IDs. Read to resolve `file`, `command` and `reads` from that mod’s table. |
| `landing_timeout_s` | One proposed 60-second deadline covering selection, candidate materialization, all selected deciders and cleanup. Read by the supervisor. |

[guess ~90%] Initially register GSS’s `T_STUB_ART_CENSUS` and ExplosiveKnockback’s `T_CENSUS`. This is a general registration mechanism with two initial entries. [measured] Both commands passed here, taking approximately 0.17 and 9.74 seconds respectively. Those are individual runs, rather than a measured landing budget.

[guess ~90%] Select registered checks when the change touches their mod’s source root, their test file, a declared `reads` path, their table definitions or their registration. Compare directory paths by component prefix. Use the union of base and candidate dependencies so deletions remain visible. Compare a first publication with an empty tree. Git errors produce an unreadable outcome.

[guess ~90%] For table-only changes, compare parsed tables after removing only `tests.*.runs_today`. A difference confined to those stamps selects nothing, including a recorded red. Definition changes trigger checks. Replace ExplosiveKnockback’s prose read `"src/RimMandrake (every storage ThingDef)"` with `"src"`, matching its actual XML traversal. Its external `defs.sqlite` remains a required runtime input. [measured] The prose declaration and traversal are present today. [table:197](/home/mandrake/rm/bench/design/concepts/ExplosiveKnockback/version/test_table.json:197) [storage census:71](/home/mandrake/rm/bench/src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_storage_census.py:71)

[guess ~90%] Read configuration and tables from Git objects, then execute in an isolated checkout of the pinned candidate using the existing `full_head_tree()` pattern. Give that helper an explicit candidate and remaining deadline. A parent-independent supervisor watches a caller-liveness pipe and the deadline. It owns the worker’s process group, kills that group on cancellation or expiry, and reaps before returning. Registered commands share that group. This ownership must pass the cancellation acceptance test before use.

[guess ~90%] The complete file inventory is below. Each path exists today.

| Files touched | Change |
|---|---|
| `src/RimMandrake/Utils/publish.py` | Selection, bounded supervisor, candidate checkout and landing-phase integration. |
| `src/RimMandrake/Utils/publish_tree_checks.json` | Explicit registrations and deadline. |
| `src/RimMandrake/Utils/selftest_publish_tree_checks.py` | Selection, outcome, deadline, cancellation and sparse regressions. |
| `src/RimMandrake/Utils/selftest_publish.py` | Actual landing refusal, first-publication and rebase regressions. |
| `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py` | Shared landing checks inside `offline_gate()`. |
| `src/RimMandrake/GimmeSomeSlack/northstar/selftest_proof_all.py` | Gate regression with existing expensive steps stubbed. |
| `src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py` | Explicit unreadable verdict for instrument failures. |
| `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_storage_census.py` | Explicit unreadable verdict and terminal failure verdict. |
| `design/concepts/ExplosiveKnockback/version/pilot_throwaway/make_test_table.py` | Machine-readable `T_CENSUS.reads`. |
| `design/concepts/ExplosiveKnockback/version/test_table.json` | Matching generated declaration. |

[guess ~95%] Dispatch’s added tick work is zero scans, zero Git walks and zero subprocesses. Execution belongs to the builder’s landing process. Full-table execution belongs to certificate workers. [measured] The existing certificate worker already publishes changed tables, which makes stamp-only publication essential. [maturation_dispatch.py:1182](/home/mandrake/rm/bench/src/RimMandrake/rimflow/maturation_dispatch.py:1182)

## 4. The four outcomes

[guess ~90%] Every new selection or execution return uses one temporary record containing `sha`, `result`, `selected`, `ran`, `failed`, `error`, `seconds` and `steps`. Each `steps` entry, keyed by mod/test ID, contains `result`, `rc` and `last`. The worker writes it, the publisher reads it, and GSS stores it under proposed `steps.landing_deciders`.

| Outcome | Required representation and decision |
|---|---|
| **Could not look** | `result=UNMEASURED`, explanatory `error`. Unknown lists/counts are `null`. Timeout, missing input, malformed output and startup failure refuse landing. |
| **Failed** | `result=FAIL`, identified failing steps and nonempty `failed`. Refuse landing. |
| **Zero** | Completed checks, `result=PASS`, numeric `ran>0`, `failed=[]`. Permit landing. Zero means zero failures. |
| **Empty set** | Successful selection, `result=EMPTY`, `selected=[]`, `ran=0`, `steps={}`. Permit landing. |

[guess ~90%] Require matching terminal verdict and exit status from registered deciders. Worker exits are 0 for PASS/EMPTY, 1 for FAIL and 3 for UNMEASURED, accompanied by the record. Preserve partial failures when another check becomes unreadable. Publisher refusals include the record. GSS adds both FAIL and UNMEASURED entries to existing `red`, preserving enforcement through existing callers.

## 5. Alternatives considered

- [measured] **Full table in a push hook** lost on measured runtime, evidence-publication deadlock and sparse-checkout failures in the supplied reviews.
- [guess ~95%] **GSS-only insertion** loses general mod coverage. The shared registered phase supplies the common door.
- [guess ~90%] **Certificate stamps alone** lose immediate execution against the final landing candidate.

## 6. Tickets

[guess ~90%] Each ticket first adds its regression to the named existing selftest. Run that command against today’s implementation with the new assertion present, then against the fix. These red/green expectations are proposed and unrun.

| Ticket, one change each | Acceptance assertion | Runnable command and selftest |
|---|---|---|
| Explicit registration | A second registered mod selects its red check. Unregistered long commands stay unselected. | `python3 -B src/RimMandrake/Utils/selftest_publish_tree_checks.py` |
| Machine-readable dependencies | A ColdStorage XML edit selects ExplosiveKnockback’s census. | `python3 -B src/RimMandrake/Utils/selftest_publish_tree_checks.py` |
| Stamp-only filtering | Recording a red stamp selects nothing. Changing its command selects it. | `python3 -B src/RimMandrake/Utils/selftest_publish_tree_checks.py` |
| Four-outcome protocol | Missing census inputs produce UNMEASURED. Failure, zero failures and empty selection remain distinguishable. | `python3 -B src/RimMandrake/Utils/selftest_publish_tree_checks.py` |
| Shared deadline | Several sleeping checks exhaust one deadline, with explicit unreadable results. | `python3 -B src/RimMandrake/Utils/selftest_publish_tree_checks.py` |
| Cancellation ownership | Timeout and killing the publisher release a descendant-held lock within the cleanup bound. | `python3 -B src/RimMandrake/Utils/selftest_publish_tree_checks.py` |
| Candidate materialization | A sparse candidate with a red out-of-cone input refuses. Dirty worktree repairs cannot hide it. | `python3 -B src/RimMandrake/Utils/selftest_publish_tree_checks.py` |
| Initial-publication selection | An empty remote checks the initial candidate and successfully lands a green fixture. | `python3 -B src/RimMandrake/Utils/selftest_publish.py` |
| Landing integration | A registered red mod commit leaves the remote unchanged, including after a peer-induced rebase. | `python3 -B src/RimMandrake/Utils/selftest_publish.py` |
| GSS gate integration | A red registered census appears in `offline_gate().red`. | `python3 -B src/RimMandrake/GimmeSomeSlack/northstar/selftest_proof_all.py` |

## 7. Open questions for the owner

- [guess ~90%] **Approve the existing `./publish` gate as the common builder door?** Recommended yes. Its selected checks also apply to other publishers changing declared inputs.
- [guess ~85%] **Approve both initial registrations and a 60-second ceiling?** Recommended yes. ExplosiveKnockback’s broad `"src"` dependency adds roughly ten measured seconds to source-change checks. End-to-end deadline and cancellation behavior still require the proposed tests.