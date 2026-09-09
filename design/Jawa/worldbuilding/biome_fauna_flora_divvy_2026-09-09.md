<!-- status: SUPERSEDED 2026-09-09, same day it was written. DO NOT USE FOR ASSIGNMENT.

     Built entirely from raw creature-census + tile-temperature data, in ignorance of
     `design/Jawa/worldbuilding/biomes/*.md` (34 real, per-biome design sheets) and of
     `design/Jawa/worldbuilding/biomes/_assignment_prep.md` (611 lines: real per-biome
     admission tests, KEEP/EVICT/IMPORT menus with cited laws, a MEASURED 27%-homeless
     census, a NEW-ART/DEF ledger) — the actual, already-built prep for
     `BIOME_FAUNA_ASSIGNMENT_SITTING_1`, unblocked and ready since both its sequence-rider
     items closed. Checked against 6 of the 34 real sheets after the owner caught the
     BiomeGRimond error below: 6 of 6 directly contradict what this document says (e.g.
     it puts warm-blooded surface fauna and cold-icy-dayside-analogs on biomes whose own
     sheets hard-ban exactly that). Read `_assignment_prep.md` and the sheets themselves;
     do not carry any species pick from this file forward without re-deriving it from its
     real sheet. Left in place as a record of the mistake, not as an input. -->

# Biome fauna + flora divvy — pass 1 (baseline)

**Source of truth for the biome list**: `world/ASHKARR_WORLDMAP_tiles.csv`, read live
2026-09-09 — **29 placed biomes, 21,872 tiles**, the frozen canonical world (matches
`w9_run.py`'s `EXPECT_TILES`). This is the real, final list — nothing here is
speculative about WHICH biomes exist, only about what lives in them.

**Source of truth for creatures**: `design/Jawa/worldbuilding/review/creature_register_rows.json`,
1165 live (non-cut, non-dropped) creatures, generated 2026-09-05 against a 595-mod dump.
⚠️ **4 days stale relative to today's mod-consolidation work** (Cuisine/Armoury/SW
Bestiary absorptions this week) — defNames below that are `RSW_`/`RUT_`-prefixed and
recently absorbed should be spot-checked against current source before anything is
patched for real; everything else (vanilla, Alpha Animals, Biomes! Team, Jurassic
Rimworld, GRiNDTerra, etc.) is untouched by this week's consolidation and should still
be live as listed.

**Source of truth for flora**: `design/Jawa/mods/biome_flora.py`'s `FAMILIES` dict —
554 plants already assigned across 22 biomes, in 8 families. **8 placed biomes have
ZERO flora roster today**: `BiomeCypreJungle`, `BiomeGRimond`, `COMIGO_GreaterSwamp_Tropical`,
`RUT_GreySea`, `RUT_NightsideIce`, `RUT_PropaneLake`, `RUT_TheScald`, `RUT_TwilightSea`.
Those get a real starter proposal below; the other 21 are left alone (already done,
not re-litigated here) — see `biome_flora_rosters.md` for their existing lists.

---

## 0. The size-tier taxonomy (proposed — argue with it)

Built off the real distribution in the 1165-creature census (`bodySize` field), not
guessed:

| tier | bodySize | population in census | reference points |
|---|---|---|---|
| **Small (S)** | < 1.0 | 379 (33%) | human ≈0.85, rabbit-scale |
| **Medium (M)** | 1.0 – 2.5 | 391 (34%) | dromedary 2.1, boar-scale |
| **Large (L)** | 2.5 – 5.0 | 275 (24%) | elephant-scale, rancor-scale |
| **Titanic (T)** | ≥ 5.0 | 118 (10%) | Krayt Dragon 15, Reefback 32, Lanternwhale 40 |

**Why these cuts, not round numbers**: they roughly quarter the actual population
(33/34/24/10), so "titanic" stays rare in the data the way it should read in the
world — not a label anyone can slap on a merely-big animal. The already-shipped
**VAST tier** (`setting_physics.md` Part 5 — world-object-scale entities like
`RUT_LongHunger`, treated as weather/music-bearing map furniture, not a huntable
animal) sits ABOVE Titanic and is a different KIND of thing, not a bigger number —
it is not part of the 4-tier ladder below.

