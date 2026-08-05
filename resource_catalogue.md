# Master Resource Catalogue — the arbitration worksheet

_The full universe of "common resources" a biome/terrain might produce, across vanilla + Odyssey DLC + the adopted mod stack. This is the **raw inventory** we cut the deck from: the next step (a separate pass) is to **arbitrate** each resource onto the four axes (① Abundant / ② Scarce / ③ Exotic / ④ Threat) per terrain, so no tile carries them all. Companion to `desert_world_design.md` §3A (which has the first, coarser inventory + the six-anchor partition) and `biome_terrain_palette.md` (the verified biome/terrain list)._

**Created:** 2026-08-04
**Status:** DRAFT inventory for arbitration. This list is deliberately *over-complete* — we'd rather enumerate too much and prune than miss a resource. Items are tagged by evidence level:

- **✓ vanilla/Odyssey** — base-game or Odyssey DLC resource, certain to exist.
- **✓ mod (verified)** — real defName read from an adopted mod's source this session (Alpha Biomes especially).
- **○ mod (candidate)** — from a mod we intend to adopt but whose exact defs are still 🔎 confirm-at-machine, or a mod whose 1.6 source is still pending Fetcher.
- **◇ author** — no mod; would be a save-edit / RimBridge / `GravshipCompat` fabrication if we want it.

> **How to use this for arbitration:** for each resource below, we'll later decide (a) which terrain(s) it's ① Abundant on, (b) which terrain(s) it's ② Scarce/absent on, (c) whether it ever plays the ③ Exotic role, and (d) whether its *extraction* carries a ④ Threat. A resource can appear on multiple axes across different terrains — that's the point. The design rule stays: **no terrain is Abundant in everything, and every terrain is Scarce in something.**

---

## Family 1 — FOOD (the survival floor)

The thing that, if a tile denies it, times your exit as hard as water does.

| Resource | Evidence | Notes for arbitration |
|---|---|---|
| Arable/fertile soil (crops) | ✓ vanilla | The classic Abundant of the oasis/river; flatly ✗ on desert/salt/volcanic. Fertility is a *terrain* stat we set in Map Designer. |
| Wild game / huntable fauna | ✓ vanilla | Meat + leather. Biome-dependent wildlife density. Guardrail: no fast-breeding ranchable printer (existing §3 rule). |
| Foraged wild plants (berries, agave, etc.) | ✓ vanilla | Low-yield desert forage (agave, healroot); the thin margin that lets you *cross* a dry tile, not live on it. |
| Fish (vanilla Odyssey fishing) | ✓ Odyssey | Coast/river/oasis water tiles. Odyssey adds fishing as a food route → strengthens water-tile Abundant. |
| Alpha Biomes exotic meats/fish | ✓ mod (verified) | `AB_JellyfungusMeat`, `AB_OcularFishMeat`, `AB_SlimefishMeat`, `AB_SpiderfishSteak`, `AB_PolarEelChunks`, `AB_ForsakenAnglerfishChunks`, `slime meal`. Biome-locked exotic food — a tile's ① or ③. |
| Alpha Biomes mushroom/fungal food | ✓ mod (verified) | Mycotic Jungle fungal biomass; `AB_Jellyfungus`. The "dark-larder" food alternative to sunlit crops. |
| Nutrifungus / cave crops | ○ mod (candidate) | If CaveBiome / Caveworld Flora is adopted (pending Fetcher `aj`) — food that grows *without light*, the dark-biome survival hook. |
| Eggs (from poultry) | ✓ vanilla | Animal product — food route that needs *penned/tamed* birds, so it's tied to a tile that can *support* grazing, not the tile itself. Ranchable-printer guardrail applies (no egg-factory loop). |
| Milk (from grazers) | ✓ vanilla | Same as eggs: needs a tile that can pasture animals → oasis/river fringe, ✗ on barren desert/salt. |
| Insect jelly | ✓ vanilla | From insect hives — a *threat-gated* food (you fight for it). Lands on ④-adjacent ③: harvest after clearing a hive/infestation tile. Ties to the VFE-Insectoids & Sarlacc-cavity strands. |
| Chocolate / cocoa | ✓ vanilla | Warm-climate cash/mood crop — needs arable warm soil (oasis). Minor; a morale/trade good more than a staple. |
| Hemogen / animal-blood feed | ✓ vanilla (Biotech) | Only relevant if any pawn is a sanguophage — not our Jawa. Park as N/A unless a raider xenotype needs it. |
| Kibble / preserved/pemmican | ✓ vanilla | Derived, not terrain-sourced — belongs to *processing*, not the partition. Listed so we don't accidentally "place" it. |

