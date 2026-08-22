## spec

Found 2026-08-22 while answering the owner's *"There's only 8 factions? I think there's a few
more..."* — he was right to doubt the number, and the gap is on our side.

**MEASURED, 2026-08-22, off `src/Jawa/Jawa_Patches/Defs/` and the 578-mod dump
`OFFICIAL-2026-08-21T22-44-59Z`:**

| | |
|---|---|
| `Jawa_*` FactionDefs authored | **8** |
| `Jawa_Culture_*` CultureDefs authored | **12** |
| cultures reached by a Jawa FactionDef's `allowedCultures` | **8** |
| 🔴 cultures with **no** Jawa FactionDef | **4** — `Blackstar` · `DeepDesert` · `Empire` · `Homestead` |
| FactionDefs in the whole stack | 86 |

The eight that resolve, one culture each:
`Jawa_AscendantHelix`→Helix · `Jawa_DeepwaterCompact`→Deepwater ·
`Jawa_FreeDroidEnclaves`→Droid · `Jawa_GeonosianFoundryHive`→Geonosian ·
`Jawa_HuttCartel`→Hutt · `Jawa_Junkers`→Junkers · `Jawa_WildsteamClan`→Wildsteam ·
`Jawa_IndigenousTribes`→**TradeMoot**.

⚠️ **That last pairing is worth a second look on its own.** A faction named *Indigenous
Tribes* carrying the *TradeMoot* culture reads like a copy-paste, not a design. Confirm it is
deliberate before building on it.

🔴 **Each of the four homeless cultures has a full four-role pawnkind roster already authored**
— `Jawa_Blackstar_{Grunt,Heavy,Leader,Specialist}`, and the same for `DeepDesert`, `Empire`,
`Homestead`. **16 PawnKindDefs that no faction can field.** They load clean and never occur;
this is the silent kind of defect, not a red error.

**The plausible-but-unwritten explanation, which is the actual question for DECIDE:** `Empire`
and `Homestead` may be intended to ride Outer Rim's existing `OuterRim_GalacticEmpire` and
`OuterRim_MoistureFarmers` rather than get Jawa factions of their own — both exist in the
stack. ⚠️ **Nothing in our files says so.** If that is the design, write it down and give
those FactionDefs the culture; if it is not, the four need factions. `Blackstar` and
`DeepDesert` have no such candidate either way.

## verify

    grep -c '<defName>Jawa_' src/Jawa/Jawa_Patches/Defs/FactionDefs/*.xml
    then map each FactionDef's <allowedCultures> against the 12 Jawa_Culture_* defNames

**PASS = every authored `Jawa_Culture_*` is named in some FactionDef's `allowedCultures`**, or
is explicitly recorded as deliberately unfactioned with the reason.

## criteria

- [ ] Each of Blackstar, DeepDesert, Empire, Homestead either gains a faction or is recorded
      as riding a named existing one.
- [ ] The `Jawa_IndigenousTribes` → `Jawa_Culture_TradeMoot` pairing is confirmed or corrected.
- [ ] No `Jawa_*` PawnKindDef is left with no faction that can field it.

## watch out

- ⛔ **This is a WORLDGEN-time roster.** The world is hand-made once and frozen — a faction
  absent when the owner builds it is absent from every player's game forever. Fix before the
  build, not after.
- `src/Jawa/JawaFactionSlate/Patches/OnlyOurFactions.xml` zeroes
  `startingCountAtWorldCreation` on 48 FactionDefs. A new faction that is not exempted there
  will not appear in the DEFAULT world list even once it exists.
- ⚠️ Do **not** zero `maxConfigurableAtWorldCreation` to control this — at 0 the row is
  deleted from the Configure Factions page entirely, not capped, and the owner cannot add it
  back at the screen. That header warning is already in the slate file and is load-bearing.
