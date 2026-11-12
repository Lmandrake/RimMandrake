# CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1: judge verdict

Judge: CLAUDE_STEVEDESKTOP_OFFLINE3 judge seat, 2026-11-11. I did not read DONE.md or BROADEN.md.
I ran: `selftest_rustcathedral_survey.py` (exit 0, 60 checks, 0 failed) and
`gm_blackboard_shadow.py --fixture .../cathedral_survey_ordinary_play.json --log /tmp/judge_gm.jsonl`
(exit 0, 160 polls). I also ran `cathedral_arc_lint.py --xml` on both survey XML files at stages -1, 0 and 3 (all PASS, 0 findings).

## The statement as written

STATEMENT.md has no real claims. It holds one blank bullet and a cut-off `*Depends on:**` fragment.
A lesson about this already exists: `infrastructure/state/lessons/20261112T054039Z-CLAUDE_STEVEDESKTOP_OFFLINE3-wc-py-setup-wrote-whittle-cathedral.md`.

- `- ` (blank): cannot tell. There is nothing to judge.
- "Depends on: item 1 (Regard/exposure sinks), item 3 (linter), pursuit ...": true as a description. The blackboard has Regard and exposure sinks, the item 3 linter runs, and the C# binds the EmpirePursuit pursuit faction (selftest 1k, 1l). It is a dependency note, not a claim that the work is done.

Because of that, I judged the item file's own spec, verify and criteria lines (`infrastructure/state/items/CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1.md`):

## Verify lines

1. **Fires from the pursuit spine dressing without inventing a faction: true (offline).** In the shadow log the hail fires only when Heat is at or over 10 on Cathedral ground (polls 20 and 142). It stays closed as `heat_below_pursuit_band` otherwise. No FactionDef is shipped in CathedralPass. The C# falls back to `Faction.OfEmpire` (selftest 1a-1l). This is shadow mode, so the incident is never actually fired.
2. **(b) success moves Regard up in shadow mode and Heat not at all: true.** My run, poll 22: `survey_regard_gain_this_poll=12.0`, Regard -4.1 to 8.1. Heat goes 10.514 to 10.114, the same 0.4 per-poll decay as every other poll. Selftest 2e/2f: Heat, Hutt Interest and the orbital timer match the lapse run poll for poll.
3. **(c) moves exposure pressure: true.** In `evidence/ordinary_play_pointed.txt`, exposure goes 0.40 to 20.40 at each pointed answer, while Regard and Heat match the silent run. Selftest 3a-3f show it can flip go-dark.
4. **All dialog passes item 3's linter, and no line explains what the player protected: true.** I re-ran the linter myself and it passed. I read the shipped text (see the selftest output): the (b) letter says what the surveyors did, never why. One judgement note: the (c) letter has a silver pod arriving. Nothing in the spec asks for that, but it does not break any rule I can see.
5. **Completes Oracle-absent with prescribed fallback text: true (offline).** `text_source` says "shipped defs (fallback text); the survey path calls no LLM" on every row. Selftest 5a-5h agree.

## Spec lines

- Three outs (a)/(b)/(c), success = large Regard gain, zero text saying why: true. +12 is more than the 10.05 a sale costs.
- No new faction: true.
- K2, (b) scrubs no Imperial Heat: true.
- NEW defName `RUT_CathedralSurveyMisdirection`, RUT_ tier: true. It is in `Defs/QuestScriptDefs/RUT_CathedralSurveyMisdirection.xml`.
- "Same CQF/bridge-letter surface and caveat as item 4": cannot tell. Settling it needs a side-by-side with item 4's surface. Nothing in the evidence shows one.

## Criteria (the owner's done bar)

- **"Quest lands": cannot tell.** Nothing shows the quest landing in RimWorld. The only in-game evidence is static: a C# build log, a static validation PASS, and the selftest's `+a..+g` source and DLL checks. A quicktest log or screenshot of the hail letter, plus the dialog, would settle it.
- **"All three branches playable on a quicktest": false as evidenced.** Every branch was played by a simulated player in a fixture (`"simulated": true` on every quest row). No quicktest was run. The ledger says needs=offline, but the owner's criterion names a quicktest.
- **"Consequences logged on the blackboard": true.** Each answer writes a `cathedral_survey_answered` row with the outcome and the deltas.

## Staged or flattering

- All four ordinary_play runs use one hand-built fixture. That fixture's sale pushes Heat to 10.91, just over the 10.0 band, so the hail fires exactly on cue. It is a tidy best case. No run shows Heat hovering near the band or a sale off the pursuit timeline.
- The evidence is all shadow mode, "fired nothing". No incident, letter, dialog or save was exercised in the game.
- The offline half is strong and has real negative controls: no sale, off-Cathedral ground, toggle off, after full discovery, and reload/restart. Planted explanatory lines are refused (7/7).

## What is owed

A quicktest (BENCH, needs=owner live look or the quicktest lane) that fires `RUT_GiveQuest_CathedralSurveyMisdirection` and plays all three answers. It should capture the hail dialog, each outcome letter, and the blackboard rows the live bridge reads. The statement also needs regenerating from the item file.

would show: no
