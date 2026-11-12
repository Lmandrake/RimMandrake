The work is the live proof of PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS: in FlowWorks, a colonist who digs a square down to
superdeep (D3 -> D4, 2 m) turns up a chunk of a deep stone that is not on this map's surface, with a first-find "Deep stone"
letter. It should feel like digging finally pays: the chunk lands by the pit lip and the letter names the stone.

The owner's words and what we owe the user are in `whittle/pit_deepstone_build_digging_finally_pays/STATEMENT.md`. That is
the only thing you may not change. The owner's later rulings are in `whittle/pit_deepstone_build_digging_finally_pays/NOTES.md`,
newest first. Reread both before you claim done; when they and this conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: on SteveDesktop game A,
`infrastructure/whittle_claude/steve.sh run 'python.exe src/RimMandrake/FlowWorks/northstar/deep_stone_live.py <out.json> --fresh-map'`,
then `infrastructure/whittle_claude/steve.sh fetch <out.json> whittle/pit_deepstone_build_digging_finally_pays/evidence/`.
Take a bridge screenshot of the pit, the chunk and the letter when a row is in doubt. Save what you judge by in
`whittle/pit_deepstone_build_digging_finally_pays/evidence/`. Show ordinary use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- The run command above (a fresh quicktest map, about 90 s, plus up to 6000 ticks for the cut). Fast checks:
  `RM_DigDiscoveryProof.ProofReport("deepstone")` through `jawa/static_call`, and the FlowWorks SelfTest
  `DeepStone_superdeep_strikes_and_stable_pick`. Game control: `steve.sh deploy | up | status | restart` (no argument lists
  the verbs). C# is built here with `python3 src/RimMandrake/Utils/winbuild.py FlowWorks`; the DLLs travel with `steve.sh sync`.
  Bridge: `rimflow bridge who|take|release --host stevedesktop`.
- Past runs and their MOD/SITE/HARNESS classifications in NOTES.md; sibling items `DEEP_STONE_FIX_NOBODY_PICKS_UP_SHOVEL`,
  `DEEP_STONE_FIX_PROBE_NEVER_NAMES_PAWN`, `DEEP_STONE_PROOF_FIX_RERUN_LETTER_FAILS` (`rimflow show <ID>`); the last rerun
  `D:\ClaudeWork\rimmandrake\scratch\bridge_run_1f\deep_stone_s5.json`; Player.log on Steve's game; source
  `src/RimMandrake/FlowWorks/Source/RM_DigDiscovery.cs`; staging `src/RimMandrake/FlowWorks/northstar/shovel_stage.py`;
  skills `live-debugging-proof-harness`, `rimbridge`, `rimworld-debug-testing`.
- A second model: the `chatgpt-consult` skill (`python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`).

What you may not touch: Archmagi's game (never `./game`, `deploy_custom_mods.py --apply`, rimbridge or a proof script on
Archmagi), SteveDesktop game B, the owner's mod list on his campaign, canonical world saves, any flyer's flight, anything
outside this item; and the Whittle machinery itself: `whittle/pit_deepstone_build_digging_finally_pays/STATEMENT.md`,
`whittle/pit_deepstone_build_digging_finally_pays/NOTES.md`, `whittle/pit_deepstone_build_digging_finally_pays/STOP`,
`whittle/pit_deepstone_build_digging_finally_pays/JUDGE_PROMPT.md`, `whittle/pit_deepstone_build_digging_finally_pays/JUDGE.md`,
the Stop hook and its settings. Those belong to the owner and the judge. Work lands on main through ./publish: commit what
works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/pit_deepstone_build_digging_finally_pays/BLOCKED.md` and stop;
  that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/pit_deepstone_build_digging_finally_pays/BROADEN.md`.
2. Write `whittle/pit_deepstone_build_digging_finally_pays/DONE.md` from its template: every statement line, your honest
   verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/pit_deepstone_build_digging_finally_pays/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs
   one. It writes `whittle/pit_deepstone_build_digging_finally_pays/JUDGE.md`; you don't. If it would not show the work,
   keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.
