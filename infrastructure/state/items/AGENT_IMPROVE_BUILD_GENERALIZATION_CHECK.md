# AGENT_IMPROVE_BUILD_GENERALIZATION_CHECK

Design: `design/RimMandrake/daily_agent_improvement_2026-11-02.md` section 4.3. It is the one piece of
AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS left owed (steps 1 to 3, the ramp, tags and change records are built:
`src/RimMandrake/Utils/agent_improve.py`, shas 427c3c7f0e, d0e7cf984a, 48a6e0fbbc, 383b26a722).

Smallest version: `agent_improve.py gencheck <target> v<N>`.
- Sample from the last 14 days of the ledger: 6 closed items whose kind is not one of the change's `source_kinds`, plus 2 of a source kind.
- Each item gets two fresh agents in scratch clones, one per version, writing a plan and a first step only. A blind judge
  picks per pair against what closed the item.
- The result appends to `infrastructure/state/agent_improve/changes/<target>_v<N>.json` as general, narrow or overfit.
- The run is gated on the ramp level: L1 checks every fifth change, L2 checks every change.
- Cost bound: 16 short runs plus 8 judge calls.

It does not run until the ramp reaches L1 (now L0, rate 1.0 over 1 pass), so it is not urgent.
## criteria
A selftest with stub agents covers the harm, gain, narrow and no-gain verdicts. One real check runs on agent/rimworld-modding/v1.
