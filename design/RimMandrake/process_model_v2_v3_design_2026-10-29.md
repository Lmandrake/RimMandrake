# Process model v2 + v3: design (2026-10-29)

Item `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY`, designed by BENCH, to be built by FOUNDRY. Read the explainer first:
`design/RimMandrake/process_model_explainer_2026-10-29.md`. It says what today's model is and why its backtest
failed. That failure shapes most of this design.

## 1. The ruling

Owner, 2026-10-29 (verbatim): "Operations should be using a custom v3-based model fit. v2 models should be specific
to that v2 workflow and parameterized appropriatley, only fit to past v2 data logs. v3 should have different
parameterizations for the differences in workflow, plus both should share overall pipeline characteristics that can
be like-for-like compared. v3 model should be tuned at least once a day on the ongoing data record
(deterministically, statistically) so that it's available as a tool for understanding and prediction. This is an
Operational model, so it's Operations. It can be then used by Producer for estimation/scheduling, anyone for
debugging, Innovator for process improvement / radical changes. I would also like to learn a lot more about the
model that was created, how it fits, etc. It's worth investing in here."

What this design adds on top: three lessons from the failed backtest, each turned into a rule.

- **R1. Count work, not tickets.** The shared core's unit is work (helpers, ITE, verify results). Ticket counts are
  reached through a measured "recording" layer (how work turns into ledger items), and that layer is fitted per era.
- **R2. One instrument.** Fit targets come from the same code and the same windows that `v3_vs_v2.py` uses
  (`rimflow_metrics.compute` on Monday-07:00-local weeks, or the same function on daily windows). Never from a
  separate ad-hoc count.
- **R3. Nothing is trusted until it has predicted something it did not see.** Every refit is scored on the newest
  held-out day(s) before it replaces the previous fit.

## 2. Shape: core + v2 + v3

One engine (today's `rimflow_v3_sim.py`, refactored, not rewritten), three parameter layers:

```
core (shared, like-for-like)        era layer (separate fits)               recording layer (per era)
- owner presence by hour            v2: seats self-drive, owner nudges,     - ledger items per unit of work
- owner arrivals / pings / cards        helper_cap_v2, p_stall, r_self_h,   - quick-close share
- helper cost+duration (census)         p_park/pull, no roles               - bulk-ingest events per day
- defect birth (mu, kappa)          v3: Dispatcher ring (measured wakes),   - owner-message -> item share
- verify / escape / discovery           lease "doing", role runs+costs,
- token accounts + weekly reset         Arbiter verdicts, Auditor finds,
- follow-up breeding                    Producer queue order, card batching
```

**Core** (one meaning in both eras, so v2 and v3 can be compared like for like): arrivals of owner work per present
hour, presence profile, card queue (hazard per present hour), helper cost and duration drawn from the spend census,
defects per unit of work, verify coverage and catch, escape and discovery, token accounts, follow-ups per close.
Core parameters are fitted separately in each era, but they keep the same names and units. "v3's `q_card` vs v2's
`q_card`" is therefore a real comparison, with intervals.

**v2 layer.** Today's parameters, refitted once, on v2 logs only, then frozen. Fit window: the three v2 weeks ending
10-12, 10-19 and 10-26 (Monday 07:00 local, as `v3_vs_v2` defines them), with one change: the recording layer and
`q_card` get **a value per week**, and the rest are shared across the three weeks. That is a hierarchical fit (shared
core + per-week nuisance parameters), and it is exactly what the backtest showed was missing. Its own check is
leave-one-week-out: fit on two weeks, predict the third's work metrics (helpers, ITE, verify-fail share, rework
share) inside p5-p95. Ticket metrics are predicted given that week's measured recording layer. Once it passes it is
written as `v2_fit_<date>.json` and never refitted, unless an error is found in the v2 data (then it is deleted and
redone; it is never superseded).

**v3 layer.** The roles become measured mechanisms wherever v3 already logs them, replacing the typed-in multipliers:

