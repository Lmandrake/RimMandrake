# WRECKED_DISTILLATION_MODULE_1 — the ship's Distillation system in WreckedMachines

Filed by BENCH, 2026-09-13 (owner, verbatim intent: the crashed ship's
Wrecked Machines "should now include a Distillation system that produces
clean water out of the appropriate sources (e.g. not oil)").
Design: `design/RimMandrake/liquids_framework_design.md` §4/§5.

## spec

A new WreckedMachines module in the existing wreck-tier grammar
(Wrecked→Kludged→Repaired): the ship Distillation system. Input: any liquid
row flagged distillable (water family — salt, fouled, toxic, brine; NOT tar,
oil, chemfuel, slime); output: clean/fresh water at a rate per repair tier.
Reads liquid identity from the registry (LIQUID_REGISTRY_CORE_1), so new rows
opt in by data.

## verify

Quicktest: feed it salt water → fresh out; feed it tar → refuses (visible
message, no output, no crash). Rate differs across repair tiers.

## Watch out

- Follow WreckedMachines' existing module pattern — this is a sibling of the
  modules already there, not a new framework.
- Depends on LIQUID_REGISTRY_CORE_1 for the distillable flag.
