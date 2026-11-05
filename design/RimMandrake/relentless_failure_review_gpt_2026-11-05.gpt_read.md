# GPT deep skeptical review of Relentless failures, 2026-11-05 (raw answers, guidance not authority)

Model gpt-6.1-sol, effort high, via src/RimMandrake/Utils/gpt_consult.py. Three consults, files inlined. Prompts and bundles: consult A (structure, judges, gates, contracts), B (recovery, ownership, alarms, cheapest first), C (answered owner holds). Each answer restates its subject; checked. Verdicts on each claim live in relentless_recovery_plan_2026-11-05.md.

---

# Consult A (raw)

SUBJECT: A - STRUCTURE, JUDGES, GATES, CONTRACTS

## Findings

1. **BLOCKER — A defect label substitutes for evidence of causation.**  
   **Evidence:** `relentless_wall.py:37-39,521-543`; `relentless.py:4227-4246`; `relentless_game.py:1076-1085`.  
   `--defect` establishes FAIL without establishing that the instrument worked or that the assigned product caused the failure. Conversely, repeated “measured nothing” becomes a proof defect at the game dispatch boundary. Repetition establishes persistence, not responsibility. Attribution interception exists at `relentless.py:355-361`; its coverage is **outside this slice**.  
   **Concrete fix:** Require validated measurement and target attribution before a product return. Test `--defect "proof exited ENOSPC"`: it must create an environment incident, preserve the candidate, and increment no product-return counters.

2. **BLOCKER — Structured WEAK can discard unreachable evidence and close.**  
   **Evidence:** `relentless_wall.py:526-534,546-551`.  
   The structured `unreached` branch includes PASS, FAIL and UNMEASURED, but excludes WEAK. Consequently:

   ```python
   read_as("WEAK", "GAP:OTHER ...", [], ["required evidence: ssh denied"])
   # => ("PASS", None)
   ```

   With `GAP:DIFF`, the same inaccessible evidence instead becomes WEAK and reaches `proof_weak` handling.  
   **Concrete fix:** Without a validated product defect, required unreachable evidence must prevent PASS and proof-rework dispatch regardless of the supplied word. Test every verdict word against nonempty `unreached`, including both WEAK tags.

3. **MAJOR — Admission gates block repair without establishing relevance or readiness.**  
   **Evidence:** `relentless.py:3655-3662,4821-4845`.  
   `check_backlog_max` returns before considering any individual item—including system repairs. Separately, degraded health plus a queued system item pauses content even when that system item cannot launch because of an incident or pending help: those checks occur elsewhere, after pause computation.  
   **Concrete fix:** Apply backpressure to the actual constrained capability and count launchable demand. Test five candidates blocked on checker repair plus an independent repair item: the repair must remain admissible. Test a queued system item waiting on an incident: it must not imply that a worker place would help it.

4. **MAJOR — A broken live reader is encoded as a false predicate.**  
   **Evidence:** `relentless_reach.py:134-165`.  
   `live_reading()` catches reader exceptions and returns `holds=False`; `write_live()` renders that as `DOES NOT HOLD`. The Marker instructions then prohibit calling that reading unreached. This collapses “the predicate is false” and “evaluating it failed” before the Judge sees it.  
   **Concrete fix:** Preserve three states: measured true, measured false, evaluation failed. Inject an exception from `check()`: the packet must report measurement failure, never predicate falsity.

5. **MAJOR — Recovery permission replaces evidence that recovery happened.**  
   **Evidence:** `relentless.py:1206-1225`; `relentless_reach.py:117-124,177-183`.  
   `unhold()` clears `blind`, removing the evidence used to prevent an unchanged recheck. Any `offbox` entry bypasses all static uncovered-needs checks and disables `repays`; it need not cover the failed dependency.  
   **Concrete fix:** Preserve blindness history and require a successful probe of each failed dependency before retry. Test a git-history failure with only `steve_c_free` added: that unrelated adapter must not authorize rechecking git evidence.

6. **MAJOR — The ticket’s source failure is not an enforceable acceptance boundary.**  
   **Evidence:** `testq/ingest.py:197-219`; `relentless.py:690-698`; `relentless_wall.py:26-28`.  
   Ingest supplies a truncated title, not a reproduction or protected acceptance condition. The first worker authors the proof contract. The Judge is instructed to reject an easier contract, but cannot reliably reconstruct omitted obligations from that title.  
   **Concrete fix:** File a source-owned acceptance contract before builder admission. For a colonist-harm ticket, disabling the surprise detector must fail a protected fault-injection control even if the ordinary run becomes green.

7. **MAJOR — Fault correction is expressed as prose rather than a demonstrated dependency transition.**  
   **Evidence:** `testq/ingest.py:380-404`.  
   Quarantine annotates earlier verdicts as uncountable and repair sightings as host faults, then asks someone to drop unsupported tickets. This function shows no recomputation of the repair’s surviving evidence or its admission eligibility. What `FM.quarantine_move()` additionally does is **outside this slice**.  
   **Concrete fix:** Link tickets to individual sightings and their validity. Invalidating a sighting must recompute support automatically. Test a ticket with two sightings: quarantine one → retain it; quarantine both → withdraw unsupported repair work while retaining the audit trail.

