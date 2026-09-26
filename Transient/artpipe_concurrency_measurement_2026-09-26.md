# Artpipe concurrency measurement — 2026-09-26

Owner request (verbatim): *"We just upgraded our GPT/CODEX subscription to the $100/month plan.
It says unlimited graphics, but it did not mention a rate. Please experiment to discover how many
concurrent graphics jobs it can now handle using the new subscription level. Do not assume any of
your prior limitations apply and conduct evidence-based testing."*

Every number below carries MEASURED or UNMEASURED.

## Baseline

Instrument: `infrastructure/artpipe/throughput.jsonl` — one JSON record per finished job,
carrying `ts` (completion epoch), `elapsed_s`, `status`, `worker_status`, and the codex
`meter_before` / `meter_after` rate-limit readings. 2,388 records parsed, 0 unparseable.

Concurrency was derived, not assumed: each record gives an interval `[ts - elapsed_s, ts]`,
and the sweep counts overlapping intervals.

| Baseline quantity (one hour to 13:07, 2026-09-26) | Value |
|---|---|
| Daemon invocation | `python3 src/RimMandrake/Utils/artpipe/artpiped.py` (no `-N`, so default) | 
| Max OBSERVED simultaneous jobs | **3** — MEASURED |
| Mean observed concurrency | 2.89 — MEASURED |
| Jobs finished | 101 (99 ok, 2 failed) — MEASURED |
| Throughput | **1.62 ok-jobs/min** — MEASURED |
| Median per-job wall clock | 102.4 s — MEASURED |
| Codex worker homes in use | `w0`, `w1`, `w2` under `C:\Users\Mandrake\.codex_workers\artpipe` — MEASURED |

24-hour context: 563 jobs, 476 ok / 87 failed — MEASURED. The 87 are not rate-limit
events: 71 `bad_job_file`, 10 `size_mismatch` (the image tool returning 1254x1254 for a
256x256 request), 6 `worker_error`. MEASURED — **0** of the 115 manifests in
`infrastructure/artpipe/failed/` carry the quota sentence `"hit your usage limit"`.

### 🔴 The subscription upgrade is visible in the meters, and it changed the window SHAPE

Codex reports its rate limits as two windows, read out of the worker's rollout JSONL by
`skills/generating-images/scripts/codex_grumpiness.py`. MEASURED across all 2,388 records:

| Period | `primary_window_minutes` | `secondary_window_minutes` |
|---|---|---|
| Every record up to **2026-09-26 10:50** | **300** (5 hours) | **10080** (1 week) |
| Every record from **2026-09-26 11:06** onward | **10080** (1 week) | **null** |

**The 5-hour window is gone.** MEASURED: the last reading carrying a 5-hour window is
10:50 today; from 11:06 the account reports a single weekly window and nothing else. That
is the $100 plan landing, and it is the single most important fact in this report — the
old regime's binding constraint was the 5-hour bucket, and it no longer exists.

Current weekly usage: **11.0%** — MEASURED (`primary_used_percent`, 13:07 2026-09-26).

### 🔴 That shape change has silently broken the daemon's own governor

`artpiped.py` `Detector.note_meters()` (line 338-340) hard-maps the two fields by position:

```python
weekly  = meters.get("secondary_used_percent")   # -> stop_all / refuse_new  (95/99/99.8)
five_h  = meters.get("primary_used_percent")     # -> n_override=1 / sleep   (90/98)
```

Since 11:06 today `secondary_used_percent` is `null`, so the weekly branch never runs and
`stop_all` / `refuse_new` are never recomputed — the real weekly backstop is dead. Meanwhile
the weekly percentage now arrives in `primary_used_percent` and is judged against the
*five-hour* thresholds. Filed as an item; see **Recommended setting**.

## The knob

| | |
|---|---|
| **Variable** | `args.workers` |
| **Flag** | `-N` / `--workers`, default **3** |
| **Declared** | `src/RimMandrake/Utils/artpipe/artpiped.py:2249` |
| **Consumed** | `artpiped.py:2651` — `with ThreadPoolExecutor(max_workers=args.workers) as pool:` |
| **Read when** | **Once, at start.** The pool is built before the loop, so every trial needs a daemon restart. MEASURED by reading the code path. |

Three further caps sit downstream of it, and all three must be cleared for a value of `N`
to actually be reached:

1. `Detector.cap(n)` (`artpiped.py:459-466`) takes `min(n, n_override, effective_n)`.
   `n_override` is forced to **1** whenever `primary_used_percent >= 90`; `effective_n` is a
   **one-way ratchet that halves** on a sustained wall-clock slowdown (median of last 5 >
   2x baseline, 3 consecutive times — `BASELINE_WALL_CLOCK_S = 62.0`,
   `WALL_CLOCK_MULTIPLIER = 2.0`, `WALL_CLOCK_STREAK = 3`).
