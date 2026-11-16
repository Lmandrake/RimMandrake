# Why the mod pipeline keeps stopping: measured diagnosis, Mon 2026-11-16

The automatic pipeline takes each mod through design, an offline build, AI-judge rounds, a live-game test, a final
check, and then your walk-through. The data covers 12 mods, from 11-13 to 2:24 PM today. A *pause* means no work on
a mod for 10 minutes or more. *Mod-hours* are pause hours summed across mods. *Bars* are a mod's fixed pass
conditions. Spend is in weighted tokens (M = million).

## Five conclusions

1. **Mods move, but none finishes.** The pipeline moved mods forward 20 times, and no mod has ever passed the
   live-game test.
2. **Long pauses wait for a person.** Of 182 paused mod-hours, 76% ended only when you or the Conductor acted, or
   pipeline code was fixed, or are still paused.
3. **The biggest cause is the pipeline's own limits, which have no automatic release.** These are spending ceilings,
   "one try only" rules and daily caps: 43% of paused time.
4. **The pipeline is still being built while it runs.** At least 24% of the 571M weighted tokens spent went to
   fixing the pipeline, not the mods.
5. **The AI judge never runs out of new problems.** It finds 8 to 14 new problems a round on two mods, against a
   limit of three automatic rounds.

## Fixed and broken

| | what | evidence |
|---|---|---|
| Fixed | Work starts automatically | 103 runs were started with no hand in 41 hours. On 11-14, mods sat 6 to 9 hours waiting |
| Broken | Limits with no release | 22 pauses, 79 mod-hours. Now 2 mods are at the spending ceiling and 4 at the daily cap |
| Broken | A block naming a finished fix stays put | one mod has been blocked 5.6 hours on a job that is already done |
| Broken | The judge's list has no end | 8 to 14 new problems a round. Each mod has 43 to 123 bars |
| Broken | The last two steps have never run | 0 mods have reached the final check |
| Waits on you | Questions, and holding the game for you to look | 8 pauses, 27 mod-hours |

## Remedies, ranked

1. **Do this: finish one mod first.** Drive Explosive Knockback alone to 0.1.0. Its judge rounds fell 10, 12, 6, 1
   and its live failures 9, 4, 2. This costs no extra runs. It would not fix the limits or the judge.
2. **Do this too: every pause names what releases it, and a program releases it.** This targets 43% of paused time.
   The build effort is not measured.
3. **Safety net: a watchdog.** It starts one repair run after a 60-minute pause. That is about 15 a day, 9 to 15M,
   or 6% to 9% on top of today's 158M a day.
4. **Not recommended: your Conductor woken every 10 minutes.** It would cost 41 to 48M a day, 26% to 30% more. It
   would have shortened only the 28 mod-hours that the Conductor ended by hand. It cannot fix code bugs or the judge.
5. **Also:** freeze pipeline code while the one mod runs. Let the judge fail a mod only against its fixed bars, and
   put new ideas on the next version's list.

**Unsure:** whether the judge's new problems are real defects or new requirements. Who ended 14 pauses before
11-15 2:09 PM, when hand acts were first recorded. A second AI model, given the table blind, named the same top
causes.

---

## Detail

### How it was measured