⚠️ **Every map gets all four tiers represented in its roster** (per your instruction),
even where a tier is one single rare entry on a small biome — never zero.

---

## 1. Hard rules already binding (from `fauna_placement.md`, live doc — not re-argued here)

- 🔴 **Cold-named creatures (frost/arctic/ice/snow/glacier/blizzard/cryo) go ONLY on
  `RUT_NightsideIce`.** A tidally-locked world has no latitude gradient — an arctic
  animal anywhere dayside is a continuity error, not a balance choice.
- 🔴 **Nightside creatures die dayside and vice versa** — `comfyTempMin/Max` re-tuned
  together, not transportable. (Re-tuning itself is phase-2 work, not this pass.)
- **Water-margin fauna** (`AA_Agaripawn/Agaripod`, `AA_AnimaColossus`, `AA_Animalisk`,
  `AA_Wildpawn/Wildpod`, `BMT_CactusCrab`, `AA_Mantrap`/`BMT_Creature_Mantrap`,
  `MA_Deermoss`, plus `AA_Atispec`+`AA_LarvalAtispec` and `Gomphotaria`) belong on
  biomes that actually touch open water — the three seas, the two propane lakes, the
  oasis, the mangrove/swamp family. Not deep desert.
- **The ikee (`AA_Eyeling`) is already placed** (D26 ruling): `Wasteland` (main
  population), `ExtremeDesert` (sparse), `ZBiome_DesertOasis` (uncommon). Nowhere else.
  Not repeated per-biome below except to note it stays out of the other 26.

---

## 2. Dayside desert family (the campaign's core — most scrutiny)

### Desert (3,932 tiles — largest biome, full 20)
Hot dayside floor, our home ground. Real desert-survival grounding used here: sand-
swimming (fringe-toed-lizard style), ear/heat-dissipation, nocturnal burrowers, water-
retentive physiology — cite these when arguing sizing/behavior in phase 2.

| tier | species | note |
|---|---|---|
| T | `GreaterKraytDragon` | apex predator, canon SW, already wired near here |
| T | `WarWyrm` | second titanic predator — burrow-ambush, fills the "sand-swimmer" niche real fringe-toed lizards suggested, at titanic scale |
| L | `Bantha` | canon SW pack animal, herds |
| L | `Dewback` | canon SW mount/beast of burden |
| L | `Skalder` | large predator/scavenger |
| M | `Dromedary` | vanilla, water-storage physiology already modeled |
| M | `Jerbal` | jerboa-scale, real-world burrower analog |
| M | `BMT_Diggerpede` | burrowing arthropod |
| M | `AA_SandProwler` | mid predator |
| M | `AA_DesertAve` | flying scavenger |
| M | `DA_Pilgrim` | wandering herbivore |
| M | `BMT_CactusCrab` | water-margin exception: only where Desert touches an oasis/river tile |
| S | `Urusai` | small burrower |
| S | `BMT_Batbird` | nocturnal flier |
| **NEW** | *sand-swimmer, small* | unbuilt — the exact niche `SAND_SWIMMERS_MOD_1` names: a real fringe-toed-lizard analog, S-tier, "swims" through Deep Sand once that mechanic exists. Seed the placeholder now, build with that item |
| S | `AA_KitFox`-analog | *(verify defName exists; placeholder for a small nocturnal predator if not)* |

*(14 named + 1 seeded NEW = 15; round out to ~20 in phase 2 with 5 more small/medium
once the sand-swimmer mechanic and a jerboa/fennec-analog pass are designed together.)*

### ExtremeDesert (3,172 tiles — the dune sea, full 20)
Emptier than Desert by design — "little else survives there" per `fauna_placement.md`'s
own ikee note — so the roster leans rare/titanic, sparse in the middle tiers.

