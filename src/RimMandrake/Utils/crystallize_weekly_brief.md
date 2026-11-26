You run the weekly Crystallize pass of RimMandrake for week {WEEK}. Your ledger item is {ITEM}, seat BENCH.
rm-crystallize.timer launched you (`src/RimMandrake/Utils/crystallize_weekly.py`). Nobody is at the machine. Do not
wait for the owner and do not ask him anything in this run.

Read first:
- `design/RimMandrake/standing_rulings.md` §The weekly Crystallize pass improves the agents. That section names the
  two jobs of this pass.
- The `crystallize` skill (`~/.claude/skills/crystallize/SKILL.md` and the reference files that it names). Its table
  "What needs Mandrake and what does not" decides what you land and what goes on his sheet.
- The report of the last pass ({PREV_WEEK}): {PREV}

The report of this pass is `{FOLDER}/CYCLE_REPORT.md`. Keep every working file of the pass in `{FOLDER}/`. Make the
folder first. Write the report skeleton at the start and fill it in as each job ends, so a stopped run leaves a record.

The jobs, in this order:

1. Judge the last pass. Read the change that the last report adopted and its success criterion. Measure the criterion
   now. Write `held`, `did not hold`, or `could not measure` with the cause. Never rebuild a criterion from memory.
2. Improve the agents and the skills. For each role file in `src/RimMandrake/rimflow/roles/` and each registered skill
   in `skills/README.md`, ask: does the evidence since the last pass improve it? The evidence is the lessons filed
   since then (`infrastructure/state/lessons/`), the items closed since then, the findings judge's decisions, and the
   lines that a later ruling or measurement made false. Fix each false line on sight, with what disproves it. Land
   only what the skill's table lands without asking. Put each other change on his sheet in the report, as before and
   after. A role or skill that the evidence does not touch gets no edit: list it as "no evidence since the last pass".
3. The lessons inbox and the handoffs. Merge the lessons as `references/other-inputs.md` of the skill says. Cull
   handoffs only through the handoff tool, after their citations are repointed and their lessons filed.
4. One file pass. Run the skill's `scripts/due.py --scope` on this repo and take the first file that it lists. Do the
   seven steps of the skill on that file, with its lister and inspector as agents that are not the writer.
5. The skill and tool proposals. Put in the report each proposal for a new skill, and each proposal to move a skill
   or tool up to the user-level tools. Each entry gives its name, what moves, why it is general, and the measured
   evidence. He decides each one. Look at the open ledger items whose name starts `RIMMANDRAKE_PROPOSE_` and at the
   lessons whose home is a user-level tool or skill.

Land with `./publish` and explicit paths, one commit for each kind of change, subjects that start `crystallize {WEEK}:`.
The project rules still bind: CLAUDE.md §Correctness outranks seat ownership, §Touching code has a cost, and
§Only five acts stay his. A loaded rule file that another live run is editing gets its pass in a `git worktree` from origin/main, rebased
before it lands. Say in the report which runs edited it during the pass.

The report has these sections: 1 the last pass's change and its verdict; 2 what each job did, before and after, with
the commit of each change; 3 the change adopted this pass, with one success criterion that the next pass measures and
how to measure it; 4 his sheet (what waits for his yes); 5 the skill and tool proposals; 6 what was not done, and why.

When every job has its outcome in the report, write the line `Status: FINAL` under the title, alone on its line. The
week's outcome check reads that line (`crystallize_weekly.py report {WEEK}`), so write it last and only when it is true.
Then write a note on {ITEM} with the report path, and close {ITEM} with the sha of your last publish.
