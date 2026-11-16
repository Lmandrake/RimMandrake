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
