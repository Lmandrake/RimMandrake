# The process model, explained (2026-10-29)

Item `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY`. For the owner, readable cold. It explains the model that exists today:
`src/RimMandrake/Utils/sim/rimflow_v3_sim.py`, its parameters in `rimflow_v3_sim_params.json`, and its data in
`D:\ClaudeWork\rimmandrake\rimflow_sim\`. The plan for the model that replaces it is in
`design/RimMandrake/process_model_v2_v3_design_2026-10-29.md`. Every number below was read from those files or
recomputed from the ledger on 2026-10-29. Where a number is my arithmetic, I say so.

## 1. What it is, in one paragraph

It is a "factory in a bottle": a program that plays out a week of RimFlow work as a sequence of events. Tickets
arrive. Two builder seats work them with helpers. Some work carries hidden defects. Verify runs catch some of them,
and the rest escape and come back later as rework. You are a person with limited hours who answers cards and
notices stalled windows. Three token accounts drain and reset every Wednesday at 13:00. On top of that v2 baseline,
the v3 roles (Dispatcher, Conductor, Operations, Producer, Arbiter, Auditor, Innovator) can be switched on one at a
time. It does **not** simulate the game or the mods, only the process that builds them. It needs no AI to run:
Python with numpy, about a quarter of a second per simulated two weeks.

## 2. What it simulates: things, events, clock

**Things (entities).**
- **Ticket.** Has a class (product, process or rework), a seat (FOUNDRY gets 42%, BENCH the rest), whether it is a
  "quick close" with no helper, an attempt count, and a list of hidden defects. A defect is either latent or found,
  and some defects are "blind": no check can ever see them.
- **Seat.** FOUNDRY and BENCH. Each has three queues (repairs first, then product, then process), one serial "brief
  and launch" slot, up to `helper_cap` helpers running at once, and a stalled flag (the window has stopped and waits
  for a nudge).
- **Owner.** An hourly coin flip says whether you are present that hour (the probability for each local hour comes
  from 23 days of your messages). While present you file new work, send status pings, answer waiting cards, and
  notice stalled windows.
- **Token accounts.** lukas, steven, system. Every helper, close and role run charges input-equivalent tokens (ITE)
  across the accounts that are not yet dry.
- **Roles (v3 only).** Each is a small mechanism with an effect multiplier and a token cost: the Dispatcher rings
  stalled windows, the Arbiter re-checks closes on two rig slots, the Auditor samples yesterday's closes, and so on.

**Events.** The engine is a discrete-event simulation: a priority queue of timed events, processed in time order.
The event kinds are: `hour` (owner arrivals, pings, card answers, throttle), `day` (role runs), `launch` and
`helper_done` (helpers start and finish), `quick_done`, `resume` (a stalled seat restarts, by itself or because you
nudged it), `disc` (a latent defect is discovered after the close), `arb_done`, `ring_tick` (the Dispatcher every
120 s), `activate` (a role switches on), `week_reset` (accounts reset) and `snap128` (the account reading at hour
128, which is used to derive quotas).

**Clock.** Continuous time in seconds, with no fixed step. Owner behaviour is decided per hour, roles per day, and
the week starts at the Wednesday 13:00 reset. A standard run is 2 weeks: week 0 warms the queues up, and only week 1
is scored. Policy experiments run 1 warm v2 week plus 4 policy weeks.

**Randomness, and why runs can be compared fairly.** Every random draw is a hash of (seed, what is being decided,
which ticket, which attempt...) and not a call to a shared random stream. So when you switch the Arbiter on, ticket
X still arrives at the same minute and still carries the same defects. Only the policy differs. This is what makes
"v3.3 minus v2 on the same seed" a clean comparison.

**One ticket's life.** You are present at 20:00 and file a product ticket. With probability `p_owner_card` it needs
a decision from you first and waits in your card queue. Otherwise, with probability `p_park` it is parked
(proposed, never worked). Otherwise it joins a seat's queue. The seat either quick-closes it in a few minutes or
launches about `helpers_per_job` helpers. Each helper's token cost and duration come from the real distribution of
1,271 helper transcripts. When the last helper finishes, the ticket gets Poisson(`mu_prod`) hidden defects (more if
many helpers ran at once: `kappa`). The maker's self-check finds a few (`s_self`). With probability 0.66 a verify
run happens; it catches each visible defect with probability `s_rig` and false-fails with probability `fr_rig`. A
catch sends the ticket back to the front of the queue as a repair. Otherwise it closes, and each defect still
latent is discovered some days later (`e_disc` per day) and filed as a rework ticket. The close itself breeds
follow-up tickets (`f_prod`, `f_proc`). After finishing a job the seat may stall (`p_stall`) until it resumes by
itself (`r_self_h`) or you notice it (`p_watch`, `notice_min`). That notice is a "nudge".

**Two structures, because the data cannot choose.** In "park", parked tickets are never worked, so the factory is
limited by demand. In "pull", an idle seat pulls the oldest parked ticket, so the factory is limited by capacity.
Both were fitted separately and every finding is reported under both.

## 3. The parameters, group by group

There are 75 numbers: 15 fixed values and 60 ranges ("priors"). Every one carries a label:

| label | meaning | count |
|---|---|---|
| CALIBRATED | measured directly on disk, source named | 7 fixed |
| DERIVED | computed from calibrated numbers by a stated rule | 2 fixed |
| CONFIG | read from our config or the v3 design | 5 fixed, 1 CONFIG/ASSUMED |
| ASSUMED | no direct measurement: a uniform range | 60 |

The 60 ASSUMED ranges split in two. **34 are "v2-visible"**: the fit narrows them, because they change what v2
does. **26 are "V3_ONLY"**: they describe roles v2 never had, so v2 data says nothing about them. Each ensemble
member gets a fresh draw from their full range (seed 4242) and they are never fitted.

"Shrink" below = (posterior p10-p90 width) / (0.8 × prior width), from `results.json`. 1.0 means the fit learned
nothing about that knob; 0.2 means it pinned it down hard.

**A. Fixed, measured (CALIBRATED / DERIVED / CONFIG).**

| name | value | from |
|---|---|---|
| `helper_ite_q`, `helper_dur_q` | 41 quantiles per seat | spend census, 1,271 helper transcripts in 7 days (cost and duration drawn together, Spearman 0.89) |
| `seat_ite_per_close` (DERIVED) | 184,000 ITE | top-level BENCH 126M + FOUNDRY 45M / 928 closes |
| `background_ite_week` | 146.8M ITE | spend census: everything not BENCH/FOUNDRY (art-eval headless 107M...) |
| `owner_present_p_by_hour` | 0.04 (02:00) to 0.78 (19:00, 22:00) | share of 23 days with at least one typed message in that PDT hour; about 11.8 present h/day |
| `p_verify` | 0.66 | 615 verify results / 928 closes |
| `foundry_share` | 0.42 | FOUNDRY 2,337 of 5,572 seat ledger events |
| `account_used_at_128h` | lukas 0.93, steven 0.69, system 0.71 | account_usage series 2026-10-26 (lukas, steven ESTIMATE) |
| `account_quota` (DERIVED) | per member | each member's own simulated hour-128 burn / the fractions above, so token results are relative to today's burn |
| `dispatcher` (CONFIG) | tick 120 s, stall after 240 s, 3 wakes/seat/h, 30/day, 80/day, FOUNDRY only | `dispatcher_schedule.json` |
| `throttle_order` (CONFIG) | Innovator, Auditor, Producer, Arbiter, Operations | schedule; v3 design §3 |
| `auditor_max_per_day` (CONFIG) | 4 | v3 design §2 (since lifted by `RIMFLOW_AUDITOR_RETHINK_DAILY_CAP`) |
| `n_rig` (CONFIG) | 2 | two test machines |
| `role_costs` (CONFIG/ASSUMED) | Operations 2 × 60k + 150k a day | schedule caps used as costs; every other role cost is ASSUMED |

**B. Arrivals and the owner (ASSUMED, fitted).** Posterior p10-p90 in brackets.
- `lam_ext_h` owner tickets per present hour, range 2-14 [7.5-11.0], shrink 0.36.
- `p_prod_ext` product share of your tickets, 0.3-0.7 [0.33-0.59].
- `lam_status_h` "how is it going" pings per present hour, 0.2-2.5 [1.87-2.46], shrink 0.32.
- `p_owner_card` share of filed tickets that need your decision, 0.03-0.09 [0.039-0.084].
- `q_card` chance you answer any one waiting card in a present hour, 0.01-0.2 [0.024-0.049], shrink **0.17**,
  the best-determined knob in the model.
- `p_watch` 0.4-1.0, `notice_min` 3-45 min: how fast you notice a stalled window. Both are barely constrained.
- `owner_presence_mult` 0.8-1.2 [0.94-1.17]: scales the presence profile.

**C. The work (ASSUMED, fitted).** `p_park` 0.2-0.55 [0.36-0.52] (shrink 0.55), `p_quick` 0.35-0.85 [0.44-0.79],
`helpers_per_job` 1.0-3.5 [1.79-3.21], `helper_cap_v2` 2-4 [2-3], `dispatch_min` and `quick_min` (seat minutes),
`init_queue` 5-60, `f_prod` 0.1-0.8 and `f_proc` 0.2-0.9 (follow-ups per close), `p_proc_child` (process share of
follow-ups), and `commits_prod`, `commits_proc`, `commits_ledger` (which make the process share).

**D. Defects and checking (ASSUMED, fitted).** `mu_prod` 0.1-0.9 and `mu_proc` 0.05-0.5 (defects per ticket),
`kappa` 0-0.15 (extra defects per concurrent helper), `b_shared` 0.1-0.5 (blind share), `s_self` 0-0.15,
`s_rig` 0.2-0.8 [0.22-0.47] (shrink 0.53), `fr_rig` 0-0.06, `p_fix` 0.6-0.95, `e_disc` 0.02-0.3 per day, and
`p_link` (a discovered defect is filed with `caused_by`, which is what the rework share counts).

**E. Stalls (ASSUMED, fitted).** `p_stall` 0.03-0.35 [0.09-0.25] and `r_self_h` 0.05-1.5 per hour.

**F. Tokens (ASSUMED, fitted).** `acct_w_lukas` 0.2-0.45: lukas's share of the burn.

**G. v3 roles (ASSUMED, V3_ONLY, never fitted).** Arbiter: `arb_s_lo`, `arb_s_hi`, `arb_fr_max`, `arb_ite`,
`arb_check_min`, `arb_batch_q`, `arb_batch_gamma`. Auditor: `s_aud`, `aud_ite`, `p_rule`, `rule_delta`,
`rule_check_min`. Operations: `m_ops_stall`, `m_ops_waste`. Producer: `m_prod_f`, `prod_ite_day`. Innovator:
`m_innov`, `innov_ite_week`. Conductor: `m_cond`, `cond_ite_msg`. Dispatcher: `p_ring_ok`, `p_unwork`, `c_wake_ite`.
Rollout: `role_build_tix`, `role_cards_day`, `teeth`. Each range includes "no effect", and most include harm.

**The plain reading.** Of the 34 fitted knobs, only five shrank below 0.6: `q_card`, `lam_status_h`, `lam_ext_h`,
`s_rig` and `p_park`. Most of the rest have a shrink of 0.8-1.07: the fit left them almost as uncertain as the
guess. Nine targets cannot pin down 34 knobs. Many combinations reproduce the same week, which is why the model is
used as an ensemble and not as one best setting.

## 4. How the fit works

**Data: one week of v2.** The ledger's 7 days to 2026-10-27 06:25Z (`rimflow_metrics.py --days 7`), the spend census
for the same 7 days, account usage at hour 128, and owner messages 10-05 to 10-27 for the presence profile. Brief:
`D:\ClaudeWork\rimmandrake\rimflow_sim\calib_brief.md`.

**The 9 targets** (`targets` in the params file), with value, tolerance and source:

| target | value | tolerance | source |
|---|---|---|---|
| `filed_d` tickets filed/day | 221.4 | ±10% | ledger: 1,550 in 7 d |
| `done_d` closes/day | 132.6 | ±10% | ledger: 928 |
| `rework_share` | 0.128 | ±0.03 | 198 of 1,550 filed are `caused_by` a done item |
| `vfail_share` | 0.093 | ±0.03 | 57 fails / 615 verify results |
| `nudges_d` | 31.0 | ±15% | friction census: 40% of about 78 typed messages/day drive the machine |
| `ite_week` | 1.896e9 | ±15% | spend census |
| `helpers_week` | 1,271 | ±15% | BENCH 624 + FOUNDRY 647 helper transcripts |
| `proc_share` | 0.703 | ±0.07 | `process_share.py` 721 / 1,026 commits |
| `owner_resolve_med_d` | 1.59 d | ±35% | median wait of 61 resolved owner-decision items |

**Loss.** For each target, error ÷ tolerance (relative or absolute). The loss is the **worst** of the nine. A
parameter set is "inside" when the worst is ≤ 1, meaning every target is within tolerance at once. This is
Approximate Bayesian Computation (ABC): with no formula for the likelihood, you keep the parameter sets whose
simulated output looks like the data.

**Search, in three stages, all with fixed seeds.**
1. `calibrate`: uniform draws from the full prior box (`--prior-seed 7`), one 2-week run each. These are the pilot.
2. `narrow`: take the best 5% of pilot draws (score = sum of squared, capped errors), make a box around their
   2.5-97.5 percentiles widened by 25%, clipped to the prior.
3. `mcmc`: 40 chains, up to 600 steps, `--prior-seed 11`. Each step moves every knob by a Gaussian of 4% of its prior
   width (reflected at the edges), runs the model on a **fresh** seed, and accepts the move if the worst error stays
   ≤ max(1, current). A chain first walks downhill into the tolerance region, then wanders inside it, recording
   every 10th step. At step 400, 26 of the 40 chains were still outside, so they were restarted once from chains
   that were inside (`--respawn`).

**Ensemble.** "park" recorded 1,588 states, 636 of them distinct. "pull" recorded 1,120, 353 distinct. From each,
240 members are spread evenly across the chains. The 26 V3_ONLY knobs are then redrawn per member from their
priors (seed 4242), so the ensemble carries the full uncertainty about the roles.

**Seeds.** Pilot: run seed 1000 + member. MCMC: hash(11, chain, step). Validation: 900000 + 7 × member + k.
Experiments: 50000 + 97 × member + k. Counterfactual and backtest: 700000 + 7 × member + k. Re-running any command
reproduces it bit for bit.

**Validation** (`validation.json`): the 240 members re-run on 3 fresh seeds each (720 runs). The ensemble medians
sit on the targets (filed 213.7, done 135.0, nudges 28.7, ITE 1.92e9, helpers 1,276, owner wait 1.48 d). Each target
alone is inside its tolerance in 67-92% of runs. All nine at once: only **16%**. One simulated week is about as noisy
as the tolerances are wide.

## 5. Worked examples with real numbers

**Example 1: why your cards wait about a day and a half.** The posterior middle of `q_card` is about 0.036: in any
hour you are present, each waiting card has a 3.6% chance of being answered. You are present about 12.4 hours a day
(11.8 × a presence multiplier near 1.05). The median wait is the number of present hours until the chance of still
waiting falls to one half: ln 2 / −ln(1 − 0.036) ≈ 18.9 present hours, or 18.9 / 12.4 ≈ **1.5 days**. The target was
1.59. (My arithmetic, on the fitted range.) Now the held-out week ending 10-12, where the real median was 6.36 days
with presence scaled by 1.10 (about 13.6 h/day): reproducing it needs q ≈ 1 − 2^(−1/86.5) ≈ **0.008**. The prior's
floor is 0.01. The week ending 10-19 (7.81 days at about 9.7 h/day) needs 0.009. **The model was not allowed to
produce those weeks:** the behaviour that made them was outside its prior box.

**Example 2: same work, a third of the tickets.** The three v2 weeks as `v3_vs_v2.py` measures them
(`D:\ClaudeWork\rimmandrake\v3_vs_v2\v2_weeks.json`):

| week ending | helpers | tokens (ITE) | closes | helpers per close | ITE per close | your messages | tickets you filed |
|---|---|---|---|---|---|---|---|
| 10-12 | 1,388 | 1.65e9 | 267 | 5.2 | 6.18M | 448 | 18 (4%) |
| 10-19 | 917 | 1.11e9 | 279 | 3.3 | 3.98M | 355 | 122 (34%) |
| 10-26 (tag) | 1,171 | 1.59e9 | 773 | 1.5 | 2.06M | 434 | 271 (62%) |

The work actually done (helpers launched, tokens spent) was flat or higher in the week ending 10-12. Your input was
flat (448 messages). What tripled was the number of **ledger closes** per unit of work. In the model one ticket is a
fixed amount of work: `helpers_per_job` and `p_quick` were fitted so that 1,271 helpers go with 928 closes, about
1.4 per close. Feed it the 10-12 week and it launches about 1,400 helpers (inside the real range) and so must close
about 1,000 tickets. The real ledger recorded 267.

## 6. The backtest, and why it failed

**What it did** (`cmd_backtest`, run 2026-10-27, `D:\ClaudeWork\rimmandrake\v3_vs_v2\backtest.json`). It took the
two v2 weeks the fit never saw (ending 10-12 and 10-19). For each, it scaled the ensemble's owner presence by your
active hours ÷ the tag week's (1.10, 0.78), and your arrival rate by your messages per active hour ÷ the tag week's
(0.94, 1.04). It ran 240 members × 2 seeds and asked whether each of 7 real metrics fell inside the p5-p95 range. It
needed 75% of the 14 cells. It got 6/14 (park) and 4/14 (pull).

| metric | 10-12 real / range | 10-19 real / range |
|---|---|---|
| closes | 267 / 813-1,132 MISS | 279 / 621-939 MISS |
| filed | 522 / 1,302-1,811 MISS | 476 / 1,006-1,461 MISS |
| owner wait median | 6.36 d / 0.85-2.27 MISS | 7.81 d / 1.11-2.99 MISS |
| rework share | 0.080 / 0.088-0.152 MISS | 0.107 / inside |
| tokens | inside | 1.11e9 / 1.29-2.02e9 MISS |
| helpers | inside | inside |
| verify-fail share | inside | inside |

**Why: four causes, the first two decisive.**

1. **The unit changed under it (decisive).** The model measures work in tickets. Through v2, a ticket was not a
   fixed amount of work: the ledger was still being adopted. Your messages that became ledger items rose from 4% to
   34% to 62% (example 2). Bulk ingestion arrived, for example 128 tickets filed between 04:00 and 05:00 UTC on
   10-24, mostly "found by GPT review, verified". So did file-and-close bookkeeping: in the calibration week, 697 of
   928 closes were never started and 194 closed within 5 minutes of filing. The real effort (helpers, tokens) stayed
   level while the ticket count tripled. Every metric that counts tickets (closes, filed) missed by about 3x. Every
   metric that counts work or a ratio (helpers, tokens, verify-fail share) passed. That split is the signature of a
   measuring stick that changed, not of a factory that changed.
2. **Your answering practice changed (decisive for owner wait).** Example 1: the earlier weeks need `q_card` below
   the prior's floor. Question cards and the owner-wait practice matured over those weeks. Old items cleared in
   bulk also raise the median of "resolved this week". Nothing the backtest feeds the model (presence, message rate)
   carries that.
3. **The calibration week is not quite the tag week (contributes).** The targets came from the 7 days to
   2026-10-27 06:25Z. `v3_vs_v2` measures the tag week as the 7 days to 2026-10-26 14:00Z (Monday 07:00 PDT). I
   recounted the raw ledger: file events 1,545 vs 1,281, close events 806 vs 647. The extra 16.5 hours caught 276
   filings from the heavy 10-26 tag day (536 filed that UTC day). The fitted model therefore expects about 17-20%
   more closes than the tag week that `v3_vs_v2` compares against, which is outside the ±10% tolerance. On closes
   and filed, the model would not even cover its own reference week as `v3_vs_v2` defines it. Same story for the
   process share: target 0.703, tag week 0.616.
4. **A one-week fit cannot extrapolate a trend (structural).** The calibration brief already said so: 21-day rates
   were about half the 7-day ones ("rates not stationary"). The test asked a snapshot of the steepest point of a
   ramp to reproduce the bottom of the ramp. In that sense it was designed to fail.

**What would have passed.** Comparing on work-based measures (helpers, tokens, verify-fail share, rework share),
which passed 7 of 8 cells, plus fitting on the same window the comparison uses. Closes become a fair measure only
once ledger practice is stable, and v3 changes it again (the Dispatcher, lease-based "doing", the Arbiter's
"done"). That is the main reason the design gives v2 and v3 separate fits that share a work-based core.

## 7. What it can and cannot tell us

**Can.**
- Reproduce one v2 week on average, and show how noisy a single week is (16% of runs land all 9 targets).
- Compare policies on identical worlds: same arrivals, same defects, only the policy differs. The direction of a
  policy effect is trustworthy when it holds across the ensemble and under the quota variants (1x, 1.3x,
  unlimited).
- Price a mechanism: given that the Conductor suppresses pings, what does it cost in blocked hours? Given the
  Arbiter's sensitivity range, how much output does it defer on today's budget?
- Show which assumed knob a result depends on (the "splits": rank correlation of each knob with the effect).

**Cannot.**
- Say whether a v3 role works. Its benefit is a typed-in range. Results that follow from that range are marked
  "(programmed)" in the findings.
- Forecast a date or a count for next week. It was never checked against a week it did not see, and when it was, it
  failed.
- Explain the v2 ramp, or any change in how work is recorded. It has no "practice" variable.
- Measure tokens absolutely: quotas are derived from each member's own burn.
- Speak for your effort. "Nudges" is a count; card handling time is not modelled.
- Bind the process share to real commits: the commit counts per close are fitted knobs, not measured ones.

## 8. Where everything lives

- Code: `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\sim\rimflow_v3_sim.py`, params `rimflow_v3_sim_params.json`,
  selftest `selftest_rimflow_v3_sim.py`.
- Fit and experiments: `D:\ClaudeWork\rimmandrake\rimflow_sim\` (`calib_members*.jsonl`, `mcmc_state*.json`,
  `validation*.json`, `results*.json`, `exp_*.jsonl`, `deltas.txt`, `iso.txt`, GPT rounds `gpt_round*.md`).
- Backtest and counterfactual: `D:\ClaudeWork\rimmandrake\v3_vs_v2\backtest*.json`, `v2_weeks.json`.
- Findings: `D:\Luke\dev\RimMandrake\design\RimMandrake\rimflow_v3_sim_findings_2026-10-27.md`.
- Commands: `rimflow_v3_sim.py [--structure park|pull] {calibrate|narrow|mcmc|validate|experiment NAME|report|one|backtest|counterfactual}`.
