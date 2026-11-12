# Broaden: a different model on what a real player would try

Model: GPT via `src/RimMandrake/Utils/gpt_consult.py --codex wsl` (the quest XML and CathedralSurvey.cs inlined), 2026-11-11.

## The question (verbatim)

> I built a RimWorld 1.6 quest beat and need you to broaden my testing. The owner's spec (verbatim): "An Imperial survey/research party works Cathedral-adjacent ground — pursuit-spine dressing, no new faction. Three outs: (a) nothing; (b) feed the surveyors boring expected answers — salvage-guild banality, text/menu dialog — success = large Regard gain, zero text saying why; (c) point them at the anomaly = exposure input. Anti-laundering: (b) scrubs no Imperial Heat." Verify: fires from the pursuit spine dressing without inventing a faction; (b) moves Regard up in shadow mode and Heat not at all; (c) moves exposure pressure; all dialog passes the arc linter (no line explains what the player protected); completes with no LLM, prescribed fallback text.
> 
> What I built: a hidden, auto-accepted quest whose faction is the existing pursuing Empire. A choice letter (the attached quest XML has every string) offers 3 answers + Postpone; (b) ends Success, (c) ends Fail and drops 150-250 silver, (a) refused or 2-day lapse ends Unknown. An external Python "GM blackboard" (shadow mode: logs what it would fire) fires the quest when the clan is on Cathedral ground and Imperial Heat >= 10, at most once a month, and reads the quest list: Success = Regard +12, Fail = exposure +20, Unknown = nothing; Heat never changes.
> 
> What I tested (offline, fixture-driven, 51 checks): paired runs show Regard +12 on the answer poll and Heat identical poll-for-poll vs a lapse run; exposure +20 for (c), Heat identical; (a) identical to survey-disabled; no hail at low Heat, off Cathedral ground, after full discovery, or with the toggle off; answer read once; linter passes all 13 strings at every stage and catches planted explanatory lines; runs with no claude on PATH. NOT tested: the live game (no quicktest available in my lane).
> 
> Question: what would a real player try that I haven't — a newcomer, an experienced RimWorld player, someone trying to break or exploit it, a messy real save? Which 1-2 of those are most likely to reveal a real defect, in the design or the text? Be concrete and brief (under 400 words).

## The answer (verbatim)

> I’d prioritize these two:
> 
> 1. **Messy-save player / exploiter: cross the save boundary between answering and the blackboard poll.** Postpone the hail, save, reload, reopen it, choose (b), then save before the next poll. Restart the blackboard and reload that save. Also reload the earlier unanswered save after the blackboard has recorded +12, and choose (c).
> 
>    Check that the hail survives reload, its original deadline holds, and each answer is counted once. Crucially, check whether Regard, exposure, the processed-answer record, and the monthly cooldown agree with the loaded timeline. An abandoned branch’s +12 should not silently combine with the replacement branch’s exposure. Your fixtures establish polling behavior; they haven’t established consistency between a real save and an external process. This is the strongest technical defect candidate.
> 
> 2. **Newcomer: encounter it immediately on first reaching Cathedral ground, without prior anomaly knowledge.** Give someone only the actual hail and ask what each answer means before they click; then show the resulting letter.
> 
>    The pointed label—“Tell him what the crews have seen out there”—sounds like ordinary cooperation. Only afterward does the response commit the clan to knowing about hollow plates, underground sounds, and extensive buried works. Meanwhile, “the clan’s crews have worked these plates for years” asserts history your stated trigger doesn’t establish. Test whether the beat reveals information the player hasn’t learned or makes them disclose something they couldn’t knowingly choose.
> 
>    Also ask what (b) accomplished. “The officer stops taking notes” followed by lamps moving “away from the old works” may communicate the protected location through implication despite passing the linter. The spec permits reporting surveyor actions, so this needs human judgment, not another banned-phrase fixture.
> 
> The first tests whether the machinery survives ordinary player behavior; the second tests whether the concealed choice actually works as a choice.
## What I tried, and what it found

**1. Save-scum across the save/blackboard boundary: a real defect, fixed.** I reproduced it in the fixture first. The
player answers (b), the blackboard credits +12 Regard, then the player reloads a save from before the answer and
answers (c) for the silver. The old code skipped any quest id it had already read, so the (c) never counted and the
+12 stayed: the player kept the Regard, took the silver, and added no exposure. That is the exact exploit GPT
predicted. Fix (`gm_blackboard_shadow.py`, `observe_survey_quests` / `_reverse_survey_credit`): the blackboard now
stores what it credited for each survey quest. When a credited quest reads Ongoing again, ends with another answer,
or is gone from the list (a reload from before the hail; vanilla never prunes ended quests, checked in
`QuestManager`), it takes back exactly that credit, then reads the new answer.
Proof: `selftest_rustcathedral_survey.py` [6] 6a-6e. Over that run the net is survey Regard 0 and exposure +20, one
pointed and no dull, and no second hail fires while the reloaded one is out.

The independent code reviewer raised the matching restart case, also real and fixed. A restarted blackboard
re-credited every old (c) at full +20, so three old answers could flip the place dark in one poll. Now a restart
treats ended surveys as history: old (b)s rebuild Regard once, as old missions do; old (c)s add nothing; the month's
gap restarts. Proof: [6] 6f-6h.

**2. The newcomer reading the text cold: three text defects, fixed.**
- "The clan's crews have worked these plates for years" assumed a history the trigger does not promise. It now
  reads "Salvage crews work these plates, he says; they must see things."
- The (c) button "Tell him what the crews have seen out there" did not say what the player was giving away. It is
  now "Tell him what the crews have seen: the hollow plates, the drone from the old works, the ground that settles
  overnight", so the player knowingly chooses to disclose. Those are things the player has heard and seen on that
  ground; none of them is an explanation.
- The (c) letter's "old works that run on further down than any wreck has a right to" hinted at scale, which is
  reveal material (A2), before the reveal. It now describes only surface oddities.
- The (b) letter's "lamps moving west, away from the old works" pointed at what had been protected. It now reads
  "moved on to the next grid square of their charts".

All of it re-lints clean at stages -1 to 3. I took one false step: my first rewording used "somebody's map", and the
linter's agency rule refused it ("somebody").

Not acted on: GPT's view that "the officer stops taking notes" still implies success is a judgment call. The spec
allows describing what the surveyors did, and the line explains nothing. The judge and the owner can overrule.