## Answers Q1 Q3 Q4 Q7

**Q1 — Roots ranked by blast radius**

| Rank | Catalog roots | Assessment |
|---|---|---|
| 1 | **1, 5 — reading validity and cause routing** | Real, but “routing by word only” is overstated. Structured blindness, attribution interception and harness routing already exist. The missing invariant is that every product return requires valid, target-attributed evidence. |
| 2 | **3 — global gates** | Directly demonstrated. Backlog blocks all builder leasing; degraded pause depends on queued system work rather than demonstrated causal relevance. |
| 3 | **6 — acceptance easier than failure** | Real for the visible machine filer. “Nothing checks” is wrong: the Judge prompt checks semantically. The source contract needed to make that check dependable is missing. |
| 4 | **2 — amplification** | Partly demonstrated. There is per-cause/per-attempt deduplication, but no visible source-event identity or automatic withdrawal of unsupported repairs. |
| 5 | **4 — repair depends on broken machinery** | A repair can be blocked by the global backlog gate. Deployment/bootstrap claims beyond that are outside this slice. |
| 6 | **7 — owner discovers first** | Reported by the catalog; alarm delivery and escalation cannot be verified here. |
| 7 | **8 — missing levers** | Operationally plausible, but absence of a hold verb cannot be established from excerpts. Locking alone does not establish whether hand edits lack an audit record. |

**Missed root: conclusions outlive the evidence that authorized them.** Reading validity is one issue; invalidating dependent decisions is another. Fault-window reclassification must invalidate supporting sightings, contracts and affected verdicts. Recovery must positively establish readiness rather than erase failure history. Findings 5 and 7 expose both sides.

**Q3 — Decision procedure**

Classify **per obligation**, relative to the item’s assigned target. A broken harness can be PRODUCT failure for a harness-repair ticket and MEASUREMENT failure for the mod it was testing.

1. **Bind the observation.** Require item/criterion revision, candidate SHA, execution identity, instrument version, environment identity, timestamps and raw result references. Missing or mismatched identity → UNMEASURED.
2. **Validate prerequisites and instrument operation.** Did the intended build/save/load run? Were dependencies present, commands actually executed, outputs readable and controls successful?
3. **Classify responsibility using evidence:**

   | Class | Required evidence | Route |
   |---|---|---|
   | **PRODUCT** | Valid measurement of a violated obligation, with evidence locating responsibility in the assigned target. A red exit alone is insufficient. | Product builder; only validated product defects enter return/strike accounting. |
   | **MEASUREMENT** | Wrong invocation, broken oracle, inaccessible evidence, invalid contract binding, incomplete coverage, or failed instrument control. | Judge/reach/proof/contract repair lane; preserve product SHA. |
   | **ENVIRONMENT** | Identified failed prerequisite: account rejection, disk exhaustion, wrong game load, host fault, unavailable service; supported by resource/session receipts or a matching control. | Operations incident scoped to that dependency; preserve product SHA. |
   | **UNKNOWN** | Evidence does not establish the preceding classes. | Diagnostic wait/quarantine; no builder return or product strike. |

4. **Handle mixed results independently.** A valid product defect remains actionable while another clause is unreachable. Return only that validated defect; retain unresolved clauses as unresolved. Environment errors must not become additional builder requirements.
5. **Retry on changed evidence.** A relevant successful probe or corrected binding authorizes a retry. Elapsed time, repeated blindness or a different verdict word does not.

A legitimate WEAK means the Judge independently established the product obligations and demonstrated a proof gap. Route it to proof repair on the fixed product SHA. Distinguish that from an instrument unable to establish the obligations.

**Visible change points:**

- **`relentless_wall.read_as`, `521-543`:** normalize syntax; do not infer responsibility from prose or list presence. Fix the WEAK/unreached hole immediately.
- **`relentless.py:4227-4246`:** dispatch validated classifications before calling `fail()`.
- **`fail()`, `355-393`:** enforce the invariant before generation, return and strike mutation—even when callers bypass attribution.
- **`unmeasured()`, `441-465`, and `unhold()`, `1221-1225`:** retain candidate and failure history; require relevant recovery evidence.
- **No-verdict handling, `4197-4224`:** reaching `same_failure_limit` proves repeated missing verdicts, not product failure.
- **`relentless_game.py:1056-1085`:** retain harness routing, but require attribution before `dud`/`here` becomes `_back`. The helper predicates and `_back` may already add protections; that is outside this slice.
- **`relentless_reach.py:134-165`:** preserve evaluation errors separately from measured falsity.

**Q4 — Scoped gates**

