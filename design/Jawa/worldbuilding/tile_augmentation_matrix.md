<!-- status: draft — owner's AFK brief 2026-09-05, "err on the side of too many good ideas". Expansion of tile_augmentation_catalogue.md; design only, nothing here is built. -->
# tile_augmentation_matrix.md — everything a tile could be given, by biome × territory × arc

_The **expansion** of `design/Jawa/worldbuilding/tile_augmentation_catalogue.md` (the 41-row
mechanism-first catalogue) and `structure_injection_roster.md` (22 promises + 22 whispers).
Neither is restated: catalogue rows are cited as `↩A5`, roster rows as `↩P7` / `↩W9`. This
file adds the **three axes** the owner asked for and a much longer parts list under them._

**The owner's framing (2026-09-05):** *half of what we are carrying in mods is actually to
engage the inhabited dream* — drilling lasers, crashed ships, broken wagons, dead beast
skeletons. The frozen planet's tiles must feel **inhabited and alive** when the player lands.
This file is the enumeration of what "inhabited" can mean on each kind of tile.

---

## 0. The mechanism this enumerates FOR — measured, not assumed

The `RimMandrake.Inhabited` mod (`src/RimMandrake/Inhabited/`) is the proven injector, live
2026-09-05:

| piece | what it is today | what it means for this file |
|---|---|---|
| `TileMutatorDef RM_InhabitedPlace` | `extraGenSteps` → `Inhabited_Cast`, `RM_InhabitedStock`; **no `chanceOnNonLandmarkTile`** — assigned to a named Ash'karr tile by hand | every row below is a **hand-placed** augmentation on the frozen map, never a roll. Rarity columns are *authoring budgets*, not probabilities |
| `InhabitedPlaceDef` (`RM_InhabitedPlace_Scrapyard` ships) | archetype: `defaultCast`, `fate` (`Resident` / `FleeIfThreatened`…), `workRadius`, `homeRadius`, sleep/wake hours, `larder`, `stock` + `stockLabel` | **RESIDENTS and TRADING rows are one PlaceDef each** — a place is its cast, its routine, its larder and its stock |
| `SettlementManifestDef` (`Inhabited_Manifest_TheClaimJump`) | `factionDefName`, `securityProfile`, `districts[]` (label · approxSize · adjacentTo · required), `castSlots[]` (role · district · count) | **HOMES / GARRISON / BREEDING rows are districts** — one rimplace template each, composed by `GenStep_ComposeSettlementDistrict` |
| `CastRoster_*.xml` × 12 | individual `CharacterDef`s for BLACKSTAR · DEEPWATER · DROIDS · EMPIRE · GEONOSIAN · HELIX · HOMESTEAD · HUTT · JAWA · JUNKERS · TUSKEN · WILDSTEAM | **every faction already has a named cast to draw from** — the RESIDENTS axis is not blocked on characters |
| `Templates/junkers_{scrapyard,dwelling_cluster,cantina_block,depot}.txt` | 4 compiled rimplace flat plans (Gravel footprint, 30×26 etc.) | the district vocabulary exists for ONE faction; 11 more faction "dialects" are the largest gap this file names (§4) |
| `SecurityProfileDef` | gate behaviour (the Claim Jump "waves you through both ways") | GARRISON rows are security profiles + a district, not a new system |

**So the fodder question per row is only ever:** *does the ThingDef / PawnKindDef / terrain
exist in the stack, and does a template exist to arrange it?* Feasibility tags:

`✅` fodder in stack, place-and-go (scatter/prop) · `🔶` fodder in stack, needs a rimplace
template or a Cast/PlaceDef authored · `🆕` new content (def, art or C#) · `⚠️` gated on a
standing ruling or prerequisite strip named in `required_mods.md` / the catalogue §5.

⚠️ **Every defName below is either verified in the catalogue (`✅ verified live` there) or
carried from a roster that names it; anything I could not source from a read doc is written
as a *mod* + *shape*, never as a guessed defName.** Verify against the frozen dump
(`1742630eb6253187`) before any template names it — `rimplace verify` does exactly this.

---

## 1. THE THREE AXES

### 1.1 "Latitude" is ARC from the substellar point — six bands

Ash'karr does not spin; its only gradient is great-circle arc from the sun-point
(`reconciled_lore/02_world.md`). Band edges are the painted curve `[70, 58, 38, 14, −22,
−58, −80] °C` at arc 0/30/60/90/120/150/180. **Biomes are assigned to bands by their painted
temperature medians** in `biome_flora_rosters.md` — a measurement, not a guess.

| band | arc | avg °C | light | biomes that actually sit here (median °C) | who holds it |
|---|---|---|---|---|---|
| **A · THE ANVIL** | 0–30 | +70→+58 | unmoving sun, no shadow | `ExtremeDesert` (48) · `AB_MechanoidIntrusion` (62) · `Scarlands` (60) · `ZBiome_Grasslands` = the Pyrelands (50) · `AB_PyroclasticConflagration` (50) · `Volcano` (42) · `LavaField` (42) · `AB_FeraliskInfestedJungle` (46) · `AB_MiasmicMangrove` (41) — the Scald's jungles are HOT | **Galactic Empire** (dead centre, 2–3 ground seats + the spaceport) · **Geonosian Foundry Hive** (under the rock) · **Free Droid Enclaves** (Rust Cathedral plateau, volcanic) · **Wildsteam Clan** (Scald jungle holds) · **Deepwater Compact** (the Scald itself) · **Tuskens** (dune-sea interior) |
| **B · THE NEAR-DESERT** | 30–60 | +58→+38 | high sun, long fixed shadows | `Desert` (24) · `ZBiome_DesertOasis` (35) · `AridShrubland` (26) · `ZBiome_Badlands` (27) · `AB_OcularForest` (23) | **Hutt Cartel** (8 oasis palaces + 11 dry service posts, the Kiln) · **Deep Desert Tribes** (canyons, caves) · **Jawa Trade Moot** (canyon fortresses, crawler circuits) · **the Junkers** (wreck fields) · **Blackstar Company** (road junctions) · **Deepwater** (every oasis) |
| **C · THE MARGIN** | 60–80 | +38→+22 | low sun | the cooler `Desert`/`AridShrubland` tail · `Wasteland` (1, wide range) · `AB_TarPits` (3) · `AB_GelatinousSuperorganism` (13) · rivers end at arc ~71.5 | **Homestead Defense League** (13 farmsteads, the arable margin) · **Junkers** (tailings) · **Blackstar** · **Free Droid** cracking works on poisoned water |
| **D · THE TERMINATOR** | 80–100 | +22→+6 | perpetual twilight | the **Twilight Sea**, the **Gray Sea**, their shores · `Wasteland` · `AB_TarPits` · first `PoisonForest` (−18) at the seam | **Deepwater Compact** (the seas) · **Homestead** (shade-side condensation farms) · **Ascendant Helix** (seam outposts) · contested god-country — every landing here is a Council argument (`sacred_sites_pass_1.md`) |
| **E · THE DARK MARGIN** | 100–130 | +6→−30 | light failing | `AB_MycoticJungle` (−19) · `PoisonForest` (−18) · `BMT_FungalForest` (−24) · `HorrorWastes` (−49, upper edge) | **Ascendant Helix** (HorrorWastes first) · **Free Droid** hidden seats · nobody else can live here |
| **F · THE DEEP NIGHT** | 130–180 | −30→−80 | total dark; crags glow 0.34 | `AB_RockyCrags` (−45) · `HorrorWastes` (−49) · `AB_PropaneLakes` (−60) · `BMT_CrystalCaverns` (−62) | **the Forgotten Arsenal's leavings** · Helix · Free Droid · the player, hiding |

🔑 **Two barriers the matrix must respect** (`fauna_placement.md` R-H10): nightside biology
dies on the dayside and vice versa. **A GIANT BEAST row is band-locked**, and a
nightside carcass on a dayside tile is a continuity error, not colour.

### 1.2 Territory is faction × god

Twelve settlement-holding factions plus **UNCLAIMED** (the Junkers' "nobody's territory by
design", the dune-sea interior, the deep night) plus the **Forgotten Arsenal**, which holds no
tile but leaves things everywhere. Over that, `sacred_sites_pass_1.md`'s **god-country** read
(landmark > biome > arc-band) gives every tile a *voice* for its whisper: Sh'kaar (dayside
proper) · Oomo (water) · Rekko (ruins, salvage) · Mob'Unloo (roads, tolls) · Ta'Baa (open
dune sea) · Zizzik (wasteland, contamination) · Ohm (the Rust Cathedral, droid sites) · Ozzik
(the Ashfall Road, monuments) · Ishko (the deep night). **A row's god is which whisper table
it can join** (`↩W`), nothing more.

### 1.3 Biome is eight families, not twenty-four labels

Grouping from `biome_flora_rosters.md`: **dayside desert** (Desert · ExtremeDesert ·
AridShrubland · Badlands · Grasslands/Pyrelands · DesertOasis) · **contamination** (Wasteland
· TarPits) · **mycoid belt** (MycoticJungle · PoisonForest · FungalForest) · **river jungle**
(FeraliskInfestedJungle · MiasmicMangrove) · **frozen nightside** (RockyCrags · PropaneLakes ·
HorrorWastes · CrystalCaverns) · **volcanic** (Pyroclastic · Volcano · LavaField) · **machine
and scar** (MechanoidIntrusion · Scarlands) · **alien** (GelatinousSuperorganism ·
OcularForest) — plus **the three seas** (`Lake`/Ocean: the Scald, Twilight, Gray) which carry
no flora but do carry shores, shallows and wrecks.

---

## 2. THE STRUCTURAL MATRIX — biome family × territory × band → what appears

Read each cell as *"a tile of this family, inside this faction's country, in this band,
plausibly carries…"* — IDs point into §3. Cells marked `—` are **deliberately empty**
(a faction that does not go there); emptiness is content on this world.

### 2.1 Dayside desert family (`Desert` · `ExtremeDesert` · `AridShrubland` · `ZBiome_Badlands` · `ZBiome_Grasslands` · `ZBiome_DesertOasis`)

| territory | band A (Anvil) | band B (near-desert) | band C (margin) |
|---|---|---|---|
| **Galactic Empire** | GA1 GA2 GA3 IN14 IN15 SV12 TR14 SH13 XX9 | GA4 TR14 SV13 IN16 | GA5 (a checkpoint on the Homestead road) |
| **Hutt Cartel** | — | RS6 RS7 TR1 TR2 TR3 TR9 TR10 IN5 IN6 BR1 BR2 BR3 SH6 SH7 XX3 XX4 GA8 | TR9 TR10 |
| **Deep Desert Tribes** | RS10 RS11 GB1 GB2 SK1 SH8 SH9 BR6 XX10 | RS10 RS11 RS12 GB1 SK1 SK2 SH8 SH9 BR6 GA9 IN20 | — |
| **Jawa Trade Moot** | RS13 (crawler laager) | RS13 RS14 RS15 TR4 TR5 TR6 IN7 IN8 SV1 SV2 SV14 SH10 BR7 GA10 | RS14 |
| **the Junkers** | SV3 | RS16 RS17 SV1 SV3 SV4 SV5 SV15 TR7 IN9 BR8 GA11 XX11 | RS16 SV4 SV5 |
| **Blackstar Company** | — | RS18 TR8 GA12 SV16 BR9 | RS18 TR8 |
| **Homestead Defense League** | — | RS1 RS2 RS3 IN1 IN2 IN3 TR11 BR4 BR5 GA13 SH11 | RS1 RS2 RS3 RS4 IN1 IN2 IN3 IN4 TR11 TR12 BR4 BR5 GA13 SH11 XX5 |
| **Deepwater Compact** | — (rivers/Scald handled in 2.4) | RS19 (oasis pump-house) IN10 IN11 TR13 GA14 SH1 | IN10 |
| **Geonosian Foundry Hive** | RS20 IN12 IN13 SV6 BR10 GB3 GA15 | RS20 SV6 SV17 | — |
| **Free Droid Enclaves** | RS21 IN17 IN18 SV7 SH12 | SV7 | IN18 (cracking works on a poisoned pool) |
| **Wildsteam Clan** | — | — | — (their holds are the Scald's jungles, 2.4) |
| **Ascendant Helix** | — | SV8 (a derelict `GR_AbandonedLab`) | SV8 |
| **UNCLAIMED / Ta'Baa's dune sea** | NA1 NA2 NA3 NA4 GB1 GB4 GB5 SK1 SK3 SV9 SV10 SV11 SV18 SV19 XX1 XX2 GA6 GA7 | NA5 NA6 NA7 NA8 GB6 GB7 SK4 SV9 SV10 SV18 SH2 SH3 XX1 XX6 | NA6 NA9 SV9 SK5 |
| **Forgotten Arsenal leavings** | SV20 SV21 GA6 XX7 | SV20 XX7 | SV20 |

### 2.2 Contamination family (`Wasteland` · `AB_TarPits`) — bands C–D, Zizzik's country

| territory | what appears |
|---|---|
| **Free Droid Enclaves** | IN18 (hydrogen-cracking works on water they poisoned) · RS21 · SV7 · XX8 |
| **the Junkers** | RS16 (tailings warren) · SV4 (tailings) · SV22 (the tar-pit bodies, stripped) · TR7 |
| **Hutt Cartel** | IN5 (tar-seep pumping rig ↩F3) · IN19 (oil refinery on the tar, the owner's named example) · BR2 (tibbak tappers' camp) |
| **Ascendant Helix** | SV8 · XX12 (quarantine marker line) |
| **UNCLAIMED** | NA10 NA11 NA12 (the tar seeps with visible bones) · SK6 SK7 (what went in and did not come out ↩§8.4) · GB8 GB9 (tibbak herds, sizzik swarms) · SV23 (the truck that drove into the tar) · XX13 (Consortium labour-line remnants — no wild clade in Wasteland by ruling) |

### 2.3 Volcanic + machine-and-scar families (`AB_PyroclasticConflagration` · `Volcano` · `LavaField` · `AB_MechanoidIntrusion` · `Scarlands`) — band A, Sh'kaar / Ohm / Zizzik

| territory | what appears |
|---|---|
| **Galactic Empire** | IN15 (sterile scar wall-out — visible from orbit) · GA2 · SV12 |
| **Free Droid Enclaves** | RS21 (dormancy hall in cooled flow) · IN17 (geothermal battery bunker) · SH12 (a Rust Cathedral chapel) · SV7 |
| **Geonosian Foundry Hive** | IN12 IN13 (deep drills, condensate works) · GB3 (karrak war-caste kennel) · SV6 |
| **Hutt Cartel** | IN6 (helixien pocket tap ↩A4) · BR2 |
| **UNCLAIMED** | NA13 NA14 NA15 NA16 (lava layers, fumarole fields, obsidian flats, the Kiln crater) · GB10 GB11 (vaskarr — one exists; kessik packs) · SK8 (a cooked herd in a pyroclastic flow) · SV24 (`CoreDrill` as a found Volcanic-tile treasure) · SV25 SV26 (mechanoid intrusion wreckage, Purge-catalog carcasses) · XX14 (the migrating burn front — the Pyrelands) |

### 2.4 River-jungle family + the Scald (`AB_FeraliskInfestedJungle` · `AB_MiasmicMangrove` · dayside `Lake`) — band A/B, Oomo vs Sh'kaar

| territory | what appears |
|---|---|
| **Deepwater Compact** | RS22 RS23 (stilt house, pump-house) · IN10 IN11 (desalination plant, cistern battery) · TR13 (water depot) · GA14 · SH1 (shore-rite altar) · BR11 (scalefish hatchery) |
| **Wildsteam Clan** | RS24 RS25 (tree-freehold, sacred grove) · BR12 (wildpod herding camp) · GA16 (bowcaster watch) · SH14 · TR15 (trophy-and-hide post) |
| **Homestead** | RS3 (river-margin homestead) · IN2 |
| **UNCLAIMED** | NA17 NA18 NA19 (canopy-to-sand hard stop, the poison-to-clean river gradient, mangrove roots) · GB12 GB13 GB14 (wildpod, feralisk nests, chirrik-felled treeline) · SK9 (a wildpod that died standing) · SV27 (sunken wreck in the shallows) · XX15 (poison briar) · XX16 (quicksand / sink-silt) |

### 2.5 The terminator seas and their shores (Twilight Sea · Gray Sea · `Wasteland` shores) — band D, Oomo / Ishko

| territory | what appears |
|---|---|
| **Deepwater Compact** | RS22 RS23 RS26 (harbour village) · IN10 IN11 IN21 (tidal condensation array) · TR13 TR16 (fish market) · GA14 GA17 (harbour battery) · SH1 SH15 · BR11 BR13 |
| **Homestead** | RS4 (shade-side condensation homestead) · IN4 |
| **Ascendant Helix** | RS27 (seam outpost) · SV8 |
| **UNCLAIMED** | NA20 NA21 NA22 NA23 (bioluminescent shallows, salt crust, sea-fog band, the Dead Beacon ↩P14) · GB15 GB16 GB17 (reefback offshore, sando shallows, the great filter-feeders) · SK10 SK11 (a beached lanternwhale; a colossus skeleton the shore built round) · SV27 SV28 SV29 (sunken wrecks — the sea as the galaxy's largest scrap-heap, `the_seas.md` Lane 2) · XX17 (the Glimmer Field ↩W9) |

### 2.6 Mycoid belt (`AB_MycoticJungle` · `PoisonForest` · `BMT_FungalForest`) — bands D–E, contested → Ishko

| territory | what appears |
|---|---|
| **Ascendant Helix** | RS27 RS28 (lab compound, containment hall) · SV8 SV30 (`GR_BiomechanicalLab` derelict, escaped-experiment spoor) · BR14 (growth-vat hall) · GA18 · XX12 |
| **Free Droid Enclaves** | RS29 (hidden nightside seat) · IN22 (battery bunker on a geothermal seam) |
| **UNCLAIMED** | NA24 NA25 NA26 (glowing agarilux groves, the spore bubble ↩AB_AgariluxPrime, tinkle-grass fields) · GB18 GB19 (blizzarisk clutch, frostweaver galleries) · SK12 (spore-hollowed carcass) · SV31 (a Helix retrieval party that did not come back) · XX18 (the Listening Dark ↩W2) |

### 2.7 Frozen nightside (`AB_RockyCrags` · `AB_PropaneLakes` · `HorrorWastes` · `BMT_CrystalCaverns`) — band F, Ishko

| territory | what appears |
|---|---|
| **Ascendant Helix** | RS28 · SV30 · GA18 |
| **Free Droid Enclaves** | RS29 · IN22 · SH12 |
| **Forgotten Arsenal leavings** | SV20 SV21 SV32 (a vault forecourt ↩P9, a sleeping war-form's shell, the mega-structure patch) · GA19 (dormant guardian line) · XX19 (the Sleeper's Knock ↩W21) |
| **UNCLAIMED** | NA27 NA28 NA29 NA30 NA31 (crystal fields, the propane lakes, flash-frozen trees, crag defiles, the last self-glowing landscape) · GB20 GB21 GB22 (hoarfrost mastodon, frostbound behemoth, crag manhunters) · SK13 SK14 (a frozen herd; the Arsenal's own casualties) · SV33 (the crashed heater-convoy — the player's own future) · IN23 (a dead heater station ↩P19 the Cistern) · XX20 (propane as fuel that kills by cold) |

### 2.8 Alien family (`AB_GelatinousSuperorganism` patches · `AB_OcularForest` × 3 tiles) — patches only

| territory | what appears |
|---|---|
| **Ascendant Helix** | RS27 (the one ocular-forest outpost on the Scald's mountainous shore) |
| **UNCLAIMED** | NA32 NA33 (the slime that is one organism; the red spore-stream headwaters) · GB23 (sookal — the oasis is calm because they make you calm) · SK15 (bones the superorganism is still digesting) · XX21 (the Wrong Spark ↩W4 — nothing mechanical works right here) |

---

## 3. THE CATALOGUE BY CATEGORY

Columns: **biome(s)** (family or defName) · **territory** · **band** · **fodder** (mods/defs)
· **feas.** Entries already in the catalogue or roster are cross-referenced, not restated.

### 3.1 RESIDENTS & HOMES — who lives here and in what (RS)

_Each row is one `InhabitedPlaceDef` (cast + routine + larder + stock) over one or more
districts. The fate lever — stays, flees, sells, fights — is what makes two identical huts
two different tiles._

| ID | augmentation | biome(s) | territory | band | fodder | feas. |
|---|---|---|---|---|---|---|
| RS1 | **Humble abode** — one room, one vaporator, one family, a dog. The baseline "someone lives here" | Desert · AridShrubland | Homestead | B–C | `dwelling.lua` (ships) · `KotOR_MoistureVaporator_big` · Uncle Boris cots · a `Jawa_Homestead_Grunt` pair + child | 🔶 template exists; PlaceDef needed |
| RS2 | **Moisture-farm homestead, occupied** ↩B1 flipped from abandoned to lived-in: vaporator ring, cistern hut, walled yard, militia rifle by the door ↩P1 | Desert · AridShrubland | Homestead | B–C | + `KotOR_watertank`, `Sandbags`, `Jawa_Homestead_Heavy` well-guard | 🔶 |
| RS3 | **Family compound** — three generations, three huts round a shared cistern, a workshop, a pen | AridShrubland · river margin | Homestead | B–C | RS1 ×3 + `nursery.lua` + BR4 pen | 🔶 |
| RS4 | **Shade-side condensation homestead** — the terminator's second water mechanism made a house: condensers on the dark wall, greenhouse on the lit one | Wasteland shore · terminator | Homestead | D | condenser props (VFEPD `Ancient*` tank family) · `Plant_Nightgrass` bed | 🔶 |
| RS5 | **The hermit** — one pawn, one hole in a mesa, thirty years of hoarded parts, will not trade, will talk | Badlands · Crags | UNCLAIMED | B, F | a single `CharacterDef` with a `Resident` fate; `Hollow`/`Caves` mutator | 🔶 |
| RS6 | **Hutt palace annexe** — the *beside-the-oasis* rule made a tile: throne room, walled cistern, kennel yard, Gamorrean gate | DesertOasis-adjacent | Hutt | B | `CastRoster_HUTT` · Torment Master (`Brazen Bull` etc. as court dressing) · `Effigy` terror spike at the gate · Fortifications `AM_Palisade` | 🔶 ⚠️ palace-only rule binds (`tidally_locked_world.md` "palaces only") |
| RS7 | **Hutt dry service post** — one of the 11 non-oasis holdings: a skimhouse, a spicehouse, a casino, each a different district recipe | Desert · Badlands, on a road | Hutt | B | `CastRoster_HUTT` · Torment `Auto-Vending Machine` · Outer Rim furniture · `Stuff on Tables` clutter | 🔶 — **11 posts = 11 templates**, the second-largest template ask |
| RS8 | **Squatters in someone else's ruin** — a family living inside an `AncientWarehouse` shell, tarp roofs over the good corner | Desert · Badlands | UNCLAIMED → Junkers | B | vanilla `AncientWarehouse` landmark ↩E2 + `dwelling.lua` inside its walls | 🔶 |
| RS9 | **The refugee camp** — a dozen tents at a dry well, half a faction's worth of species, nothing to sell, something to ask | AridShrubland | Homestead edge / UNCLAIMED | B–C | Uncle Boris "planetside camp" pack · `PrimitiveWell` · mixed cast | 🔶 |
| RS10 | **Tusken stone-hut camp** — three domes in a canyon mouth, bantha corral, concealed cistern, funeral pyre ash | Badlands · Desert canyon | Deep Desert Tribes | A–B | `CastRoster_TUSKEN` · Tribal Furniture · `PrimitiveWell` hidden · SW bantha | 🔶 |
| RS11 | **Tusken cave-hold** — a `Caves`-mutator tile whose cave mouth is walled with rock and stakes; nobody home by day | Badlands · Crags-edge | Deep Desert Tribes | A–B | `Caves` mutator · stake barricades (`Barricade`) | 🔶 |
| RS12 | **The camp in the scar behind the burn** — Tuskens following the Pyrelands' fire front, tents on fresh ash | ZBiome_Grasslands | Deep Desert Tribes | A | RS10 furniture on `BurnedTree` / ash terrain · fate `FleeIfThreatened` | 🔶 |
| RS13 | **Crawler laager** — a Jawa sandcrawler parked, ramp down, awning out, a market on the sand ↩P6's living twin | ExtremeDesert · Desert | Jawa Trade Moot | A–B | the fallen-crawler hull art (P6) upright + `CastRoster_JAWA` + TR4 | 🆕 hull art; 🔶 cast |
| RS14 | **Ridge-cave clan hold** — Jawa fortress in a canyon wall, still-condensers on the ridge, buried cistern | Badlands · Desert | Jawa Trade Moot | B | `Caves` · crawler-still props (KotOR tank family) · Ugnaught smithy | 🔶 |
| RS15 | **The wreck-field settlement** — Jawa clan living IN a wreck, hull plates as walls ↩P5 | Desert | Jawa Trade Moot | B | VFEPD destroyed family (`VFEPD_DestroyedLargeThruster`…) · `VGE_DamagedSubstructure` terrain · `dwelling.lua` | 🔶 |
| RS16 | **Junker warren** — the dwelling cluster template on tailings: lean-tos against a spoil heap | Badlands · Wasteland | Junkers | B–C | `junkers_dwelling_cluster.txt` **ships** · `ChunkSlagSteel` heaps | ✅ template exists |
| RS17 | **Gamorrean breeding colony** — a warren that is also a farm; see BR8 | Badlands | Junkers | B | `CastRoster_JUNKERS` + BR8 | 🔶 |
| RS18 | **Blackstar rough outpost** — a walled yard, a repair bay, two cells, a landing scorch; no one answers the gate | road junction, any dry biome | Blackstar | B–C | Fortifications `AM_Entrance_Bunker` · Security Doors Expanded · `CastRoster_BLACKSTAR` | 🔶 |
| RS19 | **Oasis pump-house** — the Compact's one-building presence at a lesser oasis: pump, guard, ledger | DesertOasis | Deepwater | B | `MoisturePump` · `AncientPipelineSection` · `Jawa_Deepwater_Grunt` shore guard | 🔶 |
| RS20 | **Foundry surface mouth** — the hive's only visible piece: a ramp into rock, chitin baffles, a drone on watch, ore stockpile | Badlands · Volcano · ExtremeDesert | Geonosian | A–B | VFE-Insectoids 2 hive props (enemy hives kept, player vats stripped) · `CastRoster_GEONOSIAN` | 🔶 ⚠️ Insectoids-2 cherry-pick prerequisite |
| RS21 | **Droid dormancy hall** — a roofed slab, charging pylons, six chassis standing in the dark, one awake | LavaField · Crags · Wasteland | Free Droid Enclaves | A, E–F | `CastRoster_DROIDS` · charging props (VFEPD industrial family) · no larder needed — droids drink nothing (water doctrine 1) | 🔶 |
| RS22 | **Stilt house on the shallows** — a Compact fisher family over the water, boat racked, nets | Scald / sea shores | Deepwater | A, D | Odyssey fishing zones · Vehicle Framework watercraft (mobility only) · `Plant_Reeds` | 🔶 |
| RS23 | **Harbour pump-house** — the desalination front door: a plant, a queue of empty jugs, a Selkath warden | sea shores | Deepwater | A, D | `MoisturePump` · Compact `Jawa_Deepwater_Specialist` | 🔶 |
| RS24 | **Wildsteam tree-freehold** — an open hold built INTO the deep jungle trees, communal hall, no walls, bowcaster racks | FeraliskInfestedJungle | Wildsteam | A | `AB_JungleTree` as structure anchors · `CastRoster_WILDSTEAM` | 🔶 (tree-integrated build is a template problem, not a def problem) |
| RS25 | **Sacred grove hold** — a freehold whose centre is a ring of `AB_KeeningCordax`, tended | FeraliskInfestedJungle | Wildsteam | A | flora roster defs · SH14 | 🔶 |
| RS26 | **Harbour village** — five stilt houses, a pump-house, a fish market, a battery; the Compact's real face | Twilight / Gray Sea shore | Deepwater | D | RS22 ×5 + RS23 + TR16 + GA17 | 🔶 — the largest single Deepwater manifest |
| RS27 | **Helix seam outpost** — sterile prefab, airlock door, a growth vat humming, three pawns who do not want you there | PoisonForest · OcularForest | Ascendant Helix | D–E | `CastRoster_HELIX` · biosculpter/vat props (Biotech) · Security Doors | 🔶 |
| RS28 | **Containment hall** — Helix, but the thing inside the walls is the resident | HorrorWastes · MycoticJungle | Ascendant Helix | E–F | Anomaly containment furniture · one `GR_` hybrid | 🔶 |
| RS29 | **Hidden nightside seat** — Free Droids where no organic follows; the lights are on for nobody | Crags · PropaneLakes | Free Droid Enclaves | E–F | RS21 + IN22 | 🔶 |
| RS30 | **The abandoned home** — every RS row above with the cast removed and the larder left: beds made, a meal on the table, no one | any | any | any | same template, `castSize 0` | ✅ trivially — the cheapest variant in the file, and the eeriest |
| RS31 | **The wrong resident** — a Homestead-style farmhouse whose cast is Junkers: the family is gone and the squatters are eating their stores | AridShrubland | Homestead country | B–C | RS2 template + `CastRoster_JUNKERS` | 🔶 — a cast swap; zero new content |

### 3.2 INFRASTRUCTURE & MACHINERY (IN)

_The owner's named examples first. Every "working" machine here is **found, never
buildable** — `designationCategory` strip, not Cherry Picker (catalogue §5)._

| ID | augmentation | biome(s) | territory | band | fodder | feas. |
|---|---|---|---|---|---|---|
| IN1 | **Moisture farm, working** — the vaporator field itself as infrastructure: 6–12 units on a grid, wires to a hut | Desert · AridShrubland | Homestead | B–C | `KotOR_MoistureVaporator_big` · `PowerConduit` · `Battery` | ✅ |
| IN2 | **Cistern + windpump** — a buried tank, a wind turbine, a tap the whole valley walks to | AridShrubland · river margin | Homestead | B–C | `KotOR_watertank` · `WindTurbine` · `MoisturePump` | ✅ |
| IN3 | **Sandbag perimeter with a bell** — Homestead's whole defence doctrine: no walls, a bell for the kraddak | Desert · AridShrubland | Homestead | B–C | `Sandbags` · MiningCo `Alert speaker` (the bell) | ✅ |
| IN4 | **Shade-wall condenser array** — the terminator's condensation harvested: a long wall on the dark side dripping into a trough | Wasteland shore | Homestead | D | VFEPD `AncientFuelTank`/tank props as condensers · `AncientPipelineSection` | 🔶 — props exist; a real condensing building is 🆕 |
| IN5 | **Tar-seep pumping rig** ↩F3 — working, with a tapper's shack | AB_TarPits | Hutt | C–D | `AncientDrillPlatform` · `AncientExcavator` · `AB_Tar` | ✅ |
| IN6 | **Helixien pocket tap, working** ↩A4 — gas geyser + generator + pipe + tank, unwalled, **wires running off the map edge** to a settlement one tile over | ExtremeDesert · Wasteland · Volcano | Hutt / Free Droid | A–C | `VHGE_GasGeyser` · `VHGE_HelixienGenerator` · `VHGE_HelixienPipe` · `VHGE_GasTank` · conduit to map edge | ✅ ⚠️ Helixien pump strip prerequisite (`required_mods.md:489`) |
| IN7 | **Crawler-still condenser** — the Jawa water tech: a salvaged still on a ridge, drip line down to a jug | Desert · Badlands | Jawa Trade Moot | B | KotOR tank family · `Filth_MachineBits` | 🔶 (a "still" ThingDef is 🆕; a dressed tank is ✅) |
| IN8 | **Scrap smelter, banked** — a smelter still warm, slag heaps, a droid arm in the feed hopper | Desert · Badlands | Jawa Trade Moot / Junkers | B | `ElectricSmelter` · `ChunkSlagSteel` · `Filth_MachineBits` | ✅ |
| IN9 | **Casket-foundry** — the Junkers' one industry: an open forge, warcasket shells on racks | Badlands | Junkers | B | `FueledSmithy` · warcasket apparel as items on racks | ✅ |
| IN10 | **Desalination plant** — the Compact monopoly made a building; pipes to a cistern battery; a queue | shores, DesertOasis | Deepwater | A, B, D | `MoisturePump` ×n · `AncientPipelineSection` · `KotOR_watertank` battery | 🔶 |
| IN11 | **Cistern battery with EMP traps** — the Compact's layered defence around the water | shores, oasis | Deepwater | A, B, D | tanks · `TrapIED_EMP` | ✅ |
| IN12 | **Deep drill field** — Foundry ore extraction: 3–4 drills, conveyor of ore, chitin windbreaks | Badlands · Volcano | Geonosian | A–B | `DeepDrill` · ore chunks · `ChunkSlagSteel` | ✅ |
| IN13 | **Deep-rock condensate works** — Geonosian water from stone: a pump in a fissure | Volcano · ExtremeDesert | Geonosian | A | `MoisturePump` in a `Caves` mouth | ✅ |
| IN14 | **Imperial atmospheric condenser** — the Empire trucks its water, and where it cannot, it makes it: a tower and a reservoir bunker | ExtremeDesert | Empire | A | VFEPD industrial tower props · `KotOR_watertank` · `CastRoster_EMPIRE` | 🔶 |
| IN15 | **The sterile scar** — the Empire's wall-it-out fire strategy: a firebreak trench a whole map wide, burned dead, a sensor post | ZBiome_Grasslands · Pyroclastic | Empire | A | `BurnedTree` · `Ash` terrain paint · `AncientUplink` | 🔶 terrain paint proven |
| IN16 | **Drop-pod battery** — a landing grid, fuel, a beacon | Desert | Empire | B | `ShipLandingBeacon` · `Chemfuel` · MiningCo landing pad | ✅ |
| IN17 | **Geothermal battery bunker** — Free Droid power on a hot seam: one `GeothermalGenerator`, twenty batteries, a door | LavaField · Volcano | Free Droid | A | `SteamGeyser` · `GeothermalGenerator` · `Battery` ×20 · Security Door | ✅ |
| IN18 | **Hydrogen-cracking works** — the Enclaves' poisoned pool: a rig on a pond, the water toxic, the tile a standing hazard | Wasteland | Free Droid | C | `PoisonMud`/`NuclearWaste` terrain ↩B2 · `AncientDrillPlatform` | ✅ terrain + props |
| IN19 | **Oil refinery on the tar pits** — the owner's named example: Rimefeller derricks on `AB_Tar`, a cracker, a loading bay, storage, a tapper crew | AB_TarPits · Wasteland | Hutt | C–D | `OilWell` · `DeepOilWell` · `DerrickDrill` · `CrudeCracker` · `OilStorage` · `RefineryLoadingBay` ↩F4 | ✅ ⚠️ **F4's buildability strip has never been applied** |
| IN20 | **The hidden cistern** — Tusken water: nothing on the surface but a stone lid; digging it out is the reveal ↩W1's shape | Desert · Badlands | Deep Desert Tribes | A–B | `KotOR_watertank` buried under `Sand` paint | 🔶 |
| IN21 | **Tidal condensation array** — the Compact's terminator engineering: a shore-long rack condensing sea fog | Twilight / Gray shore | Deepwater | D | IN4 props on a shore | 🔶 |
| IN22 | **Nightside battery bunker** — Free Droid, but the batteries are also the heater | Crags · PropaneLakes | Free Droid | E–F | IN17 + `Heater` ×n | ✅ |
| IN23 | **Dead heater station** — a waystation for crossing the dark: heaters, fuel racks, all cold ↩P19 | Crags · HorrorWastes | UNCLAIMED | F | `Heater` · `Chemfuel` · `PassiveCooler` inverted (dressing) | ✅ props; the station as a working lifeline is 🔶 |
| IN24 | **Comms mast** — a working uplink on a hill with a shed ↩P7; **using it raises Visibility** | any elevated | Empire / Blackstar / Ohm country | any | `AncientUplink` mutator · `CommsConsole` | ✅ |
| IN25 | **Relay chain** — three masts on three tiles in a line; the middle one is the one you can reach | Desert · Badlands | Empire | A–B | IN24 ×3 across tiles | ✅ (a map authoring pattern, not new content) |
| IN26 | **Drilling laser, still running** — the MiningCo drill turret chewing a rock face, ore piling up unclaimed | Badlands · Volcano · Crags | UNCLAIMED / Junkers | any dry | MiningCo `DrillTurret` (immobile; "found-already-running = ideal salvage flavour") | ✅ ⚠️ strip buildability |
| IN27 | **Mining rig, abandoned mid-shift** — Ancient Mining Industry's screening line, belts stopped, one lamp still on | Badlands | Junkers / UNCLAIMED | B–C | Ancient Mining Industry props (**"do NOT build it"** — furniture only) | ✅ ⚠️ |
| IN28 | **Solar field** — a hundred panels facing the sun that never moves; half sand-buried | ExtremeDesert · Desert | Empire / Hutt / UNCLAIMED | A–B | `SolarGenerator` ×n · `Sand` paint over half | ✅ — Sh'kaar's country taxes and pays in the same coin ↩W7 |
| IN29 | **Wind farm on the terminator** — the only band with weather has the only wind: turbines on a ridge | Wasteland · shores | Homestead / Deepwater | D | `WindTurbine` ×n | ✅ |
| IN30 | **The Kiln** ↩P11 — a geothermal works half-alive, contested Ohm vs Sh'kaar | Volcano · Pyroclastic | Hutt (the Kiln blast-zone is theirs) | A | `SteamGeyser` · `GeothermalGenerator` · slag · crater terrain | 🔶 |
| IN31 | **Propane tap** — a pump on a propane lake, feeding a heater ring: the deep night's one economy | AB_PropaneLakes | UNCLAIMED / Free Droid | F | `AB_PropaneLake` terrain · `AncientDrillPlatform` · `Heater` | 🔶 (a propane-fuel building is 🆕; the dressing is ✅) |
| IN32 | **Automated biofuel plant, still running** ↩A9 | Desert · AridShrubland | Hutt | B | `VFEFactory_AutomatedBiofuelRefinery` | ⚠️ pillar check owed |
| IN33 | **Power line off the map edge** — no source on this tile at all: just pylons and conduit crossing it, live, from somewhere to somewhere. Tapping it is theft from a named faction | any | any owned territory | any | `PowerConduit` line + a `Battery` at the edge; the "somewhere" is the adjacent settlement tile | ✅ — the cheapest "this land is used" signal in the file |
| IN34 | **Pipeline crossing** — the same, in Rimefeller/Helixien pipe: a pipeline cutting the map corner to corner | Desert · Wasteland | Hutt / Empire | B–C | `VHGE_HelixienPipe` or `AncientPipelineSection` run | ✅ |
| IN35 | **Fuel dump** — a fenced lot of `Chemfuel` barrels and `VFEPD_AncientFuelTank`s, one guard | road tiles | Blackstar / Hutt / Empire | B | ✅ | ✅ |
| IN36 | **The Ashfall Battery** ↩P17 — launch-fuel farm on an `AncientLaunchSite` | Desert | Ta'Baa country | B | existing mutator + fuel room | 🔶 |

### 3.3 TRADING OPPORTUNITIES (TR)

_A `stock` list on a PlaceDef + a cast with `trades: true`. **A tile is a shop if it contains
someone who deals** (`InhabitedCastDef.cs` framing)._

| ID | augmentation | biome(s) | territory | band | fodder | feas. |
|---|---|---|---|---|---|---|
| TR1 | **Tiny trading outpost** — one counter, one dealer, one guard, one thing they are known for | any dry, near a road | Hutt / Moot / Blackstar | B | PlaceDef `stock` + `stockLabel` — **the exact shape `RM_InhabitedPlace_Scrapyard` already proves** | ✅ mechanism live |
| TR2 | **Hutt toll post** — a gate across the road with a price on it; pay, fight, or go round through the dunes | Desert · Badlands road | Hutt (Mob'Unloo) | B | Fortifications `FT_PalisadeGate` · `AM_Entrance_Bunker` ↩D2 · `CastRoster_HUTT` | 🔶 ⚠️ faction-defender question ↩§6.1 — **now answerable: the cast IS the defenders** |
| TR3 | **Hutt market post** — awnings, stalls, a slave-block (Torment Master) the player can choose not to look at | Desert | Hutt | B | Outer Rim furniture · Torment `Live Target Range` · `Stuff on Tables` | 🔶 |
| TR4 | **Jawa crawler market** — RS13's ramp-down sale: droid parts, restraining bolts, one thing that should not be for sale | ExtremeDesert · Desert | Jawa Trade Moot | A–B | `CastRoster_JAWA` · droid-part items (KotOR/Outer Rim droid depot) | 🔶 |
| TR5 | **Claim marker cache** — Jawa salvage claim: a painted post and a locked crate. Take it and Rekko's "Old Reasons" ↩W3 fires | Desert | Jawa Trade Moot | B | `AncientMetalCrate` · a signpost prop | ✅ |
| TR6 | **Scrap-Singer's stone** — the quest-giver elder sitting on the same rock every day | Desert · Badlands | Jawa Trade Moot | B | `Jawa_TradeMoot_Specialist` with a `Resident` fate and no stock — **a shop that sells quests** | 🔶 |
| TR7 | **Junker depot** — the template ships; bribable, never trading | Badlands | Junkers | B | `junkers_depot.txt` **ships** | ✅ |
| TR8 | **Blackstar contract board** — a bunker with a board of bounties; some of them are you | road junction | Blackstar | B–C | RS18 + a `CommsConsole` dressed as the board | 🔶 |
| TR9 | **Caravan rest-stop** — a well, a wall, shade, a fee; caravans of three factions asleep in it at once | Desert · AridShrubland road | Hutt / neutral | B–C | `PrimitiveWell` · Uncle Boris cots · multi-faction cast (`Peaceful` group makers) | 🔶 — a *mixed-faction* cast is the novel bit |
| TR10 | **Warehouse along a road** — a locked `AncientWarehouse` with a Hutt factor's mark and a Gamorrean asleep on the step | Desert road | Hutt | B | vanilla `AncientWarehouse` ↩E2 + one guard | ✅ |
| TR11 | **Homestead farm-gate stall** — a table, a jar, an honesty box: produce and water for silver, nobody watching | AridShrubland | Homestead | B–C | `Table` · `stock` of vegetables/water items | ✅ |
| TR12 | **Well-keeper's tap** — the Iktotchi warden sells water by the jug from a locked spigot | AridShrubland | Homestead | C | `Jawa_Homestead_Specialist` + `KotOR_watertank` | 🔶 |
| TR13 | **Compact water depot** — the monopoly's retail face: jugs in, silver out, a Water Warden watching the queue | shores · oasis | Deepwater | A–D | RS23 + `stock` water items | 🔶 |
| TR14 | **Imperial requisition post** — not a shop: a board of what the Empire will pay for, and what it will take. Trading here raises pursuit heat ↩P21 | Desert | Empire | A–B | `CastRoster_EMPIRE` officer · Imperial waystation prefab | 🔶 |
| TR15 | **Wildsteam hide-and-trophy post** — skins, bowcaster bolts, a wildpod tusk you cannot afford | jungle edge | Wildsteam | A | `Jawa_Wildsteam_Grunt` hunter + `stock` leathers | 🔶 |
| TR16 | **Fish market** — the harbour's morning: scalefish on ice, yobshrimp in baskets | sea shores | Deepwater | D | Odyssey fish items · `sea_beasts_roster.md` scalefish once defs exist | 🔶 / 🆕 sea-beast defs |
| TR17 | **Droid parts bazaar** — Free Droids selling components to organics, at arm's length, through a hatch | Wasteland · LavaField | Free Droid | A, C | `CastRoster_DROIDS` protocol droid `trades: true` | 🔶 |
| TR18 | **Fuel stop** — Chemfuel and Helixien by the barrel, the only one for six tiles; the price says so | Desert road | Hutt / Blackstar | B | IN35 + a dealer | 🔶 |
| TR19 | **Kennel market** — one of the 11 Hutt posts: beasts for sale, some of them stolen from you last season | Desert | Hutt | B | BR1 + a dealer | 🔶 |
| TR20 | **The dead drop** — a strongbox under a marked stone, a ledger page: Mob'Unloo's Debtor's Cache ↩W8 as a *trade* — leave silver, come back for goods | any road | Blackstar / Hutt | B–C | `AncientMetalCrate` + a scripted swap (C#) | 🆕 small C# |
| TR21 | **Salvage broker's yard** — a Junker who DOES trade, alone among his kind, because he owes the Hutts | Badlands | Junkers / Hutt | B | `junkers_scrapyard.txt` + `trades: true` on the boss | ✅ cast flag |
| TR22 | **Paleontologist's camp** — Biomes! Fossils trader kinds camped on a fossil bed, buying bones | ExtremeDesert · salt flat | UNCLAIMED | A–B | `BMT_Caravan_Paleontologist` kinds · `BMT_MineableFossils` | ✅ |
| TR23 | **The trader ship, landed** — a Trader Ships vessel on its pad, ramp down, for three days | Desert | Hutt / neutral | B | Trader Ships (`automatic.traderships`) landing | ✅ mod behaviour; placement as a *tile fixture* is 🔶 |

### 3.4 SALVAGE OPPORTUNITIES (SV)

_Rekko's country. **The verb is strip; the reward is parts** (catalogue §7.4). Most of the
1,828 `VFEPD_` props and the whole vanilla `Ancient*` family live here._

| ID | augmentation | biome(s) | territory | band | fodder | feas. |
|---|---|---|---|---|---|---|
| SV1 | **Crashed hauler** ↩C1 | any desert | UNCLAIMED / Moot | A–C | `AncientIndustrialTruck` · `AncientMetalCrate` · `Filth_MachineBits` | ✅ |
| SV2 | **Downed gravship section** ↩C2 | Desert · ExtremeDesert · Badlands | UNCLAIMED | A–B | VFEPD destroyed family · `VGE_DamagedSubstructure` | ✅ |
| SV3 | **Junkyard drift** ↩C3 — 15× junk | Desert · Scarlands · Wasteland | Junkers | A–C | `TileMutatorDef Junkyard` (global, 1%) | ✅ retune |
| SV4 | **Tailings field** — worked-out Geonosian mining ground the Junkers squat (the Claim Jump's own premise) | Badlands | Junkers | B–C | `ChunkSlagSteel` · ore chunk scatter · `MineralRich` mutator inverted (depleted) | ✅ |
| SV5 | **The scrapyard** — the template ships | Badlands | Junkers | B | `junkers_scrapyard.txt` | ✅ |
| SV6 | **Sonic-blaster wreckage** — a Foundry skirmish site: chitin shards, drone carapaces, a jammed sonic cannon | Badlands · Volcano | Geonosian edge | A–B | Insectoids 2 carcass/prop defs · `CastRoster_GEONOSIAN` weapon items | 🔶 |
| SV7 | **Dead droid field** — a dozen chassis face-down in the sand where a memory-wipe convoy was hit; one still twitches | Wasteland · LavaField | Free Droid edge | A, C | droid corpses (Outer Rim / KotOR droid kinds as corpses) · `Filth_MachineBits` | ✅ spawn-as-corpse |
| SV8 | **Derelict Helix lab** — `GR_AbandonedLab` / `GR_BiomechanicalLab` as a tile fixture: vats cracked, a cage open | any | Helix leavings (world-wide) | any | the two `GR_` derelict site shapes | ✅ mod ships the shape; hand-placing it is 🔶 |
| SV9 | **Dead caravan** — six pack animals and their drivers where the water ran out; the cargo is intact. **Someone will come for it** ↩W3 | ExtremeDesert · Desert | UNCLAIMED | A–B | SW bantha corpses · caravan cargo items · a `Jawa_*` corpse set | ✅ corpses + items |
| SV10 | **Battle site, fresh** — two factions' dead where they fell, weapons still in hands, a smoke column | Desert · AridShrubland | contested borders | B | corpses of two `CastRoster`s · `Filth_Blood` · `Custom Gas Types` residue | ✅ — `[SR]Factional War` makes these emergently; this is the *authored* one |
| SV11 | **Battle site, old** — the same, a decade on: sand-scoured bones, rusted rifles (`Awful`), a helmet | Desert | UNCLAIMED | A–B | skeleton corpses (`Corpse` rotted) · `ChunkSlagSteel` · deteriorated weapons | ✅ |
| SV12 | **Imperial convoy wreck** — an `LG-3 Draywork` smokebeast and its crates, ambushed; the Empire's attack surface made a site (`Alien_Bestiary.md` 3.13) | ExtremeDesert · Desert | Empire routes | A–B | VGE mech corpse · `AncientMetalCrate` · Imperial gear items · VehicleRaid vehicle wreck if the framework spawns disabled vehicles | 🔶 / 🆕 vehicle-wreck state |
| SV13 | **Crashed TIE / shuttle** — a small Imperial craft nose-down in a dune, pilot still strapped in | Desert | Empire airspace | A–B | KotOR Ships VGE hull art · VFEPD thruster props · one `Jawa_Empire_Grunt` corpse | 🔶 hull art is a ship-pack reskin |
| SV14 | **Crawler graveyard** — three dead sandcrawlers nose to tail ↩P6 ×3: the Moot's own mass grave of machines | Desert | Jawa Trade Moot | B | P6 hull ×3 | 🆕 hull art (shared with P6) |
| SV15 | **Warcasket rack** — Junker armour on stands, the wearers gone; **only salvageable from corpses, never player-built** — so these are on corpses | Badlands | Junkers | B | warcasket apparel on `Jawa_Junkers_Heavy` corpses | ✅ |
| SV16 | **The hunter's last kill** — a Blackstar tracker dead beside the thing he was hunting; both are loot | any | Blackstar | B–C | `Jawa_Blackstar_Specialist` corpse + a megafauna corpse | ✅ |
| SV17 | **Abandoned mining seam, tools and ore** — the owner's named example: a `MineralRich` vein half-worked, picks, a cart, ore in bags, a lamp | Badlands · Crags · Volcano | UNCLAIMED / Junkers | any dry | `MineralRich` mutator · Ancient Mining Industry props · ore items · `Jawa_Junkers_Grunt` corpse (the reason it was abandoned) | ✅ |
| SV18 | **Meteoric metal field** ↩C5 | ExtremeDesert · Badlands | UNCLAIMED | A–B | `ChunkSlagSteel` + `MineralRich` | ✅ |
| SV19 | **Podracer wreck** ↩P4 | dune sea | Ta'Baa | A | engine-pod props | 🆕 small |
| SV20 | **Arsenal wreck** — a mechanoid cluster that lost: shattered `Mech_*` hulks, a dead assembler, sand in everything | Desert · Crags | Forgotten Arsenal leavings | any | vanilla mech corpses · `AncientMechDropBeacon` · `GenStep_ScatterAncientMechs` ↩C4 | ✅ |
| SV21 | **The mega-structure patch** — the ONE (`the_forgotten_war.md`): sacred to the Free Droids; not a salvage site, a place you are watched salvaging | Crags | Ohm country | F | authored one-off | 🆕 arc-critical, out of scope here — listed so nobody re-derives it |
| SV22 | **Tar-pit bodies, stripped** — a Junker crew has already been at the tar: ropes, a winch, half a skeleton pulled out | AB_TarPits | Junkers | C–D | `AB_TarPuddle` · skeleton corpses · `Winch`-shaped prop (VFEPD) | ✅ |
| SV23 | **The truck that drove into the tar** ↩SV1 in `AB_Tar` — cab above the surface, cargo below | AB_TarPits | UNCLAIMED | C–D | `AncientIndustrialTruck` on `AB_Tar` | ✅ |
| SV24 | **CoreDrill, found** — the cut buildable surviving as a Volcanic-tile treasure (`required_mods.md`) | Volcano · LavaField | UNCLAIMED | A | `CoreDrill` unbuildable | ✅ ⚠️ strip |
| SV25 | **Mechanoid intrusion wreckage** — `AB_MechanoidIntrusion`'s own furniture, plus a dead Purge-catalog `PX-4 Bulwark` | AB_MechanoidIntrusion | Empire / Arsenal | A | biome's own scatter · VGE mech corpse | ✅ |
| SV26 | **Scarlands rig** — Odyssey's toxic-industrial read with a Rimefeller cracker rusted through | Scarlands | UNCLAIMED | A | `CrudeCracker` · `OilStorage` · `ScarlandsJunkClusters` pattern | ✅ |
| SV27 | **Sunken wreck in the shallows** — a hull half out of the water, reachable at low silt; Rekko's tithe (`the_seas.md` Lane 2) | shores · shallows | UNCLAIMED | A, D | VFEPD destroyed family on `WaterShallow` · fishing zone round it | ✅ props; underwater reach is the Depths' v2 |
| SV28 | **Beached gravship** — a whole hull on a shore, keel split, a Compact salvage claim painted on it | Twilight / Gray shore | Deepwater | D | SV2 ×3 + a Compact guard | 🔶 |
| SV29 | **Orbital ring segment in the sea** ↩P20 — the Broken Ring's other half, a reef now | Gray Sea | UNCLAIMED | D | P20 art | 🆕 |
| SV30 | **Escaped-experiment spoor** — not a wreck: a Helix transport crate split open from inside, tracks leading into the fungus | MycoticJungle · HorrorWastes | Helix | E–F | `AncientMetalCrate` broken · `Filth_Blood` trail · one `GR_` hybrid alive on the map | ✅ |
| SV31 | **The retrieval party** — six Helix agents in Excellent gear, frozen mid-stride: the cold got them first | Crags · FungalForest | Helix | E–F | `Jawa_Helix_Grunt` corpses (min Excellent gear — **the richest corpse loot on the planet**) | ✅ |
| SV32 | **Vault forecourt** ↩P9 — a sealed door, a plaza, nothing opens | Crags · Badlands | Arsenal | B, F | authored | 🆕 (dungeons arc) |
| SV33 | **The heater convoy that stopped** — six heaters on sledges, fuel gone, a Wookiee crew that almost made it | Crags | UNCLAIMED | F | `Heater` ×6 · `Jawa_Wildsteam_*` corpses (furred — they lasted longest) | ✅ |
| SV34 | **Ancient urban block** — AUR's multi-building city ruin as a tile fixture, walls with real HP (Hit Point) | Badlands · Wasteland | Rekko country | B–C | Ancient Urban Ruins + AURAD + Hit Point (install at worldgen only) | ✅ mod-driven; ⚠️ worldgen-time install note |
| SV35 | **Drone scrapyard** — VQE Drone Factory's derelict robotics warehouse | Wasteland | Free Droid edge / Arsenal | C | VQE Drone Factory site shape (**never build a drone workforce**) | ✅ ⚠️ |
| SV36 | **Cryptoforge crash** — VQE's shattered nomad ship, once | Desert | UNCLAIMED | B | VQE Cryptoforge | ✅ one-time |
| SV37 | **Rubble piles** — Odyssey `Salvage Rubble` finite deconstruct-only debris, scattered at 4× | Wasteland · Scarlands | any | any | Salvage Rubble | ✅ |
| SV38 | **Broken wagon / dead speeder** — the owner's "broken/mashed wagons": a landspeeder on its side, repulsor coils exposed, a Jawa already under it | Desert road | UNCLAIMED / Moot | B | VVE vehicle spawned **disabled/damaged** if Vehicle Framework exposes a wreck state; else `AncientIndustrialTruck` reskin | 🔶 / 🆕 — **no wagon or wrecked-vehicle prop exists in the stack** (agent sweep: zero "wagon" hits) |
| SV39 | **Mashed faction settlement** — a whole Homestead farmstead flattened: the Empire's `IN-6 Censer` burned the ground, the vaporators are slag, the well is capped with a stormtrooper helmet on a stake | AridShrubland | Homestead country, Empire's doing | B–C | RS2 template with every thing swapped for its destroyed twin (VFEPD `Ruined*`) + `BurnedTree` + `Ash` | 🔶 — a **destroy-pass over an existing template** is a generator feature worth building once and reusing for every RS row |
| SV40 | **Mashed Tusken camp** — RS10 after the Empire: domes cracked, bantha bones, pyre unlit | Badlands | Tusken country | B | RS10 + destroy-pass | 🔶 |
| SV41 | **Mashed Junker warren** — RS16 after a Blackstar contract | Badlands | Junkers | B | RS16 + destroy-pass | 🔶 |

### 3.5 NATURAL BEAUTY & INTEREST (NA)

_Terrain and flora, no cast. `beautiful_tilemap.md` owns the general beautification pass;
these are the **specific set-pieces** a tile can be *about*._

| ID | augmentation | biome(s) | band | fodder | feas. |
|---|---|---|---|---|---|
| NA1 | **Wind-scoured bedrock shelf** — the ExtremeDesert's only landmark: a bare rock table in a sea of nothing | ExtremeDesert | A | `Sandstone` rough terrain island in `Sand` | ✅ paint |
| NA2 | **The dunemother's grazing track** — a swathe of cropped `AB_EuphorbiaRimworldia` a mile wide: the beast passed | ExtremeDesert | A | flora removal in a curve | ✅ paint |
| NA3 | **Glass sea** ↩P16 — fused sand, mirror flat, brutal glare | ExtremeDesert | A | 🆕 terrain (a glass/obsidian-like floor; `AB_*` obsidian family may serve) | 🔶 / 🆕 |
| NA4 | **Mirage twin** ↩W19 | ExtremeDesert | A | scam-prop | 🆕 |
| NA5 | **Rock outcrops as navigation landmarks** (`biome_and_fauna_roster.md` §5) | Desert | B | Geological Landforms | ✅ |
| NA6 | **Wadis** — dry channels, visibly water-cut, no water | AridShrubland | B–C | `Gravel`/`Sand` channel paint | ✅ |
| NA7 | **The oasis rings** — water, green, scrub, sand in concentric bands; the most legible tile on the world | ZBiome_DesertOasis | B | `Oasis` mutator + `Plant_Reeds`/`VEE_Plant_DatePalm`/`AB_FanPalm` rings | ✅ paint + flora |
| NA8 | **Mesa and erosion channels** | ZBiome_Badlands | B | Geological Landforms | ✅ |
| NA9 | **Salt flat with fossil bed** — dead seabed; `BMT_MineableFossils` scatter reads as bones in the crust | Desert/ExtremeDesert salt | A–C | `BMT_MineableFossils` (global mineable, needs hand seeding for per-biome) | ✅ seed |
| NA10 | **Tar seeps with visible bones** — Biomes! Fossils' perfect home | AB_TarPits | C–D | `AB_TarPuddle` · `BMT_MineableFossils` · `BMT_MineableAmber` | ✅ |
| NA11 | **Resin flats** ↩§8.4 — the brittle cousin, a sheet not a pool | Desert · Wasteland | B–C | 🆕 terrain (amber-coloured floor) | 🆕 |
| NA12 | **The blooming corpse grove** — `BMT_Plant_BloomingCorpse` at 3× round a seep | AB_TarPits | C–D | flora roster | ✅ |
| NA13 | **Lava layers, newest on top** | Volcano · LavaField | A | Odyssey lava/cooled terrain in bands | ✅ paint |
| NA14 | **Fumarole field** — twenty `SteamGeyser`s, none tapped | Pyroclastic · Volcano | A | `geyserCountFactor`-style mutator ↩A3 | ✅ |
| NA15 | **Obsidian flats** | Pyroclastic | A | `AB_*` obsidian terrain family (`biome_terrain_palette.md` §B3) | ✅ |
| NA16 | **The Kiln crater** — the Hutt disaster site; Zizzik's | Volcano | A | crater paint + slag | ✅ |
| NA17 | **Canopy-to-sand hard stop** — jungle right to the waterline, then sand; the ring visibly thin | FeraliskInfestedJungle edge | A | flora density edge paint | ✅ |
| NA18 | **The red headwaters** — an ocular-forest spore stream, red, detoxifying downstream to clear: the river everyone drinks begins as poison (`02_world.md`) | OcularForest → river | A–B | `AB_EyeGrass` · red-tinted water terrain (🆕) | 🔶 |
| NA19 | **Mangrove root maze** | AB_MiasmicMangrove | A | `AB_ParasiticMangrove` · `AB_MangroveTree` dense | ✅ |
| NA20 | **Bioluminescent shallows** — `BMT_BiolumiAlgae*` in six colours on the tideline | sea shores | D | flora roster (FungalForest family — cross-family use needs a ruling, the "no plant in two families" law) | ⚠️ flora law |
| NA21 | **Salt crust shore** — hypersaline sea edge, white, cracked | shores | D | salt/`Ice`-like terrain paint | ✅ |
| NA22 | **The sea-fog band** — permanent fog on the terminator shore; `Fog` weather forced | shores | D | weather override (C# or scenario part) | 🆕 small |
| NA23 | **The Dead Beacon** ↩P14 | shores | D | 🆕 tower | 🆕 |
| NA24 | **Glowing agarilux grove** — `AB_GlowingAgarilux` / `AB_LuminescentTree` at 5×: light in the failing dark | AB_MycoticJungle | E | flora roster | ✅ |
| NA25 | **The spore bubble** — one `AB_AgariluxPrime`, radius-8 gas, ringed by dead things | AB_MycoticJungle | E | flora roster + corpses | ✅ |
| NA26 | **Tinkle-grass field** — `AB_TinkleGrass` in a hollow; the Choir Wind ↩W18 has somewhere to live | AB_MycoticJungle | E | flora roster | ✅ |
| NA27 | **Crystal field** — `CrystalBig` / `CrystalShard` / `BMT_CrystaltipBrambles` at 4×, glow mineral not alive (owner 2026-08-30) | BMT_CrystalCaverns · PropaneLakes | F | flora roster · `TreeCrystal` | ✅ |
| NA28 | **The propane lakes** — liquid fuel that kills by cold alone | AB_PropaneLakes | F | `AB_PropaneLake` terrain | ✅ |
| NA29 | **Flash-frozen forest** — `AB_FlashFrozenTree` at 10×: a wood that died in a second | AB_RockyCrags | F | flora roster | ✅ |
| NA30 | **Crag defiles** — vertical relief, ambush geometry | AB_RockyCrags | F | Geological Landforms | ✅ |
| NA31 | **The last light** — a `Glowforest`-style self-glowing patch inside the crags (the owner's "oases of light") | AB_RockyCrags | F | `Plant_Nightgrass` · `RG_Plant_Nightguide` · Odyssey glow flora | ✅ (Glowforest biome itself is cut; its flora is not) |
| NA32 | **The slime that is one organism** — `AB_Slime`/`AB_RichSlime` patch, never a band | AB_GelatinousSuperorganism | C | terrain | ✅ |
| NA33 | **Hot springs** — vanilla landmark, retuned | any geothermal | any | `LandmarkDef HotSprings` · `AB_HealingSprings` | ✅ |
| NA34 | **Natural arch / balanced rock** | Badlands · Crags | B, F | Geological Landforms | ✅ |
| NA35 | **Sinkhole** — a `Hollow` mutator whose floor is a different biome's flora | Desert · Badlands | B | `Hollow` mutator + flora swap | ✅ |
| NA36 | **The rootstock** ↩W20 — a dry lake that blooms after water | Desert `DryLake` | B | dormant seedbank (C#) | 🆕 |
| NA37 | **Wildpod wallows** — mud pits the size of houses along a river | river margin | A | `Mud` terrain circles + `AA_Wildpod` | ✅ |
| NA38 | **Sarlacc ring of totems** ↩P2 polish | dunes | A–B | `sw_Sarlacc` + totem props (Tribal Furniture / Effigy) | ✅ |

### 3.6 GIANT BEASTS and the NESTS/LAIRS they build (GB)

_Band-locked. One colossal per region (`Alien_Bestiary.md` 3.11). **A lair is a mutator
(`sw_SarlaccLair` proves it) plus a beast plus the wreckage of its meals.**_

| ID | augmentation | biome(s) | territory | band | fodder | feas. |
|---|---|---|---|---|---|---|
| GB1 | **Krayt dragon lair** — a cave mouth, a bone midden, pearl-bearing skulls ↩P3; the owner still patrols | Desert · Badlands · Crags-edge | Tusken country (rite-of-passage hunt) | A–B | SW `Krayt Dragon` · `Caves` mutator · SK1 midden | ✅ beast; 🔶 lair template |
| GB2 | **Sarlacc pit** ↩F1 — already live | dunes | UNCLAIMED | A–B | `sw_Sarlacc` / `sw_SarlaccLair` | ✅ live |
| GB3 | **Karrak war-caste kennel** — Foundry heavies penned at a surface mouth | Badlands · Volcano | Geonosian | A–B | VGE `karrak` (Bearscarab) · chitin pen | 🔶 |
| GB4 | **The dunemother** — a living terrain feature grazing; non-hostile; the encounter is logistical | ExtremeDesert · salt flat | Ta'Baa | A | VGE `vhorbantha`/Thrumffalo · NA2 track | ✅ |
| GB5 | **Kessorak roost** — the tyrant-ruping's nest on a mesa top: a rideable apex if you are insane | Badlands · Crags | UNCLAIMED | A–B, F | VGE Thrumbochicken · mesa (Geological Landforms) | ✅ |
| GB6 | **Kor'dak in the wreck hull** — the dune-owl nests in wreck hulls (`Alien_Bestiary.md` 3.1): SV2 with a resident | Desert | UNCLAIMED | A–B | VGE Bearchicken + SV2 | ✅ — **two rows for one tile** |
| GB7 | **The passing herd** ↩W6 — obbak / drovak / ghorn migration crosses mid-stay | AridShrubland · Desert | Oomo herd routes | B | VGE Muffalohorse / Muffalowolf / Bearffalo · SW bantha herds | ✅ (herd event is C#) |
| GB8 | **Tibbak herd on the tar margin** — bladderbacks eating what they shouldn't; Cartel tappers follow | AB_TarPits | Hutt edge | C–D | VGE Boomabear | ✅ |
| GB9 | **Sizzik swarm** — sparkmites: how the tar pits stay dangerous | AB_TarPits | UNCLAIMED | C–D | VGE Boomsquirrel ×20 | ✅ |
| GB10 | **The vaskarr** — the tibanna colossus; ONE exists; killing it changes the map | Volcano · TarPits | UNCLAIMED | A | VGE Thrumbalope | ✅ (one authored placement) |
| GB11 | **Kessik pack** — emberhounds, the volcanic tile's mobile threat | Volcano · Pyroclastic | UNCLAIMED | A | VGE Wolfalope pack | ✅ |
| GB12 | **Wildpod** ↩§8.1 — megafauna in a group, living where the water is; the reason the jungle is still empty | FeraliskInfestedJungle · river | Wildsteam's claim | A | `AA_Wildpod` · `AA_Wildpawn` · `AA_AnimaColossus` (`fauna_placement.md`) · Megafauna | ✅ beasts; herd AI 🆕 |
| GB13 | **Feralisk nests** — the biome's own predators, HIGH threat, a nest cluster with silk | FeraliskInfestedJungle | UNCLAIMED | A | Alpha Biomes feralisk · `thessik` silk-caste escaped populations (Insectoids 2) | ✅ |
| GB14 | **Chirrik-felled treeline** — grovegnaw beavers; the reason the tree line moves | river jungle | Compact hates them | A | VGE Wolfbeaver + stump scatter | ✅ |
| GB15 | **Reefback offshore** — a colossus with a reef on it, a moving ecosystem | Gray Sea | UNCLAIMED | D | `sea_beasts_roster.md` Reefback (32) | 🆕 defs pending (art ruled) |
| GB16 | **Sando shallows** — a storm sando ranges the open water off a harbour; the Compact posts a watch | Twilight Sea | Deepwater edge | D | Storm sando (12) | 🆕 |
| GB17 | **Lanternwhale lane** — the largest living thing, trailing blue lanterns; navigate by it | Gray Sea | UNCLAIMED | D | Lanternwhale (40) | 🆕 |
| GB18 | **Blizzarisk clutch** — `AA_BlizzariskClutchMother` and her eggs in a fungal hollow; the Egg Sands ↩W13 inverted for the cold | FungalForest · Crags | UNCLAIMED | E–F | Alpha Animals cold list | ✅ |
| GB19 | **Frostweaver galleries** — `BMT_FrostweaverSpider` webs across a defile; passable at a cost | FungalForest · Crags | UNCLAIMED | E–F | Biomes! Caverns | ✅ |
| GB20 | **Hoarfrost mastodon herd** — `BMT_HoarfrostMastodon`, the nightside's bantha | Crags · HorrorWastes | UNCLAIMED | F | Biomes! Caverns | ✅ |
| GB21 | **Frostbound behemoth** — `AA_FrostboundBehemoth`, one, asleep in a crystal cavern | BMT_CrystalCaverns | UNCLAIMED | F | Alpha Animals | ✅ |
| GB22 | **The crags' manhunters** — most creatures manhunt on arrival (`02_world.md`); the augmentation is the *arrival*: a pack already circling the landing zone | AB_RockyCrags | Ishko | F | biome fauna + arrival script | ✅ / 🆕 |
| GB23 | **Sookal calm** — balm-cats at the oasis; the oasis feels safe because they make you feel that way | ZBiome_DesertOasis | UNCLAIMED | B | VGE Catrabbit (A-grade reclassify) | ✅ |
| GB24 | **Mynock roost** ↩P18 | cave mouths | UNCLAIMED | any | SW mynock + `Caves` | 🔶 |
| GB25 | **Grondrak burrow field** — the elder deep-digger; craters where it surfaced, near-immune underground | Glowforest-patch · ExtremeDesert | UNCLAIMED | A, F | VGE Thrumborat · crater paint | ✅ |
| GB26 | **Dead sarlacc** ↩F2 — a carcass to strip; `sw_DeadSarlacc` is a MapPortal into an undercave dungeon | dunes | UNCLAIMED | A–B | `sw_DeadSarlacc` · `sw_DeadSarlaccCave` | ✅ live |
| GB27 | **Karrakoth siege caste, dormant** — the Foundry colossus asleep at a ruined hive; vulnerable to fire, and the tile telegraphs it (scorch marks) | Badlands · Rust Cathedral | Geonosian ruins | A–B | VGE Thrumbospider + burn paint | ✅ |
| GB28 | **Insect hive, active** — VFE-Insectoids 2's enemy hive as a tile fixture: broods, tunnels, the smell | Badlands · Caves | UNCLAIMED (Unbound Hive is CUT as a faction — wildlife only) | A–B | Insectoids 2 hive (enemy side kept) · Better Infestations group AI | ✅ ⚠️ cherry-pick |
| GB29 | **Rancor pen, broken** — a Hutt arena beast that got out; the pen and the bodies say so | Desert | Hutt edge | B | SW `Rancor` · Torment Master arena props · corpses | ✅ |
| GB30 | **The sea's silt ambushers** — opee lures visible in a shallow; the tile *is* the warning | shores | UNCLAIMED | A, D | Opee family (1.4–2.0) | 🆕 defs |

### 3.7 DEAD BEAST SKELETONS & GRAVEYARDS (SK)

_Bones are content because a scavenger clan reads them as inventory. **Rotted `Corpse`
things are the in-stack skeleton**; a dedicated bone-terrain set is the one 🆕 art ask._

| ID | augmentation | biome(s) | band | fodder | feas. |
|---|---|---|---|---|---|
| SK1 | **Krayt graveyard** ↩P3 — rib-cage terrain set, pearl skulls | ExtremeDesert | A | 🆕 rib-cage terrain + skull props; interim: rotted krayt `Corpse`s | 🆕 art / ✅ interim |
| SK2 | **Bantha graveyard** ↩P15 — ivory scatter; herds return in season | herd routes | B | 🆕 ivory scatter; interim: rotted bantha corpses | 🆕 / ✅ |
| SK3 | **Dunemother's kin** — one colossal skeleton the size of a settlement; a Tusken camp built inside the ribs (RS10 inside SK) | ExtremeDesert | A | SK1 terrain set reused at 3× scale | 🆕 shared art |
| SK4 | **The predator's larder** — a dhakmaw kill-field: twenty carcasses in a ring round a den it will return to | AridShrubland · Badlands | B | VGE Thrumwolf + herbivore corpses | ✅ |
| SK5 | **Gallatross graveyard** — Alpha Biomes ships `AB_GallatrossGraveyard` as a BIOME (rare tier); the owner wants it as a *patch*: its bone props scattered on another biome | Desert · Wasteland | B–C | AB gallatross bone props (biome's own scatter) | ✅ if scatterable out-of-biome ↩§8.5 |
| SK6 | **Tar-pit preserved bodies** — things that died in it and STAYED: a bantha, a droid, a stormtrooper, a thing nobody can name | AB_TarPits | C–D | corpses on `AB_Tar` (preservation via `Corpse` rot stage lock, C#) | ✅ / 🆕 rot-lock |
| SK7 | **The tar-pit that ate a caravan** — SV9 + SK6: six humps in the tar, a pack saddle showing | AB_TarPits | C–D | as above | ✅ |
| SK8 | **The cooked herd** — a pyroclastic flow caught them running; a dozen charred `obbak` in a line | Pyroclastic | A | corpses + `Ash`/`BurnedTree` paint | ✅ |
| SK9 | **A wildpod that died standing** — the jungle grew through it | FeraliskInfestedJungle | A | rotted `AA_Wildpod` corpse + flora inside its footprint | ✅ |
| SK10 | **Beached lanternwhale** — the largest carcass on the planet; a whole Compact village's meat for a year; and what it draws | Gray shore | D | 🆕 (roster def pending) | 🆕 |
| SK11 | **The shore built round a skeleton** — a colossus skull as a harbour breakwater; RS26 with SK as architecture | Twilight shore | D | 🆕 colossus bone set | 🆕 |
| SK12 | **Spore-hollowed carcass** — a mastodon the mycoid belt is eating from inside; glowing | MycoticJungle | E | rotted corpse + `AB_GlowingAgarilux` on it | ✅ |
| SK13 | **The frozen herd** — twenty mastodons standing dead in a crag defile, not rotted: the cold keeps them | AB_RockyCrags | F | fresh `Corpse` with rot locked (C#) | 🆕 rot-lock (shared with SK6) |
| SK14 | **The Arsenal's own casualties** — mech hulks and Forsaken-war bones together, the only place both lie | Crags | F | SV20 + skeleton corpses | ✅ |
| SK15 | **Bones the superorganism is still digesting** — half-sunk in `AB_RichSlime` | AB_GelatinousSuperorganism | C | corpses on slime terrain | ✅ |
| SK16 | **Fossil bed** — `BMT_MineableFossils` hand-seeded thick on a dead seabed; mineable bones | salt flat · ExtremeDesert | A–B | Biomes! Fossils (global mineable → hand seed) | ✅ |
| SK17 | **Amber seam** — `BMT_MineableAmber` in a former-forest cut | river margin · PoisonForest | A, D | Biomes! Fossils | ✅ |
| SK18 | **Mech graveyard** — the Empire's Purge-catalog dumping ground: a hundred `SW-1 Tick` shells by the crate | Wasteland · Scarlands | A–C | VGE mech corpses ×n · `AncientMetalCrate` | ✅ |
| SK19 | **Droid ossuary** — Free Droids bury their dead; a field of chassis standing upright in rows, Ohm's country | LavaField · Wasteland | A, C | droid corpses posed (spawn standing is a C# nicety) · SH12 | ✅ / 🆕 pose |
| SK20 | **The sarlacc's midden** — around GB2, what it spat out: belt buckles, a helmet, a boot with a foot in it | dunes | A–B | apparel items + one body part | ✅ |

### 3.8 GARRISONS & MILITARY (GA)

_A `SecurityProfileDef` + a district + a cast. **The faction-defender blocker of catalogue
§6.1 is discharged by the Inhabited mechanism** — the cast is the garrison and the
manifest names the faction; no `map.ParentFaction` read is involved._

| ID | augmentation | biome(s) | territory | band | fodder | feas. |
|---|---|---|---|---|---|---|
| GA1 | **Imperial garrison** — fortified, kill corridors, a drop-pod battery, forty troopers | ExtremeDesert | Empire | A | `CastRoster_EMPIRE` · Fortifications Industrial · Security Doors · Custom Gas Types (authored enemy-fortified areas) | 🔶 |
| GA2 | **Sensor post** — three troopers, a mast, a bunker: the Empire's eyes on a scar | Pyroclastic · Scarlands | Empire | A | `AncientUplink` · `AM_Entrance_Bunker` · `CastRoster_EMPIRE` ×3 | 🔶 |
| GA3 | **Prisoner pool** — the Empire's Wookiee/Mon Calamari/Geonosian labour camp: cells, a wall, a water ration | ExtremeDesert | Empire | A | cells (Security Doors) · mixed-species prisoner cast · `Jawa_Empire_Grunt` guards | 🔶 — the prisoner cast is a **liberation quest hook** |
| GA4 | **Imperial waystation** ↩P21 | road | Empire | B | modular prefab | 🔶 |
| GA5 | **Checkpoint** — a barrier across the Homestead road, two troopers, a scanner; the Homesteaders queue | AridShrubland road | Empire in Homestead country | C | `Barricade` · `CastRoster_EMPIRE` ×2 | 🔶 |
| GA6 | **Wired chokepoint** ↩D1 — ancient turret, no faction | Badlands · Canyon | UNCLAIMED / Arsenal | A–B | `Sandbags` · `GenStep AncientTurret` | ✅ |
| GA7 | **Minefield** — the Sapper's patience (`Alien_Bestiary.md` 3.12): a wasteland approach mined by something that placed charges on a schedule nobody remembers | Wasteland · Desert approaches | UNCLAIMED | A–C | `TrapIED_HighExplosive` ×n · warning stakes | ✅ |
| GA8 | **Hutt gate** — RS6's Gamorrean gate as its own tile: the palace is one tile over, this is where you are stopped | DesertOasis-adjacent | Hutt | B | `FT_PalisadeGate` · `Jawa_Hutt_Heavy` bodyguards | 🔶 |
| GA9 | **Tusken ambush geometry** — no building: a canyon whose every ledge holds a marksman; traps at the throat | Badlands | Deep Desert Tribes | B | `Jawa_DeepDesert_*` cast placed on ledges · deadfall/spike traps | 🔶 |
| GA10 | **Crawler guard post** — Jawa heavies on a ridge above RS14 | Badlands | Jawa Trade Moot | B | `Jawa_TradeMoot_Heavy` ×3 | 🔶 |
| GA11 | **Junker roadblock** — a wall of wrecks across a road, warcaskets behind it; bribable | Badlands road | Junkers | B | SV1 hulls as walls · `Jawa_Junkers_Heavy` | 🔶 |
| GA12 | **Blackstar hide** — a sniper's nest overlooking a junction; the hunter is *hunting you* | any elevated | Blackstar | B–C | `Jawa_Blackstar_Specialist` on a mesa · `Sandbags` | 🔶 |
| GA13 | **Homestead militia muster** — a bell tower, a rack of bolt-actions, a drill yard; the whole valley turns up when the bell rings | AridShrubland | Homestead | B–C | MiningCo `Alert speaker` · weapon racks · `Jawa_Homestead_Grunt` ×8 | 🔶 |
| GA14 | **Compact reservoir guard** — turret grid + EMP traps round IN11; never leaves the tile | oasis · shore | Deepwater | A–D | `Turret_MiniTurret` ×n · `TrapIED_EMP` · `Jawa_Deepwater_Grunt` | ✅ |
| GA15 | **Foundry surface watch** — a soldier-drone pair and a sonic emplacement at RS20 | Badlands · Volcano | Geonosian | A–B | `Jawa_Geonosian_Heavy` ×2 | 🔶 |
| GA16 | **Bowcaster watch** — a Wildsteam hunter in a tree platform; the freehold's only fortification | jungle | Wildsteam | A | platform prop + `Jawa_Wildsteam_Grunt` | 🔶 |
| GA17 | **Harbour battery** — the Compact's one heavy gun facing the sea (the sando, not you) | shore | Deepwater | D | `Turret_AutocannonTurret` facing water | ✅ |
| GA18 | **Helix prototype guardian** — one engineered thing on a chain at the lab door | HorrorWastes · MycoticJungle | Helix | E–F | one `GR_` hybrid + Anomaly restraint furniture | ✅ |
| GA19 | **Dormant guardian line** — Arsenal mechs in a row across a vault approach, asleep until you are close ↩C4 | Crags | Forgotten Arsenal | F | `GenStep_ScatterAncientMechs` dormant | ✅ |
| GA20 | **Tiny garrison** — the owner's phrase, literal: a 4×4 bunker, two pawns, a flag, a kettle. Any faction. The smallest possible "this is ours" | any | any | any | `AM_Entrance_Bunker` + 2 cast + a faction banner (Ideology `Ideogram`) | 🔶 — **one template, twelve casts** |
| GA21 | **Watchtower** — a tower and one pawn who sees you before you see them; a flare goes up | any | any owned | any | tower prop (VFEPD industrial) + 1 cast + `Flare` | 🔶 |
| GA22 | **Deserted garrison** — GA20 with the cast gone and the kettle still warm ↩RS30 | any | any | any | `castSize 0` | ✅ |
| GA23 | **Vassal outpost** ↩D4 — Faction Territories' own generation | owned territory | any | any | `FactionTerritories_VassalOutpost` (**vassals OFF** per ruling; territory/ambush only) | ⚠️ ruled off |

### 3.9 PET / BEAST BREEDING FACILITIES (BR)

_Always mobility + muscle, never a production ladder (`required_mods.md` taming ruling).
Pens hold what the faction's culture rides, eats, fights or sells._

| ID | augmentation | biome(s) | territory | band | fodder | feas. |
|---|---|---|---|---|---|---|
| BR1 | **Hutt kennels** — one of the 11 service posts: fighting beasts in cages, a handler, a betting board | Desert | Hutt | B | `AnimalSleepingBox`/cages · SW `Rancor` juvenile, `nirrik` scale-cats, `murrik` gland-cats · Torment Master | 🔶 |
| BR2 | **Tapper's ranch** — `tibbantha`/`vaporjerba`/`haskir` gas-bladder stock in corrals, a tapping shed, everything downwind | Desert · TarPits margin | Hutt | B–D | VGE Boomalope clade · `Pen` markers · `Chemfuel` yield | ✅ |
| BR3 | **Shessa-fowl coop** — Cartel smokedown product birds, penned, never wild | DesertOasis-adjacent | Hutt | B | VGE Chickenbear · coop | ✅ |
| BR4 | **Homestead pen** — kiba-fowl, a soffa string, a korrbal that will die for the herd | AridShrubland | Homestead | B–C | VGE Chickenffalo / Muffalocat / Muffalochicken | ✅ |
| BR5 | **Bantha corral** — the caravan spine, six head and a calf | Desert · AridShrubland | Homestead / Tusken / Moot | A–C | SW `Bantha` · fence | ✅ |
| BR6 | **Tusken bantha bond-yard** — corral where young Tuskens are paired with their mount; sacred obbak string beside it | Badlands | Deep Desert Tribes | A–B | SW `Bantha` · VGE Muffalohorse (sacred) | ✅ |
| BR7 | **Ikee hutch** — `AA_Eyeling`, the clan's pet, **must be findable** (`fauna_placement.md`): a Jawa keeps a dozen | Desert | Jawa Trade Moot | B | `AA_Eyeling` ×12 | ✅ |
| BR8 | **Gamorrean breeding colony** — the Junkers' talent pipeline into Hutt bodyguards; a warren that is a farm; monkey-lizards everywhere | Badlands | Junkers | B | `CastRoster_JUNKERS` Gamorrean-heavy · Kowakian monkey-lizard (SW) as vermin/pets | 🔶 |
| BR9 | **Vokkir stable** — Blackstar's carnivorous leaping cavalry, fed on meat, unmistakable | road junction | Blackstar | B–C | VGE Cathorse ×3 · meat stock | ✅ |
| BR10 | **Foundry caste pens** — sterile castes by function: karrak, grallik haulers, k'krri fragfowl; nothing breeds, everything is issued | Badlands · Volcano | Geonosian | A–B | VGE insectoid clade | ✅ |
| BR11 | **Scalefish hatchery** — the Compact farms the sea: pens in the shallows, mee/faa fry | shore | Deepwater | A, D | Odyssey fishing zones · scalefish defs (🆕) | 🔶 / 🆕 |
| BR12 | **Wildpod herding camp** — the Wildsteam's whole claim: a camp on the pod's route, a beast-handler with a bond, no fence (you cannot fence a wildpod) | jungle | Wildsteam | A | `Jawa_Wildsteam_Specialist` + `AA_Wildpod` | ✅ |
| BR13 | **Yobshrimp beds** — bottom-feeders farmed for carcass-cleaning; the Compact's sanitation | shore | Deepwater | D | swarm defs (🆕) | 🆕 |
| BR14 | **Growth-vat hall** — Helix breeds the labour-line; the vats are the pens | HorrorWastes | Helix | E–F | Biotech growth vats · `Jawa_Helix_Heavy` brute-stock | ✅ |
| BR15 | **Hunting lodge** ↩P12 — trophy hall, kennels, cold room; something still uses the kennels | AridShrubland · Grasslands | Ishko / Blackstar | B | rimplace template | 🔶 |
| BR16 | **Pikka colony** — camp-cats that are just *around*; every settled tile's ambient life-signal | any settled | any | any | VGE Chickencat ×6 free-roaming | ✅ — **add to every RS row's cast by default** |
| BR17 | **Veska breeder** — the best domestic animal on the planet, and one Homesteader breeds them; a queue of buyers | AridShrubland | Homestead | B–C | VGE Catwolf + kennels + `trades: true` | ✅ |
| BR18 | **Krayt-egg poachers' camp** — a Blackstar or Junker crew beside GB1 with an egg in a crate; the mother is coming back | Desert | UNCLAIMED | A–B | egg item · corpses-to-be | 🔶 |
| BR19 | **Sivvik problem** — knitflesh rabbits at 20×; the oasis has an infestation and a bounty | ZBiome_DesertOasis | Compact-posted | B | VGE Rabbitcat ×20 | ✅ |
| BR20 | **Consortium "Cultivator", still tending** — the Gardener colossus in a walled garden at a Wasteland ruin; mythic, never explained | Wasteland · OA ruins | Helix leavings | B–C | VGE Thrumboman + garden flora | ✅ |

### 3.10 SHRINES, MONUMENTS & SACRED GROUND (SH)

_One per god at least; the whisper letter names the god, the tile shows the shrine._

| ID | augmentation | biome(s) | god / territory | band | fodder | feas. |
|---|---|---|---|---|---|---|
| SH1 | **Shore-rite altar** — Oomo's; offering bowls at the waterline, a `Fishing_Sacred` precept made a place | shores · oasis | Oomo / Deepwater | A–D | VIE Memes & Structures altar · `Plant_Lotus` | ✅ |
| SH2 | **Oasis shrine** ↩P10 | ZBiome_DesertOasis | Oomo | B | spring-side shrine, bowls | 🔶 |
| SH3 | **Dune cairn** — Ta'Baa's: a stone pile with a bantha skull, one every day's walk across the sea | ExtremeDesert · Desert | Ta'Baa | A–B | `ChunkSandstone` pile + skull prop | ✅ |
| SH4 | **The Monument** ↩P8 — Ozzik's colossus, half-buried | Desert | Ozzik | B | 🆕 statue | 🆕 |
| SH5 | **Roadside milestone** — Ozzik's Ashfall Road marked every tile: a carved post with a distance | road tiles | Ozzik / Mob'Unloo | any | Medieval Signs / sculpture prop | ✅ |
| SH6 | **Effigy line** — Hutt turf markers: Terror Spikes with heads, GibbetCage, Skullspike along a border | Desert | Hutt | B | `Effigy` (Effigys – Terror Spikes) · `GibbetCage` · `Skullspike` | ✅ |
| SH7 | **Incense tower** — Epochs' burner on a Hutt post roof; the smoke is the sign | Desert | Hutt | B | Epochs – Incense Burner/Tower | ✅ |
| SH8 | **Funeral pyre** — Tusken; ash and a gaderffii planted upright | Badlands · Desert | Deep Desert Tribes | A–B | `Campfire` burned out · `Ash` · gaderffii item | ✅ |
| SH9 | **Krayt-tooth trophy stone** — the rite-of-passage record: teeth set in a boulder | Badlands | Deep Desert Tribes | A–B | boulder + tooth items (`Filth`/small props) | ✅ |
| SH10 | **Scrap-Singer's shrine** — Rekko's: a cairn of the best parts ever found, never sold | Desert | Jawa Trade Moot / Rekko | B | component items arranged · sculpture | ✅ |
| SH11 | **Homestead grave-row** — wooden markers, each with a name; the valley's history in a line | AridShrubland | Homestead | B–C | `Grave` ×n filled · `Sarcophagus` for the founder | ✅ |
| SH12 | **Rust Cathedral chapel** — Ohm's: a droid shrine, a dead reactor core as the altar, chassis kneeling | LavaField · Wasteland · Crags | Free Droid / Ohm | A, C, F | VFEPD industrial props · droid corpses posed | ✅ / 🆕 pose |
| SH13 | **Imperial memorial** — a black obelisk to a battle the Empire won; the names are numbers | ExtremeDesert | Empire | A | sculpture prop (More Sculpture) | ✅ |
| SH14 | **Sacred grove** — Wildsteam; keening cordax ring, a life-debt stone | jungle | Wildsteam | A | `AB_KeeningCordax` ring | ✅ |
| SH15 | **Drowned shrine** — a Compact altar the sea took; visible at low silt | shore | Oomo | D | SH1 on `WaterShallow` | ✅ |
| SH16 | **Rakatan trace** ↩P9 | vault-adjacent | Narrator | B, F | authored | 🆕 |
| SH17 | **Zizzik's warning stones** — Wasteland boundary markers, glyphs for *do not drink*; the Free Droids' cracking works behind them | Wasteland | Zizzik | C | glyph props (Ideogram) | ✅ |
| SH18 | **The choir ruin** ↩W18 — Ozzik's wind-sung stones | Badlands | Ozzik | B | ruin walls in a pattern | ✅ |
| SH19 | **Mass grave marker** — after SV39: the Homesteaders came back and buried everyone under one stone | AridShrubland | Homestead | B–C | `Grave` field + one `Sarcophagus` | ✅ |
| SH20 | **Ishko's nothing** ↩W12 — a tile with a single standing stone and, verifiably, nothing else | Crags | Ishko | F | one `ChunkGranite` | ✅ — "consider how rare that is" |
| SH21 | **Static ghosts** ↩W11 — Ohm's holograms at night, old crew scenes | Wasteland ruins | Ohm | C | hologram fleck (C#) | 🆕 |
| SH22 | **Relic house** — a locked hut with one VIE relic on a plinth; a faction will trade for it, another will kill for it | any | any | any | VIE Relics and Artifacts (40+ inert relics) | ✅ |

### 3.11 ANYTHING ELSE THAT FITS (XX)

| ID | augmentation | biome(s) | territory | band | fodder | feas. |
|---|---|---|---|---|---|---|
| XX1 | **Quicksand veins** ↩W15 / **soft ground** ↩W5 | dunes · marsh | UNCLAIMED | A–B, D | `AB_QuicksandPits` mutator (cited by the roster; **agent sweep of `required_mods.md` found no quicksand mod — verify the defName exists in the dump**) | ⚠️ verify |
| XX2 | **Iron rain** ↩W17 — periodic debris falls all stay | ring-adjacent | Zizzik / Sh'kaar | A–B | meteorite incident retuned | ✅ incident |
| XX3 | **Slave pen** — the Hutt thing the player cannot unsee; a liberation choice with a price | Desert | Hutt | B | Torment Master `Water Prison` · prisoner cast | 🔶 |
| XX4 | **The casino** — one of the 11; a Hutt post whose stock is *chance*: gamble silver against a crate | Desert | Hutt | B | Torment `Auto-Vending Machine` reskin · scripted gamble (C#) | 🆕 small |
| XX5 | **Plague quarantine** — a Homestead farm under a red flag: rothrik plague-bantha got in; the cast is sick, the stores are clean | AridShrubland | Homestead | B–C | RS2 + `Plague` hediff on cast + VGE Ratffalo corpse | ✅ |
| XX6 | **The exile** — one pawn from a faction that will pay to have them back, or to have them not come back | Desert | UNCLAIMED | B | one named `CharacterDef` with a faction tag | 🔶 |
| XX7 | **Something buried** ↩W1 — a working machine under the sand | any | Rekko | any | buried thing (C# reveal on mine) | 🆕 small |
| XX8 | **Poisoned well** ↩B2 | Desert · Wasteland | Zizzik | B–C | `PrimitiveWell` + toxic terrain + corpses | ✅ |
| XX9 | **Imperial propaganda** — a holo-board on a pole in the middle of nowhere, still playing | ExtremeDesert | Empire | A | `CommsConsole` reskin + light | ✅ |
| XX10 | **Bantha dung fire circle** — a Tusken camp's footprint after it moved: the ring of stones, the ash, still warm | Desert | Deep Desert Tribes | A–B | `Campfire` ×1 · stone ring · `Ash` | ✅ — the *absence* of RS10 |
| XX11 | **Junker toll of a different kind** — a "pay to pass" that is actually a robbery; the roadblock's cast is hostile-but-bribable | Badlands road | Junkers | B | GA11 + security profile "bribe" | 🔶 |
| XX12 | **Quarantine marker line** — Helix stakes with biohazard tags across a valley; beyond them the fungus is wrong | MycoticJungle · Wasteland | Helix | C–E | stake props + `Ideogram` | ✅ |
| XX13 | **Labour-line remnant** — a Consortium `Model` still working at a dead facility: the Steward cycling lights in an empty room (`Alien_Bestiary.md` 3.12) — **Wasteland has no wild clade by ruling; this is what lives there** | Wasteland | Helix leavings | C | VGE humanoid hybrids as `Resident` cast | ✅ |
| XX14 | **The burn front** — the Pyrelands' migrating fire crossing the tile mid-stay; ash soil behind it | ZBiome_Grasslands | Sh'kaar | A | fire + dry thunderstorm weather (built from shipped mechanics) | ✅ |
| XX15 | **Poison briar** ↩§8.2 — area denial by terrain | jungle | Wildsteam's defence | A | 🆕 damaging plant (only `AB_AgariluxPrime` exists) | 🆕 |
| XX16 | **Sink-silt** ↩§8.3 — where `AA_SandProwler` lives | marsh · seafloor | Deepwater's defence | A, D | `AA_SandProwler` + XX1 terrain | ⚠️ as XX1 |
| XX17 | **Glimmer field** ↩W9 | terminator | Ishko/Oomo | D | biolum flora + night-hunter spawns | ✅ |
| XX18 | **The Listening Dark** ↩W2 | nightside | Ishko | E–F | `Hollow`/`Caves` pre-connected | ✅ |
| XX19 | **The Sleeper's Knock** ↩W21 | Rakatan traces | Arsenal | F | timed sound (C#) | 🆕 small |
| XX20 | **Propane as a trap** — a lake that is fuel, in a place that kills the unprepared by cold alone; the augmentation is a *dead player-analogue*: a heater ring round a propane pump, everyone in it frozen | AB_PropaneLakes | UNCLAIMED | F | IN31 + SV33 | ✅ |
| XX21 | **The Wrong Spark** ↩W4 | broken places | Zizzik | any | glitch script (C#) | 🆕 |
| XX22 | **Gas battlefield** — Custom Gas Types residue still hanging in a hollow where two factions fought with it; masks on the dead | Badlands hollow | contested | B | Custom Gas Types (5 agents) · corpses with gas masks | ✅ |
| XX23 | **Landing scorch** — no building: a black circle in the sand, tracks leading away, a dropped `Chemfuel` can. Someone landed here last week | any | Empire / Blackstar | any | `Filth_Ash`/burn paint · one item | ✅ — cheapest "recently inhabited" in the file |
| XX24 | **Caravan tracks** — a worn path corner to corner, `Gravel` through `Sand`, dung, a lost sandal | Desert | Mob'Unloo | any | terrain paint line + `Filth_AnimalFilth` + apparel item | ✅ |
| XX25 | **Migration fence** — a wildpod-proof line of stakes a mile long, and the gap in it | jungle edge | Wildsteam | A | stake props | ✅ |
| XX26 | **The hermit's warnings** — RS5's tile edge: signs in three scripts saying *go away* | Badlands | UNCLAIMED | B | Medieval Signs | ✅ |
| XX27 | **A hive underfoot** — Better Infestations' defending group under the map; the surface shows only the butchered carcasses they drag down | Badlands · Caves | UNCLAIMED | B | Better Infestations + Insectoids 2 hive below | ✅ |
| XX28 | **Sunken road** — the Ashfall Road's old bed, a metre below the sand, paved, with milestones sticking up | Desert | Ozzik | B | `Concrete`/paved terrain strip under `Sand` paint gaps | ✅ |
| XX29 | **Cache of another player-analogue** — a gravship's dropped cargo pod, unmarked, full: whoever they were, they were like you | any | UNCLAIMED | any | `VFEPD_AncientCratePile` · cargo items | ✅ |

---

## 4. FEASIBILITY BY CATEGORY — does the fodder exist today?

| category | rows | ✅ in stack | 🔶 template/cast | 🆕 new | the gap in one line |
|---|---:|---:|---:|---:|---|
| RESIDENTS & HOMES (RS) | 31 | 2 | 28 | 1 (crawler hull, shared with P6) | **Every faction has a cast; only the Junkers have districts.** The work is 11 faction "dialects" of dwelling/compound templates, not content |
| INFRASTRUCTURE (IN) | 36 | 25 | 10 | 0 (+1 ⚠️ IN32 pillar check) | Fodder is rich (Helixien, Rimefeller, KotOR vaporators, MiningCo drill, `Ancient*`); **three buildability strips are prerequisite** and none has been applied (Helixien `:489`, Rimefeller `:517`, CoreDrill/DrillTurret) |
| TRADING (TR) | 23 | 8 | 13 | 2 (dead-drop swap, ship-as-fixture) | The mechanism (`stock` + `trades`) is **live and proven**; the ask is PlaceDefs. A *mixed-faction* rest-stop cast (TR9) is the one novel shape |
| SALVAGE (SV) | 41 | 28 | 8 | 5 (crawler hulls, podracer, ring, vault, the patch) | Richest category by far — VFEPD's 1,828 defs and `Ancient*`. **Two structural gaps:** no wrecked-vehicle/wagon prop exists (SV38), and a **destroy-pass generator** (SV39–41: turn any RS template into its mashed twin) would multiply the whole RS list at near-zero cost |
| NATURAL (NA) | 38 | 30 | 3 | 5 (glass sea, resin, red water, fog, rootstock) | Flora rosters and terrain palette cover it; **the "no plant in two families" law blocks cross-biome flora scatter** (NA20) and needs a ruling for shoreline biolum |
| GIANT BEASTS & LAIRS (GB) | 30 | 23 | 3 | 4 (the sea beasts; herd AI is a C# rider on GB12) | Beasts abundant (SW Animal Collection ~150, Alpha Animals, Megafauna, VGE hybrids via `Alien_Bestiary.md`); **sea beasts have ruled art and no defs**; a *lair* as a mutator-plus-midden template exists only for the sarlacc |
| SKELETONS & GRAVEYARDS (SK) | 20 | 14 | 0 | 6 (bone terrain set, colossus bones, rot-lock; posed corpses are a rider) | Rotted `Corpse`s are the interim skeleton and work today; **a rib-cage/ivory terrain+prop set is the one art ask** and it serves P3, P15, SK1–3, SK10–11 at once. A rot-lock C# nicety serves SK6/SK13 |
| GARRISONS (GA) | 23 | 7 | 15 | 0 (+1 ⚠️ GA23 ruled off) | **Catalogue §6.1's blocker is discharged**: the Inhabited cast is the garrison. Fortifications Industrial + Security Doors supply the silhouette. GA20 "tiny garrison" is one template × twelve casts |
| BREEDING (BR) | 20 | 14 | 5 | 1 (yobshrimp beds; the hatchery rides the sea-beast defs) | VGE hybrids (renamed per `Alien_Bestiary.md`) give every faction a culturally-specific pen animal today; pens are vanilla. BR16 pikka should be a default cast member everywhere |
| SHRINES (SH) | 22 | 18 | 1 | 3 (statue, trace, holograms) | VIE relics/altars, Effigy, Incense, Ideograms cover nine gods; only Ozzik's Monument needs art |
| OTHER (XX) | 29 | 19 | 3 | 5 (briar, casino, buried, knock, spark) + 2 ⚠️ verify (XX1, XX16 quicksand) | Quicksand is cited by the roster (`AB_QuicksandPits`) and **absent from `required_mods.md`** — the defName must be measured before XX1/XX16 are counted as ✅ |
| **TOTAL** | **313** | **188** | **89** | **32** (+4 ⚠️) | **60% place-and-go, 28% needs a template or a cast def, 10% new content, 1% gated on a ruling or a measurement** — the stack carries the inhabited dream; the templates do not yet |

Counting the catalogue's 41 and the roster's 44 alongside, the design surface is ~400
distinct augmentations, of which roughly three-quarters need **no new def**.

### 4.1 The four builds that unlock the most rows

1. **Faction district dialects** (RS, GA, TR, BR — ~80 rows): 12 factions <!-- corrected from 11: canon roster is 13 total, 12 hold settlements/dossiers (the territorial sense here); matches §1.2 --> × {dwelling,
   compound, gate, pen, shop} rimplace templates. The Junkers' four prove the format; the
   FOUNDRY iteration protocol (`structure_injection_roster.md` §5) is the process.
2. **A destroy-pass over any template** (SV39–41 and every RS/GA/TR/BR row's ruined twin —
   ~90 rows): swap each ThingDef for its `Ruined*`/`Destroyed*` VFEPD twin where one exists,
   else damage-to-50%, burn paint, remove cast, drop corpses. One generator feature, hundreds
   of tiles.
3. **A bone terrain + prop set** (SK1–3, SK10–11, P3, P15): rib arcs, skulls, ivory scatter,
   at two scales. One art pass.
4. **The three buildability strips** (IN6, IN19, IN26–27, SV24): prescribed in
   `required_mods.md` since August, never executed, gating every "working machine" row.

---

## 5. WHERE THE ROSTERS WERE TOO THIN

| axis | thin where | why it matters here |
|---|---|---|
| **Band D–F territory** | Only Helix, Free Droid and the Arsenal are placed nightside; Helix's dossier says HorrorWastes/mycoid but names no *architecture* beyond "sterile labs" | RS27–29, GA18, BR14 are inferred from `pawnkind_roster.md` gear tiers, not from a dwelling description. The nightside RESIDENTS column is the weakest in the matrix |
| **Wildsteam, Deepwater dwellings** | `faction_roster_v2.md` gives economy and species; "tree-integrated freeholds" and "stilt houses" are my reading of "open tree-integrated" / "amphibian coalition" | RS22–26 need the owner's LOOK — these are exactly the "options he must LOOK at" that should ship as a savegame grid |
| **Vehicles as wrecks** | `required_mods.md` adopts Vehicle Framework/VVE for *player mobility* and VehicleRaid for the Empire; nothing says whether a vehicle can spawn disabled as a prop. Zero "wagon" hits anywhere | SV38 (the owner's "broken/mashed wagons") is 🔶/🆕 until someone measures VF's wreck state |
| **Sea beasts** | ruled art, no defs (`sea_beasts_roster.md` "Next") | every GB15–17, SK10–11, TR16, BR11/13 row is 🆕 pending that def pass |
| **Skeleton props** | no doc names a bone/skeleton ThingDef in the stack; Biomes! Fossils gives mineables, Dungeon Core (rejected) had the tone | SK rows lean on rotted `Corpse`s, which rot *away* — the rot-lock is a real need, not a nicety |
| **Quicksand** | roster cites `AB_QuicksandPits`; `required_mods.md` never mentions quicksand | XX1/XX16 hang on one `measure` |
| **The alien family** | `AB_OcularForest` is 3 tiles; `AB_GelatinousSuperorganism` is patches | §2.8 is correctly tiny; do not enrich it |
| **God-country whisper tables** | `sacred_sites_pass_1.md` is spec-only; Ishko's landmark is unfilled | SH20/XX18–19 have a god but no shipped table to join |

---

## 6. COMPOSITION RULES CARRIED FROM THE PARENTS

1. **One promise, one whisper, per landable tile** (`structure_injection_roster.md` §4). A
   §3 row is either the *promise's responder content* or a *whisper's payload*; it never
   ships as a third channel.
2. **Density follows the band, not the biome.** Band A is the Empire's and the void's —
   `ExtremeDesert` stays the emptiest tile on the planet (`biome_and_fauna_roster.md` §3:
   *"emptiness is content"*). Band B is where "downright replete" lives. Bands E–F carry one
   thing each, and it is usually dead.
3. **Nothing walks across the terminator.** A GB/SK row's band is a constraint, not a
   suggestion.
4. **Terrain treasures are operable, never buildable** (`02_world.md` four axes). Every
   working machine here is a `designationCategory` strip away from being a pillar breach.
5. **Water is always defended** (water doctrine 2) — an oasis without a GA or GB row is a
   bug.
6. **The Hutt beside-the-oasis rule binds the 8 palaces only**; the 11 service posts sit on
   dry ground and *sell a service* — RS7's eleven templates are eleven different services.
7. **Every RS row has a `castSize 0` twin (RS30) and a destroyed twin (SV39 pattern).** Three
   tiles for the price of one template.
8. **Pikka everywhere settled** (BR16). If a tile has residents and no ambient animal, it
   reads as staged.
