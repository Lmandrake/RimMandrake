
Today is Friday: after the daily judging, do the WEEKLY MEMORY SWEEP. Read the table at the end of findings_fold.md
for general patterns (a machine fault, one failure across runs). Write each into the owning skill or fact file
(under .claude/skills/ or infrastructure/state/facts/) and record it with `findings_fold.py decide <SIG> --as memory
--into FILE:LINE --why ... --seat BENCH`; never the lessons inbox. A repeat error class goes to the Auditor as a rule
candidate: `python3 src/RimMandrake/rimflow/cli.py file <ID> --for BENCH --kind finding --title "Auditor rule
candidate: ..."` (name it with `rimflow namecheck`). Count these in `memory=`.
