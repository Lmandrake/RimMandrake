The work is the owed live proof for GSS_WATER_STUB_FIX_PASSED_LAST_WEEK: with FlowWorks co-loaded (deep swim on), Gimme Some Slack's
matrix scene MX_F60_T15_S0 must again see both waterproof-conduit water stubs (stubs 2, cord_edges 2, strands [2,2]). The
fix is built (4b01d06994); what is missing is a clean PASS on the fw_gss_sitting list, on Archmagi's game.

The owner's words and what we owe the user are in `whittle/gss_water_stub_fix_passed_last_week/STATEMENT.md`. That is the only thing you may not change.
The owner's later rulings are in `whittle/gss_water_stub_fix_passed_last_week/NOTES.md`, newest first. Reread both before you claim done; when they and this
conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: `python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --only matrix`
(read its docstring first) on the `fw_gss_sitting` tier, bridge held; its result JSON (`--out`, or the timestamped
`proof_all_*.json` beside it) holds the MX_F60_T15_S0 row. A zoomed screenshot of the scene's board shows the two buried
waterproof runs. Save what you judge by in `whittle/gss_water_stub_fix_passed_last_week/evidence/`. Show ordinary
use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- Run: the command above. Setup: `python3 src/RimMandrake/Utils/modset_builder.py --tier fw_gss_sitting --apply`,
  `deploy_custom_mods.py --mod GimmeSomeSlack` and `--mod FlowWorks` (plan, read, then `--apply`), `live_session.launch_and_wait()`
  (see the lane brief). Fast check: `proof_all.py --offline-gate` (seconds) and GSS SelfTest WaterStubChecks.
- Past runs: `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261107T031035.json` (PASS, but gimmesomeslack tier);
  the 2026-10-23 FAIL `D:\ClaudeWork\rimmandrake\scratch\br1_gss\gss_A.json`; `Player.log`; `rimflow show <ID>`.
  Skills: `live-debugging-proof-harness` (classify MOD/SITE/HARNESS), `rimbridge`, `rimworld-deploy`.
- A second model: the `chatgpt-consult` skill (`python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`).
What you may not touch: any game but Archmagi's (the lane brief says why), the canonical world saves, other
lanes' items, uncommitted FlowWorks edits in this clone that are not yours (deploy from committed state); and the Whittle machinery
itself: `whittle/gss_water_stub_fix_passed_last_week/STATEMENT.md`, `whittle/gss_water_stub_fix_passed_last_week/NOTES.md`, `whittle/gss_water_stub_fix_passed_last_week/STOP`, `whittle/gss_water_stub_fix_passed_last_week/JUDGE_PROMPT.md`, `whittle/gss_water_stub_fix_passed_last_week/JUDGE.md`, the
Stop hook and its settings. Those belong to the owner and the judge. Work lands on main
through ./publish: commit what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/gss_water_stub_fix_passed_last_week/BLOCKED.md` and stop; that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/gss_water_stub_fix_passed_last_week/BROADEN.md`.
2. Write `whittle/gss_water_stub_fix_passed_last_week/DONE.md` from its template: every statement line, your honest verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/gss_water_stub_fix_passed_last_week/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs one. It writes `whittle/gss_water_stub_fix_passed_last_week/JUDGE.md`; you
   don't. If it would not show the work, keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.
