# Routing a red supporting test


> **Status: Codex draft (gpt-6.1-sol), 2026-11-17, read by the Conductor, NOT approved by the owner.** Nothing is built from this until he answers the open questions. Acceptance tests listed are proposed and unrun.

## 1. Problem

[measured] `T_H_EXPLODE_PARSE` is an offline test marked `"support_only": true` in [test_table.json:706](/home/mandrake/rm/bench/design/concepts/GimmeSomeSlack/version/test_table.json:706); the bar lists it under `"supports"` at line 7244. Its current stamp is `PASS`. The approximately 16-hour ownership gap is reported in the supplied ticket, not reproduced here.

[measured] The missing connection is between execution and filing. [judge_certificate.py:113](/home/mandrake/rm/bench/src/RimMandrake/rimflow/judge_certificate.py:113) says `"Run every offline test"`, but `certify` examines `offline_decides` at line 188. [maturation_dispatch.py:960](/home/mandrake/rm/bench/src/RimMandrake/rimflow/maturation_dispatch.py:960) selects only certificate rows with `"REFUSED"` and clause `"green"`. A supporting failure therefore produces no repair item through this route.

## 2. Why the attempts failed

All findings below are [measured] from the supplied reviews, not independently rerun.

- **Blocking inputs:** a FIFO table or fingerprint member could hang observation.
- **Execution ambiguity:** missing tools, launch errors and timeouts looked like test failures; real signal failures disappeared.
- **Stale evidence:** old builds and changed commands could still trigger filing.
- **Missing-data ambiguity:** absent, sparse or unreadable observations sometimes became zero.
- **Beat interference:** scanning could consume the watcher’s remaining publication budget.
- **Ownership races:** deferred payloads survived changes to owners and failing tests.
- **False reopening:** a refreshed Dispatch timestamp revived the same old failure.
- **Incomplete coverage:** directory reads were mishandled; an actually failing test with a green stamp remained invisible.

## 3. Design

[guess ~90%] Extend the existing certificate-rerun worker. File supporting failures there once, using the filing portion of the red-decider route. Do not introduce an alarm, retry queue or builder launch.

**Files touched:** `src/RimMandrake/rimflow/judge_certificate.py`, `src/RimMandrake/rimflow/maturation_dispatch.py`, and the existing `src/RimMandrake/rimflow/selftest_maturation_dispatch.py`. All fields introduced below are **proposed**, not existing APIs.

[guess ~90%] In `judge_certificate.py`, extend `run_offline` at lines 120–151:

- Require a regular table before opening it. Reject nonregular fingerprint members, including files encountered beneath directories; retain directory-content hashing.
- Record launch/tool failures and timeouts as `runs_today.result="UNAVAILABLE"`. Preserve actual signal return codes as `FAIL`, including `-1`; exceptions without a process return code use `rc=null`.
- Recognize the existing missing-.NET diagnostics and exhausted `UtilAcceptVsock` launch diagnostic. [measured] Those diagnostics are documented in `Utils/winbuild.py:52–77,191–198`.
- Add two return fields: `unavailable`, a test-to-reason map; and `support_reds`, a test-to-evidence map. Each evidence record copies existing stamp fields `build`, `command`, `at`, `rc`, `result`, `last`, plus proposed `advisory=true`.
- Include only failures actually executed in this invocation, with unchanged command and matching content fingerprint after execution. A supporting test must appear in a bar’s `supports` and in no bar’s `decides` or `offline_decides`. Conflicting declarations remain decider work.
- Require `PASS` as well as rc 0 for resume skipping. Never manufacture supporting failures from old stamps.

[measured] `maturation.py:3446–3450` already carries the `run_offline` return value into certificate JSON as `run`; it needs no change.

[guess ~90%] In `maturation_dispatch.py`, extract the item-selection and filing portion of `cert_launch:1255–1284` for shared use. Preserve its existing decider caller. The worker uses only this portion, never the builder-launch portion.

[guess ~90%] Immediately after `cert_rerun_worker` parses certificate JSON at line 1179, read `run.support_reds`, even when the certificate itself passed. For each candidate:

1. Recheck current ownership under the existing ingest lock. Read ledger data strictly: unreadable or malformed ownership data means “could not look”, never “no owner”.
2. Reuse an open `known_red` item, or an existing route item whose identity matches the **full mod and test**, including previously allocated `_AGAIN` names. Truncated-name collisions must not reuse unrelated items.
3. Otherwise file one item using `cert_item_id` and `file_and_publish`. Mark its title **ADVISORY SUPPORTING** and include the full test identity, command, build and failing-run time. Preserve the route’s existing assignee.
4. Write the confirmed item into the test’s existing `known_red`, then publish the table through the worker’s existing path. A closed item is never reopened by a timestamp refresh; only a newly executed failure may justify a successor item.