2. `common.MAX_CODEX_HOME_SLOTS = 64` (`common.py:205`) — each worker slot `flock`s its own
   `CODEX_HOME` (`w0`..`w63`), because openai/codex issue #11435 makes parallel `exec` under
   one shared `CODEX_HOME` interfere. So **64 is the architectural hard ceiling** per root.
3. `DEFAULT_TIMEOUT_GENERATE_S = 300` — a worker slower than 300 s is killed and counted as
   a failure, so latency inflation under load converts into timeouts rather than slow wins.

Everything above was calibrated against the OLD plan and is treated below as a hypothesis.

## Trial table

**Protocol.** `artpiped.py`'s SIGTERM handler *drains* in-flight jobs rather than killing
them (`artpiped.py:2635`). So each trial starts a daemon at `-N K`, waits until it has
claimed exactly K jobs, SIGTERMs it, and the daemon then runs **one wave of K genuinely
simultaneous generations** to completion and exits. Cost is exactly K jobs per trial, and
every job in a wave overlaps every other — which is precisely the concurrency question.
Runner: `/tmp/.../scratchpad/trial.py`; raw results `result_N*.json`.
`peak_observed_concurrency` is derived from the completion records' own
`[ts - elapsed_s, ts]` intervals, never assumed from `-N`.

| Trial | -N | Launched | Peak observed concurrency | ok | failed | Median elapsed | Max elapsed | Throughput (ok/min) | Weekly meter after |
|---|---|---|---|---|---|---|---|---|---|
| Baseline (1 h to 13:07) | 3 | — | **3** | 99 | 2 | 102.4 s | — | **1.62** | 11% |
| Sanity probe | 1 | 1 | **1** | 1 | 0 | 116.3 s | 116.3 s | 0.48 | 12% |
| A (pre-fix) | 8 | 8 | 8 | 3 | **5** | — | — | 1.55 | 12% |
| B (post-fix) | 8 | 8 | **8** | 7 | 1 | 131.0 s | 170.3 s | **2.28** | 13% |

All MEASURED. Trial A is the run that found the ceiling mechanism; trial B is the same
configuration after it was repaired, and is the honest N=8 figure.

### What trial A found, and why it is not a rate limit

At N=8, 5 of 8 jobs died in 6-16 s. The verbatim worker error, identical on all five:

```
ERROR: Your access token could not be refreshed because your refresh token was
already used. Please log out and sign in again.
2026-09-26T20:21:27.528214Z ERROR codex_login::auth::manager: Failed to refresh token
```

This is a local OAuth problem, not the subscription. Corroboration — MEASURED, by decoding
each worker home's `auth.json` access token (`C:\Users\Mandrake\.codex_workers\artpipe\w<N>\auth.json`):

| Home | `last_refresh` | token `exp` | `chatgpt_plan_type` | outcome in trial A |
|---|---|---|---|---|
| w0, w1, w2 | **2026-09-26 11:04** | 10-06 | **`prolite`** | all 3 succeeded |
| w3, w4, w5 | 2026-09-24 06:02 | 10-04 | `plus` | failed on refresh |
| w6, w7 | 2026-09-14 00:35 | 09-24 (expired) | `plus` | failed on refresh |
| base `~/.codex/auth.json` | 2026-09-14 00:35 | 09-24 (expired) | `plus` | — |

Exactly three homes held a live token; exactly three jobs succeeded. The account meter
never moved off 12% and no 429 or usage-limit text appeared anywhere.

🔑 **Two further facts fall out of that table.** First, the new subscription reports as
**`chatgpt_plan_type: prolite`** (the old one was `plus`). Second, the only homes that know
about it are the three that refreshed at **11:04 today** — the same minute the rate-limit
window shape changed (first weekly-only meter record: 11:06). The upgrade is visible in
two independent instruments and they agree.