| Gate | Appropriate scope | Leakage prevention |
|---|---|---|
| **Degraded pause** | Capabilities affected by the spent SLI: host, instrument/test family, lane or incident cause. An aggregate historical budget is insufficient to identify scope. | Match explicit execution dependencies. System/expedite status cannot bypass an unavailable dependency. Keep genuinely shared integrity/resource failures broad. |
| **`check_backlog_max`** | The actual checker pool/capability constrained by runnable candidates. Family scope applies only where families have separate capacity. | Preserve shared host limits and bounded queued capacity. Reserve repair/check capacity so backlog cannot block its own remedy. |
| **Account breaker** | The real shared quota/credential pool and operation, across all seats using it. Host launch faults require a different key. | Resolve account aliases to the same resource; coordinate one recovery probe; check every launch path. Per-item breakers would multiply retries. Current implementation is outside this slice. |
| **Token reserve** | Per running execution, aggregated against the actual funding/quota pool. | Separate reservations, estimates and measured consumption; release/reconcile on every termination path. Never present a reserve as measured spend. |
| **Clone/check reserve** | The actual disk/clone pool, usually shared by a host. | Preserve the shared physical ceiling; reserve enough capacity for checking and recovery. `pool_check_reserve` is distinct from token `run_reserve`. |

The visible rules describe token limits as advisory; the admission implementation is outside this slice. Do not assume `run_reserve` currently constitutes a global stopping gate.

Every gate needs a cause key, affected dependencies, evidence revision and recovery predicate. All execution paths—including checks, consults, staging and offbox readings—must enforce the relevant resource gates. A timer may authorize one probe, not unrestricted reopening.

**Q7 — Minimum machine-ticket contract**

The **filer**, using an Operations-owned detector template, must supply:

- **Identity:** ticket/schema revision, detector/version, responsible component and repair owner.
- **Source:** incident and sighting IDs; attempt, SHA, criterion, environment and immutable artifact references.
- **Validity:** provisional/confirmed/quarantined status and supporting sightings still considered valid.
- **Failure obligation:** observed versus expected behavior; explicit behavior the repair must preserve.
- **Reproduction:** executable procedure or fixture, prerequisites and expected baseline failure.
- **Acceptance:** exact predicates, required coverage, valid environment and evidence outputs.
- **Controls and prohibitions:** healthy control, fault control, and forbidden weakening such as disabling detection, widening tolerances or dropping rows.

The Conductor resolves incomplete attribution or missing prerequisites before builder admission. The builder may propose a contract amendment, but must not silently replace the source obligation. The Judge receives that authoritative contract and evidence references.

**Concrete refusal test:**

1. Execute the proposed acceptance procedure against the original failure fixture. It must detect the named failure.
2. Execute it against the repaired normal case. It must demonstrate the promised behavior.
3. Reintroduce the named fault under the candidate detector and routing. Detection must still work.
4. Verify the healthy control and required coverage.
5. Refuse acceptance if any required control is absent, unevaluable or produces the wrong distinction.

For colonist harm:

| Candidate behavior | Required outcome |
|---|---|
| Quiet, correctly staged site | Mod measurement completes. |
| Mod deliberately harms a pawn | MOD finding; harm remains observable. |
| Surprise check disabled | Fault control fails; ticket cannot pass. |
| Host-fault evidence invalidates the run | Quarantine/environment route; no product conclusion. |

An easier acceptance contract is a **CONTRACT refusal**. An unreachable control is **UNMEASURED**. Neither licenses a product rebuild. For intermittent failures, specify exposure and detection requirements rather than inventing a deterministic reproduction.

## Where my catalog is wrong

- **“Unhold no longer clears blindness” contradicts the supplied implementation.** It explicitly sets `st["blind"] = None` at `relentless.py:1224`. Other reach-repair protections may still prevent a launch.
- **155 system items do not prove permanent pause.** The visible predicate requires queued, non-clock-waiting, non-refused items—not merely membership in `system_items` (`relentless.py:3655-3662`). Blocking, holding or completing work can change that predicate.
- **The phantom-spend → degraded-pause causal chain is unverified.** Current measured-zero charging is fixed (`relentless.py:551-556`). The catalog names `infra_share` and `nightly_reds` as spent; it does not establish that inflated `returned_tokens_pct` caused this pause. `ops_health` is outside this slice.
- **Cause routing is not absent.** Attribution interception, binding repair, account-loss handling and harness handling are visible (`relentless.py:355-382,4187-4214`; `relentless_game.py:1056-1071`).
- **WEAK does not uniformly return work.** `GAP:OTHER` becomes PASS; untagged WEAK remains WEAK (`relentless_wall.py:546-551`).
- **Reach preflight exists.** It is incomplete and broadly bypassable, rather than nonexistent (`relentless.py:662-698`; `relentless_reach.py:117-124`).
- **The Steve gate is not exclusively retroactive.** Its documented contract also holds results awaiting a clean canary (`testq/ingest.py:23-25`); enforcement is outside this slice. Automatic withdrawal is absent from the shown quarantine function, not proven absent everywhere.
- **“Nothing checks an easier contract” is false.** The Judge prompt explicitly requires it (`relentless_wall.py:26-28`). The defect is insufficient authoritative input and enforceable controls.
- **Two throttles do not establish deadlock.** They establish backpressure and possible underutilization; a permanent cycle requires evidence that checking cannot drain the backlog.

