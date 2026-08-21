## spec
`PirateWaster_Yield.xml` shipped and deployed 2026-08-21 (`42ad3ec`). It removes
Biotech's `<replacesFaction>Pirate</replacesFaction>` and adds
`<requiredCountAtGameStart>0</requiredCountAtGameStart>` to `PirateWaster`, so vanilla
`Pirate` — which `BlackstarCompany.xml` reskins and which already reads label
**Blackstar Company** — is no longer displaced at worldgen.

BUILD proved the ops MATCH (both 1 hit, 0 errors) and that the pre-state carried the
defect. ⛔ **Offline cannot see a PatchOperation's EFFECT, only that it matches**, so
everything below needs a load.

## verify
On the next load, off a regenerated def dump:
- `PirateWaster.replacesFaction` is **absent**
- `PirateWaster.requiredCountAtGameStart` is **0**
- `Pirate.label` still reads `Blackstar Company` and its
  `settlementGenerationWeight` is unchanged at **0.6**
  ⚠️ `PIRATE_VESSEL_RESTORED_1`'s spec says that weight is 1. Measured on the
  2026-08-21 08:20:20Z dump it is **0.6**. Do not "restore" it to 1.

## criteria
🔴 On the **Configure Factions** screen, before the owner generates the real world:
`Blackstar Company` appears in the DEFAULT list without anyone adding it by hand, and
`waster pirate band` does not appear at all.
🪤 **HOW THIS LIES:** the authored settlement import places Blackstar holdings regardless,
because an import writes settlements directly and never consults
`settlementGenerationWeight`. **A planet with Blackstar holdings is NOT evidence the
faction generates.** Judge it on the Configure Factions screen, or on a world where the
roster import has not run.