- **Pauses**: `D:\ClaudeWork\rimmandrake\dispatcher\maturation\ticks.jsonl`, 2,427 per-minute readings, 11-14 9:15 PM
  to 11-16 2:24 PM PST. Per mod, a run of identical "not working" readings of 10 minutes or more is one pause (37
  shorter flickers not counted). What ended each one: a recorded hand act on that mod within 20 minutes before the
  pause ended (`hand_acts.jsonl`); a stage move made by the Conductor; an owner card or word on the ledger; a pipeline
  code commit naming the mod or pause within 45 minutes; otherwise "the tick by itself". Scripts and outputs:
  `D:\ClaudeWork\rimmandrake\conductor\diag_20261116\` (`stops.py`, `final.py`, `stops_final.json`, `totals_tickera.txt`).
- **Stage moves**: every concept's `design\concepts\<Mod>\version\stage_record.json` (35 moves; `advances.py`, `advances.txt`).
- **Spend**: weighted tokens from each detached run record (`D:\ClaudeWork\rimmandrake\dispatcher\detached\*.json`,
  321 runs since 11-13, 571M), attributed to a mod by item name, title or cause chain, else to pipeline machinery
  (`spend.py`, `attrib.py`). Role runs from `dispatcher\roles\` with the pipeline's own weights (`role_launch.TOKEN_WEIGHTS`):
  Conductor quick runs n=37, median 287,010, mean 332,227.
- **Code**: decision and pause strings in `maturation_dispatch.py` and `maturation_autonomy.py` (49 kinds; 35 are
  reasons not to launch by my sorting), 14 numeric limits and 4 switches in `maturation_dispatch.json`, first
  appearance dated by `git log -S` (`gates.txt`).
- **Before the per-minute log** (11-13 to 11-14 9:15 PM): `design\RimMandrake\pipeline_interventions_census_2026-11-15.md`
  (about 134 hand interventions, 42 lessons). Its estimated rows (four mods about 9 hours each with no launcher; the
  pilot's judge refusals) are in the appendix but kept out of every percentage above.

### Totals (per-minute log only; all measured)

| cause class | pauses | mod-hours | share of time |
|---|---|---|---|
| Brake with no automatic release (working as designed) | 22 | 79.3 | 43% |
| Pipeline defect (machinery bug) | 20 | 31.2 | 17% |
| Waits on the owner | 8 | 26.7 | 14% |
| Brake that released itself (queue for a free slot, a cap that reset) | 36 | 22.8 | 12% |
| Judge or bar problem | 4 | 19.7 | 10% |
| Waits on the one live game | 2 | 2.0 | 1% |
| Mod defect | 0 | 0 | 0% |
| **all** | **92** | **181.7** | |

Mod defects show up as rework, not pauses: 5 sends back from a failed live-game test and 10 repeat judge rounds.

Within "brake with no automatic release": waiting for a parent mod to pass 25.1 h, daily design limit 17.4 h, "one
try, never a second" after a run resolved nothing 13.5 h, spend ceiling 9.9 h, three-round limit 5.7 h, live-game
launches switched off until a first hand run 5.2 h, other 2.5 h.

| what ended the pause | pauses | mod-hours |
|---|---|---|
| the pipeline by itself | 44 (47%) | 44.0 (24%) |
| still paused at 2:24 PM | 9 | 50.8 |
| the owner (card, word, or a limit he raised) | 15 | 35.6 |
| the Conductor by hand | 18 | 28.0 |
| a pipeline code fix landing | 6 | 23.3 |

Stage moves: 20 forward, of which 9 were made by the Conductor's own hand (all before 3:42 AM on 11-15). Of the 9
forward moves made after hand acts began being recorded, 3 had no hand act on that mod during the stay. The mods
that have passed a step untouched are Explosive Knockback (blind judge to live test, and bench to blind judge) and
Leaning Scrub (preflight to bench). Pre-walk arrivals: 0. Recorded 0.1.0 passes: 0.

Spend per forward step: 571M ÷ 20 = about 29M weighted tokens. By mod: FlowWorks 123M, Gimme Some Slack 104M,
Explosive Knockback 93M, Pyrelands 53M, pipeline machinery 135M or more, the rest under 20M each. Per day: 158M.
Typical runs: blind-judge round median 3.6M, routing ("steward") run 0.64M, pipeline-repair run 1.1M.

Locked bars per mod: Pyrelands 43, Graffiti 47, Gimme Some Slack 48, FlowWorks 57, Explosive Knockback 59,
Leaning Scrub 123; the six mods still at design have none locked.

### Guidance that the numbers support (read from the sources, not from memory)

- **Anthropic, "Building effective agents"** (https://www.anthropic.com/research/building-effective-agents): "we
  recommend finding the simplest solution possible, and only increasing complexity when needed" and "you should
  consider adding complexity only when it demonstrably improves outcomes". On judge loops, the evaluator-optimizer
  pattern "is particularly effective when we have clear evaluation criteria, and when iterative refinement provides
  measurable value". On agents, "it's also common to include stopping conditions (such as a maximum number of
  iterations) to maintain control". *Fits conclusions 3 and 5:* the stopping conditions exist, but the judge's
  criteria are not closed (8 to 14 new problems a round), and the pipeline grew about 50 rule strings in two days.
- **Anthropic, "How we built our multi-agent research system"**
  (https://www.anthropic.com/engineering/multi-agent-research-system): "Agents are stateful and errors compound", and
  "we can't just restart from the beginning... we built systems that can resume from where the agent was when the
  errors occurred". Also: "multi-agent systems use about 15× more tokens than chats", so they need tasks valuable
  enough to pay for it. *Fits conclusion 4:* stale state (a code copy 29 commits behind, a spent try that never
  started) caused 17% of paused time.
- **Cemri, Pan et al., "Why Do Multi-Agent LLM Systems Fail?"** (MAST, https://arxiv.org/html/2503.13657v3): 14
  failure modes in three groups (system design, inter-agent misalignment, task verification), including "Unaware of
  stopping conditions" and "No or incomplete verification". The authors "conjecture that improvements in the base
  model capabilities will be insufficient", and find that "many MAS failures arise from the challenges in
  organizational design and agent coordination rather than the limitations of individual agents". *Fits:* none of the
  92 pauses was a mod defect or a model failing at a task. All of them were organisation: brakes, routing, state and
  holds.
- **Gall's law** (John Gall, *Systemantics*, 1975, quoted at https://en.wikipedia.org/wiki/John_Gall_(author) and
  https://personalmba.com/galls-law/): "A complex system that works is invariably found to have evolved from a simple
  system that worked... A complex system designed from scratch never works and cannot be made to work. You have to
  start over, beginning with a working simple system." **Walking skeleton** (Alistair Cockburn, quoted at
  https://benchristel.github.io/process-to-processes/StartingAProject/WalkingSkeleton.html): "a tiny implementation of the system that
  performs a small end-to-end function". *Fits conclusion 1 and remedy 1:* eight stages were built, but the last two
  have never run once.
- **Little's law and work-in-progress limits** (https://capgemini.github.io/agile/Littles-Law-and-KanBan): "L = λW",
  number in the system = throughput × time in the system; "a WIP limit is defined before the bottleneck". So with
  throughput fixed, more work in progress means each item takes longer. *Fits remedy 1:* 12 mods in progress, a
  throughput of 0 finished, and one shared live game.
- **Theory of constraints, five focusing steps** (https://www.tocinstitute.org/five-focusing-steps.html;
  https://en.wikipedia.org/wiki/Theory_of_constraints): identify the constraint, exploit it, subordinate everything
  else, elevate, repeat. One named kind of constraint is "Policy: A written or unwritten policy prevents the system
  from making more". *Fits conclusion 3:* the binding constraint here is the
  pipeline's own policy (its brakes), not compute, the game or the models.
- **Stop-the-line / jidoka** (https://itrevolution.com/?p=68086; https://teeptrak.com/en/andon-2026/): detect, stop,
  fix the immediate condition, then fix the root cause. Implementations "missing element 4 (resolution loop) produce
  signal fatigue because nothing visible changes after the signal". *Fits remedy 2:* each pause stops the line, but
  for 43% of paused time no resolver was attached. These two are vendor and trade sources, so read them with care.

Not kept: nothing in Part 1 shows that the models themselves are too weak, so model-capability advice was dropped.

### Second opinion (GPT, given the table blind, before seeing this diagnosis)

Full answer: `D:\ClaudeWork\rimmandrake\conductor\diag_20261116\gpt_blind.md`. A second, fresh GPT read the top section cold (`gpt_coldread.md`); it flagged 15 unclear terms, numbers and phrases, and the top section was rewritten and shortened to answer them. It ranked: (1) automation ends at
routine limits with no automatic continuation; (2) the machinery loses or misreads its own state; (3) routine
advancement depends on human decisions and holds; (4) some gates have no usable, calibrated pass condition. It agreed
on the first three causes and on the remedies "an automatic next action for every routine stop" and "stabilise
execution state". Where it disagreed, and what I did:
- It said "brake with no exit" was overstated, because the daily design limit resets at midnight and the parent-mod
  wait ends when the parent passes. I kept the class, but split those 42.5 hours out above.
- It said "the pipeline by itself" was weak attribution before hand acts were recorded. Agreed; flagged above.
- It said the 9-hour pre-log rows gave false precision. They are now excluded from every percentage.
- It said zero mod-defect pauses does not mean defect-free mods. Agreed: mod defects appear as 5 sends back.
- It added one remedy: a finite release contract, separating new requirements from defects. That is remedy 5(b).

### Filed

- `RIMMANDRAKE_LIFT_DESIGNER_BLOCK_NAMING_DONE_ITEM_SLIME_WAITS`: a Designer block whose reason names an item that is
  already done never lifts (Gelatinous Slime, blocked since 11-16 8:55 AM PST). This run may not change pipeline
  code, so it is filed for a builder. Acceptance oracle (prints FAIL on base `1a6c7b26c7`, watched; expected one PASS
  line once fixed), run from the repo root:

```python
import json, re, subprocess
r = json.load(open('/mnt/d/ClaudeWork/rimmandrake/dispatcher/maturation/reading.json'))
bad = []
for m, row in r['mods'].items():
    if row.get('decision') == 'designer_blocked':
        for i in re.findall(r'\b(RIMMANDRAKE_[A-Z0-9_]+)', row.get('why') or ''):
            out = subprocess.run(['python3', 'src/RimMandrake/rimflow/cli.py', 'show', i], capture_output=True, text=True).stdout.split('\n')[0]
            if re.search(r'\s(done|dropped|superseded)\s', out): bad.append((m, i))
