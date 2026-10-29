# TestPilot round 2 (Opus): answer to GPT's independent design

Item TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD. Round 1: `design/RimMandrake/testpilot_design_opus_2026-10-29.md`
(cited as "R1 Dn/Kn/Sn"). GPT's design: `D:\ClaudeWork\rimmandrake\testpilot\gpt_design.md` (cited "GPT Cnn").
Sim: `src/RimMandrake/Utils/sim/testpilot_sim.py`, now with `--scenario base|gpt|gpt_guard|gpt_1G`.

## 1. GPT's claims that bear on TP+: concede, improve, defend

Concede (TP+ changes):
- A1 CONCEDE GPT C07 (full-list load time). I used ~25 min (R1 F1, X3; `.claude/skills/rimworld-load-round/SKILL.md:14`).
  The measured run is 13-19 min (03:16 to 03:35, 2026-10-11:
  `.claude/skills/live-debugging-proof-harness/references/run-checklists.md:23`); 25 is the skill's round figure.
  Change: the sim's full-load prior was 15-30; the gpt scenario uses GPT Q13's 17-30 for the whole excursion (swap,
  load, restore). Accepted/day does not move (section 3); the full-list cost is game minutes, which are not the bottleneck (E3).
- A2 CONCEDE C16. A grant expiry or an owner presence restriction is a HOLD, not a reload; a bridge timeout needs
  reconnect and reconcile, not R1. R1 D4's canary listed "grant valid > 45 min" as a session check; it becomes
  a hold-reason, and R1 (session dead) is reserved for process death, menu drop, a dead colony or failed reconcile.
- A3 CONCEDE C17. The 22 s minimal load (`.claude/skills/rimbridge-companion/SKILL.md:67`) is too short for a plan
  and critic cycle. TP+ already plans per pass (D3), but the sim's `plan_min` overlap assumption is dropped: plans
  for the next batch are written while the CURRENT batch tests, never "during the reload".
- A4 CONCEDE C33. R1 D7's full-list clash check must not start a quicktest world on the full list
  (`.claude/skills/rimworld-debug-testing/SKILL.md:65`: it has crashed the process). The full-list session loads a
  compatible scratch save instead. (R1 D7 never said quicktest, but never forbade it either.)
- A5 CONCEDE C35. "Use a scratch filename" is a prompt, not a guard. The pilot's game runs with a test save
  directory; keeper saves are write-denied at the filesystem where the OS allows it, verified at session start.
- A6 CONCEDE C10. A HARNESS/SITE hot-fix (R1 D5) makes the test run; it does not ship. Acceptance needs the same
  test to pass from a clean fixture without the in-session repair. TP+ adds: every hot-fixed PASS is re-run once
  from clean in the next session before it counts. Cost: one extra test per hot-fix (p_invalid .09, F12).
- A7 CONCEDE C24 and C30. A rejected or simplified item keeps its id, priority and round count; children of a
  split inherit the parent's budget. R1 D2 said "2 more rounds" after simplify but did not stop a split resetting it.
- A8 CONCEDE C22/C29 in part. Something must own the game process across pilot passes; R1 D3 let the loop script
  own it implicitly. TP+ names it: one serialized machine worker per machine (deploys, launches, canaries, fences)
  with an epoch per session; a pass gets the epoch, and a stale pass's bridge calls are refused.

Improve (adopt GPT's idea):
- B1 IMPROVE with C18. The claim key becomes (item, candidate fingerprint, scenario, tier, repetition), so a
  rebuilt candidate cannot inherit a PASS. R1 D4 voided a PASS on any source change; this is the same rule as a key.
- B2 IMPROVE with C12. Candidate records are immutable files (`candidates/<id>/<attempt>.json`); the session file
  of R1 D3 becomes `sessions/<machine>/<epoch>.json`. Evidence is append-only.
- B3 IMPROVE with C28. The script canary adds GPT's checks: ticks advance when they should, a state query answers,
  the loaded artifact's identity matches the claimed candidate, the instruments are live (log not capped, journal
  not wrapped). These are all script checks; none needs pilot judgment.
- B4 IMPROVE with C59-C63 for the experiment (R1 section 5): both machines per arm, exclusive by block, crossover
  blocks, planted-failure drills, owner minutes by start/stop timing, a delayed retest at 48-72 h.

Defend (with evidence):
- E1 DEFEND the script canary as the gate over GPT's written validity certificate (C26-C27). A certificate the
  pilot writes is the maker grading its own session. The canary is code that reads the bridge (R1 D4); p_invalid
  is measured at .09 (R1 F12), so one session in eleven is silently bad and a pilot that misjudges even 5-30 % of
  those (`p_misjudge`) books void PASSes. The sim's OAT shows the canary terms move accepted/day by about 0
  (R1 S12), so it costs nothing to keep; its case is the escape count, not throughput.
