## spec
CHECK, 2026-08-21: `src/Jawa/JawaFactionSlate/Patches/OnlyOurFactions.xml` zeroes
`startingCountAtWorldCreation` **and** `maxConfigurableAtWorldCreation` on 48 FactionDefs.
Four are Section-4 KEEPs in the ratified `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`.

## verify
the owner can restore any Section-4 KEEP at the Configure Factions screen, and the four
named below behave as this ruling says.

## criteria
No row the ratified checklist tells the owner to tick is missing from the screen he ticks it on.

## ruling
🔴 **DECIDE, 2026-08-21. CHECK is right, the conflict is real, and the cause is a false
sentence in the generator's own header.**

### The generator believes something untrue, and that belief is the whole bug

`OnlyOurFactions.xml`'s header states:

> *"`maxConfigurableAtWorldCreation` is only a cap and changes nothing on its own."*

⛔ **False at zero.** `FactionGenerator.ConfigurableFactions` is literally
`from f in DefDatabase<FactionDef>.AllDefs where f.maxConfigurableAtWorldCreation > 0`, and
`Page_CreateWorldParams.cs:70` builds the Configure Factions page by iterating that
enumeration. ⇒ **at 0 the def leaves the enumeration entirely: it is not capped, the row is
deleted, and the owner cannot add it back.**

⚠️ **And `requiredCountAtGameStart` does not save them.** All four carry `= 1`, which looks
like a floor and is not one: `FactionGenerator.InitializeFactions` reads it **only in the
branch where no faction list was configured**. Worldgen through the screen passes
`Current.CreatingWorld.info.factions`, and that branch adds the list verbatim with no
required-count loop at all. ⇒ **a "required" faction that is off the screen is simply
absent.**

### ⇒ FIX ONE: the generator must stop zeroing the second field. This is the ruling.

**Zero `startingCountAtWorldCreation` only. Leave `maxConfigurableAtWorldCreation` alone.**

That is sufficient for the slate's actual purpose — *"only our factions generate by
default"* — and it restores the property the checklist depends on: **anything can be put
back at the screen.** A tick-list whose rows do not exist is not a safeguard, it is a
trap, and this fixes all 48 defs rather than special-casing four.
⚠️ The generator is **not in this repo** (the file says *"Generated 2026-08-17. Do not
hand-edit."*). Whoever holds it makes the change; if it is lost, the file becomes
hand-maintained and the header's false sentence must be deleted either way.

### ⇒ FIX TWO: the KEEP list splits, because the four are not one case

Measured from each def's own 1.6 files:

| def | hidden | settlementGenerationWeight | ruling |
|---|---|---|---|
| `guy762_KotORFaction_RogueDroids` | **true** | — | ✅ **KEEP.** 🔴 The checklist calls it *"quest-critical — antagonist of the KotOR distress call. Never untick."* Hidden ⇒ it holds no settlements and cannot clutter the map. **Zero cost, and dropping it breaks a quest.** |
| `JDSCIS_CIS_Faction` | **true** | — | ✅ **KEEP.** Also hidden, so also free. The CIS is a Star Wars pillar and costs the map nothing |
| `OuterRim_BinaryStarRaiders` | no | **1** | ⛔ **RETIRE from KEEP** |
| `OuterRim_MoistureFarmers` | no | **1** | ⛔ **RETIRE from KEEP** |

🔑 **The discriminator is settlements, not sentiment.** The two hidden factions place
nothing. The other two carry `settlementGenerationWeight 1` and would generate holdings on
a planet whose **72 settlements are already hand-placed for 13 factions** in
`world/ASHKARR_WORLDMAP_settlements.csv`. Letting them place more contradicts the frozen
map, which is the one thing that cannot be fixed afterwards.

⭐ **And `OuterRim_MoistureFarmers` is a duplicate of a role we authored.** The Homestead
Defense League *is* the moisture farmers of this planet — thirteen settlements of them. A
second, unreskinned moisture-farmer faction is the same idea twice, one of them nameless.

✅ **The checklist's own header already permits this:** *"its keep list is transitional
rather than final."* Retiring two is that sentence being used, not overridden.

⇒ Filed as `SLATE_KEEPS_CONFIGURABLE_1` (BUILD, the generator) and
`CHECKLIST_RETIRE_TWO_KEEPS_1` (DECIDE, the checklist edit).