## Design claims verified

- UNMEASURED has a separate, non-builder path (`relentless.py:441-465,4229-4232`).
- Harness-tagged game failures receive a separate infrastructure route (`relentless_game.py:1056-1062`).
- Missing health verdicts disable the degraded pause and prioritize fallback system work (`relentless.py:297-311`).
- System-priority membership exempts first-touch holding (`relentless.py:1777-1783`).
- Machine repair spawning supplies a title without an explicit acceptance contract (`testq/ingest.py:217-219`).

## Outside this slice

Actual SLI computation, history quality and freshness validation; account-breaker enforcement; attribution policy; reach-repair probes; game helper predicates and `_back`; quarantine’s downstream revocation behavior; alarm delivery; complete CLI verbs; deployment-version enforcement; and the claimed costs, durations and queue-wide outcomes.
---

# Consult B (raw)

SUBJECT: B - RECOVERY MODE, OWNERSHIP, ALARMS, CHEAPEST FIRST

## Findings

1. **BLOCKER — Unusable health rules produce `healthy`.**  
   **Evidence:** `ops_health.py:270-274,284-289`. Rule problems cause `b = {}`; consequently `spent = []` and `state = "healthy"`. The explanation admits “no budget read,” while the machine verdict asserts health.  
   **Why it matters:** breaking the health instrument can remove the degraded state. A missing ledger likewise leaves scheduling-relevant information unknown without changing that state.  
   **Concrete fix:** publish separate assessment validity and operational condition. Unusable rules mean `UNMEASURED`, with affected scopes named and a measurement-repair alarm. Test unusable rules, missing ledger and insufficient coverage independently; none may assert verified health.

2. **MAJOR — Historical budget debt selects every system item, without causal relevance.**  
   **Evidence:** `ops_health.py:244-253,272-289`. The system list contains all open items passing the classifier, ordered by hand rank, recurrence, prefixes, raised status and age. It is not restricted to repairs of the spent SLIs. `content_paused` is simply `state == "degraded"`.  
   **Why it matters:** an unrelated tooling backlog can receive priority during an incident without bringing recovery any closer. Conversely, a repaired service can remain historically over budget.  
   **Concrete fix:** distinguish historical budget debt, current impairment and the incident’s recovery work. Select recovery priority by an explicit `repairs_incident` relationship and readiness. Test one spent live-lane SLI alongside unrelated tooling work: unrelated work must not become a prerequisite for recovery. Actual lease behavior is outside this slice.

3. **MAJOR — Closing an alarm ticket can acknowledge an unchanged fault indefinitely.**  
   **Evidence:** `ops_watch.py:3646-3657,3658-3683`. For an OPEN alarm, no fresh news and no worsening causes an immediate return. Whether its item remains open is examined only after that return.  
   **Counterexample:** file an alarm, close its item without fixing the reading, keep the reading unchanged. With no new names or worsening, it stays OPEN in alarm state and produces no reopening here.  
   **Concrete fix:** check incident ownership and item closure before the “nothing new” return. An unresolved crossing needs a live owner and recovery deadline, even at constant severity. Test exactly this sequence.

4. **MAJOR — Alarm deduplication failure suppresses the alarm channel itself.**  
   **Evidence:** `ops_watch.py:3564-3573`. A non-object alarm state returns before conductor-line retries or alarm processing.  
   **Why it matters:** avoiding duplicate filings is reasonable; suppressing delivery needs an independently observed failure condition. This excerpt shows no durable notification for this return.  
   **Concrete fix:** an independent watchdog must detect alarm-state unreadability and lack of successful delivery passes. Preserve the damaged state, suppress ordinary mass filing, and raise one fixed recovery incident through a separate durable path. Test both persistent corruption and process death during repair.

5. **MAJOR — Fault quarantine retracts evidence by prose, without closing the resulting obligations.**  
   **Evidence:** `testq/ingest.py:389-404`. Existing verdicts get “must not be counted” notes; repair items get “drop this item if no sighting outside a window remains.” No structured verdict invalidation or repair disposition occurs in this function.  
   **Why it matters:** downstream consumers must interpret notes correctly; unsupported repair items can remain actionable. A fault-window overlap alone also does not establish that a genuine harness defect was absent.  
   **Concrete fix:** attach validity to each supporting sighting and verification. Recompute each ticket’s surviving support after quarantine. No valid support means *unsupported*, requiring explicit drop or park arbitration; valid independent support means keep. Test a ticket with both an invalid fault-window sighting and a healthy-host reproduction: it must survive.

6. **MAJOR — Machine repair intake has neither a visible acceptance contract nor reliable destination selection.**  
   **Evidence:** `testq/ingest.py:216-219`. Spawn supplies a truncated title, offline requirement and a hardcoded FOUNDRY destination for FlowWorks.  
   **Why it matters:** the visible call does not carry the failure signature, controlled reproduction, forbidden suppression fixes or pass condition. Recovery can admit expensive ambiguous work to a retired destination described elsewhere in the supplied material.  
   **Concrete fix:** file into quarantine with structured evidence and a contract template; resolve the current receiver before admission. Require a healthy-instrument reproduction and a negative control before accepting a repair. Any downstream contract enrichment is outside this slice.

