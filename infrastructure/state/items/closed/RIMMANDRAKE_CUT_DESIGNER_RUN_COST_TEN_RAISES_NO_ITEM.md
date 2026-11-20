## spec
The Conductor log (`D:\ClaudeWork\rimmandrake\conductor\log.md`) printed "RAISE FIRST: Designer run rm-role-designer-N
went over its advisory budget: file an item and cut its cost now." 10 times and "Designer keeps overrunning: re-set its
budget or narrow its scope." 9 times, the last at 2026-11-15T20:41Z, and no ledger item was ever filed for it (the
Operations overrun has four duplicate items; the Designer has none). The `roles-20261115093955` incident adds "Designer
chained Contagion 8 times today: it is looping" (2026-11-16T00:44Z), with the plan "read Contagion's stage history with
one opus helper, fix the chain's cause in the pipeline rather than raising the cap". Token limits stay advisory (owner
2026-11-02, TOKEN_LIMITS_TAME_BARK_NO_BITE): this is about cost per run and the loop's cause, never a kill.

Do: measure the Designer's last 14 days of runs (cost, chain length, which step spends), name the cause of the
Contagion chain, fix it in `designer_stage.py` or the role brief, and state the run budget it now fits. Found by the
pipeline sleeper census (`design/RimMandrake/pipeline_sleepers_census_2026-11-15.md`).

Acceptance test: none, the cause is not yet diagnosed; the first step of the work is to write the check that the
Contagion chain stops (a replay of its stage history through the fixed chain rule), watch it fail, then fix.

## decided 2026-11-18 (DESIGN DECISION note on this item)
The Contagion "chain of 8" was one first-touch walk of Designer steps 0 to 5 in a day, not a loop; the real repeat is a
coverage refusal sending steps 2 to 5 round again with a whole exam retake, and that is built by
RIMMANDRAKE_RETAKE_ONLY_TOUCHED_EXAM_SCENARIOS_CARD_ASKED_TWICE. What is left for THIS ticket: 22 of 228 Designer runs
across ten concepts ended "result rejected: no result.json (a closing message is not a result)" and were paid again.
First step: split those 22 into killed runs (RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS classes them
void) and runs that ended by themselves without writing the file; fix the second kind in the role brief or
`designer_stage.py close`.
Acceptance test: none yet, the split is not measured; the first step writes the check (a replay of one such run's
close through the fixed path), watches it fail, then fixes.
