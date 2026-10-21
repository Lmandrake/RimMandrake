# PROPANE_CANAL_WIRE_STILL_NO_FLUID

C9-F1 (Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md) named propane beside chemfuel and astrofuel. Chemfuel and
astrofuel now carry canalFluid (CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL). Propane cannot: there is no RM_Fluid_Propane FluidDef
(generator note in Tools/generate_liquid_suite.py, "same gap as brine"), so a propane tank still spills instead of filling a
cut. Needs: a FluidDef (fill terrains Trace/Half/Brim/Superdeep, fireKind; the propane hard ban says no ignition without a
thermal trigger, which RM_LiquidFire already honours), the generator row, and a look.