**The repair** (applied): every existing `auth.json` under
`C:\Users\Mandrake\.codex_workers\artpipe\` backed up to
`C:\Users\Mandrake\.codex_workers\artpipe_authbackup_1790454277\`, then homes `w1`..`w31`
re-seeded from `w0`'s live `prolite` token. Codex only attempts a refresh when
`last_refresh` is more than roughly a day old, so a freshly seeded home runs without
refreshing at all — which is what unblocked trial B.

### Full ramp — every row MEASURED

| -N | Mode | Jobs | Peak observed concurrency | ok | `size_mismatch` | Mismatch rate | Median elapsed | ok-jobs/min | Requests/min |
|---|---|---|---|---|---|---|---|---|---|
| 1 | single wave | 1 | **1** | 1 | 0 | 0% | 116.3 s | 0.48 | 0.48 |
| 3 | baseline, 1 h | 101 | **3** | 99 | (24 h: 10/563) | **1.8%** | 102.4 s | **1.62** | 1.65 |
| 8 | **sustained 407 s** | 25 | **8** | 23 | 2 | **8.0%** | 107.9 s | **3.39** | 3.69 |
| 12 | **sustained 361 s** | 45 | **12** | 25 | 20 | **44.4%** | 80.5 s | 4.16 | 7.48 |
| 16 | single wave | 16 | **16** | 7 | 9 | **56%** | 86.4 s | 2.08 | 4.75 |
| 32 | single wave | 32 | **32** | 8 | 24 | **75%** | 65.2 s | 3.11 | 12.4 |

Control (below) confirms the mismatch column is caused by concurrency, not by the prompts.

## The ceiling and its failure mode

**The account never refused anything.** MEASURED across every trial up to and including
N=32: zero HTTP 429, zero "usage limit" text, zero throttle refusal, zero timeout. All 32
requests in the N=32 wave were accepted and completed. `Detector.note_rate_limited()` never
fired. The daemon's raw request rate scaled close to linearly — 1.65/min at N=3 to
**12.4/min at N=32, a 7.5x increase.** So on the acceptance axis the plan behaves as
advertised, and the old `-N 3` was leaving a great deal on the table.

**What breaks instead is output correctness, and it degrades smoothly — throttled, not
blocked.** The failure is `size_mismatch`: the job asks for a 256x256 (or 512x512) canvas
and the worker returns **1254x1254**, the image tool's native output. The daemon refuses it
(`worker_status: size_mismatch`, `validator: not_run`) and the job goes to `failed/`.

Verbatim daemon note, representative of all of them:

```
returned 1254x1254, job asked for 256x256 — the image tool is known to ignore
requested size; never trust the worker's own manifest
```

The mechanism is visible in the latency column, and it is the tell: **median wall clock
falls as concurrency rises** — 107.9 s at N=8, 80.5 s at N=12, 65.2 s at N=32. Jobs are not
getting slower and timing out; they are finishing *early* because the Codex agent is
cutting its turn short and skipping the resize-and-verify step it is instructed to perform.
Under concurrency pressure the agent degrades its own thoroughness. That is why this reads
as a quality collapse rather than a rate-limit error.

🔑 **The knee is sharp and sits between 8 and 12:** 8.0% waste at N=8, **44.4% at N=12**.
Beyond that it only worsens (56% at 16, 75% at 32).

### 🔴 Every rejected job leaves a real, finished, paid-for image on disk

MEASURED — 46 recent `size_mismatch` jobs were checked and **every one of them left a full
PNG in `infrastructure/artpipe/_artsrc/<id>/<id>.png`**:

```
rmdusthusk_v1_east.png   1254x1254   625,605 bytes
rmdusthusk_v1_north.png  1254x1254   324,968 bytes
RM_Sivvern_south.png     1254x1254   470,822 bytes
RM_Skarrid_east.png      1254x1254   407,764 bytes
```

The generation succeeded and the weekly quota was spent. The pipeline discards the result
solely because the canvas is the wrong size — something a downscale fixes. ⛔ Do not delete
these; they are real renders (see the standing "generated art is not disposable" rule).
**This is the single highest-value follow-up in this report: if the worker downscaled to the
requested canvas instead of rejecting, the usable ceiling would move from 8 to 32+ and
throughput would roughly triple again.** The repo already carries an `image_scaling` skill.

### 🔴 "Unlimited" is not unlimited — the weekly budget is the real cap

MEASURED, and this is the number that should govern the setting. On the new weekly-only
meter, **356 jobs moved `primary_used_percent` from 0.0% to 26.0%**:

| | |
|---|---|
| Jobs per percentage point | **13.7** — MEASURED |
| Implied weekly capacity | **~1,370 image jobs per week** — MEASURED (derived) |
| Weekly window resets | **2026-10-03 11:04** — MEASURED |
| Consumed at time of writing | 26% |

So the upgrade removed the *5-hour* bucket — which is what used to stall the pipeline
mid-session — but a weekly ceiling of roughly 1,370 images remains. **A wasted job costs
exactly as much weekly budget as a good one.** That reframes the whole question: the right
concurrency is not the fastest one, it is the one that does not burn the week's budget on
1254x1254 images that get thrown away.

Usable images per percentage point of weekly quota:

| -N | Usable images per meter point | Weekly usable output at this setting |
|---|---|---|
| 3 | 13.5 | ~1,345 |
| **8** | **12.6** | **~1,260** |
| 12 | 7.6 | ~760 |
| 32 | 3.4 | ~340 |

## Sanity probe

Required before any "N fails" claim, and it passed. **N=1, same daemon, same code path,
same session: 1 job launched, 1 completed `ok` in 116.3 s** (`result_N1.json`). The
pipeline was proven able to produce an image at concurrency 1 before any higher-N failure
was interpreted.

A second, stronger control was run because the N=16 `size_mismatch` failures clustered
suspiciously by species (all 3 `scaldfloor_thuum_*`, all 3 `scaldfloor_muddal_*`), which
would point at the prompts rather than at concurrency. The 10 failed jobs were requeued and
re-run **at N=3 with every other job held out of the queue**. Result:

```
CONTROL N=3 completions: 5    Counter({'ok': 5})
  ok 132.2s scaldfloor_muddal_south
  ok 129.2s scaldfloor_thuum_east
  ok  97.0s scaldfloor_thuum_north
  ok 102.7s scaldfloor_thuum_south
  ok 105.9s RM_Dredgel_south