| mechanism | v3 parameter | measured from |
|---|---|---|
| Dispatcher | wakes/day, ring success, idle-with-work minutes | `dispatcher/journal.jsonl`, `state.json` |
| leases | claim-to-close time, lease expiry rate | ledger claim/renew/release events |
| role runs | runs/day and ITE per run, per role | `dispatcher/roles/rm-role-*.json`, `runs.json` |
| Arbiter | verdict rate, reject share, ITE per verdict | ledger notes/closes by Arbiter (once it runs) |
| Auditor | samples/day, finds per sample | its run records and `caused_by` links |
| Producer | queue position at claim vs filed order | ledger |
| Conductor | cards per batch, pings/day | owner cards, ops_watch `steve` series |
| recording | items per helper, quick-close share, bulk files/day | ledger + spend census |

Anything v3 does not yet log stays ASSUMED with its range. The fit output names which mechanisms are measured and
which are still guessed, so nobody mistakes a programmed effect for a fitted one.

## 3. Data sources

All are read-only to the model. Windows are UTC-stored and grouped by local day/week where `v3_vs_v2` does so.

| source | path | gives |
|---|---|---|
| ledger | `infrastructure/state/ledger/events/*.jsonl` via `rimflow_metrics.compute` | filed, done, rework links, owner-decision waits, claims, leases |
| spend census | the census script `calib_brief.md` names (helper transcripts) | helpers, ITE per helper and per seat, durations |
| ops_watch series | `D:\ClaudeWork\rimmandrake\ops_watch\series\{accounts,flow,process,production,steve,testing,tps,v3,...}.jsonl` | account usage, process share, flow, owner activity, every 15 min |
| dispatcher | `D:\ClaudeWork\rimmandrake\dispatcher\journal.jsonl`, `runs.json`, `roles\*.json` | wakes, stalls, role run costs |
| owner messages | the conversation logs the presence profile used | presence by hour, message rate |
| verify results | ledger verify notes, `testing` series | verify coverage, fail share |

**Data volume, honestly.** v3 has run since about 2026-10-27, so it has about 3 days of data. The daily fit uses a
rolling window (default 14 days, or everything since v3 started if that is shorter), weighted toward recent days. The
early intervals will be wide, and that is the right answer, not a defect.

## 4. The daily fit

**Program, no AI.** `python3 src/RimMandrake/Utils/sim/process_model.py fit --era v3 --asof <date>`. Same code, same
data, same seeds give the same output byte for byte. Seeds derive from the as-of date (`seed = hash("v3", asof)`),
so tomorrow's fit is a new draw but today's can always be replayed.

**Targets.** Daily values over the window, from `rimflow_metrics.compute` and the sources above: helpers/day,
ITE/day, verify-fail share, rework share, owner-wait median, nudges or pings/day, Dispatcher wakes/day, role ITE/day,
process share, and filed/done per day (these two through the recording layer). Each target has a tolerance equal to
its measured day-to-day spread over the window, not a hand-set 10%.

**Method: warm-started ABC-MCMC, cheap.** Start from yesterday's accepted ensemble (on the first day, from the frozen
v2 core with the v3 layer at prior). Run 20 chains × 150 steps, each step simulating the window in daily blocks.
Accept when every target is inside tolerance. Keep 120 members. Budget: about 3,000 model-days of simulation,
roughly 10-15 CPU-minutes on one core, using the measured 0.25 s per simulated two weeks. Run on 4 processes.

**Statistical output** (`fit_<asof>.json`): per-parameter p10/p50/p90 and shrink, per-target posterior predictive
p5/p50/p95 vs the real value, ensemble size, acceptance rate, and the window used.

**Held-out check (R3), before the fit is trusted.**
1. Fit on the window ending yesterday 07:00 local, excluding the last full day.
2. Predict the excluded day: are the work metrics inside p5-p95? Is the coverage over the last 7 such checks at least
   70%?
3. Pass: `current.json` points at the new fit. Fail: `current.json` keeps the last passing fit, the new one is kept
   as `fit_<asof>.json` marked `HELD_OUT_FAIL`, and Operations sees AMBER with the metric that missed.
4. After 3 failures in a row: RED, which means the model structure is wrong, not the parameters. That is filed as an
   item, not auto-fixed.

**Drift watch.** Every day, each core parameter's v3 posterior is compared with yesterday's and with v2's. A shift of
more than one posterior width in a day is reported as "practice changed": for example, `q_card` doubling after card
batching starts. This is the "understanding" half of the owner's ask.

