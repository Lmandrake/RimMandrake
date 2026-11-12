The canal objects sheet is a labelled set of pictures of every FlowWorks ladder pose (lowered, raised, auto-turned, on
each of a pit's four walls), the river weir and ford stones, and the five looks (default, Futuristic, Industrial,
Modern, Scrapper) of tank, tall tank, hose reel and universal pipe, each row read back from the live game. The work is
to make `objects_sheet.py --prove` read PROVEN on a river map in SteveDesktop's game A.

The owner's words and what we owe the user are in `whittle/canal_objects_sheet_build_poses_and_styles/STATEMENT.md`.
That is the only thing you may not change. The owner's later rulings are in
`whittle/canal_objects_sheet_build_poses_and_styles/NOTES.md`, newest first. Reread both before you claim done; when
they and this conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: hold Steve's bridge (`rimflow bridge take --host stevedesktop --idle-ok --for ...`),
`infrastructure/whittle_claude/steve.sh sync`, `steve.sh deploy`, `steve.sh up`, then
`steve.sh run 'python.exe src/RimMandrake/FlowWorks/northstar/river_site.py'` and
`steve.sh run 'python.exe src/RimMandrake/FlowWorks/northstar/objects_sheet.py --prove'`. The result lands in Steve's
clone at `Transient/fw_scenes/live/objects/` (prove.txt, rows.json, index.html, *_labelled.png); copy it with
`steve.sh fetch` into `whittle/canal_objects_sheet_build_poses_and_styles/evidence/` and LOOK at the labelled pictures.
Show ordinary use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- Run: the two `steve.sh run` lines above (~6-8 min); `--only ladders|styles|river` reruns one family. Fast check:
  `python3 src/RimMandrake/FlowWorks/northstar/objects_sheet.py --mock` (seconds, no game) and
  `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_fw_walks`.
- Logs: Steve's Player.log (`steve.sh run` a tail), the script's `log_<stamp>.txt` and `<group>_traceback_<stamp>.txt` in
  the out dir; past runs: `rimflow show CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES`; skills `live-debugging-proof-harness`
  (classify every finding MOD, SITE or HARNESS), `rimbridge`, `rimworld-deploy`.
- A second model: the `chatgpt-consult` skill (`python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`).
What you may not touch: Archmagi's game, SteveDesktop's game B, the owner's campaign saves and mod list, other lanes'
items, any flyer's flight; and the Whittle machinery itself: `whittle/canal_objects_sheet_build_poses_and_styles/STATEMENT.md`,
`whittle/canal_objects_sheet_build_poses_and_styles/NOTES.md`, `whittle/canal_objects_sheet_build_poses_and_styles/STOP`,
`whittle/canal_objects_sheet_build_poses_and_styles/JUDGE_PROMPT.md`, `whittle/canal_objects_sheet_build_poses_and_styles/JUDGE.md`,
the Stop hook and its settings. Those belong to the owner and the judge. Work lands on main through ./publish: commit
what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/canal_objects_sheet_build_poses_and_styles/BLOCKED.md` and
  stop; that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/canal_objects_sheet_build_poses_and_styles/BROADEN.md`.
2. Write `whittle/canal_objects_sheet_build_poses_and_styles/DONE.md` from its template: every statement line, your
   honest verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/canal_objects_sheet_build_poses_and_styles/JUDGE_PROMPT.md` as its whole brief, plus the run command if it
   needs one. It writes `whittle/canal_objects_sheet_build_poses_and_styles/JUDGE.md`; you don't. If it would not show
   the work, keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.

## This loop's round (appended to the Whittle prompt by loop.sh)

Before anything else read `infrastructure/whittle_claude/common.md` (the project rules and the blockages) and
`infrastructure/whittle_claude/lane_steve.md` (what your lane may touch). The item is `CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES`; your Whittle
directory is `whittle/canal_objects_sheet_build_poses_and_styles`; its `MODE` file says `whittle` or `pilot`.

- Mode `whittle`: build until every STATEMENT bullet is true and shown by evidence, then let the judge pass it.
- Mode `pilot`: this is a Test Pilot sitting, not another code-and-retest round. Run `rimflow pilot CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES` and follow
  the brief it prints, with the `test-pilot-sitting` skill: experiments that discriminate between hypotheses, each
  recorded in NOTES.md, then the fix or the filed finding.
- Live evidence comes only from your lane's game, held through the bridge lock as your lane file says, and released
  before you stop. Record proof runs on the item the way its proof script does (modcheck, or `rimflow live`: read `--help`) so the ledger
  carries them.
- Commit and `./publish` your work as it lands (explicit paths). Do NOT close the item here: the wrap-up phase closes,
  parks or drops it after checking your DONE.md and the judge.
- If you cannot go on without the owner, write the question as common.md says, put one line in `whittle/canal_objects_sheet_build_poses_and_styles/BLOCKED.md`
  naming it, and stop.
