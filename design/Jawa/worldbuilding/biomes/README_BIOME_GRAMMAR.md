# Biome definition sheets — the grammar

_Owner + BENCH, 2026-09-05. Owner: "Pick principles that drive the local reasoning
and then populate to them... make biomes that radiate a powerful artistic theme and
pseudo alien biological reasoning."_

## The generative rule: **energy regime × local anomaly**

Two measured facts about Ash'karr drive everything (`the_one_map.md`):
1. The tidal lock is a **POINT**, not a latitude band — θ=0° substellar, θ=180°
   antistellar, the torn seas around **θ 63-117°**.
2. 🔴 **Concentric biome rings about the substellar point are FORBIDDEN.** A
   bullseye planet is explicitly ruled out.

Those two are in tension: the physics wants rings, the aesthetics forbid them. That
tension IS the design engine:

> **θ sets the ENERGY BUDGET. TEMPERATURE sets what METABOLISM is possible.
> A local ANOMALY sets the IDENTITY.**
> Rings never form because the anomalies are scattered.

**Three axes, not two (owner, 2026-09-05):** temperature is *similar to θ but
independent of it* — altitude, wind, water and venting all decouple the two. It is
its own axis because it decides two things θ cannot:
1. **Which metabolisms are chemically available at all** (a reaction that runs at
   40 °C may simply not run at −40 °C, whatever the energy budget says), and
2. **Which non-biological processes are at work** — frost shatter, evaporation,
   sublimation, clathrate stability, what the wind can carry.

A biome is a *reasoned intersection* of a regime, a temperature, and an anomaly.

**Energy regimes** — deep dayside (eternal noon, no diurnal cycle at all) · mid
dayside · **terminator band** (permanent low-angle light, the water, and the
day→night convection winds) · deep nightside (eternal dark, geothermal only).

**Anomalies that break the ring** — water · volcanism/vents · altitude · impact
scars · chemistry · wind corridors · and, uniquely to this world, **ancient wreck
fields**: on a scavenger planet, crashed tech is a legitimate ecological substrate.

A biome is a *reasoned intersection* of one regime and one anomaly. If you cannot
name both, the biome has no driving force and its art will drift ordinary — which
is exactly what went wrong with the poison forest.

## The lanes doctrine

Travel on Ash'karr runs on **lanes**: in a hostile biome, safe movement is a
named, ownable, contestable STRUCTURE, never open ground. The motif is
deliberate and recurs across the sheets — the Fever Wood's **boughways**
(canopy roads with tolls, the ground left to the brave and the poor,
`the_fever_wood.md`), the Greentide's **root causeways** (the giants' roots
are the road system, and the fights happen on it, `the_greentide.md`), the
Sump's poured-tar **mouse-lines** (`the_sump.md`), the Grey Deep's **pillar
navigation** (the masons' salt pillars as the only bearings in the murk,
`the_grey_deep.md`), and the dayside's **oasis strings** (caravan travel
pegged to water, the tirbak as its mount, `weeping_stones.md`). It is named
here once so future content — quests, raids, roads, caravan events, dungeon
approaches — **cites the motif rather than reinventing it**: when a new biome
or mechanic needs movement, ask first *what is this biome's lane, who owns
it, and what does walking off it cost?*

## The sheet template (nine fields)

1. **What it is** — one paragraph, the place as a person would describe it.
2. **Planetary position** — the θ band + the anomaly. *(Added: this is what makes
   the reasoning derivable rather than decorative.)*
