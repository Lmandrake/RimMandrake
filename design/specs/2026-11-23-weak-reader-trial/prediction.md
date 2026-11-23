# Prediction, written before any reader ran (2026-11-23, about 10:30 AM PST)

The unit is a case: one real section, one situation, one key. The score of an arm on a case is the share of correct
acts among the readers of that arm. The readers never see both texts. The difference is new minus old, in points.
The pilot has about 10 cases for each kind and 5 Sonnet readers for each arm.

## What difference is worth knowing

- A rewrite of the rule files costs millions of weighted tokens. One wrong act in ten (10 points) on a rule that
  every seat reads is worth that cost. A smaller difference is not worth a further rewrite.
- The readers of one case are not independent trials of the rewrite. The case is the unit, so more readers add little.
- [guess ~60%] The per-case difference has a standard deviation of about 35 points. Then 10 cases give a standard
  error of 11 points, and the pilot can see only a difference of about 30 points (2.8 standard errors). To see 10
  points needs about 95 cases for each kind. The pilot measures the standard deviation, and the full size comes from it.
- 5 readers for each arm: enough to tell a case that always fails from a case that sometimes fails. 2 Opus readers: a
  check of the ceiling only.

## The instrument can see only if all four are true

1. The grader scores at least 95% of the planted answers as planted (correct plants, wrong plants, and a correct act
   of a different case).
2. CORRECTION is the known positive: the old line is false. New must be at least 30 points above old. If it is not,
   the cases do not turn on the changed line, and the trial cannot see.
3. CONTROL is the known zero: both arms are the same bytes. The difference must be inside plus or minus 15 points.
4. Readers with NO text score at least 20 points below the new text over all cases. If they do not, common sense alone
   gives the act, and the text was not tested.

## Results and what each would show

| result | reading |
|---|---|
| BINDING new − old ≥ 30 points, with 95% interval above 0 | the rewrite helps a weak reader where a term got its meaning |
| STYLE new − old ≥ 30 points, with 95% interval above 0 | the plain style itself helps. This would overturn the earlier 0 of 5 |
| BINDING or STYLE inside ±10 points, all four instrument checks pass | no difference that this pilot can see; the interval says how large a hidden one can be |
| BINDING or STYLE ≤ −10 points | the rewrite does harm there; each such case is read and named |
| Opus old ≥ 90% on STYLE and BINDING | the owner's premise holds (Opus reads a muddled rule correctly) |
| Sonnet old ≥ 90% on STYLE | no room: Sonnet is not weak enough on these texts for STYLE to show |
| any instrument check fails | the instrument cannot see. No verdict on the rewrite is given |

My own guesses: CORRECTION +60 [guess ~75%]. CONTROL 0 ± 5 [guess ~80%]. BINDING +15 [guess ~50%], mostly from
"the text does not tell me" turning into a correct act. STYLE 0 ± 5 [guess ~75%], with both arms near the top.
Opus old near Sonnet old on STYLE [guess ~60%].

The bars above do not move after the run.