- E2 DEFEND "the critic decides output" against GPT's y (acceptance yield) as a free parameter (C44, Z-table). In
  the sim the critic's false-reject rate and sensitivity are the two largest levers on accepted/day (crit_fr
  +2.69/-3.21, crit_s +2.79/-2.02 at the prior ends, OAT `oat_park.jsonl`, round 1). GPT's own X03 (C51) agrees:
  y from .88 to .70 drops Z09 below Ralph C. Neither design can claim a win until the critic is measured.
- E3 DEFEND R1 X1 (the pilot is not the bottleneck). GPT C52 reaches it independently (775 machine-min/day of a
  much larger capacity). The sim's pilot idle share is .62 (TP+), and the GPT scenario does not change it
  (section 3). Both designs should stop spending design effort on reload tactics.
- E4 DEFEND a fresh pass per test (R1 D3) over a 50k-token handoff (P05). A pass that reads only the session file
  and one item's plan costs `pass_stack_ite` once per test; GPT's handoff carries a summary forward, and C29 itself
  says "a summary alone cannot establish" state, so the incoming pilot re-verifies anyway. With GPT's 12k startup
  (P08), the fresh pass is cheaper still (section 3: ITE/week falls).
- E5 CONCEDE (was a planned defence) R1 D6 R3's 45-min session-age guard against GPT's I-R04 2-minute drain (C31,
  P12). Run literally (scenario gpt, K=1, drain 2 min, no age guard), TP+ does not churn: reloads per accepted item
  rise .97 to 1.21, and adding my age guard back (gpt_guard) gives 1.17. The guard was a fix for my own K=2 rule's
  churn, not a general need. TP+ takes I-R04 as the trigger and keeps the age guard only as a churn alarm.
- E6 CONCEDE the full-list batch (R1 D7: 4 items / 6 h) to P13 (2 items / 30 min). It costs game minutes (TP+ game
  busy 1110 to 1350 min/day, mostly full-list loads) that are idle anyway (E3), and an item no longer waits 6 h
  for its last gate. Accepted/day does not move (+0.4, inside noise).

## 2. Critique of GPT's design

- G1 (C43-C46) The comparison is static arithmetic, n = min(C, J, (W/7 - F)/c), A = n y. There are no queues,
  no defects that escape and return as rework, no ground truth separate from "accepted". It cannot show the
  effect GPT itself names as Z08's failure mode (C49 "critic non-convergence", "contaminated evidence"): those
  are dynamics, and the formula has only their averages. The sim here models each (rounds, void verdicts,
  escapes) and still ranks the designs differently from C46 (section 3).
- G2 (C46, C48) The ranking is decided by assumed y and F, as C48 admits. Z09's y .88 vs Z07 Ralph C's .80 is
  the whole margin (X03, C51). Without a measured critic the ranking Z09 > Z08 > Ralph C is an ordering of
  assumptions; the bounds (9.8-32.6 vs 7.8-31.3) overlap almost completely.
- G3 (C46 owner touches) Z09 at 3 touches/day against v2 at 31 is unanchored. The calibrated sim's nudges/day for
  every variant, the gated ones included, sit at 19-28 (round 1 S-table); gates do not remove the owner's
  attention, they move it to parks and escalations. Footnote C47 admits the figures are assumptions; they should
  not sit in a ranking table.
- G4 (C26-C27) The validity certificate and taint scope are written by the pilot that ran the session: maker
  grading. GPT's own C40 lists "taint too weak" as a critical problem. A script canary (E1, B3) is the gate; a
  certificate is the record.
- G5 (C31-C32, P12) I-R04 with a 2-minute drain relaxes the owner's rule (C32 says so) for a benefit nobody has
  measured, and without an age guard it restarts whenever a sealed repair is ready. Section 3 shows what that
  does to the reload count.
- G6 (C38 P09) A canary every 60 s during long blocks costs bridge calls and ITE if a model reads it; it must be a
  script with no model in the loop, and the design never says which.
- G7 (C23 G07) A program-requested blind GPT review per item is a cost line the arithmetic does not price
  (Q-table has no GPT minutes); at J = 40 bundles/day (Q06, unmeasured) that is the binding gate, as X02 shows.
- G8 (C49) 7-12 working days to build Z09 against 2-4 + G for Ralph A. C50 concedes the first week can favour
  starting Ralph A; then the recommended experiment (C58) should start Ralph A as the control at once and build
  Z09 behind it, not prepare both for a matched start.
- G9 (C03, C41) "Accepted = frozen requirement + independent check + live + FULL" is the right definition and
  agrees with my accepted_strict, but GPT's counts (21/day) and mine (TP+ 42/day p50) are not comparable units:
  GPT counts parent outcomes, the sim counts items. Neither should be quoted to the owner as a forecast.
