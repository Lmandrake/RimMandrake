## spec
🔴 **DECIDE ruled 2026-08-22: "Blackstar Company" names ONE mercenary outfit.** It must
never be the word a player reads over a second pirate faction. The ruling and its full
reasoning are written into `design/Jawa/worldbuilding/FACTION_SPEC.md` entry **10**.

## what is actually owed — and it is NOT one patch per child
The Blackstar reskin patches `FactionDef[defName="Pirate"]`, which is also declared
`Name="PirateBandBase"`, the abstract root every other pirate def inherits from
(`Core/Defs/FactionDefs/Factions_Misc.xml:510`). PatchOperations run before inheritance
resolves, so `fixedName` leaks to **six** defs — `Pirate`, `CannibalPirate`,
`PirateYttakin`, `PirateWaster`, `DV_PirateKeshig`, `AG_XenohumanPirates`.

✅ **The containment already exists.** `src/Jawa/JawaFactionSlate/Patches/OnlyOurFactions.xml`
zeroes `startingCountAtWorldCreation` on **all five** siblings. If it holds, no leaked
name ever reaches a player and nothing needs building.

🔴 **But the 2026-08-21 generated world showed FOUR factions named "Blackstar Company"**,
three of them carrying separate `the Contract` ideos, one of which had `AnimalPersonhood`
and `Raider` that nobody authored. **That contradicts the zeroing and nobody has explained
it.** That explanation is the deliverable.

## verify
1. Read `OnlyOurFactions.xml` against the resolved dump: is the zeroing reaching all five
   siblings post-inheritance, or is an inherited `startingCountAtWorldCreation` winning?
2. `PirateWaster` declares `replacesFaction: Pirate` (`PRE_WORLDGEN_GATE.md` row 2) —
   check whether `replacesFaction` bypasses a zeroed count.
3. Generate a throwaway world and `jawa/list_factions`: **exactly one** faction may read
   `Blackstar Company`, and **exactly one** may read `Galactic Empire`.

## criteria
A generated world in which `Blackstar Company` and `Galactic Empire` each name exactly
one faction — or, if the zeroing provably cannot hold, the reskin moved onto a def
nothing inherits from, with `permanentEnemy true` preserved (R12).

## scope note from DECIDE
⛔ Do not move the reskin off `Pirate` as a first move. That is the expensive answer and
it is only correct if step 1 or 2 proves the cheap one is broken.


---

## 🔴 CORRECTION — BUILD, 2026-08-23, against capture `2026-08-23T07-12-04Z`

**The leak is real; verify step 2 names a field that does not exist.**

⛔ *"`PirateWaster` declares `replacesFaction: Pirate`"* — measured, it does **not**. Only
five FactionDefs in the whole load set carry `replacesFaction` (`TribeRoughNeanderthal`,
`TribeSavageImpid`, `OutlanderRoughPig`, `VRESaurids_OutlanderRoughSaurid`, `BS_LittlePeople`)
and none of them is a pirate. A check written against that step fails on a correct setup.

✅ **The defect itself stands:** six FactionDefs still wear `fixedName: "Blackstar Company"` —
`Pirate`, `CannibalPirate`, `PirateYttakin`, `PirateWaster`, `DV_PirateKeshig`,
`AG_XenohumanPirates`. The five siblings do read `startingCountAtWorldCreation 0`.

## Read live 2026-08-24 — no leak visible, and this world CANNOT show one
`jawa/list_factions`: exactly one faction is named **"Blackstar Company"** (`Pirate`, 4 settlements).
⚠️ **That is not evidence the fixedName does not leak.** This world generated only ONE faction from
`PirateBandBase`, so a leak would have nothing to leak onto. The test needs a world with two or more
pirate-base factions, or a def-level check of what inherits the `fixedName`.
