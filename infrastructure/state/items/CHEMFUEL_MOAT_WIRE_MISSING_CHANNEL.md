# CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL

FlowWorks: chemfuel/astrofuel/propane have no canalFluid, fuel moats impossible

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C9-F1** CONFIRMED MEDIUM — Chemfuel (and adopted astrofuel) have no canalFluid though detonating canal fluids exist: fuel cannot be pumped into a moat. Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml: RM_Liquid_Chemfuel (:458) and propane rows carry no <canalFluid>; RM_Fluid_Chemfuel/RM_Fluid_Astrofuel exist in Defs/Canals/FluidDefs/FlowWorks_PitFluids.xml:67,84. A liquid with no channel form spills (RM_LiquidSpill). Defense-spine gap (fire trap moat).

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
