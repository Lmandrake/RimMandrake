# PIRATE_NAMES_FIVE_SYNDICATES_1 — five canon syndicates. BUILD, 2026-08-23

DECIDE's ruling on `BLACKSTAR_NAME_ROUTE_DECISION_1`, which BUILD escalated after proving the
`fixedName` inheritance leak. DECIDE confirmed the namer route and supplied the names.

    Pirate                keeps Blackstar Company    ⛔ unchanged - the only PLACED pirate
    PirateWaster          Nova Blades                pollution-adapted wasters
    PirateYttakin         the Ohnaka Gang            hairy cold-adapted brutes
    CannibalPirate        Crimson Dawn               cannibal ideoligion
    AG_XenohumanPirates   Black Sun                  gene-modified xenohumans
    DV_PirateKeshig       Kanjiklub                  the Keshig xenotype

`src/Jawa/Jawa_Patches/Defs/RulePackDefs/Namer_PirateSyndicates.xml` (new, 5 one-rule packs)
and five ops in `BlackstarCompany.xml`. 0 errors against the full 578-mod load set. Deployed.

## why one-rule RulePackDefs and not fixedName
`Pirate` is ALSO `PirateBandBase` — a concrete faction that is simultaneously the parent every
other pirate inherits from — so a `fixedName` set there reached all six. `factionNameMaker` is
inherited too, **but unlike `fixedName` it can be overridden per child with a real value**,
which is exactly what these five now do.

## the stopgap this removes
On 2026-08-23 I pinned `CannibalPirate` and `AG_XenohumanPirates` to the vanilla
`NamerFactionPirate` so they would not inherit `Jawa_NamerFactionBlackstar`. That was correct
then and is superseded now: both have names of their own, and the two pinning ops are gone.

## the op shape, and why it is doubly conditional
    outer conditional   FactionDef exists at all -> a dropped mod is a SILENT no-op,
                        not a red error every load
    inner conditional   factionNameMaker present -> REPLACE, else ADD
Three of the five ship their own vanilla namer and take the replace branch; two do not and
take the add branch. A single bare Replace would have matched nothing on those two.

## ⚠️ a self-inflicted near-miss worth recording
My first attempt sliced the old block out of the file by searching for substrings and computing
offsets. It cut across a tag boundary and produced **`XML does not parse: mismatched tag`** —
which the validator caught immediately. Restored from git and redone by LINE NUMBER with two
asserts on the boundary lines. ⇒ When editing structured XML by script, anchor on lines and
assert both ends; a substring offset in a file with repeated tags is a coin flip.

## ⛔ what this does NOT settle
Whether these factions appear at all. Measured earlier today: all five have
`startingCountAtWorldCreation 0`, so they place no settlements; three carry
`requiredCountAtGameStart 1` and are created only in worlds generated WITHOUT the Configure
Factions screen — dev quicktests. In the campaign world the player will see one pirate faction,
Blackstar Company. These names are for the faction list in test worlds and for correctness.