3. **Driving forces** — the physical/chemical engine, in one sentence.
4. **How the biology adapted** — the consequence. Mechanism, not adjectives.
5. **Always true** — invariants.
6. **Never true** — 🔴 HARD BANS, written checkable (owner's ruling): a linter must
   be able to flag a def that violates one.
7. **Uniquely available** — what only this biome gives the player.
8. **Inhabited objects** — what structures, ruins and wrecks occur, and why here.
9. **Artistic theme** — palette, silhouette language, quality of light. The thing
   that makes it *radiate*.

## The sheet drives the roster (owner's ruling)

The definition is the **admission test**. Nothing lives in a biome that its
reasoning does not justify — flora and fauna are populated TO the principles, not
inherited from whatever mod shipped them. Two standing bans apply everywhere:

- 🔴 **The recognizability rule** (`creature_recognizability_rule.md`): if a player
  can instantly name what it is meant to be, it does not belong on this planet.
- 🔴 **THE LUSH RULE, three-part** (owner, 2026-09-05 — corrected; an earlier
  "lush = water-high biomes" phrasing was WRONG and is struck):
  1. **Dayside: lush exists ONLY along rivers and coasts.** It is a THIN LINE on
     the map, never a region — a green edge against the vast empty dune. Away from
     water there is nothing.
  2. **The terminator is NOT lush. It is SOLITARY.** Its character is sparse,
     lonely and singular; never write it as an abundant green belt.
  3. **The nightside has a DIFFERENT definition of lush** — dense, but built of
     very alien life forms rather than green plants. A future nightside-lush biome
     is the owner's stated intent.


## 🔴 The Star Wars icon carve-out (owner, 2026-09-05)

> "Iconic Star Wars status protects completely."

The recognizability rule disqualifies **terrestrial** referents, never in-universe
ones. A bantha, a dewback, an astromech reading as exactly what it is *is the
campaign working*, not a violation. Iconic Star Wars creatures and droids are
exempt from the cut rule outright — and their recognizability is an asset to be
sought, not a defect to be corrected.

---

## Progress — which biomes are defined (updated 2026-09-05)

The owner works these **one at a time, in conversation**: BENCH opens with where the biome
stands and a proposed driving mechanism, the owner rules and adds, one more pass, done.
Order is by **similarity — slowly vary** (owner, 2026-09-05).

| sheet | biome def | status |
|---|---|---|
| `poison_forest.md` | `PoisonForest` | ✅ done |
| `dune_sea.md` | `ExtremeDesert` (Dune Sea) | ✅ done |
| `terminator_sea.md` | Twilight Sea + Grey Sea (`RUT_TwilightSea`/`RUT_GreySea`, `LIQUID_BIOMES_MAP_1`) | ✅ sheet done for these two; ⚠️ **this row previously said "the three seas" — the Scald is the third and has NO biome sheet** (checked 2026-09-06, `LIQUID_BIOMES_MAP_1_RECONCILIATION.md` §2); `terminator_sea.md` uses the Scald only as a comparison foil, it does not define it |
| `nightside_ice.md` | `RUT_NightsideIce` (own def, inherits vanilla `IceSheet`; 802 tiles MEASURED — the deep-night highland) | ✅ first pass 2026-09-05; **second pass 2026-09-06** — dirty ice, the thaw pulse, tunnelers, the six reconciliations; first-pass ecology unchanged |
| `fall_line.md` | **injection layer** over `ExtremeDesert` | ✅ done — no new BiomeDef |
| `deep_desert.md` | `ExtremeDesert`, far ring | ✅ done |
| `desert.md` | `Desert` | ✅ done |
| `arid_shrubland.md` | `AridShrubland` | ✅ done 2026-09-05 |
| `wasteland.md` | `Wasteland` | ✅ done 2026-09-05 — the dryland ladder is complete |
| `forsaken_crags.md` | `AB_RockyCrags` (Forsaken Crags, 1,170 tiles MEASURED on V26 — earlier "1,225" and "4,440" here were stale; the sheet's own §0 is the number's home) | ✅ done 2026-09-06 — donor content incorporated wholesale, the Dark's physics ratified |
| `the_rot.md` | `AB_MycoticJungle` ("The Rot", owner-named; 1,939 tiles MEASURED) | ✅ done 2026-09-06 — the planet's gut; nightside-lush honored; gene-reactor mechanic RESERVED for `AB_GelatinousSuperorganism` |
| `the_slime.md` | `AB_GelatinousSuperorganism` ("The Slime", owner-named; 96 tiles MEASURED) | ✅ done 2026-09-06 — the living registry; Assailant-sibling of The Rot; gene machine, slime rain, Slime Pit |
| `assailant_weapon_remnants.md` | `HorrorWastes` ⛔ DISSOLVED · `AB_OcularForest` → the Overdrive site | ✅ ruled 2026-09-06 — neither is a biome: Horrors = raiding faction + injected dungeons; Ocular = named site + custom dungeon |
| `the_contagion.md` | `AB_OcularForest` ("the Contagion", owner-named; moves to the peaks above the green — placement item open) | ✅ done 2026-09-06 — the weapon at open throttle; the UV cage; the Burn and the Bloom |
| `the_blue_desert.md` | `BiomeGRimond` ("Blue Desert", name kept; Deadstone's receiving ground as a lobe mosaic) | ✅ done 2026-09-06 — the phase boundary; hydrocarbon biology; the ice hands up the weapon; 🔴 no bullseye |
| `the_propane_lakes.md` | `AB_PropaneLakes` + Umbra, the antistellar cap (1,589 tiles MEASURED) | ✅ done 2026-09-06 — two solvents; the reconnection aurora and the electrojet tap; the terramanufacture history; the war lab and the crater ending |
| `the_lantern_deeps.md` | `BMT_CrystalCaverns` ⛔ NOT a worldmap biome — an **injected underground layer** beneath any ≤ −40 °C nightside map | ✅ ruled 2026-09-06 — lanternstone, kyber, the Shard-minds in the dead's technology, the mindstone race; the surface tiles re-homed to the ice sheet and the Blue Desert |
| `BMT_FungalForest` | ⛔ DISSOLVED 2026-09-06 (an underground def wearing 425 surface tiles) | raided into `the_rot.md` §7b (the spore-warfare kit, fungal materials, marsh fungi); tiles merge into the Rot (and the Wasteland at South Crags sector 9) — `FUNGALFOREST_RAID_MERGE_1` |
| `the_cracked_lands.md` | `ZBiome_Badlands` ("the Cracked Lands", owner-named; 1,086 tiles MEASURED) | ✅ done 2026-09-06 — the flood; soil in the shade; the fliers' feeding country; Moisture Farmers only; the roads. **Enrichment backfilled 2026-09-06** — time-sorted bestiary; water chimes; discovery surveys; NEVER-the-bottom; explosive growth ruled world-wide (`EXPLOSIVE_PLANT_GROWTH_1`) |
| `weeping_stones.md` | `ZBiome_DesertOasis` ("the Weeping Stones", owner-named; 236 tiles MEASURED) | ✅ done 2026-09-06, enrichment included — dew+relic engine; biome+landmarks architecture; the truce and the claim law; the comb convergence; the recapture ladder; seep oases; the singing vanes |
| `the_greentide.md` | `BiomeCypreJungle` ("the Greentide", owner-named; 191 tiles MEASURED, all river) | ✅ done 2026-09-06, four rounds, enrichment included — water is the only argument; STEAM and the Roil; NO truce; the dying river and its graves; blowers, domes, the habitable band; the Greatboles; owner: "I really like how this one turned out" |
| `the_webwork.md` | `AB_FeraliskInfestedJungle` ("the Webwork", owner-named; 172 tiles MEASURED, bimodal rain) | ✅ done 2026-09-06, two rounds — the drunk river; a biome-sized creature of shade; the Wyyyschokk/Feralisk canon; the light-moat; Shokkweave IS hyperweave, sole source; the three wars; NOT the Greentide, by inversion |
| `the_scarlands.md` | `Scarlands` (name kept; 🔑 vanilla Odyssey, not a mod; 90 tiles MEASURED, all in the Scorch) | ✅ done 2026-09-06, two rounds — the Rakatan last stand (🔴 lore PARTITIONED §P/§GM, reveal-gated); the visible defense with no enemy; Glowers, plated grazers, the mynock comes home; rainbow pools; reclaimable droids; the curse as mechanics |
| `the_rust_cathedral.md` | `AB_MechanoidIntrusion` ("the Rust Cathedral"; 236 tiles MEASURED, one region, 211 flat — the plateau IS the works) | ✅ done 2026-09-06, two rounds, mostly ASSEMBLY of ruled canon (defers to `reconciled_lore/03_deep_history.md`) — 🔴 lore partitioned; naming settled (Forsakens=Rakatans=Ancients, Sentinels=mechanoids, Arsenal=faction); the hum; coolant canals + eels; living bolts; wall ladder; kyber-mind §GM |
| `the_miasma.md` | `AB_MiasmicMangrove` ("the Miasma", owner-named; 92 tiles MEASURED, the deltas) | ✅ done 2026-09-07, three rounds — the lifeboat at the drain; breath-tide + moving salt line; the Working (no gene machine — the Slime's); fever-forged; rainbow flora that never lies; the attar; Wildsteam worship-pilgrimage |
| `the_fever_wood.md` | `COMIGO_GreaterSwamp_Tropical` ("the Fever Wood" — region name; def-label call at freeze review; 60 tiles MEASURED) | ✅ done 2026-09-07, one round + ratification — the held breath; water from below; the causeway vs the water; the Tenant (one aquifer, one creature, never seen whole); anti-Miasma by design |
| `the_sump.md` | `AB_TarPits` ("the Sump", owner-named; 62 tiles MEASURED, night edge, elev 1 m) | ✅ done 2026-09-07, two rounds — the trap that remembers; R-H9's tar (Pyrelands-made, Sump-collected); the moat trade and Junker stations; the tar beast (third of the Patient family); sump-mice; wick-gardens; booby traps outweigh remains |
| `the_pyrelands.md` | `ZBiome_Grasslands` ("the Pyrelands", ruled 2026-08-15; 226 tiles MEASURED) | ✅ done 2026-09-07 — assembly on the fire canon + the built FireEcology mod; Rakatan quickgrass; four igniters (lightning, fire-hawks, furnace-beasts, deliberate hands); flame harvest, fire raids, the Sun-Debt reconciliation |
| `the_forge.md` | `Volcano` 5 + `LavaField` 8 + `AB_PyroclasticConflagration` 31 — **one sheet, one massif** ("the Forge", owner-named) | ✅ done 2026-09-07 — the only unstolen fire; foundry towers (the god-project's smeltery, 🔴 partitioned); boiling closed rain; Beldons + tibanna; 🔴 the Imperial gas embargo as a campaign clock; two faiths, no correction |
| `the_scald.md` | `RUT_TheScald` (312 tiles, the substellar crater sea; FOUNDRY's waiting def now has its soul) | ✅ done 2026-09-07 — the boiler of the dayside; fouled heart, clean breath (the Contagion as the distillery's filter stage); welcome blankets, bottom-walker herds, silver shoals, bubble-sailors; the two-faith shore; salinity ruled fouled-not-toxic |
| `the_grey_deep.md` | the bottom of `RUT_GreySea` — design done, 🔵 implementation deferred to the diving mods (standing ruling) | ✅ done 2026-09-07, two rounds — the statuary; brine pools with shores; the pillar forest; the crusted ill-tempered giant; the ossuary shrimp; the soluble-mineral treasury |
| `the_twilight_deep.md` | the bottom of `RUT_TwilightSea` — design done, 🔵 implementation deferred to the diving mods | ✅ done 2026-09-07 — the last ordinary sea; the mat as roof (why the Twilight outlives the Grey); skylights; kelp forests + real crowding (scoped below the roof); dry-looking bottom rivers; 🔴 the Deepwater Compact revealed as ark-keepers, dwellings in v1, full settlement 🔵 v2 |
| **THE CAMPAIGN IS COMPLETE** | — | 🏁 **Every biome on Ash'karr — land, sea, and sea-bottom — has a ratified sheet** (2026-09-05 → 2026-09-07). Remaining sheet-adjacent work rides the items: the full plant-and-animal assignment pass, the mechanics kits, the Wednesday canon propagation, and the deferred diving-mod implementations. |
| `wreck_fields.md` | — | ⛔ superseded by `fall_line.md` |

### 🔑 The dryland ladder is ONE number: the sun's angle

Sun elevation is `90 − arc`; insolation scales as its sine. This is the instrument that
generated the deep desert and desert sheets and it should generate the rest.

| biome | sun above horizon | insolation vs overhead | shadow length | hilliness | temp |
|---|---|---|---|---|---|
| `ExtremeDesert` | 47.4° | 74% | 0.9× height | 1.0 | 48.3 °C |
| `Desert` | 14.4° | 25% | 3.9× height | **2.0** | 24.5 °C |
| `AridShrubland` | 9.2° | 16% | 6.2× height | 1.0 | 20.9 °C |
| `Wasteland` | −9.9° | 0% | — | 1.0 | 0.5 °C |

**Deep desert** = absence (distance from water). **Desert** = the shade economy, because the
terrain is hilly enough to cast shadows and the sun is high enough to make them matter.
**Arid shrubland** = where the shade economy *ends* — the terrain flattens again and the sun
drops to 16% of overhead, so nothing has to hide any more. That is the proposed hinge, put to
the owner 2026-09-05 and **not yet ruled**.

### Arid shrubland — done

Sheet: `arid_shrubland.md` (2026-09-05, three passes). The taint question resolved by the
Hadley-cell ruling: the stormwall's toxins precipitate AT the terminator, so the fog reaching
the shrubland is the last **clean** water on the approach. The def's scatter is owed to the
band mend (in the sheet's Owed section) — plume-painted, never a bullseye, folding into
`WORLDMAP_DESERT_BAND_REPAIR_1`.

## The enrichment pass — standard since 2026-09-06 (owner: "I think we skipped this step")

A sheet is not done at field 9. Four more, written in the same conversation loop
(owner's pass owed on all of it), with `weeping_stones.md` and `the_cracked_lands.md`
as the worked examples:

10. **Bestiary sorts** — what KINDS of animals the engine produces, and how they
    divide the biome (rings in space, phases in time…). Sorts are the deliverable;
    per the owner's sequencing rule, actual animals wait for the full
    plant-and-animal assignment pass and any named now are gravy. Grade the standing
    cast (MEASURED off `design/Jawa/fauna/cast_assignment.csv`) against the sorts.
11. **Unique items, furniture, structures** — the engine made ownable and buildable:
    signature materials, trade goods, item-as-quest-seed, the structure ladder.
12. **Faction faces** — how each faction expresses itself here, derived from ruled
    doctrine (water states, settlement bans), never invented free.
    Plus **weather-and-sound** (field 4b/10b where the sheet lacks it): the engine as
    weather, and what the place sounds like — every biome so far has earned a
    signature instrument or silence.
