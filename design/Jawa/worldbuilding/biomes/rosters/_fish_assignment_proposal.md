# FISH_BY_BIOME_1 — merged fishTypes proposal, every water, one ruling each

_FISH_BY_BIOME_1 design synthesis, 2026-09-09. This doc **PROPOSES** — it writes
nothing into `rosters/*.json`, nothing into `src/`. Underscore prefix keeps it out
of the roster validator. Sources: `_fish_candidates.json` (87 fish ThingDefs,
MEASURED, dump 2026-09-09T01-54-07Z), each roster's `fish` field (rulings restated
verbatim-in-substance below; the no-fish rulings are FINAL and are not reopened
here), the sand-fishing customs (commit `9f8bc41f`:
`src/RimUtinni/UtinniPatches/Patches/SandFishing_CrackedLands.xml`,
`src/RimStarWars/SWBestiary/` RSW_DuneCrawler/RSW_SandStalker/RSW_GlassPearl/
RSW_RareSandCatches, `src/RimMandrake/ManyWaters/Defs/TerrainDefs/RM_DeepSand.xml`),
and the weeping-stones patch already written under this item
(`src/RimUtinni/UtinniPatches/Patches/BiomeFishTypes_Ashkarr.xml`, validated,
NOT deployed)._

**Engine axes (MEASURED, `_fish_candidates.json` `mechanics`):** the only binding is
`BiomeDef.fishTypes` — four buckets, `freshwater_Common` / `freshwater_Uncommon` /
`saltwater_Common` / `saltwater_Uncommon` (`{defName: weight}`), plus
`rareCatchesSetMaker` (a ThingSetMakerDef) and `maxFishPopulation`. Fresh vs salt is
chosen per-cell by the **TerrainDef's** `waterBodyType`; Common vs Uncommon is the
rarity tier. There is **no per-terrain species scoping inside a biome** — every
freshwater cell in a biome draws from the same two freshwater buckets. Campaign
water-kinds chemistry (milk, propane, red water, brine) has no engine hook; it is
flavor over the fresh/salt axis. ⚑ marks an **invented rule** (mine, this doc), not
a measured fact or an existing ruling.

Legend: **RULED** = the roster ruling stands, restated, nothing to decide.
**PROPOSED** = the species/bucket contents below are this doc's proposal for the
owner to ratify. donor = existing mod fish def from the census; custom = the other
window's new RSW/RM defs (commit `9f8bc41f`).

## 1. The waters with fish — full rows