7. **MAJOR — Churn combines a recent trigger with unbounded historical counts.**  
   **Evidence:** `ops_watch.py:2052-2063`. One failure must be recent, but `same` counts every supplied failure and `returns` comes from cumulative state.  
   **Counterexample:** two old failures of class A, followed much later by one unrelated class B failure, satisfy this function’s same-class condition if the old rows reach it.  
   **Why it matters:** recovery can quarantine previously troubled items for reasons unrelated to the event. Churn also identifies repetition, not whether the cause is product or instrumentation.  
   **Concrete fix:** report recent repetition separately from lifetime history, grouped by candidate, contract and environment versions. Test the old-A/new-B case. Caller-side filtering is outside this slice.

8. **MAJOR — The health verdict lacks the provenance needed to reconcile it after an event.**  
   **Evidence:** `ops_health.py:288-289` emits schema and timestamp, but no rules hash, collector revision or accounting revision. The supplied snapshot includes `SELFTEST_SOURCE_POLISH_STALE_SEVENTY_SUITES`, which the supplied rules explicitly put in `not_system`.  
   **Why it matters:** this discrepancy could be a classifier problem or simply different versions. The verdict cannot distinguish them.  
   **Concrete fix:** stamp rules, metric definitions, collector revision, accounting revision and source watermarks. Test replay against pinned inputs; identical inputs must produce the same verdict.

## Answers Q2 Q5 Q6, and the pause recommendation

**Q2 — Recovery mode**

Make recovery an incident-scoped process. A Steve failure, an account rejection and a broken Marker launcher need separate scopes, although one parent event may link them.

Proposed initial entry signals:

- Confirmed host fault or failed host canary: enter immediately.
- Explicit hard quota exhaustion or account authentication rejection: open the affected account circuit immediately. An ordinary transient 429 gets its stated backoff; repeated rejection of the controlled retry opens the circuit.
- Three checker deaths across distinct items within an hour, or three consecutive distinct-item deaths without a verdict: reuse the existing checker alarms.
- Three matching harness failures across distinct attempts and at least two items within 15 minutes: enter suspected recovery.
- A change to judging, accounting, gates or walls: start a reconciliation pass. A configuration change alone should not declare unrelated services failed.

These are proposed starting thresholds, not demonstrated optimal values.

| State | Entry and action | Exit |
|---|---|---|
| **NORMAL** | Ordinary admission. Continuously retain source-health history. | Event signal. |
| **QUARANTINE** | Persist incident ID, scope, uncertain onset interval and evidence. Stop affected admissions and retries; retain incoming records without leasing them. Fence conflicting transitions on already running items. | Inflow barrier and affected-attempt inventory recorded. |
| **RECONCILE** | Retract invalid readings structurally; group sightings; assign each resulting obligation drop, merge, park or keep. Restore the source through one canonical repair. | Source can be tested; affected obligations have dispositions or explicit parked reasons. |
| **VERIFY** | Run a healthy control and a known-bad control through the actual affected path. Reconcile accounting and SLI definitions. | Both controls behave correctly, readings are fresh, and no unresolved safety condition remains. |
| **RAMP** | Release one affected job, then a small batch. Confirm measurement completeness and useful completion. | Batch succeeds and the source stays healthy through a defined observation window. |
| **NORMAL** | Resume the scope. Parked obligations remain visible with wake conditions. | New evidence can reopen the incident. |
| **STALLED** | A recovery deadline expires or a required capability is unavailable. Retain the affected barrier, release unaffected scopes, and escalate one incident with a concrete next action. | New evidence, repaired capability or an authorized ruling. |

Do not require every ticket to finish before leaving recovery.

**Artefact versus real defect must be decided per sighting, not per ticket or filing timestamp.**

Required readings are the attempt interval; host boot/session and account identity; source-health observations around that interval; candidate, contract, oracle and harness versions; raw failure signature; actual versus estimated usage; and links to all supporting sightings.

Use these dispositions:

| Evidence | Disposition |
|---|---|
| The claimed test never ran, or its observation is demonstrably invalid; every supporting sighting is invalid and no independent evidence remains. | **Drop as unsupported event artefact**, preserving evidence and a reopening signature. This does not certify the product good. |
| Same invariant, compatible reproduction and same demonstrated cause, represented by several tickets. | **Merge** sightings under one canonical obligation. Preserve distinct acceptance clauses. Shared timing alone is insufficient. |
| Only correlation with a fault window; incomplete evidence; intermittent failure not reproduced; source still untrustworthy; or reproduction needs unavailable hardware. | **Park**, naming owner, missing observation and wake condition. Never automatically classify this as false. |
| Reproduces with healthy source and functioning controls, has valid pre-event evidence, or has independently established defect evidence. | **Keep**. Link it to the event if relevant. |
| The host/account/harness failure itself is established. | **Keep one source-repair obligation**. Dropping derivative noise must not drop the source defect. |

