The work is the live proof of the bleed well's switch-and-say-why build: in a running game a bleed well (RM_LiquidTap)
must show an On/Off switch, pour into a dug outlet once a debug subsurface yield is given, stop when switched off, and
show a ? with a readable reason whenever something else blocks it. The code is built (b26a96a424); what is missing is a
run that shows it, and any fix that run turns up.

The owner's words and what we owe the user are in `whittle/bleed_well_build_switch_and_say_why/STATEMENT.md`. That is
the only thing you may not change. The owner's later rulings are in `whittle/bleed_well_build_switch_and_say_why/NOTES.md`,
newest first. Reread both before you claim done; when they and this conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: Archmagi's RimWorld through the bridge (`rimflow bridge take --idle-ok --for
"BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY: live proof"`), on the small all-DLC FlowWorks tier
(`python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks --apply`), in a dev quicktest colony (skill
`rimworld-debug-testing`). Deploy first: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks` then
`--apply` (C#: `python3 src/RimMandrake/Utils/winbuild.py FlowWorks` before). Launch:
`python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/Utils/northstar_driver'); import live_session as L; L.launch_and_wait()"`.
Capture zoomed screenshots through the bridge (skill `rimworld-live-review`) and read outlet fill and inspect strings
through bridge calls (skill `rimbridge`). Save what you judge by in `whittle/bleed_well_build_switch_and_say_why/evidence/`.
Show ordinary use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- Code: `src/RimMandrake/FlowWorks/Source/Drilling/Building_LiquidDrill.cs`, `RM_DrillSurveyMath.cs`,
  `RM_MapComponent_SubsurfaceLiquid.cs`; defs `src/RimMandrake/FlowWorks/Defs/Drilling/ThingDefs/RM_LiquidDrill.xml`.
- Fast check offline: the FlowWorks selftest case `DrillWhyNot_each_condition_names_its_reason`
  (`python3 src/RimMandrake/Utils/run_selftests.py --only <flowworks test>`); live: one bridge read of the outlet fill.
- Logs: `Player.log` (read the FIRST exception), the bridge journal; `rimflow show BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY`.
- Skills: `live-debugging-proof-harness` (classify each finding MOD, SITE or HARNESS), `rimbridge`,
  `rimbridge-companion` (if a bridge tool is missing), `rimworld-deploy`, `rimworld-live-review`.
- A second model: the `chatgpt-consult` skill (`python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`).
What you may not touch: the other machine's game (it belongs to the other live lane; this loop drives Archmagi's game
only); the owner's mod list on his campaign and the canonical world saves; other lanes' items and clones; anything
outside this item. Never live-test a flyer's flight. And the Whittle machinery itself:
`whittle/bleed_well_build_switch_and_say_why/STATEMENT.md`, `whittle/bleed_well_build_switch_and_say_why/NOTES.md`,
`whittle/bleed_well_build_switch_and_say_why/STOP`, `whittle/bleed_well_build_switch_and_say_why/JUDGE_PROMPT.md`,
`whittle/bleed_well_build_switch_and_say_why/JUDGE.md`, the Stop hook and its settings. Those belong to the owner and the
judge. Work lands on main through ./publish: commit what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/bleed_well_build_switch_and_say_why/BLOCKED.md` and stop;
  that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/bleed_well_build_switch_and_say_why/BROADEN.md`.
2. Write `whittle/bleed_well_build_switch_and_say_why/DONE.md` from its template: every statement line, your honest
   verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/bleed_well_build_switch_and_say_why/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs
   one. It writes `whittle/bleed_well_build_switch_and_say_why/JUDGE.md`; you don't. If it would not show the work, keep
   going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.

## This loop's round (appended to the Whittle prompt by loop.sh)

Before anything else read `infrastructure/whittle_claude/common.md` (the project rules and the blockages) and
`infrastructure/whittle_claude/lane_archmagi.md` (what your lane may touch). The item is `BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY`; your Whittle
directory is `whittle/bleed_well_build_switch_and_say_why`; its `MODE` file says `whittle` or `pilot`.

- Mode `whittle`: build until every STATEMENT bullet is true and shown by evidence, then let the judge pass it.
- Mode `pilot`: this is a Test Pilot sitting, not another code-and-retest round. Run `rimflow pilot BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY` and follow
  the brief it prints, with the `test-pilot-sitting` skill: experiments that discriminate between hypotheses, each
  recorded in NOTES.md, then the fix or the filed finding.
- Live evidence comes only from your lane's game, held through the bridge lock as your lane file says, and released
  before you stop. Record proof runs on the item the way its proof script does (modcheck, or `rimflow live`: read `--help`) so the ledger
  carries them.
- Commit and `./publish` your work as it lands (explicit paths). Do NOT close the item here: the wrap-up phase closes,
  parks or drops it after checking your DONE.md and the judge.
- If you cannot go on without the owner, write the question as common.md says, put one line in `whittle/bleed_well_build_switch_and_say_why/BLOCKED.md`
  naming it, and stop.