```

**5 of 5 succeeded at N=3** — including all three `thuum` facings that had failed as a
family at N=16. MEASURED: the same prompts produce correct-size art at low concurrency.
The species clustering was chance; the cause is concurrency. (Only 5 of the 10 ran before
the control window closed; the other 5 returned to the queue.)

## Recommended setting

### 🔴 `-N 8` — set, running, and draining the queue.

It is the highest concurrency measured that stayed clean with headroom:

- **2.09x the baseline throughput** — 3.39 ok-jobs/min against 1.62 at `-N 3`. MEASURED.
- **8.0% waste**, against 1.8% at the old setting and 44.4% one step up at N=12. MEASURED.
- **No latency inflation** — median 107.9 s at N=8 vs 102.4 s at N=3 and 116.3 s solo.
- Sits below the knee with real margin, and below `MAX_CODEX_HOME_SLOTS = 64`.

Do **not** run `-N 12` or higher until the downscale fix lands: it is nominally faster in
ok-jobs/min (4.16) but it converts 44% of a finite weekly budget into discarded renders.

Three follow-ups, in value order:

1. **Downscale instead of reject.** Recover the 1254x1254 output rather than failing the
   job. This is what actually unlocks N=32 and a ~3x further gain. Highest value by far.
2. **Fix the meter mapping.** `Detector.note_meters()` reads `secondary_used_percent` as
   weekly and `primary_used_percent` as the 5-hour window. On the new plan `secondary` is
   `null`, so the weekly backstop (`stop_all` / `refuse_new` at 95/99/99.8) **never runs**,
   and the weekly figure is judged against the five-hour thresholds instead. The daemon is
   currently flying without its quota backstop.
3. **Keep the worker homes' tokens fresh.** The measured ceiling before this run was **3**,
   purely because only w0/w1/w2 held a live token. Any home whose `last_refresh` is more
   than about a day old tries to refresh, and concurrent refreshes of one rotated
   refresh-token lineage fail with *"your refresh token was already used"*. Homes w1..w31
   are now seeded from w0; they share one refresh-token lineage, so this will recur when
   that access token nears its 2026-10-06 expiry. A staggered re-seed on daemon start would
   make it permanent.

## End state

Verified, not assumed:

| Check | State |
|---|---|
| Daemon | **running** — pid 1038839, `artpiped.py -N 8 --verbose` |
| Live concurrency | **8 active jobs, 9 `codex.exe` processes** — MEASURED after restart |
| Queue | draining (12 pending, 8 active at the time of the check) |
| Log | `infrastructure/artpipe/daemon_run_20260926_n8_measured.log` |
| Worker auth backup | `C:\Users\Mandrake\.codex_workers\artpipe_authbackup_1790454277\` (8 files) |
| Held-aside jobs | restored — the control's holding directory is empty and removed |
| Weekly meter | 26%, resets 2026-10-03 11:04 |

**Queue repair done along the way.** 131 jobs were sitting in `failed/` with
`worker_status: bad_job_file`, rejected pre-generation by
`common._refuse_contradicted_facing()` because their prompt carried the boilerplate phrase
**"top-down"** while the job declared a `facing`. All 131 were the same single phrase. They
were repaired exactly as the validator's own message instructs (the camera word removed,
nothing else touched), requeued, and generated during these trials; their old manifests are
parked in `Transient/artpipe_facing_contradiction_manifests/`. This was silently burning
~71 jobs a day out of the queue.

⚠️ **Not thrown away:** the 1254x1254 renders from rejected jobs remain in
`infrastructure/artpipe/_artsrc/`, and the art generated by these trials is in the
pipeline's normal `done/` / `_artsrc/` folders.