## Family 2 — WATER (the master-resource, already first-class)

Kept as its own family per the existing design; three physical forms, and *which form a tile offers* IS its rating.

| Resource | Evidence | Notes for arbitration |
|---|---|---|
| Surface fresh water (river/oasis pool) | ✓ (landform + water mod) | Pump freely → refill onboard Water Butt. The ✅✅ of oasis/river. |
| Surface saline water (coast/sea) | ✓ | Present but needs desalination work → coast is ✅-with-effort, not ✅✅. |
| Groundwater / aquifer | ○ mod (DBH-Lite / well) | Reached by well; slow, power-hungry. 🔎 confirm well placement is biome-gated so dry tiles can't cheat (existing open item §3A). |
| No water at all | ✓ (by design) | Deep desert / salt flat = ✗. This *absence* is the engine — dwell time bounded by the Butt. |
| Atmospheric/condensed water | ○ mod (candidate) | **Atmospheric Water Collection (Continued)** `3377426469` — the oasis's non-buildable well treasure. Also a possible desert lifeline if we let it be *found*, not built. |
| Ice / snow melt | ✓ vanilla | Not desert-relevant; park unless a polar/ocular tile enters the rotation. |

## Family 3 — CONSTRUCTION BULK (stone & wood)

| Resource | Evidence | Notes for arbitration |
|---|---|---|
| Vanilla stone (sandstone/granite/limestone/slate/marble) | ✓ vanilla | Chunks → blocks. Which stone types a tile has is a Map Designer setting. Salt flat & volcanic = stone-rich; oasis/coast = stone-poor. |
| Odyssey stone types (if any new) | ○ Odyssey (🔎) | Confirm at machine whether Odyssey's 5 surface biomes add new stone defs. |
| Alpha Biomes stone: cragstone, mudstone, onyxglass, rose quartz | ✓ mod (verified) | `AB_FinestoneCragstone/Mudstone/Obsidian/RoseQuartz`; smoothable variants exist. **Rose quartz & onyxglass** read as *pretty* stone → possible ③ Exotic décor stone, not just bulk. |
| Alpha Biomes "ancient metal" (smoothable) | ✓ mod (verified) | A stone-category ancient-material floor → salvage/ruins flavor bulk. |
| Wood (vanilla trees) | ✓ vanilla | Scarce in true desert; the oasis/river fringe supplies it. |
| Alpha Biomes crystalline wood / red wood / mushroom stalks | ✓ mod (verified) | `AB_CrystalWood`, `GU_RedWood`, `AB_MushroomWoodLog` — wood-substitutes for biomes with no normal trees (dark/mycotic tiles get a wood analog → keeps them from being flatly ✗ on construction). |
| Cordax resin / asphalt | ✓ mod (verified) | `AB_CordaxResin`, `AB_AsphaltBucket` — exotic construction/sealant materials, tile-locked. |

## Family 4 — METALS & COMPONENTS (the industrial feedstock)

