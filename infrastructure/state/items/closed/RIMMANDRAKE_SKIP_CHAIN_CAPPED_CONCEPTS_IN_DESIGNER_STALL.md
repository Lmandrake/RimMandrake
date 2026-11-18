
## spec

`ops_watch._q_designer` (src/RimMandrake/Utils/ops_watch.py) counts every `status=ready` concept as pending unless
`designer_stage.rejection_parked`. A concept the launcher holds on the per-concept daily chain cap
(`role_launch.chain_ask`: `chain_day["<local day> <concept dir>"] >= chain_max_per_day` and not a forward stage)
is a deliberate hold that already raised `role:<Role>:chain_cap` once; it must not also read as a queue stall.
Exclude it from `plist`, reading the dispatcher state (`RM_DISPATCHER_STATE`/state.json, roles Designer and
DesignerCodex, `chain_day`, `chain_stages_day`) through one shared predicate in role_launch (no second copy of the
cap rule). An unreadable dispatcher state is blind (UNMEASURED), never a calm 0.

Measured 2026-11-16 11:05 PST: Cauldron, FeverWood, Stillsand each at 8 DesignerCodex chains today; stall read
60.7+ min from 17:17Z; cap resets at local midnight.

## verify

Acceptance test (drafted at filing; NOT yet watched failing, the quick run builds nothing; the fixer watches it
fail on the base first): add cases to `src/RimMandrake/Utils/selftest_ops_watch_designer_stall.py`:
1. ready concept, history 90 min old, chain_day count == cap today, its stage already in chain_stages_day -> stalled_min 0.
2. same, count == cap but the stage is NEW today (forward, count < 2*cap) -> still pending (stalled 90).
3. same concept, count == cap but the key is YESTERDAY's day -> pending (stalled 90).
4. state.json unreadable -> queues.designer.stalled_min UNMEASURED, queues.blind 1.
5. existing cases unchanged (rejection_parked, waiting_owner answered).
Command: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_ops_watch_designer_stall.py` -> all PASS.

## criteria

The live alarm stops ringing for a chain-capped concept while role:*:chain_cap stays the one signal for it.
