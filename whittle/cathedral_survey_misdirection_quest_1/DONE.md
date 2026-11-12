<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

STATEMENT.md came out of `wc.py setup` truncated. It has one empty bullet and one fragment, which the Stop hook reads
as a single bullet (copied exactly below). The statement's header says the item file's spec and verify are the
owner's words, so after the bullet there is a verdict for every clause of the item's verify and criteria. The
truncation is filed as a lesson (`infrastructure/state/lessons/20261112T054039Z-CLAUDE_STEVEDESKTOP_OFFLINE3-wc-py-setup-wrote-whittle-cathedral.md`).

- true: - *Depends on:** item 1 (Regard/exposure sinks), item 3 (linter), pursuit | evidence: `whittle/cathedral_survey_misdirection_quest_1/evidence/selftest_rustcathedral_survey.txt` `whittle/cathedral_survey_misdirection_quest_1/evidence/arc_lint.txt` `whittle/cathedral_survey_misdirection_quest_1/evidence/broaden2_late_answer.txt`

  The quest is built on all three dependencies and invents none of them:
  - **Item 1's sinks.** (b) feeds item 1's Regard counter (`CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS`, the slot
    item 1 had left at "unbuilt"). (c) feeds item 1's §6.1 exposure-pressure accumulator.
  - **Item 3's linter.** `cathedral_arc_lint.py` gates every string. It gained the three answer tags and a
    "concealment explained (§4)" rule.
  - **The pursuit spine.** The quest's faction is EmpirePursuit's `PursuitFaction`, else vanilla Empire. The trigger
    is the shared Imperial Heat at or over the low band.

Each verify and criteria clause:

- true: Fires from the pursuit spine dressing without inventing a faction | evidence: `whittle/cathedral_survey_misdirection_quest_1/evidence/selftest_rustcathedral_survey.txt`
  In ordinary play the clan sells two kyber crystals on day 5 and is hailed that poll; a second sale a month later
  brings a second hail. There is no hail at low Heat, off Cathedral ground, after full discovery, or with the toggle
  off (checks 1a-1i). New this round, [8]: in messier play the clan sells one crystal at a
  time. The first sale leaves Heat at 7.6, under the band, and nobody comes. The second tips it to 10.8 and the
  survey hails that poll. A lone later sale (7.6) brings nobody (8a-8c). CathedralPass ships no FactionDef (1j), and the reflection names it binds exist in
  EmpirePursuit's source (1l).
- true: (b) success moves Regard up in shadow mode and Heat not at all | evidence: `whittle/cathedral_survey_misdirection_quest_1/evidence/selftest_rustcathedral_survey.txt` `whittle/cathedral_survey_misdirection_quest_1/evidence/broaden2_late_answer.txt`
  Regard is +12 on the poll the answer is read, against the same run with the hail left to lapse.
  Is +12 "large" (the judge's open question)? On the shipped scale in `src/RimMandrake/Utils/gm_blackboard_shadow.py`, yes. It is the second-largest single gain, after the restore choice (+30). It equals three missions (+4 each) or 2.4 kyber sales' loss (-5 each), and it is 80% of the TOLERATED floor (15). A clan starting at zero crosses into TOLERATED with one dull answer plus a few clean polls. Heat, Hutt Interest
  and the orbital timer are identical poll for poll across all 160 polls (2a-2g), and again in the messy run (8e, 8f). A late answer,
  given after the clan left the ground or the toggle went off, still settles once (`broaden2_late_answer.txt`).
- true: (c) moves exposure pressure | evidence: `whittle/cathedral_survey_misdirection_quest_1/evidence/selftest_rustcathedral_survey.txt`
  Exposure pressure is +20 on the answer poll; Heat and Regard are identical to the lapse run (3a-3f; messy run 8d).
- true: all dialog passes item 3's linter (no line explains what the player protected) | evidence: `whittle/cathedral_survey_misdirection_quest_1/evidence/arc_lint.txt` `whittle/cathedral_survey_misdirection_quest_1/evidence/selftest_rustcathedral_survey.txt`
  All 17 strings in the quest, letter and incident defs pass at stages -1 to 3 (re-run this round). Seven planted
  explanatory lines are refused (4c), and the (b) letter says only what the surveyors did (4d).
- true: completes Oracle-absent with prescribed fallback text | evidence: `whittle/cathedral_survey_misdirection_quest_1/evidence/selftest_rustcathedral_survey.txt`
  The blackboard runs with no `claude` on PATH and the survey path starts no process (5a, 5b). Every hail carries the
  shipped def text (5c), and every branch ends in its own shipped letter and outcome (5d, 5e). The full dialog and
  the four letters are printed at the end of the selftest file.
- true: consequences logged on the blackboard | evidence: `whittle/cathedral_survey_misdirection_quest_1/evidence/selftest_rustcathedral_survey.txt` `whittle/cathedral_survey_misdirection_quest_1/evidence/broaden2_late_answer.txt`
  Each answer writes a `cathedral_survey_answered` row with its outcome and deltas, and `outcomes_so_far` counts them.
- true: same CQF/bridge-letter surface and caveat as item 4 | evidence: `whittle/cathedral_survey_misdirection_quest_1/evidence/selftest_rustcathedral_survey.txt`
  New check [7]. Item 4 (`CATHEDRAL_MISSION_BOON_OFFERS_1`) settled the inherited CQF caveat with vanilla quest
  machinery: a baseChance-0 GiveQuestBase incident on the home map, fired by the blackboard through
  jawa/storyteller_fire, with the outcome read back off the quest list. The survey matches it point for point
  (7a-7e). Every quest node is vanilla or this mod's own, and CathedralPass depends on Harmony only, so no CQF.
- unseen: Quest lands, all three branches playable on a quicktest | evidence: `src/RimUtinni/CathedralPass/validation.py`
  This lane drives no game. The C# builds clean against this machine's RimWorld 1.6 assemblies (0 warnings,
  `whittle/cathedral_survey_misdirection_quest_1/evidence/winbuild_cathedralpass.txt`), and the engine paths it
  relies on were read in decompiled source. Nobody has yet seen the hail open in a running game. The step is written
  as LIVE RUN RECIPE step 8 in `src/RimUtinni/CathedralPass/validation.py`, and the item is marked needs=bridge.

