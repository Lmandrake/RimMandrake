## spec
Handed to BENCH 2026-10-23 (owner: "I want Bench owning all Flowworks from now on to prevent mutual waiting."). FOUNDRY helpers started a FlowWorks code review (a 41-file wave) and did not finish it. `code_review_status.py check` over the tracked FlowWorks .cs/.py/.xml files showed 67 not-CLEAN lines at filing; the list is `python3 src/RimMandrake/Utils/code_review_status.py check $(git ls-files 'src/RimMandrake/FlowWorks/*.cs' 'src/RimMandrake/FlowWorks/*.py' 'src/RimMandrake/FlowWorks/*.xml') | grep -v ^CLEAN`.
NEXT: run that command, spawn a background reviewer (sonnet or opus per Agent_Policy.md) over the DIRTY files in waves of about 10, `mark-clean` only after a full-file review finds nothing.
## criteria
- L0: `code_review_status.py check` over `git ls-files src/RimMandrake/FlowWorks`: 0 DIRTY.
