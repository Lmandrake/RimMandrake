# Bridge Validation Observatory — design

Status: DRAFT (planning pass, Opus 5.5, 2026-10-03). Nothing is built. Item to file when this is accepted:
`BRIDGE_VALIDATION_OBSERVATORY_1`.

## 0. Owner request

> *"Plan out a watching agent that can monitor when we are using the bridge to debug and validate using
> northstar. We need to be able to receive feedback and measurements to ensure we are being efficient in terms
> of validation script checks per second, bridge commands sent per minute, and checks passed. These metrics are
> intended to provide improvement signal. … How can we get really good at bridge validation runs?"*

**One-paragraph answer.** The watcher is a **deterministic script, not an LLM**: the bridge client and the
runner emit an append-only JSONL event stream (call start/end, component lifecycle, run identity); a cheap
offline `obs report` folds it into a per-run report after the run's own verdict is written; the existing
`belt_watchdog.py` shows one efficiency line read from that report and never depends on it. An LLM is
**optional**, called on an unfamiliar failure or a session review, never on a quota. The headline is not a
throughput number but three facts per run: **supported coverage of a versioned required-check manifest** (which
required checks produced supported evidence on this artifact), **findings** (new / recurring / resolved,
deduplicated by root cause) and **where the bridge-ownership time went**. The three requested numbers
(checks/sec, bridge commands/min, checks passed) are diagnostics *within a fixed workload*, never targets.

## Owner ruling 2026-10-03

Decision taken by question card (~21:20 PDT). A bridge run report **leads with REQUIRED CHECKS PROVEN**: the
per-mod must-have checks, each with a trustworthy pass/fail. Checks/sec, commands/min and checks passed are
**diagnostics underneath it, never targets**. This answers §8 Q1.

---

## 1. Baseline measured from tonight's runs (2026-10-03)

Every number names its instrument. "ESTIMATE" means derived from prose timestamps, not a machine record.
Sanity probes are listed where a zero or a round number could be a query bug.

### 1.1 Instruments that exist today

| instrument | what it records | per-call? | timed? |
|---|---|---|---|
| `Transient/belt_rerun<N>_20261003.txt` (runner stdout) | one line per component: `[tag] HH:MM:SS name VERDICT detail` | no | to the second, at verdict time |
| `Transient/modcheck/live_queue/situational_rerun/<Mod>_summary.json` | chains → components → `verdict`, `detail`, `evidence[{call,result}]`, `shows`, situational `ticks_spent`, surprises | **partly**: `evidence` lists calls made through `Suite._record` (`suite.py:592`), not every `session.call` | no timestamps |
| `Transient/modcheck/live_queue_results.jsonl` (`common.Job.finish`) | one row per job: started, finished, status, verdict, checks | no | job start/end |
| `.belt_state/heartbeat_<job>.json` (`belt_heartbeat.py`) | current step + its start, every 30 s, overwritten | no | yes, but **not retained** (overwritten) |
| `.belt_state/watchdog_last.json`, `watchdog_modals.json` | last watchdog CPU/NR sample; modal history | no | yes |
| `rimdrive.Session.calls` (`session.py:200`) | an integer counter | count only | no; never written anywhere |
| `northstar_driver/transport.py` `CallLog`/`TimedTransport` | per-call `(tool, ms, ok)` with p50/p95 by tool | **yes** | **yes** — but only the northstar_driver path uses it, and in memory |
| `JawaBenchArgGuard.cs` | server-side record of argument keys matching no declared parameter (Harmony prefix on `BindArguments`) | yes, drops only | no |
| `JawaBenchEventRecorder` | in-game events (damage, lineage), not bridge calls | n/a | game ticks |
| `Transient/belt_bridge_log_20261003.md` | the bridge agent's prose log: loads, hangs, kills, fixes | no | minute stamps, hand-written |

⇒ **There is no per-call bridge log on the live_queue path today.** Calls/minute, latency and retry counts are
UNMEASURED for tonight except through the `evidence` proxy below. That gap is step 1 of the rollout.

### 1.2 Numbers

Parsed by a throwaway script over `Transient/belt_rerun{1..16}_20261003.txt` (regex
`^\[tag\] HH:MM:SS name (PASS|FAIL|UNMEASURED)`), cross-checked against the per-mod summaries.

