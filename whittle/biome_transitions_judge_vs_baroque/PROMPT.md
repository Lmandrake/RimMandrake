The work is closing out the owner's C06 question on Biome Transitions. The mod was judged (verdict GO) and the crash it
was hiding was fixed on 2026-11-01 (`d85a6202`), but the item never closed. Make sure the verdict still stands on
today's main and that everything it touched is still true, then show it.

The owner's words and what we owe the user are in `whittle/biome_transitions_judge_vs_baroque/STATEMENT.md`. That is the only thing you may not change.
The owner's later rulings are in `whittle/biome_transitions_judge_vs_baroque/NOTES.md`, newest first. Reread both before you claim done; when they and this
conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Read it the way the owner would,
look at what he would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, docs, tests. If a test is wrong or in your way, fix it or drop it.

How to see what the owner sees: read the judgment doc `design/RimMandrake/biome_transitions_judgment_2026-11-01.md` and
its evidence JSON; run `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_biome_transitions_verdict`; and
validate the patch with `python3 skills/rimworld-modding/scripts/validate_patch.py src/RimMandrake/TerminalBiomes/Patches/RM_MixedBiome_Inert.xml --defs <dump>`.
Save what you judge by in `whittle/biome_transitions_judge_vs_baroque/evidence/`.

What you have, by name:
- the selftest above (it runs in seconds), and the patch validator
- `git log -F --grep=BIOME_TRANSITIONS_JUDGE_VS_BAROQUE`, the mod lists (`ModsConfig.FULL.LATEST.xml` and the sprint tiers), the offline def dump
- a second model: the `chatgpt-consult` skill (`python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`)
What you may not touch: any RimWorld game on any machine, the bridge, the owner's live mod list, other lanes' items;
and the Whittle machinery itself: `whittle/biome_transitions_judge_vs_baroque/STATEMENT.md`, `whittle/biome_transitions_judge_vs_baroque/NOTES.md`,
`whittle/biome_transitions_judge_vs_baroque/STOP`, `whittle/biome_transitions_judge_vs_baroque/JUDGE_PROMPT.md`,
`whittle/biome_transitions_judge_vs_baroque/JUDGE.md`, the Stop hook and its settings. Those belong to the owner and the
judge. Work lands on main through ./publish: commit what works, keep experiments in scratch.

How to work:
- Search before you build. Don't trust old notes without checking.
- No placeholders. Don't file tickets when you can fix it now.
- If something truly needs the owner, write it in `whittle/biome_transitions_judge_vs_baroque/BLOCKED.md` and stop.

Before you claim done:
1. Ask a different model to broaden your checking: give it the statement and what you checked, and ask what you
   missed. Try the most revealing one. Write it in `whittle/biome_transitions_judge_vs_baroque/BROADEN.md`.
2. Write `whittle/biome_transitions_judge_vs_baroque/DONE.md` from its template: every statement line, your honest verdict, fresh evidence files.
3. Spawn a fresh subagent judge (not a fork) with `whittle/biome_transitions_judge_vs_baroque/JUDGE_PROMPT.md` as its whole brief. It writes
   `whittle/biome_transitions_judge_vs_baroque/JUDGE.md`; you don't. If it would not show the work, keep going on what it found.

You're done when you would be happy to show this to the owner.
