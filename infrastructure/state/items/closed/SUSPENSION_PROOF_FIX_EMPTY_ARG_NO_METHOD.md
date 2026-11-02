## spec
found-by: BENCH bridge run (2026-10-23, run 1, build fed77f423a, 14-mod tier). Class: HARNESS.

`src/RimMandrake/FlowWorks/northstar/suspension_settings_live.py:81` calls `proof("ProofButtons", "")`; `jawa/static_call`
with `args=""` looks for a 0-param overload and answers "No public static ProofButtons with 0 params." while the method is
`ProofButtons(string arg)` (RM_SuspensionProofs.cs:184, arg ignored) -> SB_settings_off_no_button UNMEASURED/HARNESS
("old DLL?" guess is wrong; the DLL was current). Evidence `Transient/bridge_run_1_20261023/suspension_settings.json`.
Proven: the same run with the arg changed to "x" in the export copy only -> PASS (`suspension_settings2.json`).
Fix: pass a non-empty arg (and grep other northstar scripts for `static_call ... args=""` on 1-param proofs);
optionally make static_call treat "" as one empty string arg when only a 1-string overload exists.