| water | status | fishTypes contents (all freshwater; no water below is salt-bodied) | donor / custom | rare catches | why |
|---|---|---|---|---|---|
| **weeping_stones** true pools (`ZBiome_DesertOasis`) | RULED yes-fish; species **PROPOSED** (patch written, undeployed) | `freshwater_Common`: swfish_Burra, swfish_Daggert, swfish_Nyork, swfish_See (1 each). `freshwater_Uncommon`: VCEF_FrigidSwimmer, VCEF_Slimefish, VCEF_Spinyfish, VCEF_OcularFish (1 each) — **Q2 asks whether these four stay** | all donor (SW Animal Collection + Alpha Biomes' VCEF set) | donor def's existing maker untouched | sacred truce pools, fresh, standing; SW-invented names clear recognizability; no pollution/ambush flavor (sheet §6/§10 bans). Replaces the donor def's Earth-named defaults (Tilapia/Piranha…) on the fresh buckets only |
| **the_cracked_lands** — canyon no-truce water (27 tiles) **+** RM_DeepSand pools (`ZBiome_Badlands`) | RULED yes-fish; **MERGED PROPOSED** — see §2 | `freshwater_Common`: RSW_DuneCrawler (1). `freshwater_Uncommon`: BMT_Rocktooth (1), BMT_Boneblade (1) | custom (DuneCrawler) + donor (Biomes! Caverns BMT pair) | **RSW_RareSandCatches** (custom): RSW_GlassPearl 1–3, RSW_SandStalker corpse — "you caught what ate one" | one biome def serves both waters and the engine cannot split them (§2); predator-toned BMT names fit the planet's one lethal water; maxFishPopulation 90 (committed first-pass cut from 360) stands |
| **the_greentide** living river reach (`BiomeCypreJungle` / `RUT_Greentide` — live def unresolved) | RULED yes-fish; species **PROPOSED** (no patch exists; roster's "already assigned" claim was disproven — item file, Fable pass) | `freshwater_Common`: RSW_Mee (0.4). `freshwater_Uncommon`: RSW_Faa (0.3), RSW_Laa (0.3) — the roster's own three species and weights, moved into the engine's real buckets | custom-tier renames of swfish_ donors (RSW_Mee's donor row unresolved — NAMING_SCHEME_EXECUTION_1 flag) | none proposed | roster: scalefish shoals on the clean-to-living reaches only. ⚑ the reach grading has no engine hook — fishTypes is biome-wide; "living reach only" ships as map authoring (where water terrain is painted) + flavor. Blocked on: which of the two near-duplicate defs is the world-tile-assigned Greentide |
| **the_miasma** nursery channels | **RULED** — fauna channel, not fishTypes | none — RSW_Mee/Faa/Laa (+RSW_SiltLamprey) are `wildAnimals` on `AB_MiasmicMangrove` (`BiomeCast_Ashkarr.xml`, wired) | custom-tier | none | roster: the fish ARE the nursery, rostered as fauna; the adults belong to the Grey Sea, which is ruled no-fish. No fishing table proposed — netting the nursery would be the Grey Sea fishery the rulings forbid. Q3 covers the Greentide/Miasma species overlap |
| **the_twilight_deep** sub-roof shoals | **RULED** — deferred, new-def gap stands | none now; the roof-water shoal ("the only ordinary fishing on the planet", §7) rides the deferred diving-mods layer | future: bespoke silver-shoal new def (no census row passes recognizability AND has measured schooling); RSW_ColoClawFish reserved as the apex body | future | no live BiomeDef work until diving mods land; non-blocking |

## 2. The Cracked Lands merged ruling (the reconcile the item required)

**The collision:** the census proposed BMT_Rocktooth/BMT_Boneblade (+ VCEF
secondaries) for the canyon water; the other window's committed
`SandFishing_CrackedLands.xml` already sets `freshwater_Common` = RSW_DuneCrawler
alone, `freshwater_Uncommon` = **deliberately empty**, rare catches =
RSW_RareSandCatches, maxFishPopulation 90 — on the **same buckets**, because
`RM_DeepSand` declares `waterBodyType Freshwater` and the canyon water is fresh
too. One biome, one freshwater table, two waters. The engine offers no way to give
the deep-sand pools and the slot-canyon water different species.

**Merged proposal (one ruling):** keep the committed patch and **fill its empty
`freshwater_Uncommon` bucket with BMT_Rocktooth (1) + BMT_Boneblade (1)** — one
edit to one committed file. Common catch everywhere in the biome is the dune
crawler (armored, never fish-shaped); the uncommon line pulls a canyon predator;
the rare table stays the sand family's (glass pearl / stalker corpse).

**What loses:**
- the committed patch's "deliberately empty Uncommon / small family" decision —
  overridden; the bucket now carries the canyon water's species;
- the census's VCEF secondaries (VCEF_Spiderfish, VCEF_ShadowFry) — dropped
  entirely, three species is enough for one biome;
- strict per-water realism — a line dropped in a canyon pool can pull a dune
  crawler and a deep-sand line a Rocktooth. ⚑ Accepted as slop: in-lore, the
  canyon floors and the sand pools are one connected under-ground water/sand
  system. (The alternative — repainting canyon water as salt-bodied terrain to
  use the salt buckets — contradicts the census's fresh-water chemistry and is
  not proposed.)
- Unchanged, restated: the ExtremeDesert siting conflict (dune sea §6 fauna ban
  vs deep desert) stays an open follow-up exactly as the committed file flags it;
  Cracked Lands remains the family's only wired biome.

## 3. No-fish waters — rulings FINAL, restated (nothing reopened)

All RULED, list empty, chemistry as cited by each roster:

| water | why (roster ruling, compressed) |
|---|---|
| the_grey_sea — surface AND Grey Deep (covers terminator_sea/the_grey_deep sheets) | saturated brine, monoculture, planetary no-schools ban; three-resident cap; "its water is a chemistry, not a fishery"; no analogs owed |
| the_twilight_sea — surface | same brine + no-schools ban; the shoals exist only below the mat-roof (§1 row 5) |
| the_propane_lakes | liquid propane at ~−79 °C; the sea's life is the propane-native exotics — CREATURES owed as new defs, never fishTypes |
| the_contagion red pools | red water is the organism's spore/toxin load, poison until sunned; pool life is AA_BloodShrimp, a fauna row |
| the_rot milk ponds | reclaimed Sheen, not-water; pond life is fungal, rostered as flora |
| the_slime | zero water tiles; slime rain is the organism irrigating itself — floodwater is feedstock, not habitat |
| the_scald | boiling fouled brine; silver-shoal ANALOG owed as a new thermophile def — list empty until it exists |
| the_rust_cathedral canals | coolant, not water; the coolant eels are an owed new def — list ships empty until it lands |
| wasteland brine termini | hypersaline over mineral beds — "a half-charged voltaic cell"; owners are the brine-battery new-def archetype |
| the_scarlands pools | ancients' weapon chemistry, hot from its own reactions |
| the_sump | tar, and it entombs |
| the_fever_wood black mirrors | kept empty by the deep thing; their emptiness is the biome's evidence |
| poison_forest | all standing water carries the metal load; everything poisons |
| forsaken_crags (36 water tiles) | permanent Dark + etchfall acid; ban 6 forbids the sun-fed chain a fishery needs |
| fall_line | ban 5: no water beyond a wreck condenser's output |
| the_lantern_deeps | no water body anywhere in the frozen sheet — crystal cavern layer; nothing owed |

Dry biomes with a ruled no-fish row and no water at all (one line, rulings final):
desert, dune_sea/deep_desert, arid_shrubland, the_blue_desert, nightside_ice,
the_pyrelands, the_forge, the_webwork — no liquid water exists in any of them.
wreck_fields: sheet unruled, no ruling possible (roster verbatim).

## 4. Enforcement follow-up (PROPOSED, bulk-agreeable — not an owner question)

Donor mods' **own live fishTypes** stand on defs our rulings declare fishless, and
Odyssey's Earth-named set fails recognizability everywhere: the item names
VCEF's own bindings to the Forsaken Crags (DuskySprat/ForsakenAnglerfish) and the
Rot (Jellyfungus), and vanilla IceSheet's salmon/cod/frostfish. ⚑ Proposed: one
strip-patch sweep emptying `fishTypes` on every live BiomeDef bound to a ruled
no-fish water. Which no-fish waters' live defs actually carry fishTypes today is
**UNMEASURED** (only the three above are attested) — the sweep starts with a
measure, not a grep. Also noted: `ZBiome_DesertOasis`'s untouched saltwater
buckets still name Fish_Bluefish/Fish_Tuna — inert (the water has no salt-bodied
terrain) but Earth names linger in def data; the sweep should take them too.

## 5. Owner rulings (2026-09-10 morning batch — every question answered)

1. **Cracked Lands merge (§2): RATIFIED.** Fill the committed patch's empty
   `freshwater_Uncommon` with BMT_Rocktooth (1) + BMT_Boneblade (1); VCEF
   secondaries dropped. One edit to `SandFishing_CrackedLands.xml` — FOUNDRY
   build work (`FISH_TYPES_PATCH_BUILD_1`).
2. **Weeping stones: TRIM to the 4 swfish_ donors only.** The VCEF four come
   OUT of the written patch's Uncommon bucket (tonally wrong for the sacred
   pools); they stay benched. swfish_Dactopus not adopted.
3. **Greentide vs Miasma: DUAL PLACEMENT accepted.** Mee/Faa/Laa in both
   registers — fishable adults in the Greentide's fishTypes, protected juveniles
   as Miasma wildAnimals. One population, two registers.
4. **One donor family: SUPERSEDED by a commission.** The owner rejects the
   flatten-to-one-family outcome the other way — *"Commission lots of fishes!
   ... a plethora of different kinds for each biome ... Squid like. Octopus
   like. Eel like. Crustaceans. Floaters. Jellyfish. Cucumbers. Bring in that
   Star Wars creature richness."* Filed as `FISH_BESTIARY_COMMISSION_1`; the
   swfish_-backed tables above ship as v1 placeholders until the bestiary lands.
5. **New-def commissioning order: all four wait** for their biomes' build passes
   (Scald thermophile, Cathedral coolant eel, wasteland brine-battery, twilight
   silver shoal) — but they fold into the `FISH_BESTIARY_COMMISSION_1` scope
   when that item runs.
