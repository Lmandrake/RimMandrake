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
- No mandatory invention machinery, no framework for exhaustive worlds, no new margin gate. (A stall detector that
  PROPOSES a rescue, never launches one, is now ordered: owner, 2026-11-16 about 10:10 PM PST, *"yup. Then we'll watch
  stats to see if we need to tune that."* Item `RIMMANDRAKE_PROPOSE_RESCUE_WHEN_MOD_CIRCLES_BOTH_HAND_LAUNCHED`;
  ruling in `design/RimMandrake/standing_rulings.md`.)
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

## What the card said

<!-- answered 2026-11-17T07:41:59Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** The blind checker (the judge that grades a builder's proof as PASS, WEAK, FAIL or UNMEASURED) today treats a WEAK verdict as PASS when the judge cannot say what strong proof would look like or what the weak proof lets through. That comes from your words of 2026-11-05: "The Judge should have to be able to articulate what strong proof would look like". GPT calls this fail-open: a vague doubt lets work through. Should a WEAK that the judge cannot back up still read as PASS?
**Picked:** Keep: it reads as PASS (Recommended)
**Its description:** Why: a doubt the judge cannot put into words gives the builder nothing to fix. Buys: no unanswerable refusals, and no change to the frozen checker. Costs: a real but badly worded doubt slips through to the in-game visit. Recommended because your refusal rule needs a path to pass, and this one has none.
**Other options:** Ask the judge once more · It blocks until backed up

**Owed by this card** (the close names where each was done or filed): needs a path to pass

## What the card said

<!-- answered 2026-11-17T07:41:59Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** The coverage judge (reads a mod's design before building and names gaps: things promised with no scene that would prove them) has no point where it is done. On Pyrelands it took 6 rounds and about 4.17M weighted tokens, naming 8 gaps, then 6 different ones; across the pipeline 15 of 50 gaps were first named after round 1. I proposed limiting it to the rows the Designer listed; GPT warns a Designer could then hide a capability by leaving it off the list. Your own live look comes later either way. Should the coverage judge's search be bounded?
**Picked:** Open search in round 1 only (Recommended)
**Its description:** Why: catch what the Designer left off the list, but only once. Buys: round 1 looks everywhere; later rounds only check that named gaps were repaired, so the loop ends. Costs: something missed in round 1 waits for the in-game visit or your look. Recommended: it ends the Pyrelands loop without GPT's hole.
**Other options:** Bounded to the listed rows · Unbounded, as today

## What the card said

<!-- answered 2026-11-17T07:41:59Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Three mods (Pyrelands, Graffiti, Gimme Some Slack) had their designs signed as covered by the coverage judge while its instructions were unverified: they had been edited after the judge was last tested against planted cases, so nobody knows whether that version judged correctly. The records flag those three signatures but do not void them. One Pyrelands round cost roughly 0.7M weighted tokens (estimate from 4.17M over 6 rounds). Once the judge is re-tested, should the three signatures be judged again?
**Picked:** Leave them, re-judge at next version (Recommended)
**Its description:** Why: two of the three are already in live in-game visits, which find real failures better than a paper re-read. Buys: no spend or delay now; each gets a tested judge when its next Design Version opens. Costs: a design gap the old judge missed is found later, in game. Recommended: live failures beat predictive review.
**Other options:** Re-judge all three now · Re-judge only Graffiti

## What the card said

<!-- answered 2026-11-17T07:41:59Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** When the coverage judge names a new gap in a later round that it could have named in round 1, the rule today is: recorded, never a new bar, so it never blocks, however serious. That rule is deliberate (it stops the judge moving the goalposts each round), but GPT points out a serious failure found late just sails through. May a serious gap found late block the design?
**Picked:** Only if a second reader agrees (Recommended)
**Its description:** Why: stop real defects without reopening the goalpost loop. Buys: a late gap blocks only when it is a Problem a player would reject and the judge's second reader confirms it. Costs: a small code and prompt change plus a re-test of the judge. Recommended: serious defects are cheaper to fix on paper.
**Other options:** Never, as today · Any serious late gap blocks
