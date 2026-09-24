# DUPLICATE_CANON_DEFNAME_PAIRS_1 — Desktop forensic (donor vs RSW_ port), 2026-09-23

Forensic read-only pass for BENCH, run on the Desktop (the Mac could not read donor
defs). No writes made anywhere except this file. All numbers below are MEASURED by
direct file read unless marked UNMEASURED.

Donor mod: `Mlie.StarWarsAnimalCollection` (packageId case as shipped;
`mlie.starwarsanimalcollection` lowercase as referenced in our XML), Steam Workshop
folder `3497316713`, defs at
`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3497316713/1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml`
(31,962 lines).

## 0. Donor mod location and activation

- Donor folder confirmed: `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3497316713/`
  (not under the `Mods/` common folder — it's a raw Workshop subscription, About.xml
  `<packageId>Mlie.StarWarsAnimalCollection</packageId>`).
- **ACTIVE — MEASURED.** Parsed (not grepped)
  `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml`
  with `xml.etree.ElementTree`: 623 total `activeMods`, `mlie.starwarsanimalcollection`
  is present verbatim.

## 1. gizka

**Donor**: `Races_Animal_SW.xml:2156` (ThingDef `Gizka`), `:2276` (PawnKindDef `Gizka`).
**Ours**: `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Gizka.xml:45` (ThingDef),
`:165` (PawnKindDef).

