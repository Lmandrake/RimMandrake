## spec

🔴 **Six FactionDefs all carry `fixedName: "Blackstar Company"`.** Because `fixedName`
overrides the name generator, every pirate faction that generates wears the same name.

```
Pirate               fixedName="Blackstar Company"   requiredCountAtGameStart=1
CannibalPirate       fixedName="Blackstar Company"   requiredCountAtGameStart=0
PirateYttakin        fixedName="Blackstar Company"   requiredCountAtGameStart=1
PirateWaster         fixedName="Blackstar Company"   requiredCountAtGameStart=0
DV_PirateKeshig      fixedName="Blackstar Company"
AG_XenohumanPirates  fixedName="Blackstar Company"
```

⭐ **Only `Pirate` has the matching `label`.** The other five keep their own labels —
`waster pirates`, `Keshig horde`, `Xenohuman pirate gang` — so the def register and the
world disagree about what these factions are called.

### It is not theoretical — it is already in a world

`jawa/faction_name_get` on a world generated 2026-08-23 00:2x:

```
DV_PirateKeshig        stored=Blackstar Company   def=Keshig horde            generated=False
AG_XenohumanPirates    stored=Blackstar Company   def=Xenohuman pirate gang   generated=False
```

Two factions, side by side on one planet, both called Blackstar Company. `PirateYttakin`
has `requiredCountAtGameStart=1` as well, so a third is expected wherever it generates.

🔑 **`generated=False` is why nothing has caught this.** The name-audit tool asks *"is
this faction wearing a dice-picked name?"* — and a `fixedName` collision answers **no**,
correctly, for all six. The tool is not wrong; it is answering a different question.
**Nothing currently checks whether two factions were given the SAME authored name.**

### Where it comes from

`BlackstarCompany.xml` reskins vanilla `Pirate`, and `Pirate.label` reading
`Blackstar Company` is intended — `BLACKSTAR_IN_DEFAULT_LIST_1` exists to keep exactly
that faction in the default list, and it passed on this same load. ⚠️ **The defect is
scope, not intent:** whatever wrote `fixedName` reached five more pirate defs than the
reskin covers. Find the xpath that did it before editing anything by hand — a
`FactionDef[...]` predicate matching on a pirate category would do this, and hand-fixing
the six leaves the patch free to do it again.

⛔ **Do not fix this by clearing all six `fixedName`s.** `Pirate` is supposed to keep
its one. Clearing that one un-does the reskin this project deliberately shipped.

## verify

- At most ONE FactionDef carries `fixedName = "Blackstar Company"`, and it is `Pirate`.
- The other five either carry a `fixedName` matching their own `label` or none at all.
- On a freshly generated world, `jawa/faction_name_get` shows no two factions sharing a
  stored name.

## criteria

A player meeting two pirate bands can tell them apart. And there is a check that
catches a DUPLICATE authored name, not only a generated one — the gap that let six
identical names ship unnoticed.


---

## 🔴 CAUSE FOUND — BUILD, 2026-08-23. It is INHERITANCE, and our patch is innocent.

`BlackstarCompany.xml` writes `fixedName` to exactly one xpath:

    /Defs/FactionDef[defName="Pirate"]     <- one operation, one def

**But `Pirate` is also `PirateBandBase`.** Vanilla declares it with a `Name=` attribute as
well as a `defName`, so it is simultaneously a concrete faction AND the abstract parent every
other pirate inherits from. Measured in the game's own Data tree:

    Ideology/Defs/FactionDefs/Factions_Misc.xml   CannibalPirate    ParentName="PirateBandBase"
    Biotech/Defs/FactionDefs/Factions_Misc.xml    PirateYttakin     ParentName="PirateBandBase"
    Biotech/Defs/FactionDefs/Factions_Misc.xml    PirateWaster      ParentName="PirateBandBase"

⇒ Adding ANY field to `Pirate` adds it to all five children. This is the same inheritance leak
that gave the Junkers Blackstar's `forcedMemes` and a Configure-Factions row they were never
meant to have — **third occurrence of this exact trap.**

## ⛔ TWO OBVIOUS FIXES, BOTH WRONG, both ruled out from the ENGINE SOURCE not by guessing

**1. `<fixedName></fixedName>` on each child to blank it.** Does not work, and is worse than
doing nothing. `Verse/XmlInheritance.RecursiveNodeCopyOverwriteElements` — a child node with
no element children and no text causes the parent's text to be REMOVED, so the resolved value
is the empty string, not null. And `RimWorld/FactionGenerator.cs:149` reads:

    if (factionDef.fixedName != null)
        faction.Name = factionDef.fixedName;

**A null check, not `NullOrEmpty`.** So an empty string still wins and the faction is named
`""`. Five factions called nothing at all is a worse bug than five called Blackstar.

**2. `Inherit="False"` on the field.** Same method handles it, but it only clears CHILD
ELEMENTS of the node it is on — it does not un-inherit a scalar from the parent.

## ⇒ what actually has to happen, and it is NOT BUILD's call

The only mechanisms that work are (a) give each of the five children its own real `fixedName`,
or (b) take `fixedName` off `Pirate` entirely and name the Blackstar Company through a
`factionNameMaker` RulePackDef instead.

(a) needs five faction names. **That is world content — DECIDE's and the owner's, not mine.**
Their current labels are `waster pirates`, `Keshig horde`, `Xenohuman pirate gang`,
`cannibal pirates`, `yttakin pirates`, so the names exist as prose; what does not exist is a
ruling on whether these factions should carry FIXED names at all, or keep generated ones.

(b) is buildable by me in one pass and keeps generated names for the other five, but it
changes how the Blackstar Company itself is named and may not survive a settlement-name check.

🔑 **Escalating rather than choosing.** Both routes are cheap; picking between them is a
naming decision about five factions in the player's world.
