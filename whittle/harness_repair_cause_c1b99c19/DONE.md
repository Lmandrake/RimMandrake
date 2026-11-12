# Done claim

- true: the class is recorded on this item (note) with its evidence before the fix; | evidence: `whittle/harness_repair_cause_c1b99c19/evidence/class_note.log`
- unseen: `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_C1B99C19` exits 0 on a job run at the fix's sha; | evidence: `whittle/harness_repair_cause_c1b99c19/evidence/rerun_36596f_status.log` `whittle/harness_repair_cause_c1b99c19/evidence/csharp_hose_gate_rerun2.log`
- true: the negative control above exits 1. | evidence: `whittle/harness_repair_cause_c1b99c19/evidence/negative_control.log`

## What I'm least sure about
Bullet 2 is not shown. The two earlier re-runs (b4fe4d with verdicts, c68996) were quarantined for host fault windows,
so they don't count. A fresh re-run, testq J20261112T061851Z-36596f at ad165c84c2, is queued but pending: the testq lane
has been PAUSED since 2026-11-12T03:23Z because the FWLIVE Whittle loops hold both games (owner order 2026-11-11 19:10 PST).
The offline gate that refused the original run is green at ad165c84c2. Each step was run separately
(`offline_gate_20261111T2156.log` is the whole-gate attempt, which timed out at 530 s under load). The C# step went red
once on a csc.exe 0xC0000005 host crash and passed on an immediate re-run (`csharp_hose_gate.log`, `csharp_hose_gate_rerun2.log`).

## What I did not test
The live hose_live_rows run itself. Whether SteveDesktop's runner fits the gate (431 s here under load) plus the live
blocks inside the 3240 s job timeout.
