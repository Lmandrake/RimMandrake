---
state: built
needs: bridge
---

# CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Raiders at a 4 m sheer ring never fill (RAIDERS_TRENCH A3): raid_trench_proof --direct --depth 8 on 41fb948b5e, 3 AssaultColony gunners stood at the lip in curJob=Wait for 10,000+ ticks while RM_RaiderTrench.ProofDecision for each read 'RM_RaiderFillTrench (131,0,126) line=0/8/8/0'; no square filled, no ladder. The decision exists but JobGiver_RM_CrossTrench (last in the AssaultColony duty) never gets to give it - trace which earlier giver/think node hands out Wait. Evidence src/RimMandrake/FlowWorks/northstar/raid_trench_result_20261022T1015_depth8_belt.json + src/RimMandrake/FlowWorks/northstar/raid_trench_probe_20261022T1015_depth8_belt.txt. Confound to rule out: the island colonists were shot down across the moat by t+4000 (TargetFor then falls back).

Built at `c8eb3b2c8370` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-31: Test pilot (5e90c60679). Root cause, two layers: (1) HARNESS: --direct raids held no shovel (spawn_pawn skips PostProcessSpawnedPawns, so RM_Patch_Raid_Shovels never ran); FillJob null, Choose None, vanilla wander kept them 18+ out. Fixed in the proof (--shovels, read back). (2) MOD tuning: with shovels, one fill level = 6400/(MiningSpeed x 1.7 x 0.5); 4/6 raiders at the 0.1 floor = ~75,000 ticks; run3 (boxed, shipped values) filled nothing before the raid left at t+29,135. run4 --fill-speed 4 f
- 2026-10-31: RULING: answers CAUSEWAY_DECIDE_FILL_PRICE_OUTLASTS_RAID and RAIDER_SHOVELLER_DECIDE_SHOOTERS_STOP_TO_DIG.
- 2026-10-31: TESTPILOT_SAT: 5e90c60679, harness gave no shovels and fill is priced at the MiningSpeed floor; false theory: re-issue loop. See D:\ClaudeWork\rimmandrake\testpilot_causeway\PROGRESS.md

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP` first: another commit may already do it.