| Resource | Evidence | Notes for arbitration |
|---|---|---|
| Steel (from ore/slag) | ✓ vanilla | The volcanic tile's ✅✅. Surface scatter elsewhere = ⚠️. |
| Plasteel | ✓ vanilla | Rare; deep-drill or ruins. A high-tier ③ Exotic or volcanic deep-vein. |
| Components (basic) | ✓ vanilla | From ruins/wrecks (desert salvage) OR deep-drill (volcanic). Two different terrains, two different routes — good partition tension. |
| Advanced components | ✓ vanilla | Salvage/ruins only in our world (we don't *build* the fabrication ladder freely) → ties to the salvage tile. |
| Uranium | ✓ vanilla | Deep vein / volcanic. Exotic-tier metal. |
| Gold | ✓ vanilla | River placer (§3C) + ruins loot. Trade metal, borderline ③ Exotic. |
| Silver | ✓ vanilla | Currency; from trade/ruins more than terrain. Park as non-partitioned. |
| Deep-drillable ore seams | ✓ vanilla + ○ mod | Vanilla deep drill; **More and Better Deep Drill** `3378527302` for the volcanic treasure. The *drill is found, not built* (§3B). |
| Alcyonite | ✓ mod (verified) | `AB_AlcyoniteChunk` + `AB_AlcyoniteSolar` — an Alpha Biomes exotic mineral that *also feeds a solar building*. Dual-purpose: ③ Exotic material AND an energy tie-in. |
| Rogue-android / mechanoid scrap | ✓ vanilla + ○ mod | Slag, components, rare mech parts from killed droids (§4 faction). The reward for beating the guardian. |

## Family 5 — ENERGY

| Resource | Evidence | Notes for arbitration |
|---|---|---|
| Solar (open sky) | ✓ vanilla | Brutal-but-strong on desert/salt flat (no shade, long days). The desert's compensating ①. |
| Geothermal (geysers) | ✓ vanilla | Volcanic ✅✅. Map Designer geyser density. |
| Wind | ✓ vanilla | Salt flat / open terrain. Secondary. |
| Chemfuel / astrofuel feedstock | ✓ vanilla + ○ mod | **Vanilla Chemfuel Expanded** `2792917473` (already in stack via Odyssey patch) — scanner-found chemfuel feedstock = coastal/oil-tile fuel treasure. Astrofuel = ship-relevant. |
| Propane / tar / oil (Alpha Biomes) | ✓ mod (verified) | `AB_Propane`, `AB_TarPits`, `AB_PropaneLakes` biomes — a *hostile* energy source (flammable terrain). Energy ① that is also a ④ Threat. |
| Rimefeller crude oil | ○ mod (candidate) | **Rimefeller** `1321849735` (✔️1.6 confirmed) — the "found, non-buildable" oil-derrick tile (§3D item 5). Regenerating oil = fine by ruling. |
| Alcyonite solar (see Family 4) | ✓ mod (verified) | Mineral-fueled solar; a volcanic/exotic-tile energy quirk. |

## Family 6 — SALVAGE, TECH & RUINS (the Jawa bread-and-butter)

| Resource | Evidence | Notes for arbitration |
|---|---|---|
| Ancient ruins loot (weapons, apparel, artifacts) | ✓ vanilla + Odyssey | Deep desert = the ✅✅ salvage sea. Odyssey landmarks add structured ruins. |
| Ancient danger / cryptosleep caches | ✓ vanilla | High-value + high-threat sealed rooms → treasure+guardian (§3B compounding move). |
| Mechanoid/droid scrap & rare mech parts | ✓ vanilla + ○ mod | From §4 rogue-android guardians. RM2 enemy mechs drop distinctive parts (enemy-side only). |
| Salvaging-mod ancient remains | ○ mod (candidate) | **Salvaging** `3288243760` — dig ancient remains for components (desert wreck treasure). |
| Scavenging-mod terrain-gated yield | ○ mod (candidate) | **Scavenging** `3108829323` — yields *only on supported terrain* → ideal tile-binding for river placer + desert wreck. |
| Working ancient machinery (found, non-buildable) | ◇ author / ○ mod | The §3B category: found quarry/well/drill/derrick you operate but can't build. Cross-refs Rimefeller, Deep Drill, Atmospheric Water. |
| Ship chunks / crashed hull metal | ✓ vanilla + ◇ author | Our "crashed Factory ship" fiction — a desert-tile salvage staple. `AB_AbandonedShipPart` exists as verified flavor. |
| Bioferrite | ✓ vanilla (Anomaly) | `Bioferrite` — Anomaly's signature material. Fits **sealed-cache / dark-biome / android-vault** tiles as a ③ Exotic: found in mined chunks near anomalous ruins, trades and crafts into distinctive gear. Keep it tile-bound (found, not farmed) so it doesn't become a ladder. |
| Shards | ✓ vanilla (Anomaly) | `Shard` — dropped by anomalous entities/events; a high-tier ③ curio. Threat-gated (you fight the anomaly for it). Pairs naturally with the Sarlacc-cavity dungeon strand. |

## Family 7 — EXOTICS & TRADE GOODS (money, not muscle)

The ③ axis home. Purely covetable — never a survival staple, so they raise no power ceiling (the "harmless" property).

| Resource | Evidence | Notes for arbitration |
|---|---|---|
| Jade | ✓ vanilla | Baseline décor stone; the thing gems out-class. |
| Gems (cut/raw) | ○ mod (candidate) | **Gemstone** mod (1.6 ID pending Fetcher `..._gemstone_...`). Placer gems (river), veins (volcanic), evaporite crystals (salt flat). Signature ③. Fallback: author value-only gem ThingDefs. |
| Fossils & amber | ✓ mod (verified) | **Biomes! Fossils** `BMT_FossilResource` / `BMT_AmberResource` — mined finite lumps, salt-flat/deep-desert (dead seabed) + river amber. Pure ③ trade/décor. |
| Rose quartz / onyxglass (décor stone) | ✓ mod (verified) | Alpha Biomes pretty-stone — a low-tier ③ that doubles as bulk. |
| Alien biomass / organic reagents | ✓ mod (verified) | Coast/jungle Abundant that trades as Exotic elsewhere. `AB_*` fish/fungal compounds. |
| Beached-leviathan / tidal harvest | ◇ author + ○ mod | Coast set-piece Exotic (§2C). |
| Sarlacc regurgitate + SarlacciSpore | ✓ mod (verified) | Star Wars Animal Collection `SarlaccPit` — trickle slag steel + rare spore curiosity. ③ + ④ in one. |
| Evaporite chems / salt | ✓ (Map Designer) + ◇ | Salt flat's scrape-crust: salt = food-preservation & trade good; rare evaporite chemicals. |
| Luciferium / hyperweave / other endgame trade | ✓ vanilla | Trade-only; not terrain-partitioned. Park. |

## Family 8 — MEDICINE, CHEM & DRUGS

| Resource | Evidence | Notes for arbitration |
|---|---|---|
| Healroot / medicine reagents | ✓ vanilla | Wild healroot (desert-viable in patches) → the thin medical margin. Oasis can farm it. |
| Neutroamine | ✓ vanilla | Trade/ruins mostly; medicine crafting input. Mostly non-partitioned. |
| Psychoid / smokeleaf / drug crops | ✓ vanilla | Warm-climate cash crops — a *warm-tile* Abundant/③ that fits the desert theme; also a social/ideoligion lever. |
| Chemfuel-derived chems | ○ mod | Rimefeller/Chemfuel Expanded plastics & chems. Tie to the oil tile. |
| Alpha Biomes toxic/spore compounds | ✓ mod (verified) | Mycotic spores, gas byproducts — mostly ④ Threat, but harvestable variants could be a hazard-gated ③. |
| Toxifier / souring agents | ○ mod (candidate) | **Sustainable Toxic Environment** `3254886145` (1.6 inferred, pending Fetcher `aj`) OR Odyssey toxic-scarlands native — the §4 enemy-side terrain-souring tool, NOT a player resource. Listed here only to keep it off the player's Abundant list. |
| Decaying wastepacks (pre-placed) | ✓ vanilla (Biotech) | `Wastepack` — normally a *player* pollution byproduct, but **pre-placed and already decaying** they become an android **salted-earth marker** (see Family 11). The tile arrives fouled: toxic buildup ticking, ground going polluted. A found-hazard, not a player resource. |

## Family 9 — TEXTILES & ANIMAL PRODUCTS

| Resource | Evidence | Notes for arbitration |
|---|---|---|
| Cloth (from cotton/plant) | ✓ vanilla | Needs arable soil → oasis/river only. Desert = ✗ cloth. |
| Leather / hides | ✓ vanilla | From hunting; biome fauna-dependent. |
| Wool / animal fiber | ✓ vanilla | Ranchable-animal guardrail applies. |
| Feralisk silk / chitin | ✓ mod (verified) | Alpha Biomes Feralisk jungle — harvested Exotic organics (a silk *harvest*, never a silk *ranch* — existing guardrail). |
| Devilstrand / hyperweave | ✓ vanilla | Slow high-tier textile crop; oasis-only, a long-dwell ③. |

## Family 10 — VISIBILITY & TERRAIN-STATE ("resources" that are really conditions)

Not stockpile-able, but they behave like resources in the arbitration: a tile *grants* or *denies* them, and they shape every other axis. Included so we place them deliberately.

| "Resource" | Evidence | Notes for arbitration |
|---|---|---|
| Open sky / total visibility | ✓ (by design) | Salt flat & desert grant it (great for solar + defense sightlines, terrible for cover). A genuine tile ①/② depending on how you value exposure. |
| Darkness / low light | ✓ Odyssey + ○ mod | Odyssey **Glowforest** (zero-mod dark biome) / CaveBiome / Ocular Forest. Vision becomes the scarce resource (§3(e)). The dark tile *denies* visibility → ② on the sight axis. Keep RARE. |
| Cover / defensibility | ✓ (by design) | River = ✗ defensibility (linear, floods); volcanic rock = good cover. A real partition axis. |
| Buildable flat ground / landing pad | ✓ (by design) | Salt flat's ①. Rough volcanic/jungle = ✗. |
| Fog of war (LOS reveal) | ✓ mod (CAI-5000 bundled) | A global rule, not a per-tile resource — but it *converts* darkness/weather into a scarcity of information. Run only ONE FoW source (§7 checklist). |

## Family 11 — PRE-PLACED HAZARDS & TERRITORY MARKERS (the ④ axis, made physical)

_A tile shouldn't just have an abstract "threat rating" — it should **arrive already marked** by what happened there. This family enumerates hazards and signposts we place at map-gen (or via RimBridge/save-edit), the mirror image of the §3B terrain treasures: instead of a found-and-operated windfall, a **found-and-cleared danger**. All of these are non-buildable by the player (they're environmental storytelling, not colony tools), which keeps them pillar-clean by construction. This is where your "salted earth," "IED fields," "extreme heat," "eruptions," and "Hutt corpse-markers" ideas live._