print('FAIL' if bad else 'PASS', bad)
```

### Appendix: every pause, 2026-11-13 to 2026-11-16 2:24 PM PST

Pause names are the program's own. Times are PST. "census row" = before the per-minute log, from the 11-15 census.

| mod | stage pause (as the program names it) | from | to | hours | what restarted it | cause class | note |
|---|---|---|---|---|---|---|---|
| Cauldron | designer_chain_cap | 11-16 09:17 | still standing | 5.2 | nothing yet | GUARD WITH NO EXIT | 8 Designer runs a day on one mod |
| Contagion | owner | 11-15 06:21 | 11-15 12:20 | 6.0 | owner (typed decisions 11-15 11:53) plus the Evidence-for-Ask rule | WAITS ON OWNER |  |
| Contagion | designer_blocked | 11-15 13:27 | 11-15 15:56 | 2.5 | tick by itself | JUDGE OR BAR | the coverage judge is uncalibrated, so its gate needs a signature nobody can give yet |
| Contagion | designer_chain_cap | 11-15 16:57 | 11-15 17:18 | 0.3 | tick by itself | GUARD THAT LIFTED ITSELF | 8 Designer runs a day on one mod |
| Contagion | designer_chain_cap | 11-15 18:26 | 11-15 19:13 | 0.8 | tick by itself | GUARD THAT LIFTED ITSELF | 8 Designer runs a day on one mod |
| Contagion | coverage_stop | 11-16 02:08 | 11-16 08:55 | 6.8 | tick by itself | JUDGE OR BAR | coverage judge refused; 'nothing could ever pass' alarm |
| Contagion | designer_chain_cap | 11-16 12:37 | still standing | 1.9 | nothing yet | GUARD WITH NO EXIT | 8 Designer runs a day on one mod |
| ExplosiveKnockback | coverage_stop x3 (pilot) | 11-13 |  | UNMEASURED | owner card x3 | JUDGE OR BAR | census row; duration UNMEASURED |
| ExplosiveKnockback | no launcher (hand step) | 11-14 12:15 |  | 9.0 | Conductor hand | PIPELINE DEFECT | census row; duration about 6-9 h (census: 'all four mods sat at the offline build 6 to 9 hours'), counted 9 |
| ExplosiveKnockback | ingame_off | 11-15 02:17 | 11-15 05:13 | 2.9 | Conductor hand (switched in-game launches on, 11-15 ~05:30) | GUARD WITH NO EXIT |  |
| ExplosiveKnockback | steward_spent | 11-15 08:01 | 11-15 08:30 | 0.5 | Conductor hand | PIPELINE DEFECT | the steward never started (git lock at publish) but counted as spent |
| ExplosiveKnockback | fixer_spent | 11-15 08:47 | 11-15 09:02 | 0.2 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| ExplosiveKnockback | ceiling | 11-15 09:09 | 11-15 11:40 | 2.5 | owner card raised the ceiling 60 -> 100 (11:33) | GUARD WITH NO EXIT | spend at this stage reached the per-stage ceiling |
| ExplosiveKnockback | slots_full | 11-15 12:25 | 11-15 12:36 | 0.2 | Conductor hand (on owner's card/word) | GUARD THAT LIFTED ITSELF |  |
| ExplosiveKnockback | slots_full | 11-15 13:54 | 11-15 14:04 | 0.2 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| ExplosiveKnockback | fixer_spent | 11-15 18:12 | 11-15 19:29 | 1.3 | Conductor hand | GUARD WITH NO EXIT |  |
| ExplosiveKnockback | fixer_spent | 11-15 19:44 | 11-15 20:03 | 0.3 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| ExplosiveKnockback | certificate | 11-15 20:03 | 11-15 20:27 | 0.4 | tick by itself | PIPELINE DEFECT | offline deciders unstamped or stamped on an older build; the restamp costs no tokens but no program ran it |
| ExplosiveKnockback | fixer_spent | 11-15 20:41 | 11-15 23:05 | 2.4 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| ExplosiveKnockback | fixer_spent | 11-15 23:31 | 11-16 01:12 | 1.7 | pipeline code fix (commit names it) | PIPELINE DEFECT | lifted only when pipeline code changed |
| ExplosiveKnockback | fixer_spent | 11-16 01:20 | 11-16 01:35 | 0.2 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| ExplosiveKnockback | certificate | 11-16 01:35 | 11-16 02:02 | 0.5 | tick by itself | PIPELINE DEFECT | offline deciders unstamped or stamped on an older build; the restamp costs no tokens but no program ran it |
| ExplosiveKnockback | certificate | 11-16 02:04 | 11-16 03:22 | 1.3 | tick by itself | PIPELINE DEFECT | offline deciders unstamped or stamped on an older build; the restamp costs no tokens but no program ran it |
| ExplosiveKnockback | fixer_spent | 11-16 04:10 | 11-16 04:56 | 0.8 | Conductor hand | GUARD WITH NO EXIT |  |
| ExplosiveKnockback | blocked | 11-16 09:39 | 11-16 12:25 | 2.8 | Conductor hand | PIPELINE DEFECT | a live test wrote its next visit's folder early; the record reader refused |
| ExplosiveKnockback | certificate | 11-16 12:33 | 11-16 13:19 | 0.8 | pipeline code fix (commit names it) | PIPELINE DEFECT | offline deciders unstamped or stamped on an older build; the restamp costs no tokens but no program ran it |
| ExplosiveKnockback | holder_spent | 11-16 13:23 | 11-16 13:38 | 0.2 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| ExplosiveKnockback | ceiling | 11-16 13:48 | still standing | 0.7 | nothing yet | GUARD WITH NO EXIT | spend at this stage reached the per-stage ceiling |
| FeverWood | designer_chain_cap | 11-16 09:19 | still standing | 5.2 | nothing yet | GUARD WITH NO EXIT | 8 Designer runs a day on one mod |
| FlowWorks | no launcher (hand step) | 11-14 12:15 |  | 9.0 | Conductor hand | PIPELINE DEFECT | census row; duration about 6-9 h (census: 'all four mods sat at the offline build 6 to 9 hours'), counted 9 |
| FlowWorks | ingame_off | 11-15 03:53 | 11-15 05:25 | 1.5 | Conductor hand (switched in-game launches on, 11-15 ~05:30) | GUARD WITH NO EXIT |  |
| FlowWorks | driver_busy | 11-15 05:25 | 11-15 07:10 | 1.8 | tick by itself [hand acts unrecorded before 11-15 14:09] | WAITS ON THE ONE GAME |  |
| FlowWorks | ceiling | 11-15 07:10 | 11-15 11:40 | 4.5 | owner card raised the ceiling 60 -> 100 (11:33) | GUARD WITH NO EXIT | spend at this stage reached the per-stage ceiling |
| FlowWorks | stopped | 11-15 11:41 | 11-15 12:20 | 0.7 | Conductor hand | PIPELINE DEFECT | the in-game launcher refused to spawn; fixed then cleared by hand |
| FlowWorks | steward_spent | 11-15 19:00 | 11-15 19:48 | 0.8 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| FlowWorks | certificate | 11-15 20:03 | 11-15 23:03 | 3.0 | tick by itself | PIPELINE DEFECT | offline deciders unstamped or stamped on an older build; the restamp costs no tokens but no program ran it |
| FlowWorks | certificate | 11-15 23:59 | 11-16 00:15 | 0.3 | Conductor hand | PIPELINE DEFECT | offline deciders unstamped or stamped on an older build; the restamp costs no tokens but no program ran it |
| FlowWorks | certificate | 11-16 00:55 | 11-16 01:53 | 1.0 | pipeline code fix (commit names it) | PIPELINE DEFECT | offline deciders unstamped or stamped on an older build; the restamp costs no tokens but no program ran it |
| FlowWorks | steward_spent | 11-16 04:29 | 11-16 04:56 | 0.5 | Conductor hand | PIPELINE DEFECT | read on a dispatch clone 29+ commits stale |
| FlowWorks | stale_clone | 11-16 08:36 | 11-16 08:55 | 0.3 | tick by itself | PIPELINE DEFECT |  |
| FlowWorks | ceiling | 11-16 13:23 | still standing | 1.1 | nothing yet | GUARD WITH NO EXIT | spend at this stage reached the per-stage ceiling |
| GelatinousSlime | designer_blocked | 11-16 08:55 | still standing | 5.6 | nothing yet | JUDGE OR BAR | the coverage judge is uncalibrated, so its gate needs a signature nobody can give yet |
| GimmeSomeSlack | no launcher (hand step) | 11-14 12:15 |  | 9.0 | Conductor hand | PIPELINE DEFECT | census row; duration about 6-9 h (census: 'all four mods sat at the offline build 6 to 9 hours'), counted 9 |
| GimmeSomeSlack | hand_step | 11-14 21:15 | 11-14 21:30 | 0.2 | Conductor hand (stage move) | PIPELINE DEFECT |  |
| GimmeSomeSlack | steward_spent | 11-15 07:26 | 11-15 07:42 | 0.3 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| GimmeSomeSlack | steward_spent | 11-15 07:45 | 11-15 08:10 | 0.4 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| GimmeSomeSlack | stopped | 11-15 09:30 | 11-15 10:33 | 1.1 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| GimmeSomeSlack | cycle_limit | 11-15 16:51 | 11-15 17:53 | 1.0 | Conductor hand (stage move) | GUARD WITH NO EXIT |  |
| GimmeSomeSlack | cycle_limit | 11-15 19:22 | 11-15 23:37 | 4.2 | Conductor hand (stage move) | GUARD WITH NO EXIT |  |
| GimmeSomeSlack | cycle_limit | 11-16 01:07 | 11-16 01:30 | 0.4 | Conductor hand (stage move) | GUARD WITH NO EXIT |  |
| GimmeSomeSlack | auto_spent | 11-16 01:30 | 11-16 01:53 | 0.4 | Conductor hand | GUARD WITH NO EXIT |  |
| GimmeSomeSlack | ceiling | 11-16 03:31 | 11-16 04:15 | 0.7 | Conductor hand (on owner's card/word) | GUARD WITH NO EXIT | spend at this stage reached the per-stage ceiling |
| GimmeSomeSlack | stopped | 11-16 04:19 | 11-16 04:45 | 0.4 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| GimmeSomeSlack | stopped | 11-16 04:47 | 11-16 04:58 | 0.2 | Conductor hand | PIPELINE DEFECT | read on a dispatch clone 29+ commits stale |
| GimmeSomeSlack | bridge_held | 11-16 05:14 | 11-16 05:28 | 0.2 | tick by itself | WAITS ON THE ONE GAME |  |
| GimmeSomeSlack | stopped | 11-16 06:01 | 11-16 06:56 | 0.9 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| GimmeSomeSlack | stopped | 11-16 07:44 | 11-16 13:36 | 5.9 | Conductor hand on the owner's word (13:09: do not hold the game for his look) | WAITS ON OWNER | the game was held for his second look; cleared when he said not to hold it |
| GimmeSomeSlack | certificate | 11-16 13:36 | still standing | 0.9 | nothing yet | PIPELINE DEFECT | offline deciders unstamped or stamped on an older build; the restamp costs no tokens but no program ran it |
| Graffiti | owner | 11-15 06:44 | 11-15 07:13 | 0.5 | owner card (version lock 11:33; rework card 05:36) | WAITS ON OWNER |  |
| Graffiti | slots_full | 11-15 07:13 | 11-15 07:34 | 0.3 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| Graffiti | steward_spent | 11-15 07:35 | 11-15 08:15 | 0.7 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| Graffiti | owner | 11-15 08:15 | 11-15 11:42 | 3.5 | owner card (version lock 11:33; rework card 05:36) | WAITS ON OWNER |  |
| Graffiti | slots_full | 11-15 11:42 | 11-15 12:36 | 0.9 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| Graffiti | steward_spent | 11-15 12:37 | 11-15 13:04 | 0.4 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| Graffiti | stopped | 11-15 13:07 | 11-15 13:22 | 0.2 | pipeline code fix (commit names it) | PIPELINE DEFECT | lifted only when pipeline code changed |
| Graffiti | slots_full | 11-15 13:22 | 11-15 13:52 | 0.5 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| Graffiti | slots_full | 11-15 15:41 | 11-15 16:07 | 0.4 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Graffiti | slots_full | 11-15 16:29 | 11-15 16:39 | 0.2 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Graffiti | fixer_spent | 11-15 17:21 | 11-16 05:28 | 12.1 | pipeline code change: the hand-launched dispatch-clone unstick landed 05:19, the stop lifted 05:28 [guess ~70%] | PIPELINE DEFECT | the dispatch program read a copy of the code 29+ commits stale overnight |
| Graffiti | slots_full | 11-16 05:33 | 11-16 05:48 | 0.2 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Graffiti | slots_full | 11-16 05:50 | 11-16 06:01 | 0.2 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Graffiti | fixer_spent | 11-16 06:13 | 11-16 06:56 | 0.7 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Graffiti | slots_full | 11-16 06:56 | 11-16 07:41 | 0.8 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Graffiti | fixer_spent | 11-16 07:41 | 11-16 09:08 | 1.5 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Graffiti | slots_full | 11-16 09:13 | 11-16 09:24 | 0.2 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Graffiti | fixer_spent | 11-16 09:24 | 11-16 13:14 | 3.8 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Graffiti | fixer_spent | 11-16 13:19 | 11-16 13:32 | 0.2 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| LeaningScrub | owner | 11-16 04:56 | 11-16 06:25 | 1.5 | owner cards 05:07-05:25 | WAITS ON OWNER |  |
| LeaningScrub | steward_spent | 11-16 09:02 | 11-16 09:23 | 0.3 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Pyrelands | no launcher (hand step) | 11-14 12:15 |  | 9.0 | Conductor hand | PIPELINE DEFECT | census row; duration about 6-9 h (census: 'all four mods sat at the offline build 6 to 9 hours'), counted 9 |
| Pyrelands | coverage_stop | 11-14 22:01 |  | UNMEASURED | owner card | JUDGE OR BAR | census row; duration UNMEASURED |
| Pyrelands | ingame_off | 11-15 02:09 | 11-15 02:55 | 0.8 | Conductor hand (switched in-game launches on, 11-15 ~05:30) | GUARD WITH NO EXIT |  |
| Pyrelands | exit_not_met | 11-15 05:29 | 11-15 05:46 | 0.3 | Conductor hand (on owner's card/word) | PIPELINE DEFECT |  |
| Pyrelands | slots_full | 11-15 06:11 | 11-15 07:23 | 1.2 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| Pyrelands | fixer_spent | 11-15 07:34 | 11-15 07:48 | 0.2 | tick by itself [hand acts unrecorded before 11-15 14:09] | GUARD THAT LIFTED ITSELF |  |
| Pyrelands | coverage_stop | 11-15 07:48 | 11-15 12:38 | 4.8 | tick by itself [hand acts unrecorded before 11-15 14:09] | JUDGE OR BAR | coverage judge refused; 'nothing could ever pass' alarm |
| Pyrelands | owner | 11-15 14:07 | 11-15 15:48 | 1.7 | owner card (how to make the giant, 16:11) | WAITS ON OWNER |  |
| Pyrelands | owner | 11-15 15:58 | 11-15 16:13 | 0.2 | owner card (how to make the giant, 16:11) | WAITS ON OWNER |  |
| Pyrelands | slots_full | 11-15 16:13 | 11-15 16:26 | 0.2 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Pyrelands | stopped | 11-15 16:41 | 11-16 05:27 | 12.8 | Conductor hand (on owner's card/word) | GUARD WITH NO EXIT |  |
| Pyrelands | stopped | 11-16 06:18 | 11-16 07:03 | 0.8 | Conductor hand (on owner's card/word) | GUARD WITH NO EXIT |  |
| Pyrelands | slots_full | 11-16 07:03 | 11-16 07:14 | 0.2 | Conductor hand (on owner's card/word) | GUARD THAT LIFTED ITSELF |  |
| Pyrelands | stopped | 11-16 08:08 | 11-16 08:55 | 0.8 | tick by itself | GUARD THAT LIFTED ITSELF |  |
| Pyrelands | steward_spent | 11-16 08:55 | 11-16 12:38 | 3.7 | Conductor hand | PIPELINE DEFECT | steward key never re-armed after builders closed its tickets |
| Pyrelands | ceiling | 11-16 12:45 | 11-16 13:07 | 0.4 | Conductor hand (on owner's card/word) | GUARD WITH NO EXIT | spend at this stage reached the per-stage ceiling |
| PyrelandsMechanics | owner | 11-15 05:52 | 11-15 13:22 | 7.5 | relabelled by a code change to 'waits on parent mod' (not restarted) | WAITS ON OWNER |  |
| PyrelandsMechanics | upstream_wait | 11-15 13:22 | still standing | 25.1 | nothing yet | GUARD WITH NO EXIT | waits for its parent mod to pass; no mod has ever passed |
| Stillsand | designer_chain_cap | 11-16 09:17 | still standing | 5.2 | nothing yet | GUARD WITH NO EXIT | 8 Designer runs a day on one mod |
