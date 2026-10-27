# RimFlow v3 in a bottle: what the simulation says (2026-10-27)

Item `RIMFLOW_SIM_BUILD_FACTORY_IN_A_BOTTLE`. Design under test: `design/RimMandrake/rimflow_v3_2026-10-26.md`.
Code: `src/RimMandrake/Utils/sim/rimflow_v3_sim.py` (+ `_params.json`, selftest). Data: `D:\ClaudeWork\rimmandrake\rimflow_sim\`.

## What it is

A toy model of the RimFlow *process*, not of the game. Tickets arrive, some carry hidden defects. Two builder seats (FOUNDRY, BENCH) work them with a few helpers each. You are a limited-attention "server" who answers cards. Three weekly token accounts run out. On top of that, the v3 roles are switched on one at a time: Dispatcher, Conductor, Operations, Producer, Arbiter, Auditor, Innovator. Every policy is run against the *same* simulated world, so the differences are caused by the policy, not by luck.

Every parameter in the params file is labelled. CALIBRATED ones were fitted to last week's real v2 numbers. CONFIG ones come from our config. DERIVED ones are computed. ASSUMED ones are guesses with a range.

## How far to trust it

- **It reproduces v2 on average.** 240 fitted variants, two readings of how idle seats behave ("park" and "pull"). The middle of the ensemble lands inside all 9 baseline targets: tickets filed/day, done/day, rework share, verify-fail share, nudges/day, tokens/week, helpers/week, process share and your median card-resolve time.
- **Any single simulated week is noisy.** Only 15-16% of single runs hit all 9 targets at once, because normal week-to-week noise is about as wide as the targets.
- **It cannot tell us whether v3's roles work.** v2 has no Arbiter, Producer or Auditor. Their effectiveness is a guessed range. Wherever a result follows straight from such a guess, it is marked **(programmed)**: the model can only say how big it would matter, not whether it is true.
- **The token limits are synthetic.** They are derived from each variant's own v2 burn, so even v2 runs dry about 3-21 h/week. Every result below is also checked at 1.3x quota and with unlimited tokens.

## Findings, after GPT's third critique

Confidence: HIGH = same sign in >95% of runs and robust to quota changes. MED = 80-95%, or the sign depends on the regime. LOW = depends on an unmeasured assumption.

### Productive

1. **The Dispatcher removes FOUNDRY stalls (HIGH).** It cuts FOUNDRY idle-with-work time by 100-230 min/day. That only turns into more finished work when there is backlog to pull: "pull" gains +0.8 sound closes/day under quotas (80% of runs) and +2.7 with unlimited tokens. "Park" gains nothing. The caps flatten out around 3 wakes/hour and 30/day. 1/hour and 10/day keeps about 60-70% of the benefit. More delivery also means +6-12 escaped defects/week.
2. **The Conductor cuts nudges about 30%, 28 to 19.5/day (HIGH, but programmed).** The model was told batching suppresses pings. What the model adds is the price: under today's quotas, +8-11 blocked hours/week and about -1.2 to -1.6 sound closes/day. With more headroom the price shrinks.

### Dangerous

3. **The Arbiter under today's token budget (HIGH for the direction).** Measured on its own (v3.2 + Arbiter only), under quotas:
   - sound closes -8 to -11/day, done -23 to -29/day, +18-24 blocked h/week, in 100% of runs;
   - escaped defects -61/week, but mostly because less ships. The defect *fraction* falls only 1-2 points;
   - 49-77 more product tickets sit unfinished at the end. It defers work rather than clearing it.
   With unlimited tokens the quality gain is real (defect fraction -3.5 to -4 points), and the output cost shrinks to -2 to -6 sound/day. **Reading: the Arbiter buys quality only with token headroom. On today's budget it mostly buys "less, later".**
4. **Its strictness setting trades output against escapes (MED, within assumptions).** Going from 0.6 to 0.3 gives +1.7-2.8 sound/day and +12-13 escapes/week. 0.9 costs -3 to -4.5 sound/day and saves 15-17 escapes/week. How steep the trade is depends mostly on the false-reject rate, which nobody has measured.
5. **More helpers per seat (MED, partly programmed).** Caps of 4-6 give +11-60 blocked h/week and +8-25 escapes/week for +0.1-1.5 sound/day. A cap of 1 loses a lot. In "park", a cap of 2 matches 3 on output with fewer escapes and less exhaustion. That defects rise with concurrency is an assumption.
6. **The three-wave rollout (LOW).** Switching roles on in waves ships more in week 1 (+10-13 sound/day) but leaks +19-43 escapes/week in weeks 1-3. A small tail remains in week 4. The cause of the tail is not pinned down.

### Optimisation

7. **What the throttle pauses first matters (MED).** The design pauses roles in order (Innovator, Auditor, Producer, Arbiter, Operations). Lowering helper caps first instead gave +4-4.8 sound/day, -33 to -61 blocked h/week and -37 to -45 escapes/week, at -14 to -16 done/day. The catch: in the model, "pausing" the Arbiter saves no tokens (the design says it "batches daily" and never says how much that saves). So this compares against a weak default throttle.
8. **The Auditor as designed does nothing measurable (HIGH that it is small; programmed by its caps).** It is capped at 4 investigations/day and paused by the throttle on most days. So it ran about 4 per week and found 1-5 defects, against roughly 200 escapes. Even at 40/day and 30% sampling it cut escapes by about 1/week. Its sample rate is a dead knob. Any value would have to come from the rules it learns, and that is a pure guess.
9. **The Producer and Innovator cannot be judged.** Alone, both show about zero effect under quotas. The Producer's +7 sound/day with unlimited tokens is exactly the benefit typed in.

### What to do with this

- Measure the Arbiter's false-reject rate and per-verdict token cost before choosing a strictness, and give it headroom or it starves delivery.
- Decide what "Arbiter batches daily" saves in tokens, or remove it from the throttle order.
- Lift or drop the Auditor's 4/day cap.
- Consider lowering helper caps first in the throttle.

---

## Technical appendix

**Model.**
- Discrete-event engine on a heapq calendar.
- Randomness: splitmix64-keyed u01 per ticket lineage, so paired policies share the outside world.
- Builder seats: a serial window plus helper slots.
- Owner: an attention server with a card hazard per present hour.
- Tokens: 3 weekly accounts.
- Throttle: runway-based, pausing roles in config order.
- Arbiter: `n_rig=2` check slots (CONFIG). The round-3 prompt said 1, which was wrong.
- v3 composition: v3.0 Dispatcher; 3.1 +Conductor; 3.2 +Operations; 3.3 +Producer and Arbiter; 3.4 +Auditor and Innovator.

**Calibration.**
- ABC-MCMC to 9 v2 targets.
- Park: 1588 recorded, 636 unique accepted. Pull: 1120 recorded, 353 unique.
- 240 members per structure.
- Parameters marked V3_ONLY are redrawn per member from their prior (seed 4242), since v2 says nothing about them.
- Posterior shrink for each parameter: `results*.json` → `calibration.posterior`.

**Validation.** `validation*.json`:
- Medians: park filed 214 / done 135 / nudges 28.7 / ITE 1.92e9 / helpers 1276, against targets 221 / 133 / 31 / 1.90e9 / 1271.
- Share of single runs inside each target's tolerance: 67-96%.
- Share with all 9 jointly inside: 16% park, 15% pull.

**Experiments.**
- Run with `python3 src/RimMandrake/Utils/sim/rimflow_v3_sim.py --structure {park|pull} experiment <name>`.
- Names: versions, versions_unlimited, versions_q130, rollout, helper_cap, arbiter, auditor, auditor_cap, wake_caps(_unlimited), throttle, isolate, isolate_unlimited.
- Each runs 1 warm v2 week plus 4 policy weeks (rollout runs 5).
- Each uses 1 seed per member; isolate uses 2, to split seed noise from parameter spread.
- Summaries: `report` writes `results*.json`. Paired-delta table: `deltas.txt`. Isolate and defect-fraction table: `iso.txt`.
- GPT rounds 1-3: `q_round*.md` and `gpt_round*.md`.

**How the findings were read.**
- Percentages are shares of the 240 paired runs that moved in the stated direction. They are prior-conditional scenario results, not probabilities that a deployment helps.
- For the Arbiter, within-member seed noise is 3-10% of the variance in the paired delta. For the Auditor and Innovator it is 10-50%, so those medians are noise.
- "Defect fraction" = escapes / (escapes + sound closes).
- End stocks (`arb_q_end`, `prod_q_end`) are reported because a 4-week horizon can reward deferral.

**Limitations.**
- Pausing the Arbiter lowers its sensitivity but saves no tokens.
- `blocked_h` counts only the hours when all accounts are exhausted.
- Nudges are not owner effort: card volume and handling time are not modelled.
- Producer, Innovator, Conductor and Auditor-rule effects are ASSUMED multipliers.
- Rollout differences also carry role age, rules and queue state, not only defect debt.