| Hazard / marker | Evidence | Role & arbitration notes |
|---|---|---|
| **Decaying wastepacks (salted earth)** | ✓ vanilla (Biotech) | Pre-place `Wastepack` clusters mid-decay so the tile arrives *fouling itself* — toxic buildup rising, `Pollution*` terrain spreading. The android **salted-earth** signature: they didn't just leave, they *poisoned it behind them*. ④ on any android-held tile; the cleanup (haul/burn the packs before they burst) is the cost of occupying it. Pairs with the toxic-souring strand — this is the *visible, physical* form of souring vs. STE's ambient version. |
| **Armed IEDs / explosive fields** | ✓ mod (VFE-Deserters, in stack) | `TrapIED_ToxGas`, `TrapIED_Tar`, `TrapIED_Cluster`, `TrapIED_AntigrainWarhead`, `TrapIED_Shrapnel`, `TrapIED_EMP`, `TrapIED_HighExplosive`, `TrapIED_Incendiary`, `TrapIED_Firefoam`, `TrapIED_Smoke` — a full palette already in the stack. Pre-place *armed, enemy-owned* around android caches & Hutt sites: a minefield you must detect and clear (or trigger) before reaching the treasure. ④ that literally gates the ③. `_ToxGas` and `_Tar` double as souring-on-detonation. **Guardrail:** keep them enemy-faction-owned/pre-placed only — the player doesn't get a buildable IED ladder. |
| **Extreme heat (desert)** | ✓ vanilla (weather/biome) | Some desert squares carry killing daytime heat — heatstroke timer, equipment/food spoilage, crop death. Not a placed object but a *tile property* we dial up in Map Designer/weather. ④ for deep-desert & salt-flat tiles; the reason open-sky solar is a devil's bargain (great power, lethal exposure). |
| **Volcanic eruptions / ashfall / ground heat** | ✓ vanilla + ○ Alpha | Volcanic tiles get eruption events, ashfall (blocks solar, spoils air), and hot ground. Alpha Biomes' propane/tar terrain (`AB_TarPits`, `AB_PropaneLakes`) adds *flammable ground* to the mix. ④ that times your extraction from the metal-rich volcanic tile — grab the ore and beat the eruption clock (already in the §2C volcanic allocation). |
| **Hutt territory corpse-markers** | ✓ vanilla (Ideology) + ✓ mod skulls | **Dot the landscape around Hutt territory with displayed bodies** to telegraph danger. Uses vanilla Ideology `GibbetCage` + `Skullspike` (place with corpses/skulls inside) + themed skulls from the stack (`KraytDragonSkull`, `RancorSkull`, `WampaSkull`, `AB_AncientGallatrossSkull`). Pre-placed at map-gen near Hutt sites (the same structure-gen technique DragonsDescent uses to furnish dragon lairs). **Mechanical hook (your idea):** *disturbing/deconstructing them drops Hutt faction standing* — a tripwire that punishes looting the warning signs. ④ signpost + a faction-relations lever. See implementation note below. |
| **Insect hives / infestation nodes** | ✓ vanilla + ○ VFE-Insectoids2 | Pre-placed dormant hives as a ④ that *guards* an insect-jelly ③ (Family 1). Clear-to-harvest. Cross-refs the Sarlacc-cavity dungeon. |
| **Sarlacc pit** | ✓ mod (SW Animal Collection) | Already catalogued (Family 7) as ③+④ — the rooted, area-denying maw. Belongs here too as a pre-placed hazard-marker: desert-weighted `LandmarkDef`, non-buildable, deconstruct-locked. |
| **Unstable fuel nodes in salvage** | ◇ author (+ vanilla parts) | A salvageable ship/vehicle/wreck seeded with a **volatile fuel cell that detonates when tampered with** — deconstructing or damaging the wrong component triggers a blast (chemfuel/antigrain-scale). Turns the desert-wreck ③ (components/tech) into a *defusal decision*: which parts are safe to pull, which are booby-trapped by decay. Cleanest builds: reflavor a `TrapIED_HighExplosive`/`_Cluster` (VFE-Deserters, in stack) *inside* the wreck as the "fuel node," or an ◇ author comp that explodes a fuel `ThingDef` on deconstruct-begin. Fuses ③ reward + ④ risk on one object. |
| **Native flammable liquid pools** | ✓ mod (Alpha Biomes) | `AB_PropaneLakes`, `AB_TarPits` — biomes/terrain of naturally flammable ground/liquid. A tile-native ④ that ignites from any spark (weapons fire, incendiary IED, eruption) → area-denial you must *route around* in a firefight. Doubles as a propane/tar energy ③ (Family 5) if harvested carefully. The natural-hazard cousin of the salvage fuel node. |