A passing rerun does not disprove an intermittent defect. A fault-window overlap does not invalidate an independently observed defect. A shared error string does not prove one cause.

Arbitrate cheap evidence first: existing receipts, valid later fixes, duplication and supersession, then controlled reproductions, then builder work. Prioritize repairs by safety, obligations unblocked and remaining effort. High sunk spend is a diagnostic signal, never a reason to discard real work. That preserves the supplied Conductor prohibition on trimming genuine work to save resources.

**Re-baselining must repair measurements without erasing outages.**

- Preserve raw history. Publish a versioned corrected accounting view with explicit adjustments.
- Replace an erroneous reserve charge only when actual usage is established. Measured zero remains zero; unknown usage remains unknown.
- Recompute affected aggregates from corrected attempts. Zero denominators are UNMEASURED.
- Retain genuine host downtime and failed measurements in reliability history.
- Start a new metric epoch when meaning changes; combine epochs only through a validated transformation.
- Separate “currently fit to resume” from “historical budget recovered.” Any temporary policy exception must be explicit, scoped and expiring.

To prevent recovery becoming another stuck state: persist its phase, owner, deadline and next observation; make transitions idempotent; bound probe attempts; and prohibit repeated paid probes on a timer without new evidence. Repeated symptoms attach to the existing event without resetting its age. After bounded quarantine, unresolved individual obligations become parked records, not a reason to hold unrelated work forever. A watchdog outside the impaired account or service owns recovery-controller liveness.

**Q5 — Ownership and alarms**

Operations owns measurement validity, source recovery, account circuits, incident correlation, budget computation, alarm delivery and recovery readiness. Programs execute the deterministic parts.

The Conductor owns cross-role arbitration, supersession and owner-ruling conflicts, assigning unresolved obligations, and bringing genuine human decisions to the owner. It should not have to rediscover machine state or manually rewrite the store. Neither role marks its own repair accepted; acceptance remains independent.

Use existing thresholds where supplied; the additional thresholds below are proposed initial values.

| Alarm | Signal and threshold | Route | Automatic action |
|---|---|---|---|
| **Host failure** | Confirmed fault/canary failure immediately; existing INVALID streak ≥3 | Operations; Conductor receives incident summary | Quarantine affected evidence and admissions; retain source-repair obligation. |
| **Account unavailable** | Explicit hard exhaustion/auth rejection; repeated controlled retry rejected | Operations; Conductor on missed recovery deadline | Circuit-break that account; one permitted probe at retry/reset time. Preserve neutralized forecast-runway policy. |
| **Checker launch/wall failure** | Existing >2 distinct lost items/hour or >2 consecutive distinct deaths | Operations; Conductor notified | Quarantine that checker profile; preserve candidates; launch diagnostic control. |
| **Harness burst** | Same normalized failure on ≥3 attempts and ≥2 items/15 min | Operations, Conductor for disputed grouping | Quarantine derivative tickets; create one incident, not N builders. |
| **Invalid/blind health** | Unusable rules immediately; stale health >45 min; required source outside coverage allowance | Operations | Publish invalid assessment and affected scope; measurement repair takes priority. |
| **Accounting inconsistency** | Measured-zero usage charged nonzero, duplicate attempt charge, or impossible total: any occurrence | Operations | Prevent invalid charge finalization; publish adjustment and recomputation work. |
| **Failed alarm delivery** | Alarm state unreadable immediately; delivery PENDING >15 min; no successful delivery pass >30 min | Independent watchdog → Operations → Conductor | One fixed incident through an independent channel; no bulk duplicate filing. |
| **Unowned/unresolved incident** | Urgent incident unacked >15 min, recovery deadline missed, or ticket closed while crossing persists | Operations, then Conductor | Reopen/reassign canonical incident; closing a ticket cannot clear the reading. |
| **Recovery or content starvation** | No phase evidence change for 30 min, phase deadline missed, or runnable content paused >60 min | Operations and Conductor | Enter explicit STALLED state where necessary; show blocked scope, owner and next observation. No automatic unsafe release. |
| **Item repetition** | Existing churn thresholds, calculated over the intended window; same candidate/contract/environment repeatedly unmeasured | Operations for shared cause; Conductor for item arbitration | Suspend identical paid retries; attach to source incident or park with a release predicate. |
| **Stale execution** | Existing books-behind >30 min; additionally deployed repair absent from running service after its deployment allowance | Operations | Reconcile deployment; verify running revision before claiming repair. |
| **Bad intake / stale owner showing** | Any machine ticket lacking receiver or acceptance fields; any showing behind a newer applicable ruling | Conductor, Operations for filer defect | Refuse admission/showing; retain one actionable correction record. |

An acknowledgement assigns ownership; it must not count as recovery. The supplied Operations instructions already say this. Apply that contract to ordinary alarms as well as incidents.

**Q6 — Cheapest high-leverage changes first**