| field | donor `Gizka` | ours `RSW_Gizka` |
|---|---|---|
| label | gizka | gizka |
| description (120c) | "Whatever their native world, their extraordinary reproduction rate led to a fair amount of gizka on many wor" | identical text |
| baseBodySize | 0.18 | 0.18 |
| baseHealthScale | 0.4 | 0.4 |
| MoveSpeed | 3.0 | 3.0 |
| Wildness | 0.5 | 0.5 |
| foodType | OmnivoreRoughAnimal, OvivoreAnimal, AnimalProduct | identical |
| trainability | unset (default) | unset (default) |
| leatherDef / specificMeatDef | `Leather_Saurian` / `Saurian_Meat` (donor's own) | `RSW_Leather_Saurian` / `RSW_Saurian_Meat` (our renamed copies) |
| combatPower | 40 | 40 |
| lifeStages (PawnKindDef) | 3 | 3 |
| texPath | `swanimals/Gizka/Gizka` (+ `GizkaW` alt) | **same string**: `swanimals/Gizka/Gizka` (+ `GizkaW` alt, unmodified) |
| modExtension | none | none |

**Verdict: SAME CREATURE.** Description, statBases, tools, comps and race block are
byte-identical between the donor def and ours; only defName and the leather/meat/egg/
sound cross-references were renamed to our RSW_ resource copies. Our own file header
(`RSW_Gizka.xml:1-42`) says this outright: "Geometry/stats/comps copied verbatim."
texPath is the literal same string, so both defs render the identical sprite
(whichever mod's art wins by load order) — not two different-looking creatures.

## 2. kreetle

**Donor**: `Races_Animal_SW.xml:16804` (ThingDef), `:16918` (PawnKindDef).
**Ours**: `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Kreetle.xml:47` (ThingDef),
`:161` (PawnKindDef).

| field | donor `Kreetle` | ours `RSW_Kreetle` |
|---|---|---|
| label | kreetle | kreetle |
| description (120c) | "Kreetle were a fast breeding arthropod native to the planet Tatooine. They were was often found in cities, h" | identical text |
| baseBodySize | 0.2 | 0.2 |
| baseHealthScale | 0.4 | 0.4 |
| MoveSpeed | 3.5 | 3.5 |
| Wildness | 0.1 | 0.1 |
| foodType | OmnivoreRoughAnimal, OvivoreAnimal, AnimalProduct | identical |
| trainability | None | None |
| leatherDef / meat | `Leather_Insectine` / `useMeatFrom Megaspider` (vanilla, unrenamed) | `RSW_Leather_Insectine` / `useMeatFrom Megaspider` (same vanilla ref) |
| combatPower | 20 | 20 |
| lifeStages | 3 (incl. "kreetle maggot" juvenile) | 3, identical labels |
| texPath | `swanimals/Kreetle/Kreetle*` | same string |
| modExtension | none (comps: CanBeDormant/WakeUpDormant, both vanilla Core classes) | identical comps |

**Verdict: SAME CREATURE.** Identical verbatim match, same pattern as gizka.

## 3. nuna

**Donor**: `Races_Animal_SW.xml:21182` (ThingDef), `:21315` (PawnKindDef).
**Ours**: `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Nuna.xml:25` (ThingDef),
`:158` (PawnKindDef).

| field | donor `Nuna` | ours `RSW_Nuna` |
|---|---|---|
| label | nuna | nuna |
| description (120c) | "Nuna (commonly called 'swamp turkeys'), were reptavian gamebirds native to the planet Naboo. Nuna were dimin" | identical text |
| baseBodySize | 0.6 | 0.6 |
| baseHealthScale | 0.6 | 0.6 |
| MoveSpeed | 3 | 3 |
| Wildness | 0.2 | 0.2 |
| foodType | VegetarianRoughAnimal | identical |
| trainability | None | None |
| leatherDef / specificMeatDef | `Leather_Reptavian` / `Reptavian_Meat` | `RSW_Leather_Reptavian` / `RSW_Reptavian_Meat` |
| combatPower | 50 | 50 |
| lifeStages | 3 | 3, identical labels (nuna tom/hen, chick) |
| texPath | `swanimals/Nuna/Nuna_{f,m}` | same string |
| modExtension | `PathfindingFramework.MovementExtension` (MayRequire `pathfinding.framework`) | **kept verbatim**, same MayRequire gate |

**Verdict: SAME CREATURE by content — but flagged UNCERTAIN at the policy level.**
The ThingDef bodies are byte-identical (same pattern as the other three). However,
the closed item `STARWARS_DONOR_SUNSET_1` records an owner ruling (question card,
2026-09-02): *"Nuna collision: port Mlie's under a NEW name and keep both — Mlie's
version becomes a distinct species alongside vanilla Core's Nuna."* That ruling's
stated premise is a **vanilla Core defName collision**.

⚠️ **That premise does not check out on this Desktop.** A case-insensitive full-text
search for `nuna` across every `Defs/` tree under
`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/{Core,Biotech,Ideology,Royalty,Anomaly,Odyssey}`
returns **zero hits** — there is no vanilla-shipped def named `Nuna` anywhere in the
base game or its five DLCs. The bare `Nuna` wired into our biomes is the donor mod's
own def (the same file read above), not a vanilla creature. So the "distinct species
alongside vanilla Core's Nuna" framing that justified keeping both defNames appears
to rest on a false premise — this is a finding for BENCH/owner to weigh, not something
this forensic pass resolves or edits.

## 4. worrt

**Donor**: `Races_Animal_SW.xml:30760` (ThingDef), `:30881` (PawnKindDef).
**Ours**: `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Worrt.xml:30` (ThingDef),
`:153` (PawnKindDef).

| field | donor `Worrt` | ours `RSW_Worrt` |
|---|---|---|
| label | worrt | worrt |
| description (120c) | "The Worrt was an amphibious creature native to the planet Tatooine, though they could also be found on other" | identical text |
| baseBodySize | 0.6 | 0.6 |
| baseHealthScale | 0.6 | 0.6 |
| MoveSpeed | 2.5 | 2.5 |
| Wildness | 0.75 | 0.75 |
| foodType | CarnivoreAnimal, OmnivoreAnimal | identical |
| trainability | None | None |
| leatherDef / specificMeatDef | `Leather_Insectile` / `Gorg_Meat` | `RSW_Leather_Insectile` / `RSW_Gorg_Meat` |
| combatPower | 40 | 40 |
| lifeStages | 3 (incl. "worrtling") | 3, identical labels |
| texPath | `swanimals/Worrt/Worrt*`, 3 alt variants A/B/C + swimming | same strings, all 3 alt variants preserved |
| modExtension | none | none |

**Verdict: SAME CREATURE.** Identical verbatim match, same pattern as gizka/kreetle.

## 5. Biome wiring per defName (measured by reading each file, not grep -c)

Two BiomeDef "generations" exist for Greentide and Pyrelands right now: `RUT_Greentide`
/ (no `RUT_Pyrelands` exists) are the **live, tile-holding** defs; `RM_Greentide`
(`src/RimMandrake/Greentide/...`) and `RM_Pyrelands`
(`src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml`) are the **self-contained
mod** defs being prepped via `WildAnimals_Greentide.xml` / `WildAnimals_Pyrelands.xml`
patches for the future repaint (per `BIOME_PAINT_ONCE_AT_THE_END_1` — whether these
RM_ defs currently carry live tiles is out of scope for this pass and not chased).

| animal | donor defName wired in (live `RUT_*` BiomeDefs) | `RSW_` port wired in |
|---|---|---|
| gizka | `RUT_AridShrubland` (0.4), `RUT_Greentide` (1.0) | `RUT_Desert` (0.1), `RUT_ExtremeDesert` (0.01), `RM_Pyrelands` (1.0, via `WildAnimals_Pyrelands.xml:179`), `RM_Greentide` (1.0, via `WildAnimals_Greentide.xml:145`) |
| kreetle | `RUT_AridShrubland` (0.8), `RUT_Miasma` (1.0), `RUT_Webwork` (0.8) | `RUT_Desert` (1.3), `RUT_ExtremeDesert` (0.2) |
| nuna | `RUT_AridShrubland` (0.4), `RUT_FeverWood` (0.4), `RUT_Greentide` (0.4) | `RUT_Desert` (0.2), `RM_Pyrelands` (0.5, via patch line 175), `RM_Greentide` (0.4, via patch line 154) |
| worrt | `RUT_AridShrubland` (0.4), `RUT_Greentide` (0.7) | `RUT_Desert` (0.2), `RM_Greentide` (0.7, via patch line 148) |

Notes measured while building this table:
- `RUT_Pyrelands` **does not exist as a file** — only `RM_Pyrelands` does. The parent
  item's "Pyrelands" entries for gizka/nuna referred to what is now `RM_Pyrelands`,
  and that def today carries **only** the `RSW_` forms — `WildAnimals_Pyrelands.xml`'s
  own header states the donor's bare `<Gizka>`/`<Nuna>`/etc. rows were already
  repointed to `RSW_` there. **No donor-bare duplicate currently exists on
  `RM_Pyrelands`** — this part of the parent item's table reads as stale.
- `RUT_Greentide.xml`'s own `<wildAnimals>` block (the live-tile-holding def) was
  read in full: it carries **only** the donor bare names for gizka/nuna/worrt (no
  `RSW_` duplicate inside that same file — the lone `RSW_` entry there is
  `RSW_Diggerpede`, an unrelated animal). The `RSW_` counterparts for Greentide's
  gizka/nuna/worrt live on the *separate* `RM_Greentide` def via
  `WildAnimals_Greentide.xml` (dated 2026-09-22, explicitly written because
  `RM_Greentide` will inherit the tiles later). So today, a player standing on a live
  Greentide tile meets only the donor version — the double-cast is between two
  BiomeDefs, one of which holds no tiles yet, not (yet) a same-tile double-meeting.
- `RUT_Desert` / `RUT_ExtremeDesert` carry **only** `RSW_`-prefixed rows for all four
  animals — no donor-bare duplicate inside those two files.
- Despite the RUT_/RM_ split nuance above, the **distinct-BiomeDef counts** in the
  parent item check out when a same-named RUT_/RM_ pair is counted once: gizka 5,
  kreetle 5, nuna 5, worrt 3 — matching `DUPLICATE_CANON_DEFNAME_PAIRS_1` exactly.

## 6. Summary

| animal | verdict | deciding evidence |
|---|---|---|
| gizka | SAME CREATURE | Donor ThingDef/PawnKindDef (`Races_Animal_SW.xml:2156`/`:2276`) byte-identical to `RSW_Gizka.xml:45`/`:165` except renamed cross-refs; same texPath string |
| kreetle | SAME CREATURE | `Races_Animal_SW.xml:16804`/`:16918` byte-identical to `RSW_Kreetle.xml:47`/`:161` |
| nuna | SAME CREATURE (content) / UNCERTAIN at policy level | `Races_Animal_SW.xml:21182`/`:21315` byte-identical to `RSW_Nuna.xml:25`/`:158`; but the owner's "keep both, distinct from vanilla Core's Nuna" ruling cites a vanilla collision that a full-text search of Core+all 5 DLCs' Defs finds **zero** evidence for |
| worrt | SAME CREATURE | `Races_Animal_SW.xml:30760`/`:30881` byte-identical to `RSW_Worrt.xml:30`/`:153` |

Donor mod `mlie.starwarsanimalcollection` is **ACTIVE** in the live `ModsConfig.xml`
(623 activeMods, parsed via `xml.etree`).

`Shiro`/`RSW_ShiroTrap` was not investigated — the task named it explicitly out of
scope.
