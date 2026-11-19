An ordinary append to a tracked file outside a sparse checkout's cone creates a new 1-line file, which git reads as 'N deletions' and which makes every later pull --ff-only refuse. The deploy checkout /home/mandrake/rm/pulse-deploy is sparse with rimflow in its cone and no ledger: a rimflow write whose ROOT resolves there wipes a shard this way (reproduced 2026-11-19, git 2.53).
item: RIMMANDRAKE_TRACE_DEPLOY_SHARD_CUT_TO_ONE_LINE
home: infrastructure/state/facts/tool_traps.md
