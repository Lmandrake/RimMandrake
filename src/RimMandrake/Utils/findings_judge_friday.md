
Today is Friday: after the daily judging, do the WEEKLY MEMORY SWEEP. Read the table at the end of findings_fold.md
for general patterns (a machine fault, one failure across runs). Write each into the owning skill or fact file
(under .claude/skills/ or infrastructure/state/facts/) and record it with `findings_fold.py decide <SIG> --as memory
--into FILE:LINE --why ... --seat BENCH`; never the lessons inbox. A repeat error class becomes a rule
candidate for the Conductor: `python3 src/RimMandrake/rimflow/cli.py file <ID> --for BENCH --kind finding --title "Rule
candidate: ..."` (name it with `rimflow namecheck`). Count these in `memory=`.

Then EXAMINE THE FLAGGED CODE FILES (his card 2026-11-19 5:54 PM PST: "Flagged files are examined to see if we need to
change the definition of significant or there is a real instability, but this is done infrequently, say weekly or
so."; RIMMANDRAKE_WIRE_FRIDAY_JUDGE_TO_EXAMINE_FLAGGED_FILES_WEEKLY):
1. Run `python3 src/RimMandrake/Utils/code_review_status.py list --flagged`. Exit 3 means a flag shard is unreadable:
   say so in your report, examine nothing, and write `flagged=UNREAD`. No flagged file is `flagged=0`.
2. For each flagged file answer one question: must the definition of significant change, or is this code really
   unstable? Read the flag's why and `git log` of the file since the flag.
3. A definition answer: file one rule candidate item (title `Rule candidate: ...`) for all the flags that raise the same
   question, and quote those flags. An
   instability answer: leave the flag and write one line in your report. When the examination ends a flag:
   `python3 src/RimMandrake/Utils/code_review_status.py unflag <path> --why "<the answer>"`.
4. Add ` flagged=<n examined>` to the end of your JUDGED line.
