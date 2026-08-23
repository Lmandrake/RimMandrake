## 🔴 REFUTED 2026-08-23 — all twelve cultures have a faction, and all sixteen kinds are fielded

**The measurement looked only in `src/Jawa/Jawa_Patches/Defs/FactionDefs/` and the four
missing factions are in `src/Jawa/Jawa_Patches/Patches/`.** Eight cultures ride *authored*
`Jawa_*` FactionDefs; the other four ride *existing vanilla* defs, renamed by patch:

| culture | rides | fixedName | settlements on the planet |
|---|---|---|---:|
| `Jawa_Culture_Homestead` | `OutlanderCivil` | Homestead Defense League | **37** — the largest faction on Ash'karr |
| `Jawa_Culture_DeepDesert` | `TribeCivil` | Deep Desert Tribes | 9 |
| `Jawa_Culture_Blackstar` | `Pirate` | Blackstar Company | 4 |
| `Jawa_Culture_Empire` | `Empire` | The Galactic Empire | 3 |

Each patch sets `allowedCultures` to exactly one culture — the right one — in
`HomesteadDefenseLeague.xml`, `DeepDesertTribes.xml`, `BlackstarCompany.xml` and
`GalacticEmpire.xml`, alongside `label`, `description`, `fixedName` and `pawnGroupMakers`.

✅ **The sixteen pawnkinds are NOT homeless.** Every `_Grunt` / `_Heavy` / `_Leader` /
`_Specialist` of all four cultures appears in a `pawnGroupMakers` patch, plus a
`Jawa_Homestead_DesertRanger` the item never counted.

✅ **`Jawa_IndigenousTribes` → `Jawa_Culture_TradeMoot` is confirmed correct**, and it is
distinct from `TribeCivil` → `Jawa_Culture_DeepDesert`. Two tribal factions, two cultures.

🔑 **MEASURED against the world, not just the defs:** `world/ASHKARR_WORLDMAP_settlements.csv`
places **120 settlements across 12 faction defs**, and all four of these are among them.
The planet already fields them.

⚠️ **The lesson, and it is the same one that produced this item:** *a Jawa faction is not
the same thing as a faction in `Defs/FactionDefs/`.* Four of our twelve are vanilla defs
wearing our names. **Any future census of "our factions" must read `Patches/` too**, or it
will report this gap again. The owner's instinct — *"There's only 8 factions? I think
there's a few more..."* — was right, and the answer is **twelve**.

⛔ Do NOT author four new `Jawa_*` FactionDefs. The settlement layer already commits to
the vanilla defNames; new defs would orphan 53 of 120 settlements.

---

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
