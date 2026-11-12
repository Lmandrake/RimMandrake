# Judge: CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1 (fresh judge, 2026-11-11, round after broaden 2)

STATEMENT.md is malformed: it holds one empty bullet and a "Depends on" fragment, with no real lines. I judged against the
item file's spec, verify and criteria (`infrastructure/state/items/CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1.md`), which
STATEMENT.md says are the owner's words. I read the evidence/ files, reran `selftest_rustcathedral_survey.py` (73 checks,
0 failed, exit 0) and linted both shipped XML files myself at stage 0 (QuestScriptDef 15 strings, IncidentDef 2 strings,
both PASS, 0 findings).

## Lines

1. **Fires from the pursuit spine dressing, without inventing a faction**: true (offline). Selftest [1]: the hail fires only on
   Cathedral ground with Heat at or over the band (1b, 1c, 1m, 1n, 1f). 1j: no FactionDef ships. 1k: the C# binds to
   EmpireSearch / ScenPart_RuthlessPursuingMechanoids.PursuitFaction and falls back to Faction.OfEmpire. These are source
   and fixture checks. No live run shows the quest firing in the game.
2. **(b) success moves Regard up in shadow mode and Heat not at all (K2)**: true. ordinary_play_dull.txt: +12 Regard per
   answer (+24 total). Heat matches the other branches poll for poll (10.91 to 10.11 to 9.71, the same in the pointed and
   silent files). Selftest 2e: Heat is identical across all 160 polls. The spec says "large Regard gain". +12 moves the
   stage band (WARY to TOLERATED sooner), but I cannot judge "large" without the Regard scale.
3. **(c) moves exposure pressure**: true. ordinary_play_pointed.txt: exposure goes up 20 per answer (1.00 to 20.40), and
   Regard and Heat do not move with it. Selftest 3a and 3d agree.
4. **All dialog passes item 3's linter; no line explains what the player protected**: true. arc_lint.txt passes at stages
   -1 to 3, and my own runs pass. I read the shipped text (hail, three answers, four letters). The (b) letter tells what the
   surveyors did and never why. Nothing names the Cathedral, Heat or a loyalty reward. Small gap: the selftest says "13
   strings" and the lint reads 17. Probably def labels; it does not change the verdict.
5. **Completes Oracle-absent with prescribed fallback text**: true. Selftest [5]: no `claude` on PATH, no LLM and no
   process started. Each branch ends the quest with its own shipped letter.
6. **Criteria: "Quest lands, all three branches playable on a quicktest, consequences logged on the blackboard"**: false
   as it stands. "Consequences logged on the blackboard" is shown, but only in ShadowBlackboard with FixtureBridge.
   "Quest lands" and "playable on a quicktest" have no live evidence: no screenshot of the hail, no in-game run of any
   branch, no game log. The successful winbuild and the committed DLL show that the code compiles. They do not show that
   the QuestScriptDef resolves, that the dialog buttons work, or that the Postpone and reload paths behave in RimWorld.
   What would settle it: the live recipe (validation.py LIVE RUN RECIPE step 8). Fire
   `RUT_GiveQuest_CathedralSurveyMisdirection`, play each of the three answers, take a screenshot of the hail and each
   letter, and capture the blackboard lines from a real bridge.

## Staging / flattery
- All behavioural evidence comes from one scripted fixture (`cathedral_survey_ordinary_play.json`): a clean two-sale arc
  with a simulated player who answers on cue. The selftest's "messy" run (section 8) and broaden-2's late-answer probes
  widen it somewhat, but they are still fixture runs.
- "would fire ... fired nothing" means shadow mode. Not one hail has been put in front of a player.
- The winbuild log admits a first attempt that exited 5 with no compiler error, and it restored the committed DLL.
  Harmless, but the DLL it proves is the committed one, not this rerun's output.

## Verdict
Offline the design work is solid and well tested: every verify line holds there. The owner's criterion asks for a quicktest
of all three branches, and no live evidence exists. This round did not change that. I would not show it as finished until
the live step has run.

would show: no