| tier | species |
|---|---|
| T | `RUT_LongHunger` — the VAST-tier leviathan (world-object, not a normal wild spawn — see §0) |
| T | `GreaterKraytDragon`, `KraytDragon` (juvenile/lesser form, rarer here than in Desert) |
| T | `Roggwart`, `Lylek`, `Drexl` |
| T | *Sarlacc* (`SARLACC_NATIVE_HABITAT_1`, unbuilt) — pit-ambush, stationary, deep dune |
| L | `Ronto`, `Beldon`, `Vapaad`, `KellDragon`, `KwazelMaw`, `Tukata` |
| L | `Thranta` — flying, spans dune thermals |
| M | `Dactillion`, `Brezak` |
| S | `AA_Eyeling` (sparse, per the D26 ruling) |

### Wasteland (1,126 tiles — the ikee's main ground)
| tier | species |
|---|---|
| T | `AA_Atispec` (+ `AA_LarvalAtispec` juvenile — water-margin, only if the tile borders the badlands' worked-out water) |
| L | `AA_BoulderMit`, `AA_Barbslinger`, `AA_GreatDevourer` |
| M | `AA_RoughPlatedMonitor`, `AA_RipperHound`, `AA_Terramorph`, `GR_Spiderhorse` |
| S | `AA_Eyeling` (main population, D26) |
| **NEW** | a true scavenger-bird small tier — real-world grounding: desert vultures/carrion specialists; the wasteland is salt pans and buried metal, wants a "finds the dead" flier distinct from the ikee's "finds buried metal" |

### AridShrubland (665 tiles)
| tier | species |
|---|---|
| T | `Sivatherium`, `Zakkeg`, `Horax`, `Behemoth` |
| L | `Bison`, `MastiffPhalone` |
| M | *(gap — the candidate pool skewed almost entirely Titanic; needs 3-4 real mediums, phase 2)* |
| S | *(gap — same)* |

### ZBiome_Badlands (985 tiles)
| tier | species |
|---|---|
| T | `AA_MatureFleshbeast`, `Dinornis` (ostrich-scale runner, oversized here) |
| L | `Platybelodon`, `Uintatherium`, `Macrauchenia` — real extinct-megafauna body plans, already in the stack, good badlands fit |
| M | *HelixTellurox* (`HELIX_TELLUROX_BUILD_1`, unbuilt) — Ascendant Helix labour-line livestock; badlands' worked mining-scar terrain fits a labor beast |
| S | *(gap, phase 2)* |

### ZBiome_DesertOasis (223 tiles — small, but "life crowds the water")
| tier | species |
|---|---|
| T | `AA_MatureFleshbeast`, `Rancor` |
| L | `Megasloth`, `Doedicurus`, `Dactillion` |
| M | *Onnik kiln-belly* (`LIVESTOCK_STARTER_TRIO_1`, unbuilt) — desert livestock, oasis is exactly where a herded animal waters |
| S | `AA_Eyeling` (uncommon, D26) |
| water-margin | `AA_Agaripawn`, `AA_Agaripod`, `BMT_CactusCrab`, `MA_Deermoss` — this is the one dayside biome where the water-margin roster applies |

### BiomeGRimond ("Blue desert" — unrostered, unrenamed; 1,029 tiles, the biggest gap)
No RUT_/mandrake identity yet — this is the single highest-priority "who even is
this place" question for phase 2. Provisional baseline only:
| tier | species |
|---|---|
| M | `Dromedary`, `Boomalope`, `Donkey`, `Cougar` |
| S | `Vulture`, `GRimMonitorLizard`, `Iguana`, `GRimCobra`, `GuineaPig` |
| T/L | *(none found — needs a real identity pass before a titanic/large pick means anything)* |

---

## 3. Contamination family

### PoisonForest (557 tiles)
| tier | species |
|---|---|
| T | `AA_Behemoth`, `AA_OvergrownColossus` |
| L | `AA_Wildpod`, `AA_Helixien`, `Narglatch`, `DA_LeviathanCrab`, `SW_Grenadierworm` |
| M | `MA_Raptorkhan`, `AA_Groundrunner`, `AA_BlackSpider`, `AA_RipperHound`, `AA_Wildpawn` |
| S | *(gap, phase 2 — real-world grounding: toxin-tolerant small fauna, e.g. a poison-dart-frog analog)* |

### AB_TarPits (42 tiles — deliberately barren by rule, floor at 4)
| tier | species |
|---|---|
| T | `AlphaThrumbo`, `GR_Thrumbear` |
| L | `Doedicurus`, `AA_MammothWorm` — tar-trap megafauna is a real paleontological trope (La Brea), lean into it |
| M | `AA_TarGuzzler` — thematically perfect (the name says it), keep |

---

## 4. Mycoid belt family

### AB_MycoticJungle (2,258 tiles)
| tier | species |
|---|---|
| T | `AA_AnimaColossus`, `AA_MycoidColossus`, `AA_Gallatross` |
| L | `AA_Agaripod`, `Platybelodon`, `HiveQueen`, `Elasmotherium`, `Arthropleura` |
| M | `AA_Agaripawn`, `AA_Wildpod` |
| S | *(gap, phase 2 — a fungal-spore-scale swarm creature real-world grounded in insect/mold symbiosis)* |

### PoisonForest — see §3 (family C also includes it; not duplicated)

---

## 5. River jungle family

### AB_FeraliskInfestedJungle (161 tiles)
| tier | species |
|---|---|
| T | `Ronto`, `Beldon`, `AA_Gallatross`, `Lylek` |
| L | `AA_Wildpod`, `HiveQueen` |
| M | `AA_Feralisk`, `AA_Animalisk`, `AA_Dunealisk`, `AA_Junglelisk`, `AA_Agaripawn` — the `*lisk` family reads as a genuine local radiation, keep them together here |
| S | *(gap, phase 2)* |

### AB_MiasmicMangrove (93 tiles)
| tier | species |
|---|---|
| T | `Fambaa`, `AA_OvergrownColossus` |
| L | `Narglatch`, `Blixus`, `KwazelMaw`, `MarshHaunt`, `PekoPeko` |
| M | `DA_Snaptoad`, `GiantToad`, `Fanback`, `Veermok`, `Kaadu`, `Klorslug` |
| S | `Mott`, `Nuna` |

---

## 6. Frozen nightside family

### RUT_NightsideIce (1,506 tiles — EVERY cold-named creature lives here, nowhere else)
| tier | species |
|---|---|
| T | `Wampa` |
| L | `Narglatch`, `KellDragon`, `Elasmotherium`, `MA_Worhin`, `MA_Aminox`, `DA_SnowTaraal`, `DA_Taraal` |
| M | `BMT_FrostweaverSpider`, `Bear_Grizzly`, `Bear_Polar`, `Yak`, `AA_ArcticLion`, `AA_Frostling`, `AA_FrostAve`, `BMT_Snowstalker` |
| S | `Rabbuck` |
| **note** | `AA_FrostboundBehemoth`, `BMT_HoarfrostMastodon`, `AA_Blizzarisk` were mis-matched by the mechanical pass onto the propane-lake biomes below — corrected, they belong HERE only |

### AB_RockyCrags (1,170 tiles — this family's other half; NOT cold, it's the terminator highland)
| tier | species |
|---|---|
| T | `AA_SummitCrab`, `Tibidee` |
| L | `KellDragon`, `Gualaar`, `KingToad` |
| M | `Elephant`-analog scale, `Boomalope`, `Panther` |
| S | `Vulture`, `GRimMonitorLizard`, `Iguana`, `Chinchilla`, `Boomrat` |
| M | *HelixTellurox* also plausible here (labour-line, mining-adjacent terrain) — pick ONE home for it between here and Badlands in phase 2, not both |

---

## 7. Volcanic family

### Volcano (5 tiles — floor at 4, deliberately rare)
| tier | species |
|---|---|
| T | `ChrysalideRancor`, `Taozin` |
| L | `Katarn`, `Skalder`, `Uvak` |
| M | `AA_RoughPlatedMonitor` |

### LavaField (8 tiles — floor at 4)
| tier | species |
|---|---|
| T | `Taozin` |
| L | `AA_MammothWorm`, `Katarn` |
| M | `BMT_Megapleura`, `AA_Metallovore` |
| S | *(gap)* |

### AB_PyroclasticConflagration (31 tiles)
| tier | species |
|---|---|
| T | `JungleRancor`, `Roggwart` |
| L | `Mudhorn`, `KellDragon`, `Dewback`, `AA_Ravager` |
| M | `AA_SpinedGow`, `AA_RoughPlatedMonitor` |
| S | *(gap)* |

---

## 8. Machine and scar family

### AB_MechanoidIntrusion (236 tiles)
| tier | species |
|---|---|
| T | `BMT_HungeringHydra`, `GreaterKraytDragon` (rare wanderer, not a home population) |
| L | `BMT_BunkerBug`, `IridonianReek` |
| M | `AA_ChemfuelMyrmidon`, `BMT_SmolderstingScorpion`, `BMT_Basilisk`, `BMT_Woollybat` |
| S | `AA_AcanthamoebaGiganteaSmall` |

### Scarlands (90 tiles) — **the one biome the mechanical pass found NOTHING for**
Genuinely needs hand authorship, phase 2. Baseline placeholder only:
| tier | species |
|---|---|
| **NEW** | a blast-glass scavenger, M-tier — real-world grounding: post-fire/burn-scar ecology (opportunist scavengers move in first) |
| **NEW** | a crater-nesting small flier, S-tier |
*(floor of 4 not yet met — 2 more owed in phase 2, likely borrowed from AB_MechanoidIntrusion's roster since Scarlands is described as machine-adjacent scar terrain)*

---

## 9. Alien family

### AB_GelatinousSuperorganism (96 tiles)
| tier | species |
|---|---|
| T | `Harvester`, `Toraton`, `Titanis` |
| L | `Arthropleura`, `AA_Lockjaw`, `AA_ChameleonYak` |
| M | `BMT_CrystalBeetle`, `AA_Mantrap` (water-margin exception, only if adjacent) |
| S | `AA_GreenGoo`, `AA_Aerofleet` |

### AB_OcularForest (179 tiles)
| tier | species |
|---|---|
| T | `AA_UnblinkingEye`, `GR_FleshMonstrosity` |
| L | `AA_Helixien`, `JRWGeosternbergia` |
| M | `AA_Gigantelope`, `AA_SandProwler`, `Jerbal` |
| S | `AA_OcularJelly`, `AA_RedGoo`, `AA_RedSpore` |

---

## 10. The three seas + two propane lakes (water bodies; SeaBeasts is OUR OWN roster, use it first)

`mandrake.rsw.swbestiary` already ships `SeaBeasts_Colo`, `SeaBeasts_Colossi`,
`SeaBeasts_Opee`, `SeaBeasts_Sando`, `SeaBeasts_Scalefish`, `SeaBeasts_Swarm` —
absorbed and OURS, size-tiered by name already (Colossi≈T, Sando≈L, Scalefish≈M,
Swarm≈S). **These come first on every sea/lake biome below**, donor creatures fill
the rest.

### RUT_GreySea (429) / RUT_TwilightSea (479) / RUT_TheScald (312)
Same donor candidate pool (all matched "sea/ocean/aquatic"); differentiate by tone
in phase 2 (the Scald is a perched, spilling, hypersaline lake per `the_one_map.md`
— its roster should skew brinier/harsher than the two true seas, not identical).
| tier | species |
|---|---|
| T | **`SeaBeasts_Colossi`** (ours), `Gomphotaria`, `Fambaa`, `Tibidee` |
| L | **`SeaBeasts_Sando`** (ours), `Blixus`, `Dragonsnake`, `KwazelMaw`, `DA_LeviathanCrab` |
| M | **`SeaBeasts_Scalefish`** (ours), `BMT_Maxolotl` |
| S | **`SeaBeasts_Swarm`** (ours), `Mott` |
| water-margin | `AA_Atispec`+`AA_LarvalAtispec` at the shoreline tiles only |

### AB_PropaneLakes (2,531 — large!) / RUT_PropaneLake (57 — small, hand-named)
⚠️ Corrected from the mechanical pass: the cold-named creatures it surfaced here
(`AA_FrostboundBehemoth`, `BMT_HoarfrostMastodon`, `AA_Blizzarisk`, `AA_Frostling`,
`AA_FrostAve`, `DA_SnowTaraal`) are struck — they belong on `RUT_NightsideIce` only.
| tier | species |
|---|---|
| T | **`SeaBeasts_Colossi`** (ours, if the lakes are large/deep enough to host it — verify), `AA_TetraSlug` |
| L | **`SeaBeasts_Sando`** (ours), `GR_ParagonThrumbo`, `Jakobeast` |
| M | **`SeaBeasts_Scalefish`** (ours), `AA_Slurrypede`, `AA_Darkbeast`, `AA_WindBeast` |
| S | **`SeaBeasts_Swarm`** (ours), `Rabbuck` |

---

## 11. Jungle/swamp odds (unrostered flora AND fauna, lowest-confidence entries)

### BiomeCypreJungle ("Cypre Jungle" — 235 tiles, no rename yet, no flora)
| tier | species |
|---|---|
| T | `AA_MycoidColossus`, `AA_Gallatross`, `Dinornis` |
| L | `AA_Wildpod`, `AA_Agaripod`, `HiveQueen`, `Dragonsnake` |
| M | `AA_Agaripawn`, `AA_Junglelisk` |
| S | *(gap)* |

### COMIGO_GreaterSwamp_Tropical (43 tiles, no flora)
| tier | species |
|---|---|
| T | `Fambaa`, `AA_OvergrownColossus` |
| L | `Narglatch`, `Blixus`, `KwazelMaw`, `MarshHaunt`, `PekoPeko` |
| M | `DA_Barog`, `DA_Snaptoad`, `GiantToad`, `Fanback`, `Veermok` |
| S | `Mott`, `Nuna`, `Ollopom` |

---

## 12. Flora starter proposal — the 8 zero-roster biomes

Not a re-derivation of the existing 554-plant/22-biome system — a first pass matching
each gap biome to its NEAREST existing family by climate, so `biome_flora.py`'s own
rule ("no plant crosses a family") isn't violated blind:

| biome | nearest family | proposal |
|---|---|---|
| `BiomeGRimond` | A. dayside desert | needs its OWN small roster once renamed/re-identified — do not borrow Desert's 30 wholesale, that's the zoo effect on a 1,029-tile biome |
| `BiomeCypreJungle` | D. river jungle | borrow-adjacent to `AB_FeraliskInfestedJungle`'s roster, thinned to ~15 |
| `COMIGO_GreaterSwamp_Tropical` | D. river jungle / new "tropical swamp" sub-family | closest existing family is D, but "tropical" argues for its own small family if phase 2 wants it distinct from Ash'karr's other jungles |
| `RUT_GreySea`, `RUT_TwilightSea`, `RUT_TheScald` | — | **plantless by design, like Lake/Ocean/SeaIce** — argue in phase 2 whether kelp/algae belongs, but the existing convention (4 biomes already plantless) suggests seas stay bare |
| `RUT_NightsideIce` | E. frozen nightside | pairs with `AB_RockyCrags`'s existing 27-plant roster; needs its own cold-tolerant subset, not a copy |
| `RUT_PropaneLake` | E. frozen nightside (shares `AB_PropaneLakes`) | small biome, could literally inherit `AB_PropaneLakes`' family membership rather than invent one |

---

## What this pass did NOT do (owed to phase 2, one biome at a time)

- Real justification prose per species (this pass optimized for coverage over depth)
- Filling every marked *(gap)* cell to reach the ~20/≥4 target exactly
- `BiomeGRimond`'s identity (the biggest open question — 1,029 tiles with no name,
  no flora, no fauna logic of its own)
- `Scarlands`' fauna (mechanical pass found zero real candidates)
- Re-deriving the nightside roster from `comfyTemp` stats rather than names (the
  binding rule in `fauna_placement.md` §"CANON, 2026-08-15" — this pass used names,
  which that same doc warns is unreliable)
- Any actual XML/patch authorship — this is still a proposal document
