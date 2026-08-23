# Blackstar naming, and the Empire colour split — BUILD, 2026-08-23

## 1. the owner's faction question, answered by measurement

**Owner:** *"these 'other factions' shouldn't even be in our scenario, right? We only support
our chosen ones I really hope..."*

✅ **On the planet, yes.** `world/ASHKARR_WORLDMAP_settlements.csv`, 120 settlements across
**12 factions, every one ours**: OutlanderCivil 37 (Homestead), Hutt 19, Free Droid 12,
TribeCivil 9 (Deep Desert), Junkers 8, Helix 7, Trade Moot 7, Geonosian 5, Deepwater 5,
Pirate 4 (Blackstar), Wildsteam 4, Empire 3. **0 non-ours factions place settlements.**
`JawaFactionSlate` is active at 575/578 and suppresses 37.

🔴 **I nearly reported the opposite.** My first query read `requiredCountAtGameStart` and
found 34 factions at 1, which looked like 26 foreign factions forced into every world. That
is the WRONG FIELD and the slate's own header says so: *"requiredCountAtGameStart is not a
safety net. FactionGenerator.InitializeFactions reads it ONLY where no faction list was
configured; worldgen through the screen passes Current.CreatingWorld.info.factions and adds
that list verbatim."* The deciding field is `startingCountAtWorldCreation`.

⇒ The three phantom pirates that DO get created (`PirateYttakin`, `DV_PirateKeshig`,
`AG_XenohumanPirates`, all `required=1`) appear only in worlds generated WITHOUT the screen —
dev quicktests — and place no settlements even there. That is exactly where the original
`faction_name_get` evidence came from.

## 2. the fix: fixedName -> factionNameMaker

`fixedName` was unusable because `Pirate` is also `PirateBandBase`, the parent of every other
pirate. `factionNameMaker` is inherited too, **but unlike fixedName it can be overridden per
child with a real value** — and three of the five already do.

    Pirate                 NamerFactionPirate            -> Jawa_NamerFactionBlackstar
    PirateYttakin          NamerFactionPirateYttakin     already its own, untouched
    PirateWaster           NamerFactionPirateWaster      already its own, untouched
    DV_PirateKeshig        DV_NamerFactionPirateKeshig   already its own, untouched
    CannibalPirate         NamerFactionPirate            PINNED to vanilla explicitly
    AG_XenohumanPirates    NamerFactionPirate            PINNED to vanilla explicitly

⚠️ **Those last two are the part that is easy to miss.** They inherit rather than override,
so without pinning them the bug would have survived its own fix in a smaller form. Both keep
generated pirate names.

`Jawa_NamerFactionBlackstar` is a one-rule RulePackDef — a fixed name in everything but
mechanism, and the mechanism is the point because it is overridable.

## 3. the Empire colour split, using the engine's own sentinel

**Owner:** *"make the stormtrooper armor not colorable (fixed at white) and make the favored
color the dark grey-olive or near black for everything else."*

Done without removing a comp, because `PawnApparelGenerator.cs:828` reads:

    if (pawn.kindDef.apparelColor != Color.white)
        apparel.SetColor(pawn.kindDef.apparelColor, reportFailure: false);

**Pure white is the engine's own DO-NOT-TINT sentinel.**

    Jawa_Empire_Grunt        (250,250,250) -> (255,255,255)   tinting SKIPPED entirely
    Jawa_Empire_Heavy        (250,250,250) -> (86,90,78)      dark grey-olive
    Jawa_Empire_Specialist   (250,250,250) -> (86,90,78)      dark grey-olive
    Jawa_Empire_Leader       (250,250,250) -> (42,44,40)      near-black

⚠️ **(250,250,250) is NOT Color.white and therefore DID tint** — the armour was being dyed
almost-white over a texture that was already white. Now the plate keeps its own art, which is
what "not colorable" actually means here.
