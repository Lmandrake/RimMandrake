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
