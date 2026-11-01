# Fan-out on equal terms: simulator upgrade, census and refit

2026-11-01. Item `ARCH_SIM_MEASURE_FANOUT_EQUAL_TERMS`. Offline; no game, trial, pin or arm code touched.
Code: `src/RimMandrake/Utils/sim/fanout_sim.py`, `selftest_fanout_sim.py`, `fanout_census.py`.
Rows and tables: `D:\ClaudeWork\rimmandrake\fanout_sim_2026-11-01\`.

## Answer

- **Was the owner right?** Half. v2 and v3 did model fan-out (seat cap 2 to 4, defects rising with helpers) but paid no
  merge cost. All Ralph arms were serial, with their fan-out reduced to a wall-clock divisor and the collision term forced
  off; trio and TP inherited that divisor. So the comparison was unequal: fan-out was credited to v2/v3 and denied to
  Ralph, and that fed the `RALPH_A_CAPACITY = 0.5` assumption (`arena_analysis.py:250`).
- **Efficient?** Yes. One 860-line module over the existing sims, no base sim edited. 43,920 runs took about 16 minutes on 12
  processes.
- **Fan-out multiplies every arm by about 1.6 to 1.9** by cap 4. Beyond that the v3 arms lose 2 to 10% and the rest gain 3 to
  15%, because the weekly quota binds at 8.
- **Ranking:** same median leader, unresolved winner. v3.4 at cap 4 leads unattended but wins only 60 of 120 held-out members.
  Only TP has an 80% gap band wholly behind it. On equal fan-out the sim puts Ralph A at about 0.79 of v3.4 (80% 0.49 to 1.13),
  against the assumed 0.5. That is a model output, not a measurement.
- **The data tightened fan-out's costs, but barely tightened the ranking.** What drives the ranking was never measured:
  how many defects a Ralph ticket carries compared with a v3 ticket.

## 1. Which simulators lacked fan-out

| simulator | concurrency before | fair? |
|---|---|---|
| `rimflow_v3_sim` (v2, v3.x) | real: seat cap 2 to 4, kappa defects | no merge cost |
| `ralph_loop_sim` A, AB_test | serial; "+sub" only divides wall time; kappa forced 0 | no |
| `ralph_loop_sim` AB_build, C | two lanes with assumed collisions | no |
| `testpilot_sim` TP, TP+ | inherits C's divisor | no |
| trio arena | serial builder then critic | no |
| `testing_investment`, `ctx_strategy` | none, and they do not compare architectures | not needed |

## 2. What the upgrade does

Nine arms: v2, v3.0, v3.4 (the trial's v3), A (trial ralph_a), AB_test, AB_build, C, TP, TP+. There is no separate trio arm:
TP+ is its nearest relative, with a critic and test pilot, so trio results here are TP+ results by analogy.

Every arm draws from one pool of N workers, with N in 1, 2, 4, 8. No arm is unable to fan out. Every arm pays the same:

- **Pool:** one slot per helper; LLM judgement (Arbiter, critic, pilot fix, fair check) also takes a slot.
- **Defects:** one rate, theta × (1 + kappa c) / (1 + kappa c_ref), where c is the mean others beside the ticket, capped at
  k_sat. Theta was calibrated at real concurrency, so a serial run sits below it.
- **Merge:** landing checks every ticket that landed on the seat during the flight. Conflict costs a merge spell, sometimes
  a rerun.
- **Servers:** one landing server, two rigs, queue wait only.
- **Tokens:** a briefing charge per helper beside others; quota is charged as each unit starts.
- **Fair check:** any ticket that overlapped another worker and was passed by no Arbiter or critic pays a blind check. That
  includes v3's process tickets, which its Arbiter does not see.
- **Unattended means stocked.** Without a stock the only tickets were role-invented, which gave v3.4 6 a day and the rest
  0.5. That ranks proposers, not workers, so the queue now holds a stock faster than any arm clears it.

With kappa 0, A at N=1 reproduces the serial loop (selftest, 67 checks, mutation probe on the cap).
GPT reviewed four times (`gpt_a1.md` to `gpt_a4.md`). Twelve findings on the first pass, one concrete defect on the
second (overlap hidden by averaging), four on the third (process tickets skipped the fair check; a spiral ran only when the
whole pool was idle, which favoured Ralph; a redo skipped its rebase time; the flip threshold ignored cap 2), three on the fourth (machine slowdown missed queued checks, verdicts and spirals; a
clamp in the hold elasticity; bookkeeping-only commits left in the git census, which the analysis had already filtered, so no
census figure moved). All were verified and fixed except one false alarm on the window. All 43,920 runs below were redone
after the last fix; that last fix moved no leader and no median by more than about 0.5.

## 3. Census

Thirty days, 4,812 helpers. Scripts and results are in the scratch folder.

| source | finding |
|---|---|
| helper registry | mean concurrency 2.16 BENCH, 2.13 FOUNDRY, 2.89 together; 4+ workers 29% of time, 8+ 4.6%, max 22 |
| helper registry | duration and tokens do not rise with concurrency (corr -0.15, -0.07) |
| registry and ledger | output elasticity on concurrency, hour and day fixed effects: 0.47 BENCH, 0.39 FOUNDRY, 0.63 all. Observational |
| ledger verifies, 1,084 | fail rate 0.05 to 0.07 under 1.5 workers, 0.14 at 1.5 to 3, 0.11 at 3 to 5, 0.10 above: rises then saturates. Kappa 0.33 ± 0.19 |
| git | 6,482 publishes, 21 unique conflicts, about 0.3 to 1%, although 42% of commits touch a file changed within the last 30 minutes |
| relentless store, 13 h | real parallel 3 to 5 with blind checks: 44 worked, 35 done, 1.37 generations per done, check about a quarter of a work unit, blind fail 0.20 to 0.25 |
| arena | ralph_a 6 of 14 passes failed; paired ITE ralph_a/v3 0.85 on 6 tasks, wall 3.0 on 8 tasks. Serial |

`streams/series.jsonl` and the account usage series were not mined beyond the census's daily 170M ITE.

**UNMEASURED, and no existing data can measure it:** causal fan-out gain (trial arms were serial, so the elasticities above
are correlations); Ralph and trio under real fan-out; Ralph's defect rate against v3's; merge cost at 8; semantic
conflicts that land clean; landing wait; briefing tokens; trio spend (capture blocked).

## 4. Priors to posteriors

| parameter | prior | posterior | evidence | effect on ranking |
|---|---|---|---|---|
| kappa | 0 to 0.15 | 0.10 to 0.50 | verifies | moved up, not narrower; prior was wrong; now minor |
| k_sat | 7 | 2 to 4 | verifies by workers | small |
| c_merge | 0.0005 to 0.03 | 0.0003 to 0.003 | git, 10× tighter | dropped out of the drivers |
| slow | 0 to 0.05 | 0 to 0.01 | helper registry | gone |
| chk_ite | 100k to 300k | 150k to 260k | relentless | small |
| chk_min | 2 to 15 | 3 to 9 | relentless | small |
| chk_fr | 0.02 to 0.20 | 0.03 to 0.15 | relentless | weakened |
| r_p_off | 0.03 to 0.20 | 0.10 to 0.45 | arena, relentless | moved up and **wider**; now a top driver |
| r_ite_mult | 0.60 to 1.20 | 0.65 to 1.12 | paired ITE | little change |
| c_invalid, p_invalid | narrow | 0.05 to 0.40 | arms disagree | widened on purpose |
| crit_ite, crit_min | 80k to 250k, 5 to 20 | 130k to 260k, 3 to 10 | relentless, same job; trio's own capture UNMEASURED | small |
| r_mu_mult | 0.8 to 1.6 | **unchanged** | none | **top driver** |
| r_dur_mult | prior | **unchanged** | wall ratio holds restarts and off-track passes, so it does not identify this; 1 to 2.5 run as a sensitivity | moderate |

The posterior boxes are judged from the evidence column; they are not a formal likelihood fit, because the evidence is too
thin in the dimensions that matter. The base ABC members and their thetas are unchanged. The boxes are in `POSTERIOR` in
`fanout_sim.py`, each with its evidence.

Drivers of the margin over v3.4 (rank correlation, posterior, unattended, A then AB_build): r_mu_mult -0.46, -0.45;
r_p_off -0.43, -0.45; r_proc_keep -0.27, -0.30; r_ite_mult -0.21, -0.24; r_p_spiral -0.24, -0.20. Before the refit r_mu_mult
already led (-0.38, -0.41), followed by r_proc_keep, chk_fr and r_dur_mult. Merge cost and kappa do not appear. r_p_spiral and
r_proc_keep kept their priors.

## 5. Results

Sound product closes per day, 240 members. Median and 80% band over the ensemble, each arm at its best cap.

| arm | unattended, posterior | best N | prior, same scenario | attended, posterior |
|---|---|---|---|---|
| v3.4 | **39.2** (25.8 to 52.3) | 4 | 41.2 | 35.6 |
| v3.0 | 34.8 (21.1 to 49.3) | 4 | 34.6 | 36.5 |
| AB_build | 32.4 (17.8 to 48.1) | 8 | 39.4 | 32.6 |
| v2 | 31.9 (20.7 to 47.6) | 8 | 31.8 | 36.8 |
| A | 30.2 (16.8 to 46.6) | 8 | 36.1 | 30.6 |
| C | 30.0 (17.6 to 43.5) | 8 | 38.1 | 28.3 |
| TP+ | 29.8 (17.4 to 40.9) | 8 | 37.8 | 29.8 |
| AB_test | 26.3 (15.3 to 40.6) | 8 | 30.4 | 26.8 |
| TP | 21.4 (12.8 to 31.3) | 8 | 26.0 | 21.1 |

Win shares unattended, over 120 held-out members, with cap chosen on the other half, averaged over 41 splits: v3.4 60,
v3.0 24, AB_build 16, A 7, TP+ 6, v2 5, C 2. These describe this ensemble; they are not probabilities of being right.

Paired gap to v3.4 unattended, median and 80% band: v3.0 -2.6 (-12.3 to 4.5); v2 -5.4 (-13.8 to 3.3); AB_build -6.0 (-18.3 to 5.8);
A -7.3 (-20.4 to 5.1); C -8.4 (-20.4 to 2.4); TP+ -9.2 (-20.7 to 1.4); AB_test -11.7 (-24.2 to 0.6); TP -17.0 (-29.3 to -5.2).

- **Ranking change.** Same unattended leader. Ralph and TP arms fell 4 to 8 sound closes a day from prior to posterior, v3.4
  fell 2, and v3.0 and v2 did not move. AB_build's gap to v3.4 went from -2.2 to -6.0.
- **Attended and parked,** v2, v3.0 and v3.4 are a dead heat within 1.4 closes; win shares attended are 29, 29, 25 for v3.4,
  v3.0, v2 and 24 for AB_build. On the prior AB_build led attended by a hair.
- **Output uncertainty shrank only a little.** A's paired gap went from -6.2 (-19.8 to 9.3) to -7.3 (-20.4 to 5.1).
- **By cap.** v3.4 19.8, 31.5, 39.2, 35.5 at 1, 2, 4, 8. A 16.6, 19.4, 26.4, 30.2. AB_build 18.3, 23.6, 31.3, 32.4. Gain from 1
  to 4, median: v3.4 1.9, AB_build 1.7, A 1.6. At 8 these arms reach the quota: about 2.07G ITE a week against 1.8G at 4, 30 to
  41 hours a week blocked.
- **Serial, v3.0 wins** (121 of 240 members). In the sim v3.4 earns its lead only under concurrency, so a serial trial would
  not have shown it. That is a sim conditional, not evidence about the real arms.
- **Quality cost, which the headline hides.** Escapes per week for v3.4 go 28, 125, 159 at 1, 4, 8; for A 45, 118, 141.
  Escapes per done ticket rise too: v3.4 0.16, 0.23, 0.25; A 0.20, 0.31, 0.32. Merge conflicts stay under 4 a week. "Maximise
  fan-out" is limited by defects and quota, not by merging.
- **Sensitivities.** r_dur_mult 1 to 2.5 moves A's gap to -9.1; checking every ticket in every arm moves it to -9.2. v3.4
  leads in both, with 30 and 31 of 60 wins.

## 6. Hold-out

| check | predicted | observed | verdict |
|---|---|---|---|
| A at N=3 to 5, relentless excluded: done per hour | 1.4 to 1.8 (80% 0.8 to 2.6) | 2.7, breaker open for most of the run | **sim low by about 40%**, above the top of the band at each N; task mix and window not aligned |
| blind check fail share | 0.19 to 0.20 | 0.20 to 0.25 | good, but it supports check frequency, not throughput |
| arena-only r_p_off | 0.20 to 0.66 | about 0.21 | only at the bottom edge: arena alone overstates it |
| kappa, earlier vs later verifies | 0.30 | 0.34 | stable, se large |
| elasticity on realised workers, v3.4 2 to 4 | 0.80 (0.56 to 1.08) | 0.39 to 0.63, observational | **sim high** |
| elasticity, A 2 to 4 | 0.68 (0.46 to 0.88) | 0.39 to 0.63 | somewhat high |
| ITE per done, A/v3.4 | 0.86 at N=1 | 0.85 | fitted, so no test; at N=4 the sim says 1.46, never observed |

**Two misses matter, and they pull opposite ways.** The sim under-predicts A's real throughput, which could hide a smaller gap to
v3. And it over-credits scaling: if only the v arms are over-credited, a cut of 0.28 unattended or 0.16 attended (2^-d per doubling
above cap 2) puts AB_build level with the leader, and the gap to the census is about 0.2 to 0.4. The census is observational and A
is also high, so this is a warning, not a correction: v3.4's lead is not robust to model error.

## 7. What this does and does not support

- The simulator case for `RALPH_A_CAPACITY = 0.5` came from an unequal comparison, so it no longer supports that figure. This does
  not show 0.5 is wrong: no real measurement exists. Under equal terms the sim gives 0.79 unattended (0.49 to 1.13) and 0.90 attended
  for A at 8 against v3.4 at 4, and 0.72 and 0.83 at equal cap 4, resting on an assumed r_mu_mult. I did not change `arena_analysis.py`,
  because it is arm-adjacent analysis of the running trial; that is a decision for the trial's owner seat.
- Cap 4 is the supported default for the v3 arms. The others gain 3 to 15% more at 8 while spending the whole quota, so 8 is worth
  trying only with more quota, and only if the extra escapes are acceptable.
- Owner ruling: parallel maximised while reliable and fairly checked. The model supports that up to about 4, conditional on the
  escapes in section 5 being bearable, which is a product judgement, not a sim output.

## 8. Biggest unknown, and the cheapest experiment

**Biggest unknown:** Ralph's real defect rate against v3's under fan-out (r_mu_mult, never measured), with the causal gain from
more workers close behind.

**Experiment: a small 2 × 2 crossover on live unattended work.** Cap 2 against cap 6, Ralph against v3, alternating randomised
3-hour blocks, 16 in all, over about two days, drawing from one relentless queue. Record every attempted iteration with its
disposition, not only landings, because a landed-only sample cannot see off-track work, and give every landing the same blind
checker. Seed about ten tickets with known defects so the checker's hit and false-alarm rates are known; without that it measures
checker outcomes, not latent defects.

Direct cost is about 130 checks at 200k ITE, say 26M ITE, about a sixth of one day's usual spend, assuming relentless's 2.7
tickets an hour. Repairs of failed checks and any difference in execution spend come on top.

What it can resolve is modest. About 30 tickets a cell gives a 95% interval near ±14 points on a 20% rate, and wider in truth,
because each cell has only four blocks and tickets within a block are not independent. It would detect a large difference in defect
rate or a doubling-type gain, not a small one. It measures causal gain per arm directly; r_mu_mult and r_p_off only through the
calibrated checker and the disposition labels. Separate breaker-open time and backlog carry-over between blocks. Not started: it
would compete with the running trial.

## 9. Limits

- Runs share each ABC member's theta. Prior and posterior reuse unchanged parameters and the same keyed quantiles; only selected
  posterior parameters get fresh keys. So prior-to-posterior moves are partly paired, not independent redraws.
- v3 quick tickets pay no helper ITE because the base model books them in `seat_ite_per_close`; Ralph pays. Small tilt to v3.
- Off-track is keyed by lane iteration, kept for the N=1 identity: noise across N, not bias.
- Mapping a verify-fail coefficient to latent defects assumes verify sees them proportionally.
- Sim tickets are not relentless items: 2.7 done per hour compares like-ish units only.
- Weekly quota is the sim's 2.1G; recent real spend is about 1.2G a week, and cap 8 results depend on it.