1. **Correct health validity and add provenance.** Small output/decision change; prevents false health and makes reconciliation possible.  
   **Proof:** unusable rules, missing ledger and pinned-version replay tests.

2. **Fix unchanged-fault alarm reopening and independently monitor alarm delivery.** Reuse the existing durable alarm machinery.  
   **Proof:** close an alarm item while its value remains crossed; corrupt dedup state; kill a filing pass. Each yields one recoverable incident.

3. **Stop identical retries at the source.** Add account, checker-profile and harness-signature barriers before dispatch.  
   **Proof:** replay the checker-death and quota-rejection sequences; subsequent affected launches stop while unaffected work continues.

4. **Correct historical charges and window the churn calculation.** The catalog says the zero-usage charging fix already landed; verify it and repair its historical consequences.  
   **Proof:** attempt-level reconciliation; old-A/new-B churn fixture; before/after aggregates with unchanged raw history.

5. **Make quarantine invalidate support mechanically.** Replace “must not count” and “drop if…” instructions with structured evidence status and disposition.  
   **Proof:** all-invalid support drops or parks; mixed valid/invalid support survives; delayed fault discovery produces the same final state as early discovery.

6. **Require machine-ticket templates and current receiver resolution.** Cheap admission work prevents expensive ambiguity.  
   **Proof:** title-only and retired-receiver tickets cannot lease; a repair that disables its detector fails the negative control.

7. **Prioritize causal recovery repairs and introduce scoped pause behavior.** More scheduling work, but directly addresses starvation.  
   **Proof:** one defective live family cannot stop a healthy offline family; unrelated system backlog cannot prevent recovery.

8. **Persist the bounded recovery workflow.** Implement the state transitions above after the readings and levers work.  
   **Proof:** restart at every transition, replay every action, exhaust probes, and leave one hardware-dependent item parked. Recovery still terminates for healthy scopes.

**Pause recommendation**

The argument for a global pause is strongest when shared evidence, storage, accounting or execution cannot be trusted. Scope declarations may be incomplete, and continuing content can amplify damage or consume the repair capacity.

The argument for scoping is strongest when the impairment is demonstrably isolated. Historical budget debt and a broad system-item classifier are weak reasons to halt healthy work. A global pause also encourages priority exceptions that hide starvation.

**Recommend scoped pauses with a global safety fallback.** Declare which capabilities each item needs and which capabilities each incident invalidates. Unknown scope starts conservatively and narrows through controls. Reserve capacity for actionable recovery work; let verified unaffected work use remaining capacity.

A fresh owner ruling should raise priority, but should not certify a broken measurement path. Any explicit exception should name the affected item, reason, expiry and remaining uncertainty. Do not make “recent owner note” an automatic bypass.

## Where my catalog is wrong

- **The snapshot’s degradation is not caused by returned-token budget exhaustion.** That SLI has 20.75 bad hours and `spent: false`; `infra_share` and `nightly_reds` are spent. Correcting phantom spend alone would not clear this snapshot.
- **155 open system items does not establish a permanent pause.** `system_items()` filters openness and classification, not runnable queue state (`ops_health.py:249`). Actual scheduling conditions and future budget evolution are outside this slice.
- **“No cause routing” is too broad.** The supplied design explicitly gives structured unreached evidence a reach-repair route and distinguishes legitimate proof-only WEAK work. Whether all live implementations honor it is outside this slice.
- **The Steve gate is not described as exclusively retroactive.** `testq/ingest.py:23-25` also documents holding jobs pending a clean canary cycle. The visible retroactive function’s unresolved ticket disposition remains a real gap.
- **“No stale-code reading” is too broad.** The rules already alarm on books-behind age and deploy-update age. Neither proves the actual running process revision.
- **“Operations has no ownership/deadline machinery” would be wrong.** Its instructions already specify acknowledgements, `recover_by`, escalation and revisits. The exposed gap is their application to alarm lifecycle and recovery, not their conceptual absence.
- **Zero-usage charges do not automatically prove the reported ratio increased.** That depends on which charged runs enter its numerator and denominator. The calculation is outside this slice.

## Outside this slice

- `budget()` integration, gap handling, coverage requirements and historical unit migration.
- Current lease, pause, unhold, account-breaker and game-return implementations.
- Actual usage extraction, charging and returned-token aggregation.
- Fault-monitor onset detection and ingest’s executable front-door quarantine ordering.
- Consumers’ treatment of quarantined verification notes.
- Incident routing, dispatcher wakeups and independent alarm-delivery watchdog implementation.
- Whether snapshot, rules and deployed services share a revision.
---

# Consult C (raw)

SUBJECT: C - ANSWERED OWNER HOLDS NEVER RELEASED

## Design

The missing question identity is demonstrated. Creation records only prose and delivery metadata. However, `hold_is_his()` classifies a hold for routing. It does not itself enforce release authority, and the shown `unhold()` contains no owner-authorization check. “Only he can lift” is stronger than the visible enforcement. (`relentless.py:764–770`, `relentless.py:1169–1177`, `relentless.py:5011–5015`)