## 5. Where it runs and who judges it

- **Timer.** `rm-process-model.timer`, user systemd, next to `rm-ops-watch.timer`. It runs daily at 06:30 local, so
  the fit is ready for Operations' 07:30 run. The service has a hard 30-minute timeout and nice 10.
- **Outputs.** All under `D:\ClaudeWork\rimmandrake\process_model\`: `fit_<asof>.json`, `current.json`,
  `heldout.jsonl` (one line per day), `drift.jsonl`, and `digest.md` (about 30 lines, plain language). Nothing is
  written to the repo, so there are no commits and no process share.
- **ops_watch.** Adds one series line per day to `series/model.jsonl` (held-out pass, coverage, acceptance rate,
  biggest drift) and one alarm: no fit for 36 h, or RED.
- **Operations judges.** The 07:30 run reads `digest.md` and the held-out line. Its prompt (`roles/operations.md`)
  gets one paragraph: trust the model's predictions only while `current.json` is PASS, report drift that matters,
  and never retune the model by hand. The program fits; Operations analyses (the same split as "Dispatcher
  measures, Operations analyses").

## 6. Interfaces

One CLI, `process_model.py`, reading `current.json`. Every answer carries its interval and the fit date. When the
fit is not PASS, every answer is stamped `UNTRUSTED`.

**Producer (estimation and scheduling).**
- `process_model.py forecast --days 7 --json`: p10/p50/p90 closes, helpers, ITE and owner-wait for the next 7 days,
  under the current mix.
- `process_model.py eta --queue <item ids or count> --class product`: when the last of N queued items closes,
  p10/p50/p90, given the current queue position and the seat capacity.
- Producer stays token-blind, as the ruling says: the forecast hides account runway and gives Producer item counts
  and dates only. Operations reads the token side.

**Anyone (debugging).**
- `process_model.py explain --metric done --day 2026-10-30`: real vs predicted, and which mechanism moved, by
  re-running the day with each measured mechanism set back to its 7-day median, one at a time. It answers, for
  example, "closes fell 40%; 30 points of it is the Dispatcher's wakes being capped; 10 is owner absence".
- `process_model.py param q_card --history`: the posterior over time, for "when did this change".

**Innovator (process improvement and radical changes).**
- `process_model.py whatif --policy <policy json>`: a paired comparison against the current v3 on the same seeds,
  using today's experiment machinery (`experiment`), on the current ensemble. Policies are JSON, so a radical
  architecture (for example: no Arbiter, three seats, helper cap 2, no daily role runs) is a file, not code. A change
  that needs a new mechanism is a code change and an item.
- Results are labelled as in the findings: a direction that holds in at least 95% of paired runs and under the quota
  variants is HIGH. Anything resting on an ASSUMED mechanism is "(programmed)".

## 7. v3_vs_v2

Today `v3_vs_v2.py` asks the old ensemble for a "what would v2 have done this week" range, and it reports
UNMEASURED because the backtest failed. New wiring:

- **Counterfactual source.** The frozen v2 fit (§2), run with this week's measured core inputs (presence, owner
  arrivals, the helper census) and the **v2 recording layer**. Output: v2's range for the work metrics, plus ticket
  metrics recorded the v2 way.
- **Gate.** The counterfactual is MEASURED only while the v2 fit's leave-one-week-out check passes. That replaces
  `backtest.json`'s 75% rule with a check run on the metrics that are actually comparable.
- **Like-for-like table.** Each week's verdict adds a section comparing core parameters v2 vs v3 with intervals
  (`q_card`, stall rate, defects per unit of work, verify catch, ITE per unit of work). It says which part of the
  pipeline v3 changed, not only whether the totals moved.
- The existing rules (`v3_vs_v2_rules.json`: SUPERIOR at 4 of 7 primaries BETTER, and the counterfactual can only take
  a BETTER back) stay as they are.

## 8. Build order with L0 checks

Each step is one item, ends with a selftest under `run_selftests.py`, and does not start until the previous one
passes. L0 checks are pure: synthetic data, run in seconds, no live files.

1. **Instrument (R2).** `process_model_data.py`: build the daily and weekly target tables from `rimflow_metrics`,
   the census, ops_watch and the dispatcher. *L0:* a synthetic ledger with known counts gives exact targets. The
   weekly table for 10-26 equals `v2_weeks.json` (done 773, filed 1,282) field for field. A day with zero events
   gives 0 and not a missing row, and a missing source gives UNMEASURED and not 0.
2. **Recording layer in the engine.** Split "unit of work" from "ledger item". *L0:* with the recording layer set to
   today's implicit values, the engine reproduces today's v2 outputs within seed noise on 20 fixed seeds. Doubling
   items-per-work doubles closes and leaves helpers and ITE unchanged.
3. **v2 hierarchical refit, frozen.** *L0:* parameter recovery: simulate three synthetic weeks from known
   parameters, fit, and the true values lie inside p10-p90 for at least 80% of the identifiable ones.
   Leave-one-week-out on real v2 passes, or the item reports which metric fails and stops there.
4. **v3 mechanisms measured.** Replace each typed multiplier that v3 logs (Dispatcher first). *L0:* feeding a journal
   with known wakes gives the measured parameter, and a role with no log stays ASSUMED and is flagged.
5. **Daily fit + held-out + current.json.** *L0:* two runs with the same as-of date are byte-identical. A held-out
   miss keeps the previous `current.json`. Three misses give RED. A 3-day window still fits and reports wide
   intervals.
6. **Timer, ops_watch series, Operations paragraph.** *L0:* `systemd-analyze verify` on the unit. A fit older than
   36 h raises the alarm in a synthetic status. The Operations prompt edit is reviewed by `code_review_status.py`.
7. **Interfaces** (`forecast`, `eta`, `explain`, `param`, `whatif`) and the v3_vs_v2 wiring. *L0:* each CLI on a
   fixture fit returns intervals and the fit date. An untrusted fit stamps `UNTRUSTED`. `v3_vs_v2` reports
   UNMEASURED when the v2 gate fails.

Steps 1-3 alone fix the backtest problem and make the v2 model honest. Steps 4-5 give the owner his daily v3 fit.
Step 6 makes it Operations'. Step 7 makes it useful to Producer, debugging and Innovator.

## 9. Cost

- **Compute.** Daily fit about 10-15 CPU-min on 4 processes, so about 5 minutes of wall clock. The held-out
  prediction adds about 1 min. The one-off v2 refit takes about 1-2 CPU-hours. The machine idles at 06:30.
- **Tokens.** The model itself uses zero. Operations reads one roughly 30-line digest in a run it already does:
  about 2-4k weighted tokens/day, inside its 1,650,000 daily cap. Interface calls by Producer or Innovator are CLI
  output, not model calls.
- **Commits.** Process share is at 72% against a 61% target, so the design spends no daily commits: fits, digests
  and series live in `D:\ClaudeWork`. Commits come only from the build itself (about 7 items, roughly 10-15
  commits) and from deliberate changes to model structure. There is no auto-committed parameter file.
- **People.** The owner reads `digest.md` when he wants to. Nothing about it reaches him unless Operations
  escalates RED.
- **Keep it small.** One engine, one CLI, one timer. Today's `rimflow_v3_sim.py` subcommands that the new CLI
  replaces (`backtest`, `counterfactual`) are deleted once step 7 lands, and every inbound reference is fixed, as
  the "wrong material is deleted" ruling requires.

## 10. Open questions for the owner

1. **Is it a v2 counterfactual at all?** Ledger practice changed every v2 week. Is "v2 recorded the v2 way" the
   comparison you want, or only the work metrics (helpers, tokens, defects, owner wait), which can be compared
   cleanly? The design supports both. The work-only comparison is the safer default.
2. **How far back is "past v2 data logs"?** The ledger starts 2026-09-24, but the spend census and ticket practice
   are only comparable from about 10-06. Fitting three weeks (10-06 to 10-26) is proposed. More weeks would mean
   accepting older, noisier recording.
3. **Should drift reach you?** A large drift in a core parameter (for example, your card-answer rate halving) is
   information about your own practice. Should Operations put it in its owner-only route (`ops_watch/owner/`), or
   keep it in the digest you read by choice?
