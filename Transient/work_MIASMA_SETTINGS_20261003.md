# MIASMA_SETTINGS_SWITCHES_1 work note (2026-10-03)
- Started. Switches planned: predation, pollination gate, stranded deformation (+chance slider).
## Choices
- plantPredationEnabled: early return in RM_CompPlantPredator.CompTickLong.
- strandedDeformationEnabled + strandedDeformationChance (slider 1-100%, default 25%): the roll lives in the SHARED EnvironmentalHazards
  assembly (off-limits), so RM_MiasmaSettingsApplier sets the chance field on the RM_Miasma BiomeDef's extension via reflection (0 when off).
- pollinationGateEnabled: the gate is a shared Harmony patch keyed on RM_PollinationGateExtension; the Miasma applier detaches that extension
  from RM_Thessamor/RM_Quennath when off and restores it when on. Today the patch that adds the extension is campaign (RUT_Miasma_PollinationGate.xml,
  targets AB_MangroveTree), so the switch is inert until MIASMA_SWARM_COMPOSTER_PORT_1 applies the gate to the mangals; AB_MangroveTree is not touched.
- Applier runs at startup and in Mod.WriteSettings.
## Proof
- Build OK (winbuild Miasma). Miasma/validation.py static PASS; live suite (settings round-trip) written, never run live.
- Criterion "mechanic does not fire in quicktest" UNMEASURED (needs live map).
