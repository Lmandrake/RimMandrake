# Art Regeneration Registry + Dashboard Hub — design (ruled 2026-09-11)

Owner asked for a system tracking the massive art regeneration: what is
registered to regenerate, queued, regenerated, reviewed/accepted, rejected,
accepted-as-something-different (original sent back), iterations spent, tokens/
money spent, and overall status while the target keeps expanding. All four
structural calls below were ruled by question card, 2026-09-11 (BENCH sitting).

Foundation: `ART_PIPELINE_DAEMON_1` (daemon, queue dirs, `throughput.jsonl`
per-request telemetry) — this design adds the layer ABOVE the queue. Nothing
here changes the daemon's contract.

## 1. The registry — one event ledger, one CLI

`infrastructure/artpipe/registry.jsonl` — append-only events, rimflow pattern:
events are truth, views are derived, never hand-edited.

**RULED — one CLI owns every write**: `src/RimMandrake/Utils/artpipe/artreg.py`
(daemon, sheet-consumers, seats all write through it; one schema, one lock, no
raw appends, no hand edits).

**Identity**: a **target** is the thing that must exist —
`<asset_key>/<facing>` (e.g. `vaewaste_megatardi/east`). A **job** is one
generation attempt against a target; job ids stay as the daemon knows them
(`vaewaste_megatardi_v1_east`), and every `queued` event records
`{target, job_id, iteration}`. Iterations are counted from `queued` events,
never parsed from filenames.

**Event types** (all carry `ts`, `by` seat, `target`):
- `registered` — with `source` (which verdict sheet / wave / ruling added it).
  The expanding target is honest because every scope step names its source.
- `queued` — `{job_id, iteration, notes}` (notes = owner's reject feedback
  carried into the next attempt's constraints).
- `generated` — `{job_id, elapsed_s}` (join to `throughput.jsonl` on job_id
  for meter deltas; the registry does not duplicate telemetry).
- `validated` — `{job_id, verdict: pass|fail}` (the daemon's own re-run of the
  validator, never the worker's self-report).
- `sheeted` — `{sheet}` (which review sheet row it landed on).
- `verdict` — `{result: accepted|rejected|repurposed, notes, as_target?}`.
  **`repurposed`** is first-class: accepted AS `as_target` (closes that
  target) AND auto-re-registers the original target as still owed, `source:
  "repurpose of <job_id>"`. This is the "accepted as something different but
  the original was sent back" case.
- `committed` — `{repo_path, sha}`.
- `deployed` — flag only; deploys stay FOUNDRY's.

**RULED — done = committed to repo.** The burn-up's completed line and the
projection count targets with a `committed` event. `deployed` is a visible
flag, not a gate on done. `accepted` (at sheet) is a visible pre-state.

**RULED — retry cap 3, then escalate.** A target rejected 3 full owner-verdict
rounds (each job internally ≤3 validator retries, unchanged) parks on a
"needs different approach" list surfaced on the dashboard and to BENCH —
matching the already-ruled Gemini-contrast escalation
(`GRAPHICS_GEMINI_BILLING_DECISION_1`). No unbounded churn on a doomed target.

## 2. Spend

`throughput.jsonl` already logs meter before/after per job. Derived views join
on `job_id`:
- Per target / wave / total: **%-of-weekly-window** consumed, converted to
  dollars at the plan rate (weekly window = $20 ⇒ 5% ≈ $1). Gemini jobs log
  `cost_usd` directly and add in.
- The honest unit: **cost per ACCEPTED image** (all spend ÷ acceptances —
  rejects and iterations priced in), per wave and cumulative.
- Numbers are relayed MEASURED (from the join) or UNMEASURED — never bare.

## 3. The status view — burn-UP, expanding scope

Derived by `artreg.py render` (script-owned, like the queue views):
- Burn-up chart: scope line (total registered, stepping up; each step labeled
  with its `source`) vs completed line (committed). Never burn-down — the
  target is allowed to grow and the chart says when and why.
- State counts: registered / queued / generated / awaiting-verdict / accepted
  / rejected-in-retry / parked-at-cap / repurposed / committed / deployed.
- Iterations histogram; %window burn rate; projection-to-finish of CURRENT
  scope at measured velocity, restated at every scope step.

## 4. RULED — the Dashboard Hub: one multi-tab artifact

Owner, verbatim: "put all these artifacts together into a single multi tab
artifact so there's one place the human can go and the system can check is
fresh."

- One published artifact (stable URL, pinned): a thin tab shell `index.html`
  plus **one data file per tab** (`art_status.json`, `health.json`, …) using
  the multi-file artifact mechanism. A seat republishing updates ONLY its own
  file at the same URL (files not passed are kept) — many writers, no
  collisions, the shell rarely changes.
- Every data file carries `generatedAt` + a fingerprint of its source; the
  shell shows a per-tab freshness lamp (green/amber/red by age), and a checker
  can read the same fields. Tabs are #hash-addressable for deep links.
- **Dashboards in; working sheets linked, not embedded.** Review sheets (pages
  the owner works in, decisions saved as data) keep their own URLs; the hub
  lists the open ones. Status pages consolidated: art regen (this design),
  codebase health, maturity/health, worldmap audit report.
- Repo HTML source is kept alongside (native path openable offline).

## 5. What this supersedes / does not change

- Supersedes: nothing existing — no art tracking layer existed above the
  queue dirs. `throughput.jsonl` is unchanged and remains the telemetry truth.
- Does NOT change: the daemon's worker contract, the grumpiness detector, the
  queue dir layout, review-sheets mechanics, FOUNDRY owning deploys, the
  Gemini billing gate (owner's explicit word still required before enable).
- Backfill: `artreg.py backfill` seeds the ledger from existing
  `throughput.jsonl` + done/failed manifests so history isn't lost; targets
  already accepted/committed are registered retroactively with
  `source: backfill`.

## Test (how someone checks this was applied)

The owner can ask "how many art targets exist, how many are done, what did an
accepted image cost this week" and the hub's art tab answers all three with
MEASURED numbers whose sources are the registry join — and adding 50 targets
from a new verdict sheet moves the scope line with a labeled step, not a
silent renumber.
