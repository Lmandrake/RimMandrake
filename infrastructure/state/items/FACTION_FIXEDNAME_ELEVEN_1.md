## spec
Ruling and reasoning: `items/FACTION_FIXEDNAME_DOCTRINE_1.md` `## ruling`. This item is the
eleven edits.

Add `<fixedName>` to every faction below. **The string is the def's own `<label>`,
verbatim** — verified against the authored `faction` column of
`world/ASHKARR_WORLDMAP_settlements.csv`, which agrees with all twelve labels exactly.

**Eight are our own defs** in `src/Jawa/Jawa_Patches/Defs/FactionDefs/` — edit the def, do
not write a patch:

| file | `fixedName` |
|---|---|
| `JawaAscendantHelix.xml` | `Ascendant Helix` |
| `JawaDeepwaterCompact.xml` | `Deepwater Compact` |
| `JawaFreeDroidEnclaves.xml` | `Free Droid Enclaves` |
| `JawaGeonosianFoundryHive.xml` | `Geonosian Foundry Hive` |
| `JawaHuttCartel.xml` | `Hutt Cartel` |
| `JawaJunkers.xml` | ⭐ `the Junkers` — **lower-case article, deliberate.** Do not tidy it |
| `JawaTribes.xml` | `Jawa Trade Moot` |
| `JawaWildsteamClan.xml` | `Wildsteam Clan` |

**Three are reskins of other people's defs** — these go in their existing patch files in
`src/Jawa/Jawa_Patches/Patches/`, inside the `PatchOperationConditional` that is already
there:

| file | target | `fixedName` |
|---|---|---|
| `HomesteadDefenseLeague.xml` | `OutlanderCivil` | `Homestead Defense League` |
| `DeepDesertTribes.xml` | `TribeCivil` | `Deep Desert Tribes` |
| `BlackstarCompany.xml` | `Pirate` | `Blackstar Company` |

⚠️ **`fixedName` is an ADD, not a Replace, on all three.** No vanilla `FactionDef` writes
the node — `Empire` did not either, which is why `GalacticEmpire.xml:100` is a
`PatchOperationAdd` and says so. **A `Replace` matches nothing and logs a red error.**

⛔ **Do not patch `factionNameMaker` away** on any of the eleven. `fixedName` overrides it
for the faction itself; the namer is still what names that faction's SETTLEMENTS
(`FACTION_SPEC.md:124`).
⛔ **`Empire` already has one** (`GalacticEmpire.xml:102`) — leave it.
⛔ **`Mechanoid` is not on this list.** Hidden, no settlements, never named to the player.

## verify
- `grep -rc "<fixedName>" src/Jawa/Jawa_Patches/` totals **12** across the twelve files
- `validate_patch.py` clean on the three patch files, and each new op reports **1** hit
- ⭐ `Jawa_Junkers` reads `the Junkers` with a lower-case `t` — this is the one the fix
  exists to protect, because `def.LabelCap` would otherwise render it *"The Junkers"*
- no `factionNameMaker` node was removed anywhere

## criteria
A freshly generated world names all twelve factions correctly with no repair step, and the
Junkers are not capitalised.
