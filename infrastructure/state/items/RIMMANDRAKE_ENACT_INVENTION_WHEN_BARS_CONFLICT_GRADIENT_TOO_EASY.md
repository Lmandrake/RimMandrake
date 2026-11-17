# RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY

Owner, 2026-11-16 (filing): *"I tend to fix problems you're having by Inventing, Resolving two things into one same
thing, or even relaxing requirements if they've proven more trouble than they're worth. We need some of this
flexibility in the pipeline. You're not following a smooth gradient. That's too easy. This is a creative project."*

Owner, 8:56 PM PST 2026-11-16, on GPT's review: *"Yup, do the Rescue brief. Delivery first yes."*

## spec

The Slack rescue showed the method can work on one mod. Three reviews followed: the Conductor's proposal
(`D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN\conductor_pipeline_proposal.md`),
the building Fable's view from inside the work (`pipeline_view_from_fable.md`, same folder) and GPT's review
(`D:\ClaudeWork\rimmandrake\conductor\gpt_review_pipeline_changes_20261116.md`). The owner accepted GPT's order of work:
deliver first, then measure, and build no general machinery until one mod has shown the way. This item is that order.

**Done in this item's first run (2026-11-16):** the Rescue brief `src/RimMandrake/rimflow/roles/fable_rescue.md` is
v2, with Fable's ten amendments folded into its body and GPT's cuts applied. It is how a stuck mod is rescued until
step 3 says otherwise.

**Step 1. Finish one mod: Gimme Some Slack, through the owner's acceptance.** It stands at In-game acceptance
(Stage 6) after the rescue's port (published 6ecfb14c822b; certificate green on that build, two red offline tests filed
as not the rescue's). The owner made it the top priority at 8:45 PM PST. Carry it through Stage 6, the pre-human
check (Stage 7) and his live walk (Stage 8) on the pipeline's own stages. Every failure on the way goes down the road
back to the lowest stage that can show it, as the spec says; none is fixed by retuning. The rescue's in-game looks that
are UNRUN (the whip seen only as an offline animation) are checked at Stage 6.
Acceptance test: `python3 src/RimMandrake/rimflow/maturation.py show GimmeSomeSlack` reads a pass record written at
Stage 8 (his pass, his words in the ledger); before that, `maturation.py certificate GimmeSomeSlack --run` exits 0 on
the build that goes to Stage 7.

**Step 2. Learn from that delivery before building anything.** While Slack goes through Stages 6 to 8, record each
thing that went wrong after the rescue's port and where it was caught (a stage, a check, the owner's eye). Pyrelands is
being rescued on the v2 brief's amendments now (`RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE`); its
result is the second case. Revise the Rescue brief again only from what these two show.
Acceptance test: none, a record of what happened; it is read by the owner, not by a program.

**Step 3. One measurement report.** One reusable report that any check, rescue instrument or certificate can print,
so a green is read with its evidence beside it. It states, for each check: parity with the game (the agreement number
between any copy of an instrument and the game's own numbers, and every disagreement explained or named as
unexplained); the family it sampled (its generator and how many cases); the exclusions (what the family leaves out);
the worst case and the limit it is read against; the regression results (old checks and challenge cases, green or
red). Every report names the source commit, the settings and the instrument version it ran on, so a stale one can be
told. Build it on Slack's sweep first, then use it on Pyrelands. It is a report, not a gate: a worst case near its
limit is a reason to look, never an automatic failure, and no new margin threshold comes with it.
Acceptance test: a selftest that builds the report from a fixed set of check readings and refuses one missing parity,
family, exclusions, worst case or the source commit; then the report printed for GimmeSomeSlack's sweep check,
matching its own numbers.

**Out of scope for now, by the owner's acceptance of GPT's order:**
- **No universal conflict stage.** The conflict procedure stays in the Rescue brief, used on a stuck mod; it is not
  a stage of the Maturation Pipeline. Making it one is a Divergent idea for later, to be filed as its own item only
  after step 2 shows it transfers beyond Slack.
- No stall detector, no mandatory invention machinery, no framework for exhaustive worlds, no new margin gate.
- Writing a new standing ruling. This item's filing title asked for one in `design/RimMandrake/standing_rulings.md`;
  the owner's ruling tonight narrowed the work to the brief and this order, so the ruling waits for step 2.
- GPT's own first step, every owed action (a launch, a question to the owner) with a timestamp, an acknowledgement, a
  retry and a visible blocker, is filed apart as `RIMMANDRAKE_RETRY_OWED_ACTIONS_JUDGE_UNLAUNCHED_QUESTION_STUCK`
  (its launch half overlaps `RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS`).

## refs

file: src/RimMandrake/rimflow/roles/fable_rescue.md
file: design/specs/2026-11-13-maturation-pipeline.md

## verify

- Brief: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_bench_word_prose,selftest_spend_blind_agents`
  green with the v2 brief in place; the brief carries all ten amendments in its body and none of the five phrases GPT
  cut ("once and for all", "a diagnosis is worth nothing", a quota of three candidates, a fixed order of the three
  moves, "port once").
- Step 1: the pass record in `maturation.py show GimmeSomeSlack`.
- Step 2: the record exists and names, for each thing that went wrong after the port, the stage that caught it.
- Step 3: the report's selftest green, and its mutant (a report with no exclusions) refused.

## criteria

- One mod is finished, through the owner's own pass, before any general machinery is built.
- The Rescue brief states no spend; every bar it asks for is an experience a player would notice, never a tuning
  number; every question it allows to the owner carries evidence, a recommendation, what each answer changes and a
  default within the agent's authority; every refusal or "impossible" it returns carries the smallest change that
  would let it pass.
- The measurement report is a report and not a gate, and it says what it did not sample.
- No universal conflict stage is built under this item.