| metric | value | instrument / note |
|---|---|---|
| suite-runs (one mod inside one rerun) | **40** across 16 reruns (2 reruns produced 0 rows: launch-gate refusal, focus loss) | rerun stdout |
| component verdicts emitted | **1,830** = PASS 945 (51.6 %) · FAIL 130 (7.1 %) · UNMEASURED 755 (41.3 %) | rerun stdout |
| UNMEASURED by cause | surprise ended the chain **345** (46 %) · upstream failed, cascade **282** (37 %) · no bland map **60** · clock **2** · other **66** | detail-text classifier; "other" not inspected |
| distinct components represented in emitted verdicts (cascades included) | **378**; distinct components that ever FAILed **63** (130 FAIL verdicts) | rerun stdout |
| repetition | **23** components PASSed in every one of ≥5 appearances (**187** verdicts; their time cost and regression value are UNMEASURED — repetition is not proven waste); **27** components were UNMEASURED in every one of ≥3 appearances | rerun stdout |
| verdict throughput while a suite was active | 1,830 verdicts / 14,927 s of first-to-last-verdict span = **0.12 verdicts/s (7.4/min)** | spans exclude setup before a suite's first verdict, so this is an upper bound |
| burstiness | **891 of 1,790** inter-verdict gaps are 0 s (cascades and static def checks print together); the **60** gaps ≥ 60 s sum to **6,515 s = 44 %** of all span time | rerun stdout |
| the single costliest inter-verdict gap | before BlueDesert `thaw_toggle_off_mines_cleanly`: **2,093 s** over 6 runs (median 409 s, **14 %** of all span time). A gap is not the component's own execution time — it can include the chain's setup and waits. Bridge log 17:27 *hypothesises* the cause: `jawa/ordered_job queue=True waitTicks=1` at ~17 s per call (its "72 calls = 20 min" figure is that run's whole thaw chain, not this gap) | rerun stdout + bridge log |
| job wall time | 20 `situational_rerun` jobs recorded on 10-03: **16,545 s = 4.6 h**, of which 7 jobs (00:58–03:54, **8,490 s**) belong to an earlier session; 13 jobs from 08:33 onward = **8,055 s**. 6 of the 20 ended in ≤ 23 s (launch gate ×3, bland world, focus, smoke). rerun14–16 have no record (killed/still running) | `live_queue_results.jsonl` |
| evidenced bridge calls per suite (lower bound; `Suite._record` calls only, so this is a *selected* sample, not all calls) | 3,505 across the 18 latest summaries; Bacta 529, BlueDesert 509, LeaningScrub 427 … | `evidence[].call` in summaries |
| bridge calls by tool (evidenced) | `jawa/mod_settings_field` **864 (25 %)**, `spawn_pawn` 248, `list_things` 239, tick waits 208, `get_defs` 179, `pawn_need` 137, `inspect_string` 129, `execute_debug_action` 111 | same. A share of *evidenced calls*, not of time or of all calls — settings batching is a **candidate to measure**, not a proven win |
| cold loads | **≥ 10** today (load 11 in progress at 17:56). OBSERVED: the five with both ends logged, 21, 21, 20.5, 20.5, 18.5 min = **~101 min ≈ 17 %** of the 580-min window. EXTRAPOLATED (not measured): ~10 loads × ~20 min ≈ 200 min; overlaps the recovery rows below, so do not add them | bridge log, ESTIMATE |
| recovery intervals (ESTIMATE; several **contain** a cold load, so this is not additive with the row above) | stale/uncomposed deploy 08:36→09:06 (~30 min) · launch-gate refusals 09:06→09:37 (~31 min) · RealFoW wedge 12:53→13:20 (~27 min) · quest-loop hang 14:59→15:23 (~24 min) · `search_debug_actions` hang 15:33→16:01 (~28 min) · focus theft 15:23→15:28 · runner killed with its agent shell 17:06 · **≈ 2.4 h** | bridge log |
| taint | rerun3 Cauldron + LeaningScrub, rerun5 Cauldron + LeaningScrub + BlueDesert recorded while `Dialog_ModSettings` was open (modal_open) → tainted RED; rerun7 killed (map carried `RM_WS_TerminatorFront`) | bridge log 10:08, 11:00, 12:43 |
| runner occupancy | window 08:16→17:56 ≈ 9.7 h; runner job wall since 08:33 ≈ 8,055 s (jsonl) + rerun14/15/16 spans ≈ 4,980 s ≈ **3.6 h → ~37 %** of the window had a runner process alive. That is *occupancy*, not bridge activity — jobs also do local work, wait, or fail before any call; actual bridge-busy time is UNMEASURED | ESTIMATE (jsonl + rerun stdout spans) |
| **recorded north-star bar coverage** | **0** of 1,830 verdicts carried `shows=` (zero *recorded* owner-bar binding — not proof the behaviour was unvalidated); tonight's suites (Cauldron, BlueDesert, LeaningScrub, Bacta, WeepingStones, TheForge, BrainWorms) bind **no** owner bars. `modcheck floor --all`: 65 bars bind, all in FlowWorks 38 / Graffiti 8 / Pyrelands 19 | summaries + `floor`. **Sanity probe:** the same scan finds `shows` populated in `J1_situational_rerun/FlowWorks_summary.json` and two `Transient/northstar/*.json`, so the instrument can see it |
| bridge calls / minute, latency, retries, reconnects | **UNMEASURED** — no per-call record on this path | — |

**Observed bottlenecks and measurement gaps.** (1) Cold loads observed at ≥ 101 min (17 %) and plausibly about
twice that; recovery intervals of ~2.4 h overlap them; a runner process was alive ~37 % of the window — the
union of these is not yet measurable because there is no ownership timeline. (2) 41 % of emitted verdicts were
UNMEASURED and 83 % of those were a surprise or an upstream failure cascading down a chain. (3) One inter-verdict
gap (BlueDesert thaw) carried 14 % of suite span time. (4) Zero recorded owner-bar coverage. (5) Bridge calls,
latency and retries are not recorded at all on this path.

---
## 2. Goals and metric definitions

**Goal.** Every bridge-hour should buy as much *trustworthy new information about our mods* as possible, and
the observatory must make waste visible fast enough to act on within the same session. Metrics are improvement
signal for the runner and the suites; they are never a target the bridge agent is graded on (§6.1).

### 2.1 Units and the three classification axes

- **check** = one component (`suite.component(...)`), the unit the runner already prints. A *job check*
  (`Job.check`, 4–5 per situational_rerun) is a different, coarser unit and is reported separately.
- **required-check manifest** = a versioned list, per mod, of the components a run is *expected* to produce
  (generated from `validation.py`'s declared chains/components plus `shows=` ids; hashed and committed). Coverage
  is always measured against it, so deleting, renaming or deferring a check cannot silently raise a number.

Every component carries three **independent** axes, emitted explicitly by the runner (never inferred from an
exclusion list, so a new skip reason cannot default to "executed"):

| axis | values |
|---|---|
| **execution** | `not_started` · `started` · `completed` · `aborted` |
| **result** | `PASS` · `FAIL` · `inconclusive` (today's UNMEASURED, with a cause class: cascade / surprise / bland / budget / precondition) · `execution_error` (harness or tool fault — never counted as product information) · `skipped` |
| **evidence validity** | `supported` · `invalid` · `unknown`, each with reasons |

**supported** requires the component's own *recorded* preconditions (fixture present, setting read back from the
running game, intended job actually started, state observed after the act) and no contaminant *in the
contaminant detectors' covered interval*. Contamination detection reports its coverage: an interval the
watchdog did not sample (it samples every 5 min) is `unknown`, never `clean`. Contaminants are scoped to the
checks they can affect — a modal or focus loss invalidates tick-dependent checks; a static def read in the same
interval can stay supported.

**supported verdict** = execution `completed` ∧ result ∈ {PASS, FAIL} ∧ validity `supported`. This replaces the
earlier "valid verdict", which only meant "an assertion ran without a detected contaminant".

**Finding** = a supported FAIL linked to a stable issue id (ledger item or a deduplicated root-cause key: first
failing component of a cascade + detail class). States: `new` · `recurring` · `resolved` · `unconfirmed`
(seen once, not reproduced). One root failure is one finding, however many components it fails.

### 2.2 The three requested metrics, defined

| metric | definition | caveat |
|---|---|---|
| **checks/sec** | `completed components / suite-active seconds`, beside `emitted verdicts / suite-active seconds` | a throughput diagnostic **within a fixed workload** (same manifest, same mods). Emitted/sec rewards cascades (891 zero-second gaps tonight); completed/sec rewards splitting checks. Never compared across different workloads, never a target |
| **bridge commands/min** | logical requests per suite-active minute, split **by tool**, and per tool by each outcome dimension separately: transport (ok / timeout / reconnect), reply (`success:true/false`), retries (attempts per logical request), arg-guard drops (only when server-correlated, otherwise `unknown`); plus **requests per completed component** | rate is a load signal; requests per completed component is the efficiency ratio |
| **checks passed** | per run, against the manifest: supported PASS · supported FAIL · inconclusive (by cause) · execution_error · invalid/unknown validity · not reached | the headline is **supported coverage** (supported PASS + supported FAIL over manifest size), never PASS alone |

### 2.3 Recommended additional metrics

| metric | definition |
|---|---|
| **supported coverage** (headline 1) | supported verdicts / required checks in the manifest, for the stated artifact (deploy fingerprint) and environment (mod list hash, map recipe) |
| **findings** (headline 2) | new / recurring / resolved / unconfirmed, by stable id |
| **ownership timeline** (headline 3) | a **coarse** timeline of bridge ownership: `load` · `prep/deploy` · `suite` · `recovery` · `idle` · `unknown`. Exclusive and gap-free; anything unattributed is `unknown`, shown, not hidden. Finer tags (setup, tick-wait, tool latency, retry) are **nested measurements inside `suite`**, not exclusive buckets, until their precedence is defined |
| **cost per supported verdict** | suite-active seconds and logical requests per supported verdict, per suite and per chain — a *cost*, not a waste, signal |
| **yield per cold load** | supported verdicts and findings between two loads; loads that produced none |
| **recovery minutes** | per hang class from the runbook (focus, quest loop, RealFoW, modal, budget, stale deploy) |
| **inconclusive structure** | per chain: share lost to cascade and the root component; a component inconclusive for the same cause in every run is a **suite defect candidate** (27 tonight) |
| **north-star coverage** | owner-bound bars (`floor`) with a supported PASS on the current walk hash / bars bound |
| **observed outcome discordance** | (renamed from "flake rate") PASS↔FAIL flips between runs with recorded comparable identity — artifact, suite hash, mod list, fixtures, seed/state where known. Reported separately from execution_error and inconclusive flips. An identical map recipe alone is not comparability |
| **time-to-diagnosis** | first appearance of a finding → the commit or ledger close that names its cause |

Throughput-style summaries (e.g. supported verdicts per ownership hour) may be shown, but only **within a fixed
manifest**; across workloads they are gameable by splitting checks, choosing easy mods, or moving preparation
outside the ownership window.

### 2.4 Measurement rules — NORMATIVE (S0, 2026-10-03)

Implements the owner ruling above (required checks proven leads; throughput numbers are footer diagnostics).
Code: `src/RimMandrake/Utils/modcheck/required_checks_report.py`
(selftest `selftest_required_checks.py`); a rule changes here first, then in code, by commit with a reason.

**Required check.** An entry of the committed manifest `src/RimMandrake/Utils/modcheck/required_checks.json`,
generated by `required_checks.py` (`--check` reports drift). Three sources, each marked:

| source | what | owner? |
|---|---|---|
| `north_star_bar` | a must-show line of a VALIDATED, hash-matching `## north star` section | **owner** |
| `must_show_line` | a must-show line of a DRAFT section | agent-seeded |
| `script_check` | a `with t.component(...)` block in `validation.py` (id `chain/component`) | agent-written |
| `checkout_row` | a row the mod's checkout emits (walk header `checkout: <script>`, the script's `declared_rows()`) that no `script_check` already mirrors (id `checkout/<row>`); a mirroring `script_check` is marked `checkout_row` instead, never counted twice | agent-written |

`cannot_show` lines are listed but are not required (no component is obliged to claim them). The manifest
is read from walks and scripts, never written into them. A component declared only on a live branch is
invisible to the offline probe and appears in reports as *observed, not in manifest*.

**Three labels per required check.**

- **ran** — `completed` · `cascade` (an upstream component failed or a surprise ended the chain) ·
  `aborted` (a surprise, harness or budget guard ended this component) · `not_reached` (absent from the record).
- **result** — `PASS` · `FAIL` · `UNMEASURED` (with its cause: the script's own declared precondition,
  upstream-failure, surprise kind, harness, budget, unjudgeable).
- **evidence-holds** — `yes` · `no` (a taint applies) · `unknown` (nothing recorded proves it holds) ·
  `n/a` (no result to hold).

**Trustworthy (= proven).** ran `completed` ∧ result `PASS` or `FAIL` ∧ evidence-holds `yes`. A proven FAIL
is information, the same as a proven PASS. Anything else is not counted, and the report says why.

**Taints (evidence-holds = no).** Each is scoped to the run window it overlaps and the mods it names.

| taint | recorded by today | applies to |
|---|---|---|
| `modal-open` | a `modal_open` surprise in the chain, or an amendment | every check in that chain / window |
| `stale-deploy` | an amendment (deploy drift observed) | every check of the named mods in the window |
| `log-blind` | `situational.companion == false`, or an amendment (e.g. Player.log cap) | the chain / window |
| `focus-lost` | an amendment | the window |
| `upstream-failure` | the runner's cascade (`upstream failed`, `a surprise ended this chain`) | the component — it is not a result at all |
| `precondition` | chain not bland (`bland == false`, `bland_problems`, digest `unbland_chains`) | the chain |
| `unverified-calls` | `PASS(UNVERIFIED n)` | the component |
| `stale-result` | a checkout result whose `mod_hash` is not the mod's current hash | every row of that result |

A must-show line inherits the taints of every component that claims it (`shows=`), and is only judged by its
recorded screenshot verdict (YES → PASS, NO → FAIL, UNJUDGEABLE → UNMEASURED).

**Unknown is never clean.** evidence-holds is `unknown` when: no job row identifies the run (a killed job
writes none); the chain has no `situational` record (detector coverage unrecorded); or **no attestation
records the deploy as fresh** for the whole run window. Today no record carries a deploy fingerprint, so every
check is at best `unknown` — the report counts these separately as *pending deploy proof* so the one missing
instrument is visible, but never adds them to *proven*.

**Checkout results** (NORTHSTAR_RESULTS_JOIN_1, 2026-10-06). A mod whose walk names a `checkout:` script
(GimmeSomeSlack `proof_all.py`, FlowWorks `northstar/validation_v2.py`) is judged from that script's newest result
JSON with `mode` `live` (a partial or mock run is never read); the result itself is the run identity. The same
rules apply, nothing loosened: `mod_hash` ≠ the current mod hash → `stale-result` (the result is listed as stale);
running DLL (`env.assembly_sha256`) ≠ the repo DLL or its `.srchash` stamp → `stale-deploy` (compared only while
the hash is current) and unrecorded → unknown; deploy freshness needs a recorded fingerprint (`run_identity`) or
an attestation covering the run, and detector coverage a `situational` record, else unknown; a preflight row not
PASS taints every row `precondition`. A declared row missing from the result is not reached, an emitted row not
declared is *observed, not in manifest*, and a mod with a checkout but no live result is listed, never omitted.

**Amendments.** Taints and attestations that the run records cannot carry are appended to
`Transient/modcheck/obs_amendments.jsonl` (next to the records they amend, same lifetime; moves into §3.2's
store at S2): `{"kind":"taint","reason":…,"mods":"*"|[…],"from":…,"to":…,"source":"<log line>"}` or
`{"kind":"attest","what":"deploy-fresh",…}`. A taint needs only to overlap the run; an attestation must cover
it whole. A taint can only remove trust; nothing but an attestation backed by a recorded fingerprint adds it.

---

## 3. Instrumentation architecture

### 3.1 Where events are emitted

| emitter | file | events | cost |
|---|---|---|---|
| **bridge client wrapper** | `rimdrive/session.py` `Session.call` (single choke point for live_queue). `northstar_driver`'s `TimedTransport` stays separate until the counting contract is settled | `call_start` / `call_end` with a logical request id and an attempt id — tool, ms, each outcome dimension, bytes, context | two clock reads + a bounded in-memory enqueue |
| **runner** | `modcheck/suite.py` (`chain`, `component`, `wait_ticks`, `_record`), `runner.run_suite`, `live_queue/common.main` | `run_start/run_end` (with manifest hash and artifact identity), `suite_start/end`, `chain_start/end`, component **lifecycle** transitions with the three axes, precondition records, nested `phase` tags (setup/ticks/verify), `surprise`, `contaminant` | negligible |
| **heartbeat thread** | `belt_heartbeat.py` | it already knows step + budget; add an append of each **step transition** (not the 30 s beat) so the record outlives the overwrite | negligible |
| **watchdog** | `belt_watchdog.py` | `signal` events (verdict changes, modal seen, NR, log loop) — it already computes them | already paid |
| **companion (server)** | `JawaBenchArgGuard` drops; optional later: a server-side ring of `(tool, mainThreadMs, queuedMs)` read by one tool `jawa/bridge_stats` | lets us split *tool latency* into main-thread work vs queue wait vs frame-binding. Its own calls are tagged `instrumentation` and excluded from workload counts — they still cost bridge time and are reported as such | deferred until a report shows a decision gap |
| **ops log** | `rimflow`/`./game` and the bridge agent | `load_start/load_up`, `deploy`, `kill`, `focus_fix` — today these live only in prose (`belt_bridge_log`) | one CLI line per event |

### 3.2 Event schema (JSONL, append-only)

One line per event, one file per **run**: `D:\Luke\dev\_obs\runs\<run_id>.jsonl`; session index
`D:\Luke\dev\_obs\sessions.jsonl`. Outside git (like `_artpipe`): high volume, a program's input.

```json
{"v":1,"run":"20261003T164024-situational_rerun-27988","producer":"client:27988","pseq":412,
 "t":1791071234.512,"mono":8123.44,"ev":"call_end","req":"r311","attempt":1,"tool":"jawa/ordered_job",
 "ms":17043,"transport":"ok","reply_success":true,"argguard":"unknown",
 "ctx":{"mod":"BlueDesert","chain":"thaw","comp":"thaw_toggle_off_mines_cleanly","phase":"setup"}}
```

- **Identity and ordering.** `producer` (role + pid) and a **per-producer** `pseq`; there is no shared global
  sequence. `t` is wall time for joining producers, `mono` is per-producer for durations.
- **Hung calls are visible.** `call_start` is emitted *before* the socket write; a `call_start` with no
  `call_end` is a right-censored duration — exactly the hang class that today leaves no trace.
- **Logical requests vs attempts.** `req` is the logical call; `attempt` increments on retry/reconnect. Counts
  of "bridge commands" use `req`; retry storms use attempts.
- **Outcome dimensions are separate fields**: `transport`, `reply_success`, `argguard` (`unknown` until a
  server-correlated read exists).
- **Completeness is explicit.** `run_end` carries per-producer emitted/dropped counts; a run without it, or with
  drops, is `telemetry: incomplete` and every derived number is marked so. "No `pseq` gap" alone does not prove
  completeness (tail loss).
- **Lifecycle, not inference.** `component` events carry the three axes from §2.1 and the precondition records.
- **Late invalidation.** `amend` events (e.g. a modal later found open across an interval) are appended to the
  run file and to the retained record; reports and trends always re-derive from amendments, never from a frozen
  scorecard.

**Retention.** Raw run evidence is **not regenerable** — it is a record of what happened. Ordinary raw streams
expire after a retention window (open question 4), but the traces supporting a finding or an accepted experiment
are copied to `D:\Luke\dev\_obs\kept\` and never expire. Two committed outputs:
`infrastructure/state/obs/reports.jsonl` — the display summary per run — and
`infrastructure/state/obs/components.jsonl` — the **retained analytical record** (one row per component per run:
identity, three axes, cost, finding id), which is what discordance, findings and coverage history are computed
from. A few-hundred-byte scorecard alone could not support them.

### 3.3 Isolation contract (replaces "must never hang")

1. **Bounded bookkeeping in the execution path.** The emit call does two clock reads and a non-blocking put into
   a bounded in-memory queue. When the queue is full, the event is **dropped and counted**. No file I/O, no
   locks shared with the bridge socket, on the runner's thread.
2. **Separate failure boundary for the sink.** A daemon writer thread drains the queue to the run file. A slow,
   stalled or failing sink (locked file, full disk, a drvfs stall on `D:`) fills the queue and drops telemetry;
   it can never block a bridge call. Process exit does not wait on it beyond a 1 s bounded join.
3. **Authoritative result first.** `Job.finish()` writes the live_queue verdict exactly as today **before** any
   telemetry finalisation; `obs report` runs afterwards, as a separate process, offline.
4. **Health never depends on efficiency.** `belt_watchdog` reads `obs_last.json` with a size cap and a timeout
   inside its own try/except; a missing, malformed or stale file prints `EFFICIENCY unknown` and leaves the health
   verdict and exit code untouched. Folding runs in its own process, never inside the watchdog.
5. **Instrumentation calls are attributed.** Any bridge call made for measurement is tagged `instrumentation` and
   shown separately.
6. **Missing stream ≠ zero.** No stream, drops, or no `run_end` ⇒ `UNMEASURED(telemetry)`, never 0.

**Tests (S1 acceptance):** exact fake-call accounting (N logical requests on FakeWorld ⇒ exactly N `call_end`,
no duplicates); a call that never returns ⇒ one `call_start` without `call_end`; a stalled sink (writer blocked
for 60 s) ⇒ runner timing unchanged and drops counted; process kill mid-run ⇒ partial file readable;
concurrent producers ⇒ per-producer `pseq` intact. **Overhead** is judged by a controlled logger-on/logger-off
comparison on the same fixed workload (FakeWorld and a short minimal-list live suite), on end-to-end time **and**
tail latency of short calls — not by a per-event microbenchmark (1 ms on a 10 ms call is 10 %), and not against
tonight's noisy spans.

---

## 4. The watching agent

### 4.1 Recommendation: a deterministic script; an LLM only when a human-sized question appears

**Not an LLM in the loop.** Reasons, each from tonight:

1. **Cost and liveness.** A watcher that wakes every few minutes for ~10 h is hundreds of LLM turns to compute
   ratios a small script computes exactly. A backgrounded agent also dies at 600 s of silence (CLAUDE.md) —
   the worst property a watcher can have.
2. **Exactness.** Every alert below is a threshold over counters. Instruments here already return confident
   wrong numbers when a reasoning step stands in for a parse (`id` vs `item`, dict vs attribute); a script with a
   selftest does not drift.
3. **Judgement needs traces, not a scorecard.** A justified code change needs the representative trace and the
   suite source. So the LLM is **optional** and **on demand**: an unfamiliar failure, or a session review the
   operator asks for, with the report *plus* the relevant traces and suite file. There is **no** per-run review
   and **no** quota of filed items — a review expected to produce work will manufacture it.

So: **`obs report` (script)** runs offline after each run; the bridge agent (already an LLM, already reading
the runner's verdict line) is the operator who reads it.

### 4.2 Loop

```
during a run:   runner + client emit events (bounded queue -> writer thread -> D:\Luke\dev\_obs\runs\<run>.jsonl)
every watchdog cycle (300 s, existing --watch cadence), in a SEPARATE process:
    obs fold <active run> --since-last   (size- and time-capped) -> .belt_state/obs_last.json
    belt_watchdog reads obs_last.json and prints one EFFICIENCY line after its health verdict
after the runner's own verdict is written:
    obs report <run>  -> prints the report; appends reports.jsonl + components.jsonl (committed with results)
on demand:      LLM review with report + traces + suite source
```

### 4.3 Alert rules — a few, proven first

Start with the rules whose evidence is unambiguous; add others only after a week of reports shows a decision gap.

| rule (initial set) | fires when | alert text points at |
|---|---|---|
| `stale_artifact` | run_start deploy fingerprint ≠ repo for a mod under test, or mod-list hash ≠ the manifest's environment | redeploy; this run's verdicts are `invalid` for that mod |
| `telemetry_incomplete` | drops > 0, or no fresh event for 2 watchdog cycles while the heartbeat says a suite step is open | the observer, not the game |
| `retry_storm` | ≥ 5 timeout/reconnect attempts in 2 min, or one tool's error share > 50 % over ≥ 10 requests | run the watchdog remedy; likely hang class 2/7/8 |
| `call_open_too_long` | a `call_start` with no `call_end` for > 2 × that tool's p95 (or > the 30 s client timeout) | a hang in progress, seen before the timeout fires |
| `step_overrun` | a suite at 80 % of its budget (`BELT_SUITE_BUDGET_S`) | expect exit 4; note the step |

**Report-only tags (never alerts):** `idle_bridge` (bridge held, no suite, no load, 10 min), `cascade_heavy`,
`always_inconclusive`, `setup_heavy`, `slow_tool`, and `repeat` (classified by purpose: regression confirmation,
discordance sampling, recovery verification, or accidental duplicate). A long, valid operation does not trip
anything merely for producing no verdict yet.

### 4.4 Getting alerts to people without interrupt spam

The messaging doctrine says an interrupt must be worth waking someone. So **no alert sends a message.**

- **The bridge agent pulls**: its brief already says "call belt_watchdog every 5 min". The watchdog's output
  gains one `EFFICIENCY` line (worst open alert, `ok`, or `unknown`) after its health verdict. Health verdicts
  keep priority; efficiency never changes the exit code. Zero new interrupts.
- **The FOUNDRY seat pulls** the report at run end, beside the runner's verdict line it already reads.
- **The owner** sees the session trend page (§5) when he looks — never a push.
- The only push is the one that already exists: a WEDGED/DEAD health verdict. Efficiency alerts are never
  promoted to interrupts.

---

## 5. Reports and improvement signal

### 5.1 Per-run report (printed after the runner's verdict line, ≤ 8 lines; numbers illustrative)

```
OBS run 20261003T164024 situational_rerun  telemetry complete  artifact fp ok  manifest v3 (162 required)
  coverage: supported 98/162 (PASS 89, FAIL 9)  inconclusive 51 (cascade 31, surprise 20)  exec_error 2  not reached 11
  findings: new 1  recurring 2  resolved 1  unconfirmed 1
  ownership 41m: suite 37m  recovery 0  idle 4m  unknown 0   (inside suite: tick-wait 41%  tool 15%  setup-tagged 38%)
  requests 1,203 (29/min, 12.3 per completed)  attempts 1,210  open-at-end 0
  costliest: BlueDesert/thaw 20m (ordered_job 72 req, p50 17s) | LeaningScrub/defaults 33s
  north-star: bound bars with a supported PASS 0/65
```

### 5.2 Session trend

`obs trend [--since 7d]` re-derives from `reports.jsonl` + `components.jsonl` + amendments: supported coverage
per mod against its manifest, findings by state, yield per cold load, ownership-timeline shares, observed outcome
discordance, recovery minutes by class. Rendered on demand to a Transient HTML page (dark brown
theme, per owner preference) — a human reads it once.

### 5.3 Per-mod cost leaderboard

Rank (mod, chain) by **cost**: suite seconds and requests per supported verdict, with inconclusive and invalid
time shown as their own columns. Expensive validation is not necessarily wasted validation — the leaderboard
says where time goes; whether it is waste is a judgement made against the trace. Tonight's top row would have
been BlueDesert's thaw chain (2,093 s of inter-verdict gap over 6 runs).

### 5.4 From signal to action

| signal | concrete action | owner of the fix |
|---|---|---|
| one tool dominates a chain's time | **measure first** (per-request latency from S1), then try batching (e.g. `ordered_job waitTicks=0` for non-first orders — a hypothesis; it may not remove the latency) | Sonnet (suite) / companion |
| `mod_settings_field` ≈ 25 % of *evidenced* calls | candidate: one `mod_settings_batch` read/write per suite; settings snapshot once, restore once — only after S1 shows its time share | companion tool + suite helper |
| setup dominates | share setup across chains (one site, many chains), bland-world reuse (already exists: `--bland-world`), saved-base fixtures | suite authors |
| fixed `sleep`/settle in runner | replace with condition waits (the tick clock already verifies) | runner |
| repeated runs | **no automatic skipping**: identical code and map recipe do not imply identical execution (RNG, accumulated state, fixtures). Tag each repeat by purpose; drop only *accidental duplicates*, by hand | bridge agent |
| static checks (def resolve, patch landed) | candidate: cache per **load id**, only for checks whose inputs and invalidation are fully known (def dump fingerprint = live mod set) | runner + `refresh.py` |
| cascade-heavy chain | split: setup chain asserting its own preconditions, then independent checks | suite authors |
| always UNMEASURED | fix the precondition or delete the component; it costs time and says nothing | suite authors |
| many cold loads | batch deploys; load once, then run *all* changed mods; untested and new mods first (bridge log 17:51 already did this) | bridge agent |
| def-read repetition | cache `get_defs` results per load id inside the session | client wrapper |
| parallelism | **one game, one driver** stays (CLAUDE.md "one bridge driver"). Parallelism comes from offline prep and a second minimal-list game only if Windows can host two — open question | — |

---
## 6. How to get really good at bridge validation runs

### 6.1 The validity guard (comes first, because speed can lie)

Every efficiency change is judged against these, and a change that moves any of them the wrong way is reverted
regardless of its speed-up. They are *checks*, not a guarantee — each has a stated blind spot.

1. **Manifest coverage cannot drop silently.** Coverage is measured against the versioned required-check
   manifest; a deleted, renamed or deferred check shows as a coverage loss, not as a faster run.
2. **Fault injection proves the classifier.** A small fixed set of injected faults, run on the minimal list
   (and on FakeWorld where possible): *wrong fixture*, *refused operation* (`success:false`), *missing effect*,
   *unexpected effect*, *stale observation* (read before the act settles), *aborted execution*. Each must land in
   its intended class (FAIL / execution_error / inconclusive / invalid). A runner change that makes any injection
   misclassify is rejected. This is what catches a weakened helper, fixture or selector that an assertion-source
   hash cannot see.
3. **No unexplained verdict migration.** `obs ab` diffs per-component outcomes between arms; every
   FAIL→PASS or FAIL→inconclusive flip needs a cause (a code fix, or a recorded discordance). Blind spot: two arms
   sharing the same blind spot agree — that is why (2) exists.
4. **Negative controls.** Where a mechanism allows, a suite keeps a control expected to detect a known failure
   (toggle-off, broken input). A control **passes when it correctly detects the expected failure** and is never
   counted as a finding. A control that stops discriminating invalidates its chain's verdicts for that run.
5. **Contamination coverage is reported.** Unsampled intervals are `unknown`, not clean; validity is computed
   from detector output and run identity, never declared by the operator.
6. **PASS is never a target**, and neither is any throughput number. The trend shows findings by state beside
   coverage; a flat finding count is *not* auto-labelled — it can mean healthy software, weak checks or a narrow
   workload, and telling those apart is a review question (global CLAUDE.md: *"a rising score with flat findings
   is not progress"* — the report makes that comparison visible; a human or an on-demand review judges it).
7. **The grader is never edited to pass** (global CLAUDE.md). Thresholds and classifier rules change by commit
   with a reason, never mid-run.

### 6.2 Ranked practices (from the baseline; effects are hypotheses until measured)

1. **Stop paying for loads and recovery.** Observed ≥ 17 % of the window in loads, plus ~2.4 h of recovery that
   overlaps them. Batch deploys per load; check the deploy fingerprint and run `launch_gate.py` **before** the
   20-minute load, not after (a stale deploy cost ~30 min and invalidated Cauldron; launch-gate refusals cost
   ~31 min).
2. **Kill hang classes at source.** `search_debug_actions` banned from suites (done); RunInBackground set as a
   launch step (done live, make it permanent); RealFoW out of test lists (done); modal sweep at every chain start
   (done) recorded as a contaminant probe, so validity has a source.
3. **Fix the cascade structure.** 37 % of inconclusives were cascades and 46 % surprise-ended chains. Short
   chains with self-checked preconditions; surprises scoped to the chain's own fixtures.
4. **Aim at north-star bars.** Tonight recorded zero owner-bar coverage. Order the queue so mods with bound but
   unsupported bars run first, then changed mods, then the rest.
5. **Measure, then batch the hot tools.** S1 gives per-request latency; only then try `ordered_job` waits,
   settings batching, spawn/list batching. One batch tool in the companion is a one-minute cycle on the minimal
   list (rimbridge-companion skill).
6. **Classify repetition, don't skip it.** Repeats serve regression confirmation and discordance sampling; drop
   only the accidental duplicates.
7. **Profile before optimizing.** Every optimization cites the cost-leaderboard row and trace it claims to fix.

### 6.3 Experiments

**Protocol.** Judge on **total elapsed time for a fixed required workload** (same manifest), plus coverage and
fault-injection behaviour (6.1). Use **resettable paired trials**: each trial starts from the same saved base /
bland-world reset with settings snapshotted and restored, so fixtures, caches and settings do not carry over
from arm A into arm B; alternate or randomize arm order across trials; record seed/state identity. Report the
difference with its spread across trials (tonight Cauldron's span ranged 84–460 s on similar code, so a single
pair proves nothing); keep adding pairs until the interval excludes zero or the change is abandoned.

| # | experiment | hypothesis (unmeasured) | metric |
|---|---|---|---|
| E1 | `ordered_job waitTicks=0` after the first order in BlueDesert's thaw chain | lowers that chain's time (median inter-verdict gap 409 s/run); may not, if latency is not from the wait | chain seconds; outcomes unchanged |
| E2 | `mod_settings` batch read/write | fewer requests per completed component | requests/completed, elapsed |
| E3 | chain splitting on the top 3 cascade chains | cascade share of inconclusive ↓, supported coverage ↑ | coverage, elapsed |
| E4 | per-load cache of static def checks (inputs fully known) | faster first minute of each suite | elapsed; fault injection still classifies |
| E5 | bland-world reuse vs per-suite map | setup-tagged time ↓, contamination unchanged | elapsed, invalid count |

---

## 7. Rollout plan

Small steps, each with its own acceptance test. Safeguards and semantics come **before** anything that
recommends removing, skipping or batching work. Models per `infrastructure/agents/Agent_Policy.md`.

| step | build | acceptance | who |
|---|---|---|---|
| **S0** contract + baseline reconcile | Write the counting contract into this doc's §2–3 as code-facing spec: identity fields, the three axes, manifest format, ownership-timeline categories and precedence, completeness rules. Generate manifest v1 from `validation.py` for the suites run on 10-03. Reconcile §1 against the manifest | manifest for ≥ 7 mods committed; §1 restated against it with every number's instrument; owner answers Q1 | Opus |
| **S1** narrow client measurement | `Session.call`: `call_start`/`call_end`, logical request id + attempt id, separate outcome fields, bounded queue + writer thread, `run_end` counts. **live_queue path only**; no client unification, no context propagation beyond the run id and the current component name the suite already holds | the §3.3 tests: exact FakeWorld accounting (N requests ⇒ N ends, no duplicates), unfinished call visible, 60 s stalled sink leaves runner timing unchanged, kill mid-run leaves a readable partial file, logger-on/off overhead within noise on a fixed workload | Sonnet |
| **S2** component lifecycle + offline report | runner emits lifecycle with the three axes, precondition records, explicit skip causes, artifact/environment identity; coarse ownership timeline from run events + an `ops` CLI line for load/deploy/kill (replacing prose-only timestamps); `obs report` prints §5.1 | a live run's report reproduces the runner's own verdict lines exactly (counts per class) and every second of ownership lands in a timeline category, `unknown` included | Sonnet |
| **S3** guards before optimizations | fault-injection set (6.1.2), negative-control semantics, `obs ab` outcome diff, manifest coverage diff | every injected fault lands in its intended class; a planted FAIL→PASS flip and a planted deleted check are both reported | Opus design, Sonnet build |
| **S4** a few proven alerts | the five rules of §4.3 in a separate `obs fold` process; one `EFFICIENCY` line in `belt_watchdog` | synthetic stream per rule fires once; malformed/missing `obs_last.json` prints `unknown` and leaves health verdict and exit code unchanged | Sonnet |
| **S5** experiments | E1–E5 under the §6.3 protocol, each a separate change | each reports its paired difference with spread and passes S3's guards, or is abandoned | Sonnet |
| **S6** expand only on a demonstrated gap | live folding beyond the watchdog line, server timings (`jawa/bridge_stats`), the trend page, on-demand LLM review, `TimedTransport` unification | each lands only when a report showed a decision it could not support | as needed |

**First build step: S0 then S1.** S0 is a short design pass (no code beyond the manifest generator); S1 is the
first code: per-request start/end telemetry in `Session.call`, the one requested metric that cannot be measured
at all today.

---

## 8. Open questions

1. *(Answered 2026-10-03, see "Owner ruling 2026-10-03" above: required checks proven leads; the rest are diagnostics.)*
2. **Owner:** should north-star coverage gate the queue order (uncovered bound bars first), given only three
   mods bind bars today?
3. Can two RimWorld instances run concurrently on Archmagi (a minimal-list game for static/companion checks
   beside the full-list one)? UNMEASURED; it would be the only real parallelism.
4. Where does `D:\Luke\dev\_obs` get pruned? (Proposal: raw streams 30 days; `kept/` traces for findings and
   accepted experiments, plus the committed `reports.jsonl` / `components.jsonl`, forever.)
5. Modal contamination: the runner now closes modals at chain start — should it also *record* each probe
   (open/closed, type) per chain so validity has an exact source instead of the watchdog's 5-min samples?
   (Proposal: yes; it is one call it already makes.)
6. Does the bridge agent's prose log (`belt_bridge_log`) become `ops` events via a tiny CLI, or stay prose with
   a parser? (Proposal: CLI; the parser would be another confident-wrong-number instrument.)
7. Who owns the required-check manifest when a suite changes — regenerated on every `validation.py` commit by a
   hook, or by the suite author with a version bump? (Proposal: generated, hash-checked by `run_selftests`.)

---

## 9. GPT commentary

Consulted 2026-10-03 on the first draft via `src/RimMandrake/Utils/gpt_consult.py -m gpt-6.1-sol --effort high`
(model `gpt-6.1-sol`, reasoning effort **high**; no fallback was needed). Asked to attack metric gaming, observer
effects, missing signals, simpler alternatives, baseline interpretation and rollout order. Its verdict, verbatim:
*"I would approve a small measurement pilot, but reject the headline metric, skip policy, validity claims, and
rollout as written. … Its central mistake is equating **countable verdicts with trustworthy new information**."*

Its ranked criticisms, summarised faithfully:

1. **"Valid verdict" was much weaker than its name.** Executed + PASS/FAIL + no detected contaminant only means an
   assertion ran; it does not establish that it tested the intended behaviour (pawn never got the job; wrong
   fixture with a "success" setup; settings changed on disk but not in the running game; stale observation; a
   modal opening and closing between 5-minute samples; an infrastructure fault counted as a product FAIL).
   Conversely blanket taint over-invalidates static reads. Proposed three axes — execution, result, evidence
   validity — with "supported" requiring recorded preconditions, and contamination reporting its own coverage.
   The §6.1 guard was "useful checks, but not a validity guarantee": verdict agreement shares blind spots;
   assertion hashes miss weakened helpers/fixtures/selectors. Add fault injections (wrong fixture, refused
   operation, missing effect, unexpected effect, stale observation, aborted execution); a negative control
   *passes* when it detects the expected failure and is not a finding.
2. **The "new information" headline was gameable and the skip policy actively wrong.** `resolved distinct /
   bridge-hour` rewards splitting assertions, cheap static checks, easy mods, renaming, skipping repeats, moving
   prep outside the ownership window. *"skip it; it can only re-prove"* was called the strongest incorrect
   statement: identical code and map recipe do not imply identical execution, and repetition is how reliability
   is estimated. Replace with supported coverage of a versioned required-check manifest, new/confirmed findings
   (deduplicated by root cause, with stable ids), and ownership time; throughput only within a fixed workload.
   Delete the automatic `NO NEW INFORMATION` label — flat findings can mean healthy software, weak checks or a
   narrow workload.
3. **The observer could still hang the runner.** `try/except` does not help a write that blocks; line-buffered
   writes put filesystem work in the call path; `obs close` at run end could delay the result; folding inside
   the health watchdog couples them. Wanted: bounded in-memory enqueue, a separate failure boundary that drops
   on overflow, health that works when the collector is broken, final folding after the authoritative result,
   instrumentation calls attributed. Test stalled sinks, kills, partial records, concurrent emitters;
   *"`<1 ms/event` does not imply `<0.5%`: one millisecond added to a ten-millisecond operation is 10%"*; use
   logger-on/off comparisons, not tonight's noisy spans.
4. **Baseline over-claims.** Five timed loads are ~101 min ≈ 17 % of 580 min, not "a quarter"; recovery rows
   include loads, so they are not additive; 16,545 s is 4.6 h, not 3.7 h (scope unreconciled); job wall is
   *runner occupancy*, not "talking to the game"; the 25 % settings share is of selectively evidenced calls;
   "378 components exercised" counts emitted verdicts including cascades; 187 repeats are not proven waste; zero
   `shows` is zero *recorded* owner-bar coverage. Inter-verdict gaps are not component execution time. E1's
   "−15 min per run" exceeded the entire attributed cost (2,093 s over 6 runs); the 72 × 17 s figure needed a
   narrower scope, and removing `waitTicks` is a hypothesis. Rename "waste leaderboard" to "cost leaderboard".
5. **The schema could not produce several advertised metrics.** Completed-call events miss hung calls (needs
   `call_start`/`call_end` with a request id); logical calls vs transport attempts conflated; outcome dimensions
   overlap; arg-guard drops need server correlation (else `unknown`); one global sequence across emitters has no
   owner (use per-producer sequencing); no `seq` gap ≠ complete; "executed" inferred from an exclusion list
   defaults new skip reasons to executed; late taint needs amendments. Exclusive wall-clock buckets were
   underspecified — start with a coarse ownership timeline and nest finer tags. Rename "flake rate" to
   "observed outcome discordance" with recorded comparable identity.
6. **Too big for the evidence; mandatory per-run LLM review premature.** Most value needs a run manifest,
   ownership/load/recovery timestamps, component start/end/result with explicit skip causes, per-tool counts/
   errors/time, and one offline report. Remove S8's "files at least one accepted item" — *"That creates its own
   Goodhart pressure to manufacture work."* Raw evidence is not regenerable; a few-hundred-byte scorecard cannot
   support component-level history.
7. **Rollout put semantics and safeguards too late, and S1 too broad.** Alerts recommending skips/deletions
   came before the guard step that defines validity. S1 bundled logging, context propagation and client
   unification, and its "≥ evidence count" acceptance would pass duplicate logging. Back-to-back A/B on the same
   map has carryover; "three runs per arm" is arbitrary. Proposed S0 (contract + baseline reconcile) → S1 narrow
   client measurement → S2 lifecycle + offline report → S3 guards and controlled experiments → S4 a few proven
   alerts → S5 expand only on need. *"The highest-value first question is: **Which required checks produced
   supported evidence on this artifact, what prevented the rest, and where did the time go?**"*

Where I did not fully follow it: it suggested starting with operator review only; I kept the single
`EFFICIENCY` line in `belt_watchdog` (S4) because the bridge agent already polls that command every 5 min, so it
costs no new interrupt — but moved it behind the guards and made it unable to affect the health verdict.

## 10. Revisions I made because of it

All applied in place above (the first draft's wrong content was removed, not annotated — git holds it).

| # | criticism | revision | where |
|---|---|---|---|
| 1 | "valid verdict" too weak | three axes (execution / result / evidence validity); **supported** requires recorded preconditions; contamination reports coverage and is scoped to the checks it can affect; `execution_error` never counts as product information | §2.1 |
| 2 | headline gameable | headline is now supported coverage of a **versioned required-check manifest** + findings by state (root-cause deduplicated, stable ids) + ownership time; throughput only within a fixed workload | §0, §2.2, §2.3 |
| 3 | skip policy wrong | automatic fingerprint skip **deleted**; repeats tagged by purpose; static-check caching only where inputs/invalidation are known | §4.3, §5.4, §6.2, §6.3 |
| 4 | `NO NEW INFORMATION` label | deleted; flat findings are shown beside coverage and judged by review | §6.1.6 |
| 5 | observer could hang | isolation contract: bounded queue + writer thread + drop-and-count, verdict written first, folding in a separate process, watchdog health independent of `obs_last.json`, instrumentation calls attributed; stalled-sink/kill/partial/concurrency tests; logger-on/off overhead | §3.3 |
| 6 | schema gaps | `call_start`/`call_end`, logical request + attempt ids, separate outcome fields, `argguard: unknown` until server-correlated, per-producer `pseq`, explicit completeness in `run_end`, lifecycle events, `amend` for late invalidation | §3.2 |
| 7 | exclusive buckets underspecified | coarse exclusive ownership timeline with `unknown`; setup/tick/tool/retry are nested tags | §2.3, §5.1 |
| 8 | flake rate | renamed observed outcome discordance, with recorded comparable identity, separated from error/inconclusive flips | §2.3 |
| 9 | baseline over-claims | loads restated as 17 % observed + labelled extrapolation; recovery marked non-additive; 4.6 h job wall split 8,490 s earlier session / 8,055 s this session; occupancy ≠ bridge activity; settings share marked as evidenced-call share; "represented" not "exercised"; repeats not proven waste; "recorded" owner-bar coverage; inter-verdict gap ≠ execution time; summary rewritten as "observed bottlenecks and measurement gaps" | §1.2 |
| 10 | E1 estimate impossible | removed every unmeasured saving; experiments are hypotheses with metrics | §6.3 |
| 11 | waste leaderboard | renamed cost leaderboard | §5.3 |
| 12 | per-run LLM review + quota | LLM optional and on demand, with traces and suite source; no item quota | §4.1 |
| 13 | storage claims | raw evidence called non-regenerable; `kept/` retention for findings/experiments; committed `components.jsonl` as the retained analytical record | §3.2 |
| 14 | alerts before guards; too many | five unambiguous alerts only, after S3; the rest are report-only tags; no "no progress" alert on long valid operations | §4.3, §7 |
| 15 | rollout order, S1 breadth, A/B carryover | S0 contract → S1 narrow → S2 report → S3 guards → S4 alerts → S5 experiments → S6 on need; S1 acceptance is exact accounting, not "≥ evidence count"; resettable paired trials, randomized order, spread-based stopping | §6.3, §7 |