- **Key the decision being requested.** Require an immutable `question_id`, its revision, the required answer fields, and the item/decision scope it covers. Give each hold a unique `hold_id` to fence delayed releases. Cards and ledger rulings must explicitly reference that question revision. An item name, card timestamp, title similarity, or prose reason cannot identify the question.
- **Match exact references and complete decisions.** Accept an authoritative answer covering every required field for that revision and scope. Partial answers accumulate against the question without releasing dependent holds prematurely. One complete answer resolves every hold explicitly waiting on that decision. A “no” counts as an answer, with its consequence recorded.
- **Separate resolution from disposition.** Store the answer reference and resulting action before releasing anything. Permission to continue can resume compatible work. Changed requirements require re-planning with the ruling attached. Rejection requires the specified alternative or closure when the owner explicitly cancels the item. A bare “no” to an ambiguous question requires clarification.

The proposed event rules are deliberately stricter than “something changed on this item.”

| Event | When it resolves the hold | Result |
|---|---|---|
| Card answer | Authoritative, final, references the exact question revision, supplies required fields | Apply the recorded decision |
| Ledger ruling | Same matching requirements, or explicitly supersedes the referenced decision | Resume, re-plan, or close as ruled |
| `needs` change | Transition explicitly references the hold/question and records a valid disposition | Apply disposition. A bare assignment change only triggers reconciliation |
| Item re-route | Authoritative transition explicitly makes this blocker inapplicable or carries the required ruling | Retire that blocker and re-plan for the new route |
| Item closed | Closure belongs to the current item incarnation | Retire its holds and prevent further leasing |

A route change cannot establish owner permission by itself. Otherwise moving an item offline becomes a way to bypass an unresolved owner decision.

**Make resolution replayable and fenced.** Under the store lock, verify `hold_id`, question revision, current item lifecycle and answer authority. Record the consumed event, ruling attachment and disposition with the state change. Reconcile on every tick as well as on answer arrival, including answers preceding hold creation. Creation immediately sets `status="stopping"` and increments `gen`, whereas `unhold()` accepts only `"held"`. An answer arriving during stopping therefore needs a pending resolution applied after worker shutdown. (`relentless.py:765–769`, `relentless.py:1174–1177`)

Do not implement this by blindly calling existing `unhold()`. Its default branch queues the item, grants fresh spend grace and sets `needs_back`. Those effects require an explicit decision for automatic resolution, particularly after a re-route. (`relentless.py:1229–1233`)

**Alarm on invalid references separately from unanswered questions.** Validate that the referenced question exists, has an answerable schema and permits the designated authority to supply it. Alarm immediately for dangling references, incompatible revisions, retired unanswered questions and legacy prose-only holds. Name the item, hold, broken reference and responsible seat. Age alarms cover valid unanswered questions and complete answers awaiting application. Time alone cannot prove that an answer will never arrive.

## Failure cases and tests

- **Different question, same item.** Hold waits on art-regeneration permission. Owner answers a colour question. Assert the hold remains unresolved. The owner-queue documentation describes any later owner note as ending his turn, which is too broad for release matching. (`owner_queue.py:14–20`)
- **Partial answer.** Question requires permission and target scope. Permission arrives first. Assert no release until scope arrives.
- **Negative answer.** Owner rejects regeneration but requests reuse. Assert re-plan with that ruling attached. Explicit cancellation instead closes the item. Neither path resumes the rejected approach.
- **Shared decision.** Two holds reference one question revision within its declared scope. Assert both resolve. A third hold on another revision remains.
- **Bare routing changes.** Change `needs` or route without a decision reference. Assert reconciliation occurs without treating it as owner consent. Repeat with an explicit superseding disposition and assert the intended transition.
- **Stopping race.** Answer after hold creation but before `"held"`. Assert resolution survives shutdown and executes once, without concurrent old/new workers.
- **Lost or duplicate event.** Answer exists before the hold, notification is lost, or the supervisor crashes during application. Assert tick reconciliation reaches the same disposition once.
- **Replacement hold.** Delayed answer targets an earlier `hold_id` or question revision. Assert it cannot clear the replacement.
- **Closure race.** Close the item before answer replay. Assert no resurrection or new lease.
- **Accounting and routing.** Automatic release preserves existing spend accounting and does not overwrite a newer route through `needs_back`.
- **Unmatchable legacy hold.** Supply only `{why, kind, delivered, at}`. Assert an actionable migration alarm and no guessed answer match.
- **Unauthorized answer.** Builder or Conductor writes a decision without delegated authority. Assert it cannot discharge an owner-only requirement.

## Outside this slice

Card and ruling schemas, event delivery, closure/re-route implementation, worker shutdown, and actual `owner_queue` answer filtering are outside this slice. Their absence system-wide cannot be established here.

The incident chronology is catalog testimony. Its timestamps imply about **33 hours after the answer** and roughly **40 hours total held**. The excerpts establish the missing reference but cannot independently verify the lost time or whether another consumer attempted release.