# FlowWorks pulse-engine acceptance failures — 2026-10-08

Helper: FOUNDRY, offline only.

## Steps
- 1: fw_FlowWorks2.txt deduped: 37 blocks = offline tier + selftest_live_mock (clean mock run + one MockBridge fault-injection run per fault). Biome MockDesert, 'loaded mock sha'. Pulse-row FAILs are negative controls, not the live game. Only O9 is a real offline FAIL.
- 2: blocks map 1:1 onto sorted MockBridge.FAULTS (budget_ignored..worktype_disabled_once; dll_stale/settings_drift = the 2 ABORTs; pit_no_fall/worktype_disabled_once clean by design). No stale-DLL question arises: none of these rows touched the game.
- 3: O9 is the only real failure, and it is a stale ASSERTION: 45d720097 (owner ruling 2026-10-06) changed both the C# kernel and the oracle to pay scarce supply by cell index, but O9 still demanded 'earlier-dug gets the odd level'. Fixed O9 to expect lower-index inlet gets 3; O9 PASS, claim walk still red.
- 4: O-LIVE-NEG also red: fault dll_stale now aborts after folding L2 red (by design since d07fd3b37) and the selftest only tolerated settings_drift. Allowed dll_stale too. Offline tier O1-O10, O-NEG, O-LIVE-NEG all PASS.
- 5: FlowWorks selftests 12/12 PASS (incl. kernel_oracle: C# kernel == oracle). No C# change, no rebuild needed. Corrected the false 'real findings' line in belt_acceptance_resume_20261008.md. OWED: a real live run, python.exe northstar/validation_v2.py --live --fresh-map, has never been made at the current mod hash (newest live result 20261007T140351).
