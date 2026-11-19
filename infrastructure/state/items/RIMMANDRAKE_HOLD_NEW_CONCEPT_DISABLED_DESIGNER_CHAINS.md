# RIMMANDRAKE_HOLD_NEW_CONCEPT_DISABLED_DESIGNER_CHAINS

## spec
FINDING (measured 2026-11-19, bench clone at 03252bb8bc, while readying WreckedMachines' admission,
`RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST`): a newly initialised concept is chained into a Designer run
although the Designer role reads `"enabled": false` in `dispatcher_schedule.json`.

- `role_launch.decide_roles` runs `chain_sweep` (l.1640) BEFORE the enabled check, whenever `chain_stages` is true and
  the role's `off_file` (`D:\ClaudeWork\rimmandrake\designer\DESIGNER_OFF`) is absent. It is absent today.
- `chain_sweep` asks a run for any concept `ready` for more than CHAIN_SWEEP_GRACE_S (600 s) that is not owner-held.
- The enabled check (l.1647, `if not role.get("enabled") and not req`) lets a pending request through, so the asked
  run launches on the role's schedule model (opus).
- A mod newly seeded reads ON in `./pipe show` (WreckedMachines reads ON today, "no mod in the pipeline"). So
  `designer_stage.py init` on a new concept, before `./pipe off <Mod>`, gives an opus Designer run about 10 minutes
  later, whatever the role switch says.

Probe (read-only, in-memory state, nothing launched):
`D:\ClaudeWork\rimmandrake\helpers\wm_admit_20261119\probe_sweep.py`: a WreckedMachines concept `ready` for 1 h,
unheld, Designer disabled: 1 run asked (`chained_from: orphan-sweep`), and the disabled gate passes.
Control `probe_sweep_off.py`: the same concept held (`mod_owner_hold.held` patched, which `pipe off` feeds through
`off_mods`): 0 runs asked. Outputs are in `probe_sweep.txt` and `probe_sweep_off.txt` in the same folder.

Fix, to choose and land (the smallest one that holds):
(a) a mod's first appearance in the control store reads OFF until a `./pipe on` that cites a READY readiness list
    (§No mod runs forward on a broken pipeline already requires the list); or
(b) `chain_sweep` (orphan sweep only, not a harvest chain or a hand run-now) skips a role that is not enabled.
Until one lands, the admission act sequence puts `./pipe off <Mod>` before `designer_stage.py init`.

## criteria
A concept initialised for a mod that has no READY readiness list is never chained into a Designer run by the orphan
sweep, whatever the Designer role's `enabled` reads.

## verify
Acceptance test: a selftest in `selftest_role_launch.py` that builds the probe's case (a new concept `ready` past the
grace period, the mod unknown to the control store, Designer disabled) and asserts no run is asked. Watch it fail on
03252bb8bc, where it asks 1 run.