**Implementation note — the Hutt corpse-marker faction hook (design, not yet built):** the "messing with them lowers Hutt standing" behavior isn't a vanilla property of a gibbet, so it's an **◇ author** item. Cleanest routes, in order of preference: (a) a small `GravshipCompat` C#-free patch is likely *insufficient* here because faction-goodwill-on-deconstruct needs a hook — so more realistically (b) a `MapComponent`/`Thing` comp that fires a `Faction.TryAffectGoodwillWith(hutt, -X)` when the marker is deconstructed/destroyed, or (c) RimBridge live-watch: detect the gibbet's destruction event and apply the goodwill hit externally. **🔎 Confirm feasibility** at build time; the *placement* (pre-seeded gibbets/skullspikes with corpses near Hutt sites) needs no mod at all and can ship first, with the goodwill-penalty as a follow-on enhancement. This keeps the visible storytelling immediately buildable even if the mechanical tripwire takes a code comp.

**Why this family is pillar-clean:** none of these are player-buildable (they're enemy-owned or environmental), none scale colony power, and each functions as a *timer or toll* — the anti-exponential work the ④ axis is supposed to do. They raise the *cost and character* of a tile without raising the player's ceiling.

---

## Cross-cutting notes for the arbitration pass

**What's deliberately NOT in this list (and why):** processed/derived goods (kibble, blocks, meals, refined chemfuel) — those are *outputs of labor*, not things a terrain hands you, so they don't get partitioned. Pure trade-only endgame goods (luciferium, silver) — sourced from traders, not tiles. Anything player-*manufactured* — by the anti-exponential pillar we don't place manufacturing as a terrain gift.

**The two "resources" that are actually threats:** Alpha Biomes propane/tar (flammable energy) and the toxifier/souring agents. They appear in the resource families because a tile *produces* them, but in arbitration they mostly land on axis ④ (Threat), sometimes as a hazard-gated ③.

**Grounding status:** Alpha Biomes items are read from the actual 1.6 source this session (verified defNames). Vanilla/Odyssey items are certain. The candidate mods (Gemstone, Salvaging, Scavenging, Rimefeller, CaveBiome, Sustainable Toxic Environment) still have 🔎/pending tags — their exact resource defNames get confirmed at the machine or when Fetcher `aj` returns their sources.

**Decision this list set up — DONE (matrix built 2026-08-05):** this catalogue was the raw deck for the **resource × terrain matrix**, now regenerated at `resource_terrain_matrix.html`. Every resource here is assigned ①/②/③/④ across the locked **15-terrain / 6-band set** — *Desert sea* (Deep desert, Arid shrubland, Forsaken crags, Salt flat), *Water* (Oasis, River), *Volcanic* (Volcanic, Tar pits), *Coast & jungle* (Coast, Feralisk, Mycotic), *Dark* (Glowforest, Ocular), *Faction-held* (Wasteland-android, Shipyards-mech). The matrix supersedes the coarse §3A partition table with concrete, mod-cross-referenced picks, and folds Empire territory in as a threat-④ modifier row (Family 11) rather than a column. It is the artifact that makes the "purpose map" buildable in Map Designer. All 11 families here (incl. Family 11 hazards) map directly onto matrix rows.