## What I built
- `src/RimUtinni/CathedralPass/Source/CathedralSurvey.cs`:
  - `RUT_QuestNode_SurveyHail` and `RUT_QuestPart_SurveyHail`: the hail is sent on Initiate, answered once only,
    and its letter is removed on Cleanup.
  - `RUT_ChoiceLetter_SurveyHail`: three answers plus Postpone.
  - `IncidentWorker_GiveQuest_CathedralSurvey`, gated on the new `cathedralSurveyEnabled` setting.
  - `SurveyFaction`: the soft-bound pursuit faction.
- Defs:
  - `RUT_CathedralSurveyMisdirection`: hidden and auto-accepted, so no Quests-tab row ever shows "succeeded" or
    "failed". (b) ends Success, (c) ends Fail and drops a 150-250 silver finder's fee, (a) refused or a 2-day lapse
    ends Unknown.
  - The `RUT_GiveQuest_CathedralSurveyMisdirection` incident (baseChance 0) and the `RUT_CathedralSurveyHail`
    LetterDef.
- `src/RimMandrake/Utils/gm_blackboard_shadow.py`: `advance_cathedral_survey` (the trigger) and
  `observe_survey_quests` (the outcome read).
  - **A reload** that takes back an answer reverses its credit (found by the broadening pass).
  - **A restart** treats ended surveys as history (found by the code reviewer).
- `src/Directory.Build.props`: falls back to `D:\SteamLibrary` when the C: Steam paths are absent. SteveDesktop moved
  its Steam library there today, and before this fix no C# built on this machine.

## What I'm least sure about
- **The live dialog.** This needs a look in a running game: the faction strip, the `{FACTION}` substitution, the
  silver pod at the trade drop spot, the letter surviving a save and reload. I checked from decompiled source that
  an auto-accepted quest initiates on `QuestManager.Add`, that `ReceiveLetter` has no hidden-quest filter, that
  `QuestNode_End` sends no standard letter unless asked, and that `QuestUnique` scans hidden quests.
- **The tuning numbers.** Regard +12, exposure +20, Heat band 10 and a month's gap are GM tuning placeholders, like
  every number on the blackboard.
- **The (b) letter's wording.** "The officer stops taking notes" is a judgment call (see BROADEN.md).

## What I did not test
- Any live game. The quest has never been fired in RimWorld.
- Translation keys for the hail's own strings. They are plain fields, English only, and carry no TKey.
- A second save-scum layer: rewinding the blackboard's month gap after a reload from before the hail. The gap stays
  conservative, so the next hail waits.
- `selftest_cathedralpass_retaliation.py` is red on origin/main since the Descent lane's 5dba1df0f6. That file is not
  mine; the finding is noted on CATHEDRAL_DESCENT_REVEAL_SITE_1.
