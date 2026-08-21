## spec
Ruling and full mechanism: `infrastructure/state/items/PIRATE_REPLACED_BY_BIOTECH_1.md`
`## ruling`. This item is two PatchOperations.

Biotech's `PirateWaster` declares `<replacesFaction>Pirate</replacesFaction>`
(`Data/Biotech/Defs/FactionDefs/Factions_Misc.xml:576`) and inherits
`requiredCountAtGameStart` **1** from `PirateBandBase`
(`Data/Core/Defs/FactionDefs/Factions_Misc.xml:518`). Between them, vanilla `Pirate` — the
def `BlackstarCompany.xml` reskins — is stripped from the default Configure Factions list
(`Page_CreateWorldParams.cs:83-85`) and skipped outright if no list is configured
(`FactionGenerator.cs:78`).

New file `src/Jawa/Jawa_Patches/Patches/PirateWaster_Yield.xml`. Both ops inside a
`PatchOperationConditional` on `/Defs/FactionDef[defName="PirateWaster"]`, so the file is a
silent no-op without Biotech rather than a wall of red.

1. `PatchOperationRemove` on `/Defs/FactionDef[defName="PirateWaster"]/replacesFaction`
   — ⭐ **PRESENT on the def, so Remove is correct.** This is what returns `Pirate` to the
   default list.
2. `PatchOperationAdd` of `<requiredCountAtGameStart>0</requiredCountAtGameStart>` onto
   `/Defs/FactionDef[defName="PirateWaster"]`
   — ⚠️ **ADD, not Replace.** The def does not write the field; it inherits it. A Replace
   matches nothing and logs a red error. This is what stops `PirateWaster` taking the slot
   it just vacated.

⛔ **Do not touch `Pirate`.** It is correct: weight 1, `requiredCountAtGameStart` 1,
`maxConfigurableAtWorldCreation` 9999, and `BlackstarCompany.xml` already reskins it.
⛔ **Do not extend this to the other five `replacesFaction` declarations.**
`OutlanderRoughPig`, `TribeRoughNeanderthal`, `TribeSavageImpid` and
`VRESaurids_OutlanderRoughSaurid` replace `OutlanderRough` / `TribeRough` / `TribeSavage`,
none of which carries a faction of ours. Measured across all active mods: **`Pirate` is the
only one of our thirteen that is hit.**

## verify
- `validate_patch.py` clean, and each op reports **1** hit, not 0
- off a regenerated def dump: `PirateWaster.replacesFaction` is absent and
  `PirateWaster.requiredCountAtGameStart` is 0
- `Pirate.settlementGenerationWeight` is still 1 and its label still reads
  `Blackstar Company`

## criteria
🔴 **The one that matters, and it must be checked on the Configure Factions screen before
the owner generates the real world:** `Blackstar Company` appears in the DEFAULT faction
list without anyone adding it by hand, and `waster pirate band` does not appear at all.