[measured] `file_and_publish:1714–1715` currently returns `True` after any publisher response. [guess ~90%] Make success require confirmed publication. Record filing or publication failure explicitly; do not claim that the red acquired a published owner.

[guess ~90%] Add worker-result field `support_routes`: a test-to-record map containing existing-style `item` and `error` values. The worker writes it alongside the existing result at line 1194; callers and selftests read it. The tick does not consume it or act on it.

[measured] The worker already has `RuntimeMaxSec=RERUN_MAX_S`, currently four hours, at lines 1044 and 1149. [guess ~90%] Keep all added hashing, ledger reads and filing inside that bounded worker, with time reserved for recording its result. **The Dispatch tick gains no work:** no scan, git walk, subprocess, filing, retry or new trigger.

## 4. The four outcomes

[guess ~90%] Counts and empty collections are meaningful only with their accompanying error/completeness information:

| Return boundary | Could not look | Failed | Zero | Empty set |
|---|---|---|---|---|
| Table read | `(None, reason)` | Malformed data is unreadable, not a test failure | Never inferred from absence | Valid `tests={}` |
| Test stamp | `UNAVAILABLE`, explicit reason | Fresh `FAIL`, actual nonzero rc, including signals | `PASS`, rc 0 | No eligible test |
| `run_offline` | Global `error`, maps `null`; partial problems in `unavailable` | IDs in `failed`, supporting evidence in `support_reds` | `ran=0` with no global error means no execution | `{}` means no confirmed candidates; `unavailable` still shows incomplete observation |
| Ownership lookup | Explicit error, no filing | Filing returns false with reason | No matching owner after a complete read | Successfully read ledger contains no matching items |
| Worker result | `support_routes=null`, `error` explains | Per-test `error`; do not report routing success | Certificate `ok` remains about deciders | `support_routes={}` means no candidates, with run availability retained |

[guess ~90%] Advisory routing never adds a certificate refusal or changes gate `ok`. Missing final worker output means no result, never zero failures or zero ownership debt.

## 5. Alternatives considered

- [measured] **Watcher alarm:** rejected by the supplied reviews for beat overruns, deferred ownership races and reopening errors.
- [guess ~95%] **Make supporting tests block certification:** loses the required advisory behavior and changes what a bar means.
- [guess ~90%] **Scan stored stamps during Dispatch:** adds tick work and still cannot discover a failure hidden behind a green stamp.

## 6. Tickets

[guess ~90%] Each ticket adds its acceptance assertions to the existing `selftest_maturation_dispatch.py`, selected by the existing command below. Tests use temporary fixtures and fake filing, publication and launch effects.

```sh
python3 -B src/RimMandrake/rimflow/selftest_maturation_dispatch.py --cert-rerun
```

| Ticket: one change | Acceptance assertion added |
|---|---|
| 1. Separate unavailable execution from failure | Missing tool, launch exception and timeout are unavailable; real HUP/TERM are failures. |
| 2. Reject nonregular observation inputs | FIFO table and nested FIFO return promptly; a regular directory fingerprint remains valid. |
| 3. Return fresh advisory supporting evidence | A freshly red supporting row appears in `support_reds`; stale, command-changed and resume-skipped stamps do not. |
| 4. Share the filing-only ownership operation | Repeated calls reuse one matching item and launch nothing; unreadable ownership data cannot produce a second item. |
| 5. Report publication truthfully | Refused publication returns failure and never records successful routing. |
| 6. Connect the worker to advisory filing | A certificate passes while its freshly red supporting test gets one routed item; unchanged tick fixtures acquire no added calls. |

[guess ~90%] For each ticket, run the same updated selftest against today’s production sources and then the changed sources: its new assertion must fail on today’s main and pass afterward. These acceptance assertions are proposed, not claimed as already run.

## 7. Open questions for the owner

- [measured] Existing automatic reruns are triggered by stale **decider** certificates (`cert_rerun_decide:1072–1074`). [guess ~95%] **Approve discovery only when an existing rerun executes? Recommended: yes for this ticket.** This design cannot promise a maximum detection delay when no rerun occurs, or discover a hidden failure from a skipped green stamp.
- **Conductor's note on the next question:** RELENTLESS is a retired seat (owner, 2026-11-13), so "preserve RELENTLESS" is not a real option; the advisory item should go to the Conductor's lane.
- [measured] The existing filing route assigns `RELENTLESS` (`file_and_publish:1710`). [guess ~90%] **Keep that assignee or assign BENCH directly? Recommended: preserve RELENTLESS**, with an explicit advisory item, and leave automatic builder execution outside this change.