- G10 (C15 O-R02/O-R03) The three reload rules need judgments ("a state reset is insufficient", "useful approved
  test") that only the pilot can make; R1 D6 R0-R3 are script-evaluable. GPT's rules are better as the written
  justification, mine as the trigger; keep both.

## 3. GPT's parameters against the sim's, and the re-run

Where GPT gives a number that maps onto a sim input (all GPT values are its own PROPOSED/ASSUMED, C38):

| GPT | GPT value | sim (round 1) | in scenario `gpt` |
|---|---|---|---|
| Q13 FULL excursion | 22 min (17-30) | full_load_min 15-30 | 17-30 |
| Q12 minimal restart | 2 min (1-5) | reload_min 1.5-5 | 1-5 |
| P08 startup context | 12k (8-20k) | pass_stack_ite 30-120k | 8-20k |
| C31/P12 I-R04 drain | sealed repair ready, 2 min | R3: K=2, oldest 45 min, session 45 min | K=1, 2 min, 2 min |
| P13 FULL batch | 2 items / 30 min | 4 items / 6 h | 2 / 30 min |
| P03/P04 rounds | 2, then 4 total with one simplify | CAP 2, simplify, 2 more | same (already equal) |
| Q05 / C51 X01 budget | 1.9G/wk; stressed 1.0G | today's quotas (~1.7-1.9G) | `gpt_1G`: quotas scaled to 1.0G |
| P05 handoff 50k | per pilot context | TP only (handoff_n tests) | not mapped (TP+ has no long pilot) |
| y, F, c, J (Z-table) | .80-.88 yield etc. | emergent, not inputs | not mappable; see E2 |

Scenarios: `gpt` (all mappable values above), `gpt_guard` (gpt plus my 45-min session-age guard), `gpt_1G` (gpt
plus a 1.0G weekly budget). 240 members each, same seeds and member draws as base, fingerprint 709a4939ddf8 (the
base re-run reproduces round 1 to the last digit). Tables: `D:\ClaudeWork\rimmandrake\testpilot\opus\sim\
r2_compare.md`, `tables_gpt*.md`.

| p50 | base TP+ | gpt TP+ | gpt_guard TP+ | gpt_1G TP+ | gpt_1G C+sub | gpt_1G A |
|---|---|---|---|---|---|---|
| accepted_strict/day | 42.4 | 42.5 | 42.6 | 25.9 | 0 | 0 |
| sound accepted/day | 31.1 | 31.2 | 31.0 | 19.0 | (sound_prod 24.4) | (sound_prod 17.5) |
| escapes/week | 104 | 105 | 106 | 66 | 115 | 90 |
| ITE/week | 1.82G | 1.80G | 1.80G | 1.07G | 1.07G | 0.64G |
| reloads/accepted | .97 | 1.21 | 1.17 | 1.15 | 1.47 | n/a |
| game busy min/day | 1110 | 1350 | 1340 | 791 | 1170 | 0 |
| pilot idle share | .62 | .54 | .54 | .73 | | |

Headline. GPT's operating parameters do not change TP+'s output: paired median +0.43 accepted/day (p10/p90
-0.53/+1.76), TP +0.05. They cost 25 % more reloads per accepted item and 22 % more game minutes, both on a resource
that is not the bottleneck. The budget is what matters: at GPT's own stressed 1.0G (X01), TP+ falls by 16.7
accepted/day (p50, paired), and on sound production Ralph C+sub beats TP+ in 98 % of members (24.4 vs 19.0/day)
and Ralph A, which never spends more than 0.64G, draws level (TP+ ahead in only 60 %). That contradicts GPT's X01,
where Improved stays first at 1.0G (13.3 vs Ralph C 12.3): the static model charges every row the same gate, the
sim charges TP+'s critic and pilot passes against a budget that Ralph A does not need. TP+ remains the only design
with non-zero strict acceptance at every budget, because the others lack one of the two gates by construction.

## 4. Revised TP+ in six lines, and its critical flaw

1. Foundry: two Ralph C builder loops with bounded subagents; each item's spec carries its live test plan, written
   before the build; candidates are immutable records keyed (item, fingerprint, scenario, tier, repetition).
2. One blind critic gate, 2 rounds, one automatic simplify/split, 2 more, then park; children inherit the budget.
3. One machine worker per machine owns the game (deploy, launch, fence by epoch, script canary with GPT's C28
   checks); a fresh pilot pass per test reads only the session file and one plan; grant expiry is a hold.
4. Reload by rule: R0 cold, R1 dead, R2 nothing valid left, I-R04 (sealed repair ready, 2-min drain); each logged.
5. Hot-fixed PASSes are re-run from a clean fixture before they count; full-list clash check batched 2 items /
   30 min on a scratch save, never a quicktest world; keeper saves write-denied.
6. Out of the game: flyer flight, art, owner-only acts; Conductor owns parks, quarantines and owner asks only.

Critical flaw. TP+ buys its strict-acceptance lead with budget, and its lead is measured on a metric only it can
score. On sound production it loses to Ralph C+sub in 80 % of members at today's budget and in 98 % at 1.0G, and
the size of the gap is set by the critic's false-reject rate, which nobody has measured (E2; OAT swing about 6/day
across the prior). If the owner's real budget is nearer 1G than 1.9G, or the critic rejects a quarter of good small
items, the honest recommendation is Ralph C+sub with a cheap post-hoc blind sample, not TP+. The first experiment
must therefore measure the critic (false rejects on planted-good items, misses on planted defects) before
anything else is built.
