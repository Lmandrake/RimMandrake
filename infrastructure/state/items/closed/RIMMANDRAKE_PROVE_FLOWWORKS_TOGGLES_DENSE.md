# RIMMANDRAKE_PROVE_FLOWWORKS_TOGGLES_DENSE

## spec
Dense live proofs of four FlowWorks toggles that were listed as owed (fallDamageEnabled, liquidCorrosionEnabled,
liquidIgnitionEnabled, superdeepShootingRuleEnabled), plus ladder_required_off, and a fresh S3 re-run of six standing
FAIL/UNMEASURED chains. Built in 13b5f96dbd (`northstar/extensions.py`, mocked in `northstar/selftest_extensions.py`:
PASS on the designed replies, FAIL on each single defect, UNMEASURED on a blind instrument).

- Plan: D:\ClaudeWork\rimmandrake\conductor\proofs_20261112\FlowWorks\plan.md (the defect each row names).
- Inventory and Designer questions: D:\ClaudeWork\rimmandrake\conductor\proofs_20261112\FlowWorks\inventory.md
- Live clauses: infrastructure/state/live_proofs/RIMMANDRAKE_PROVE_FLOWWORKS_TOGGLES_DENSE.txt (A1 pit rules, A2 liquids, A3 re-run), on tier mods__mandrake_rm_flowworks, SteveDesktop lane.

## Watch for
- liquid_ignition_on: vanilla FireUtility refuses terrain with 0 Flammability; if the row FAILs with the source fire
  counted, LiquidIgnition does not light sap terrain (a MOD ticket, not a harness fix). Unproven until the run lands.
- Removed row ladder_required_ladder_lets_out: it duplicated ladder_prison_door.lowered_lets_colonist_out.
- Harness fix: `_fight_expected` crashed on a tuple of hediffs ("fixture fight (%s)" % (hediff,)).
