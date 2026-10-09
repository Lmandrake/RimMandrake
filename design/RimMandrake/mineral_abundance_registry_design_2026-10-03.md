# Mineral abundance registry — design (2026-10-03)

Item: `MINERALS_WHERE_THEY_BELONG_1`. Predecessor: `design/RimMandrake/minerals_where_they_belong_design_2026-10-02.md`.

## 1. Owner rulings this design serves

All 2026-10-03, recorded on the item (`rimflow show MINERALS_WHERE_THEY_BELONG_1`).

- TYPED: *"Each biome has carefully selected mineral abundances, period. Settable in configuration
  settings. Some doesn't even have iron. Requires an Excel spreadsheet (csv) to determine which biomes
  bear which of all the ores, metals, etc. Similar sheet (or the same) could also determine what other
  available sources hold. Might be time to make one of these official and track it as part of the
  future normalization process. It should not be binary yes/no presence but some unitful definition of
  abundance that can be reasoned about by the user to intelligently set it."* He also invited being
  talked out of absorbing other mineral/gem mods.
- Plasteel stays **plasteel**, its own canon material (owner typed 2026-10-09; it reversed the 2026-10-03
  card that renamed it durasteel). Durasteel's one def and the donors' fate: `canon_materials_design_2026-10-09.md` §3.0.
- TYPED: **duranium and doonium are made**: rare, salvage- and trader-available, made offworld,
  REQUIRED to build large ship and machine types (like factories).
- Deep drill: **iron plus home-biome deposits only** (card).
- TYPED (relayed by the coordinator, same day): *"Quarries work like deep drill/scanner. They do NOT
  just barf out any old material, but the local materials only."* So the registry also drives quarry
  output (§6.4).
- Already filed downstream and reading this registry: `FLOWWORKS_QUARRY_DIGGING_1` (canal digging
  uncovers local materials, sluice mining, gold panning).

Superseded by these rulings in the 2026-10-02 design: its Q1-Q4 (answered), the "deep weight → 0 or
home" row (now: Steel everywhere is itself a registry row, and a biome may set it to 0), and §5's
on/off settings list (replaced by unitful per-biome settings, §7).

## 2. Inventory — every mineral material in the active mod set

**Instruments.** Live `ModsConfig.xml` parsed with ElementTree: **634** active mods (the full list
is loaded today). Def dump capture `DefDump/captures/2026-10-03T23-20-21Z` (634 mods, captured today,
newer than `defs.sqlite`, which still describes the 09-26 628-mod set, so the JSON was parsed
directly). **26,589** ThingDefs. Sanity probes: `MineableGold` found, `Steel` found as a deep
resource. Engine facts from RimSage (decompiled 1.6). Scratch script: the inventory is regenerable
from the dump and is deliberately not committed.

**73 distinct mineral materials** (ores, metals, gems, crystals, salts, mineral fuels; stone chunks
and blocks excluded) by the mod that defines the item:

| mod | n | materials |
|---|---|---|
| RimMandrake: Baroque Biomes (ours) | 14 | brine plate, dead smartsteel, delta salt, drazz, lanternstone, live pattern metal, coarse salt, 4 crystal salts, salt cameo, seep-salt, tekk |
| Jawa Armoury Rebalance (ours) | 10 | Bronzium, KotOR Durasteel, Beskar ingot, Mandalorian iron (raw beskar), Cortosis, Rhydonium, KotOR spice, KotOR tibanna, kyber, stygium |
| Core | 8 | steel, plasteel, gold, silver, uranium, jade, components, advanced components |
| RimUtinni Patches (ours) | 6 | brine plate, drazz, tekk, salt cameo (RUT twins), metal-salt bezoar, mindstone |
| Minerals Sparkle | 5 | rough/cut gem, rough/cut ultrahard gem, small fossil |
| Outer Rim - Core | 5 | beskar, pure beskar, durasteel, tibanna, hypertech component |
| [ZAV] Glowstone | 4 | glowstone cluster, large, small, dust |
| Jewelry | 3 | diamond, ruby, sapphire |
| Star Wars: The Force - Lightsaber | 3 | synthetic, bled, cleansed crystal |
| Alpha Animals | 2 | sky steel, uranium crystals |
| Biomes! Fossils | 2 | amber, fossils |
| one each | 11 | pyrinth (RimMandrake: Pyrinth, ours), blue crystal (SW Bestiary, ours), obsidian (Odyssey), gravitonium (Research Retag), alcyonite (Alpha Biomes), sangonite (Dark Ages), uncured plasteel (Rimefeller), salt (VCE), deepchem (VCHE), helixien (VHGE), mineral sand concentrate (GravTide) |

**Pyrinth is the orange glowing gem, and it is already ours**: `DV_Pyrinth` ("A warm, bright orange
crystal. Rare and beautiful. It glows and emits warmth innately"), mod `RimMandrake: Pyrinth`, with
`DV_MineablePyrinth` (scatter 0, gated to the Lantern Deeps by
`src/RimMandrake/LanternDeeps/Patches/RM_LanternDeepGatePyrinth.xml`) and deep weight 0.4 (still
global, so a scanner anywhere can find it).

### 2a. How each reaches a map today — seven channels, none biome-aware

| # | channel | engine path | what flows through it today |
|---|---|---|---|
| C1 | **vein scatter** | `GenStep_RocksFromGrid` → `GenStep_ScatterLumpsMineable.ChooseThingDef`, weight `building.mineableScatterCommonality`, no biome filter | 24 defs (table below) |
| C2 | **MineralsFramework spawns** | `MineralsFramework.StaticMineral` per-def `allowedBiomes`/`allowedTerrains`/cluster probability, drops via `randomlyDropResources` | Minerals Rock `SolidOre{Steel,Silver,Gold,Jade,Plasteel,Tech,Uranium}` + Weathered/Hewn forms (`allowedBiomes` empty), Sparkle crystals (terrain-gated: e.g. `DiamondCrystal` on granite/basalt), `RiverRock` (gems by rivers). UNMEASURED: whether empty `allowedBiomes` means "everywhere", and whether these ore defs spawn on our maps at all (framework C# not in RimSage) |
| C3 | **deep deposits** | `CompDeepScanner.ChooseLumpThingDef`, weight `deepCommonality`, chosen at scan time, no biome filter | 27 defs (below) |
| C4 | **quarry** | `Quarry.Building_Quarry.GiveResources` → `OreDictionary.TakeOne()`: a global list of every `isResourceRock` mineable on the planet plus components, weighted by scatter × deep ÷ value. Only rock chunks/blocks come from the rock under it | the whole C1 list, planet-wide |
| C5 | **meteorite / mineral-rich mutator / long-range scanner** | `ThingSetMaker_Meteorite`, Odyssey `TileMutatorWorker_MineralRich`, `CompLongRangeMineralScanner` + `GenStep_PreciousLump` | every `isResourceRock` mineable |
| C6 | **biome-local placements we own** | per-biome GenSteps, map generators, MapComponents | salts, brine beds, lanternstone walls, kyber/pyrinth gates, bezoar seams, fossil seams, heartwood |
| C7 | **off-map** | trader stock, salvage loot, quest rewards, VOE mining outpost (`kuhlyus.modpatch.vanillaoutpost` adds modded ores to it), Ancient mining industry sites | everything with a market value |

C1 rows with weight > 0 (the "random outcrop" set): Core Steel 1.0, **Components 1.0**, Uranium 0.12,
Silver 0.10, Gold 0.07, Jade 0.065, Plasteel 0.05; LK Mineable Outer Rim Durasteel 0.5, Beskar 0.3,
Pure Beskar 0.3, Hypertech component 0.3; Armoury (ours) KotOR durasteel 0.15, Bronzium 0.10,
Rhydonium 0.0875, Cortosis 0.065, Spice 0.05, Beskar 0.001; Glowstone 0.5; Dark Ages steel beetle 0.3;
Biomes! Fossils amber 0.12, fossils 0.09; Jewelry ruby 0.08, sapphire 0.08, diamond 0.06.
✅ `RUT_Webwork_SilkKnot` now carries **0** (the 10-02 design's leak is fixed).

C3 rows (deep weight): Steel 4, live pattern metal 4, deepchem 2, Outer Rim tibanna 2, KotOR tibanna 2,
plasteel 1, uranium 1, helixien 1, rhydonium 1, lanternstone 1, SW blue crystal 1, fossils 0.8,
Outer Rim beskar/pure beskar/durasteel 0.75 each, cortosis 0.75, silver/gold/jade/ruby/sapphire/VCE
salt 0.5, amber/diamond/gravitonium/pyrinth 0.4, glowstone 0.1.

### 2b. Machines that produce minerals (registry consumers)

| building | mod | what it yields | registry role |
|---|---|---|---|
| `QRY_Quarry`, `QRY_MediQuarry`, `QRY_MiniQuarry` | Quarry (`ogliss.thewhitecrayon.quarry`, CC0) | rock chunks/blocks of the rock under it, plus a draw from the global `OreDictionary` | **must** read the registry (owner ruling) |
| `DeepDrill` (+ `GroundPenetratingScanner`, `WallMountedGroundPenetratingScanner`, VGE scanner-cluster deep module) | Core / WallStuff / VGE | whatever deep lump the scan placed | reads the registry through C3 |
| `BreadMoAM_AutomaticDrillingRig` | Ancient mining industry | "placed on a tile with a known ore deposit" (`CompDeepDrillAutomated`) | inherits C3 if it reads the deep grid; UNMEASURED |
| `AB_CoreSampleDrill` | Alpha Biomes | "standard rock types not usually present in a particular biome" | a non-local leak by design: registry says whether a biome allows it |
| `DrillTurret`, `MobileMineralSonar` | MiningCo. | mine / reveal existing rock | no change: they only touch what is on the map |
| `VCHE_DeepchemPumpjack`, `VHGE_HelixienPump`, `OuterRim_TibannaExtractor*` | VE / Outer Rim | pipe resources from deep deposits / anywhere | registry rows for those fluids |
| `RM_AcousticSounder` (ours), `RM_LiquidDrill`/`RM_LiquidTap` (FlowWorks, ours) | ours | sounding / liquids | future consumers |

No Odyssey or Vanilla Expanded quarry building exists in the active set (searched defName, label,
thingClass and comps for "quarr"; the only other hits are a sign and a pawn).

## 3. Mineral-mod sweep and absorption verdict

**Sweep.** Every `About/About.xml` under both roots (`…/common/RimWorld/Mods` and
`…/workshop/content/294100`), parsed, matched on `<name>` AND `<description>`: 2,832 files, 1,416
unique packageIds. Sanity probe: 84 About.xml files mention "gravship" (the instrument can see).
Mineral-relevant hits, plus every mod the def dump shows adding a mineral:

| mod | active | adds / does | how | licence | verdict |
|---|---|---|---|---|---|
| Jewelry (`kikohi.jewelry`) | yes | diamond, ruby, sapphire + crafted jewellery | C1 veins, C3 deep, 3 DLLs | CC BY-NC-SA 4.0 | **control, don't absorb**; absorption is legal (NC-SA, attribution) but buys nothing the registry doesn't |
| Minerals Framework / Rock / Sparkle / Frozen (`zacharyfoster.*`) | yes | replaces rock with weathered/hewn/boulder forms; ore veins incl. "Tech" (components, plasteel, aluminium); gem crystals; ice | C2 framework, 4 DLLs each | Rock/Sparkle/Frozen CC BY-SA 4.0; Framework no licence file | **control, don't absorb**: large C# with its own spawner; registry writes its `allowedBiomes` / cluster probabilities. Its Tech ore is a components-from-rock leak to close |
| LK Mineable Resources Outer Rim (`leutiankane.mineablesor`) | yes | 4 veins of Outer Rim beskar/durasteel/hypertech | C1, 4 XML files, no C# | none | **retire the mod** (canon metals are salvage-only; it has no other content) |
| [ZAV] Glowstone (`zav.glowstoneforked`) | yes | glowstone vein, lights | C1/C3, XML only | none | **control** (no licence ⇒ cannot legally absorb anyway) |
| Biomes! Fossils (`biomesteam.biomesfossils`) | yes | amber, fossils | C1/C3, 3 DLLs | CC BY(-?) per LICENSE.md | control |
| Outer Rim - Core | yes | beskar, pure beskar, durasteel, tibanna, hypertech | C3 deep, extractors | — | control; its durasteel's fate is `canon_materials_design_2026-10-09.md` §3.0 |
| Jawa Armoury Rebalance (ours) | yes | 10 KotOR materials | C1, C3 | ours | already ours; zero C1, set salvage/trade rows |
| RimMandrake: Pyrinth (ours) | yes | pyrinth | gated C1, C3 | ours | **already absorbed** — the orange gem the owner named |
| Vanilla Mining Outpost Patch | yes | adds modded ores to VOE mining outposts | XML | none | C7 consumer: registry row `outpost` |
| Ancient mining industry | yes | mining sites, automated rig, mineral scanners | C# | — | C7 consumer; rig audited under §6.4 |
| Quarry | yes | quarry buildings | C# | CC0 | consumer (§6.4); CC0 means a fork is free if Harmony ever falls short |
| [ZAV] Fantasy Metals | **no** | fictional metals | — | — | leave out |
| Asteroid Mineral Scanner | no | asteroid scanning | — | — | leave out (orbital already covered by Odyssey) |

**Verdict: control, don't own — with one widening from the GPT consult (§9).** The thing the owner wants — *every* material appearing only where
the registry says, in amounts the registry says — does not require owning the def. Placement is
decided by six engine/framework entry points (C1–C5 plus the quarry), and one runtime mod that
rewrites those weights and filters those draws controls every material from every mod, including
mods added next year, the moment they get a CSV row. Absorbing a mod buys control of the *thing
itself* (name, art, stats, recipes), which is only wanted for:

1. materials we are consolidating or adding (one durasteel from three donors; duranium/doonium new);
1a. a small subset whose port retires a substantial integration burden, with licence provenance per
    file (candidate: Biomes! Fossils' amber/fossil seams, at the Flooded Canyon sitting);
2. a donor whose only content is a leak (LK Mineable Outer Rim → simply removed from the list);
3. a gem whose art/stats fail our canon or normalization passes, decided per material at that pass.

Absorbing wholesale costs: licence exposure (two of the four candidates have no licence file;
Jewelry is NonCommercial-ShareAlike), port effort (Minerals is ~16 assemblies of framework), losing
upstream fixes, and owning their art debt. The registry also has a **coverage check** (§8) so a newly
installed mod's mineral cannot slip in unregistered, which is the actual risk the owner is guarding
against.

## 4. The unit

**Primary unit: EPM — expected units per standard map.** The number of items of the material a
colony would get by exhausting that source on one standard map: 250×250 cells, reference hilliness
"large hills", default difficulty (`mineYieldFactor` 1.0). "Gold 1,500" means *strip this map and you
get about 1,500 gold*. A player sets it the way he'd reason about it: "I want enough steel for a
mid-game base (~10k) but gold should be a find, not a mine (~500)".

Why this unit, against the engine (RimSage, decompiled 1.6):

- Vein count is per area: `GetResourceBlotchesPer10KCellsForMap` gives 4 / 8 / 11 / 15 / 16 lumps per
  10k cells for flat / small hills / large hills / mountainous / impassable, and
  `CountFromPer10kCells` turns that into `round(size² / round(10000/n))` — **69 lumps** on a 250² large-
  hills map. Each lump is `mineableScatterLumpSizeRange` cells (default 20–40, mean 30), each cell
  yields `mineableYield` (40 for metals). So one lump of a 40/cell ore ≈ 1,200 units, and EPM converts
  into an *attempted* lump count `EPM / (yield_per_cell × mean_lump_cells)`, rounded **stochastically**
  (GPT 1.1: a 600-gold setting is half a lump; deterministic rounding would give 0 or 1 every time and
  destroy the expectation). What a colony actually recovers is lower (clipped lumps, overlaps, mining
  yield), so the contract is "expected placed", and the first functional script measures recovered vs
  stated across seeds before any number is called calibrated.
- Today's weights are relative shares (`RandomElementByWeight`), so a weight means nothing on its own:
  adding one mod changes every other ore's abundance. EPM is absolute, so rows are independent.
- Reference values (worked from the above): Core-only vanilla large hills ≈ 34,000 steel EPM
  (40% share); under today's modded weight sum 6.09, steel ≈ 13,600, gold ≈ 950, components ≈ 680.
- **Map size scales EPM by area** (×size²/62,500). **Hilliness scaling is a deliberate policy**, not
  geology (GPT 1.2): we keep vanilla's ×4/11 flat … ×16/11 impassable because players expect mountains
  to be richer, and say so on the settings screen. Lumps need natural rock to land in (`CanScatterAt`
  requires an `isNaturalRock` edifice), so a rock-poor map can fall short; the generator logs a
  diagnostic **ore per 1,000 eligible rock cells** for each map so a shortfall is visible, not silent.
- The vanilla nomadic factor (`nomadicMineableResourcesFactor`, applied only when
  `useNomadicMineables` and not the starting map) and gravship-landing value rules are applied once,
  explicitly, because a forced-count scatter bypasses them (GPT 3.3).

**Secondary units**, one per source kind, each stated in the CSV's `unit` column:

| unit | meaning | used for |
|---|---|---|
| EPM | units per standard map, exhaustible | veins, nodules, crystals, seams, salvage seams on the map |
| EPM/yr | units per standard map per in-game year | regrowing sources: crusts, vent growth, organism yields |
| deep share + units/find | selection weight among the deep finds **allowed in that biome**, shown to the player as "% of finds" and "units per find" (`units_per_cell_or_find`), plus finds per scanner-year at the default scan rate | deep scanner/drill (a share alone is composition, not abundance: GPT 1.3) |
| units per 100 jobs | quarry output per 100 completed resource jobs (`quarry_per_100_jobs`, default `derive` = proportional to the biome's EPM) | quarry, and later FlowWorks digging/sluice/panning |
| UPY | units per in-game year **offered** off-map at a stated encounter rate (one trader visit per season, one salvage site per quadrum within 10 tiles) — offered, never guaranteed acquisition | salvage, trade, quests (`salvage_per_year`, `trade_per_year`) |

Settings show both the EPM and its translation ("≈ 4 deposits of ~30 cells").

## 5. Registry shape (CSV)

File: `design/RimMandrake/mineral_abundance_registry_2026-10-03.csv` (draft; the official copy moves
into the mod as `Data/mineral_registry.csv` when built). One row per **material** (several defs that
are one material in the fiction share a row: e.g. four beskar defs). Columns:

- `material`, `defs` (every def the row governs: item + every mineable/spawner/crystal that yields it),
  `form` (the F-codes of the 10-02 design), `unit`, `units_per_cell_or_find`;
- one column per biome: the 28 `RM_` biomes, the four sea floors, the five RUT-only biomes, and
  `OTHER_vanilla_biomes` (any biome not ours). RUT twins read their RM column. A cell is a number in
  the row's unit, `0`, `deep-only` (no surface form; deep allowed here), `herd`/`unbounded` (source is
  not deposit-limited; see notes);
- `deep_weight` (deep share, used only in biomes whose cell is non-zero); `quarry` (`local` = quarry
  may draw it where the biome cell is non-zero, `no` = never);
- `salvage_per_year`, `trade_per_year`, `quest_or_site` (off-map sources);
- `status` (RULED / BUILT / PROMISED with path / PROPOSED / GUESS / UNMEASURED) and `notes`.

**Draft vs emitted (GPT 3.1, taken).** The draft is the owner's reading sheet, so `defs` holds prose,
promised names and the `OTHER_vanilla_biomes` pseudo-column (expanded by the generator to every
BiomeDef not ours). The emitted registry is stricter: the generator splits each row into a stable
`material_id`, an exact **bindings** list (item defs, producer defs, yields) and source permissions,
and **emits only rows whose status is RULED or BUILT and whose every def resolves**; PROMISED/PROPOSED/
GUESS rows stay in the sheet and are reported, not shipped. Rows that merge materials for reading
(salts, bezoars, brine beds, donor oddities) split into one material each at emission so each has its
own setting.

51 rows today: every one of the 73 inventoried materials is covered (donor oddities that never reach a
map share one row), plus durasteel, duranium, doonium and the promised Scald materials.
**Every biome value is marked GUESS unless its status says otherwise**; the numbers are a starting
point for each biome's sitting, never a ruling.

## 6. How it drives the game

**Architecture: CSV → generated defs → one runtime mod.** `mandrake.rm.minerals`
(`RimMandrake.Minerals`).

1. **Source of truth** is the CSV in the repo. A generator (`src/RimMandrake/Utils/gen_mineral_registry.py`)
   validates it (every defName resolves in the def dump; every biome column is a real BiomeDef; units
   legal) and emits **`RM_MineralRegistryDef` XML**, one def per row. Checked in, diffable. XML
   rather than reading the CSV at runtime: load-time cross-reference errors name a bad defName, other
   mods can patch a row, and nothing depends on file paths inside the game.
2. **At startup** (C#, `StaticConstructorOnStartup`): for every def any row governs, zero
   `mineableScatterCommonality` and `deepCommonality`, clear `isResourceRock` on mineables that are not
   allowed in meteorites, and for MineralsFramework defs set `allowedBiomes` from the row (C2) — so
   no vanilla or donor path can place it any more. **Unregistered minerals are suppressed by default**
   (weights zeroed, one warning naming each), with a setting to leave them vanilla (GPT 3.4: leaving
   them vanilla silently contradicts "carefully selected, period"). All of this lives in one
   **policy service** with one adapter per source (vein, framework, deep, quarry, meteorite, mutator,
   scanner, outpost), and pools are cached per biome × channel × settings revision (GPT 3.5).
   Ordering against other mods' static constructors is not guaranteed, so the service also re-asserts
   at `Game.FinalizeInit` and the Quarry `OreDictionary` is rebuilt after it.
3. **Map generation**: one `GenStep` added to every surface map generator after `RocksFromGrid`. For
   `map.Biome`, it reads each row's effective EPM (CSV value × user setting × hilliness × size), turns
   it into a lump count, and scatters with the vanilla `GenStep_ScatterLumpsMineable` machinery
   (`forcedDefToScatter`, the same field Core uses for Glaciers and Odyssey uses for obsidian). Forms
   that are not veins (nodules, crystals, crusts) are each placed by their biome's own GenStep,
   which reads its count from the same registry instead of a hard-coded number.
4. **Deep drill / scanner**: Harmony **prefix** (replacing the original, GPT 3.2: a postfix lets the
   global draw run first, and the caller dereferences the result immediately) on
   `CompDeepScanner.ChooseLumpThingDef`, with an explicit empty-pool path (no deposit created), draws from rows
   whose biome cell is non-zero (or `deep-only`), weighted by `deep_weight`. Steel is a row like any
   other, so "iron everywhere" is the default data, and a biome with steel 0 has no deep iron either
   (consistent with "some doesn't even have iron"). Ancient mining industry's automated rig is audited
   at build (if it reads the deep grid it inherits this; if it rolls its own table, it gets the same
   postfix).

### 6.4 Quarry (owner ruling 2026-10-03)

Measured from the Quarry mod (CC0; 1.6 DLL metadata confirms the method names in the published
source): `Building_Quarry.GiveResources(ResourceRequest req, …)` returns rock chunks/blocks from the
rock types under the quarry (already local) or, for `Resources`, `OreDictionary.TakeOne()` — a single
planet-wide list built once from every `isResourceRock` mineable plus `ComponentIndustrial`, weighted
by scatter × deep ÷ value. **That draw is the "barfing out any old material".** Design:

- A prefix on `OreDictionary.TakeOne` cannot know the map, and a postfix on `GiveResources` lets the
  global draw run first (GPT 3.2). So a **transpiler on `Building_Quarry.GiveResources` replaces the
  single `OreDictionary.TakeOne()` call** with `MineralRegistry.QuarryDraw(this.Map)`, and the
  empty-pool fallback returns a local chunk **with `singleSpawn` reset to true**. The draw is from this
  map's biome: rows with `quarry=local` and a non-zero
  biome cell, weighted by that cell's EPM ÷ `units_per_cell_or_find` (proportional to how much of it
  the land actually holds). Components and every salvage-only row are `quarry=no`, so they cannot come
  out. If the biome has no quarryable row, the job yields chunks of the local rock.
- Settings: "Quarry output follows local minerals" (on by default) and a quarry yield multiplier.
- The same draw function is the **public API** for the other local-material consumers: FlowWorks canal
  digging, sluice and panning (`FLOWWORKS_QUARRY_DIGGING_1`), the Alpha Biomes core sample drill
  (whether non-local rock is allowed becomes a setting, default off per the ruling), VOE mining
  outposts (registry `quarry` rows for the outpost's tile biome).

### 6.5 Everything else

Meteorites draw only rows flagged meteoritic (steel, plus the Blue Desert's meteoritic metals);
Odyssey's mineral-rich mutator gets every managed def in `resourceBlacklist` and instead boosts the
tile's own rows ×2 (a "mineral-rich" Scald floor is richer in Scald minerals); the long-range mineral
scanner's target list is the rows allowed somewhere on the planet. Salvage and trade columns are read
by the loot/stock generators the salvage work (W6 of the 10-02 design) builds.

## 7. Mod Settings

One screen, `RimMandrake: Minerals`:

- **Per-biome table**: pick a biome, see every material it bears with its EPM written in units
  ("Gold — 1,500 per map ≈ 1 deposit of ~30 cells"), and a numeric field per material that edits the
  EPM directly (not an abstract multiplier). "Reset to registry" per biome and global.
- **Global multipliers** (applied on top): all vein abundance, deep finds, quarry yield, salvage
  richness, trader stock. Default 1.0.
- **Master toggle** "Minerals follow the registry": off restores vanilla weights untouched (all-off
  degrades to vanilla, not to "no ore").
- **Allow non-local rock from core sample drills** (default off).
- Labels say which settings affect **new maps only** (veins, nodules) versus live (deep, quarry,
  trade).

Stored as **sparse absolute overrides** (only the cells a player edited, as values, not arithmetic
deltas — GPT 3.5), so a registry update still reaches every cell he did not touch. Existing maps keep
their placed deposits; changed vein settings apply to new maps, deep/quarry pools rebuild live.

**Save compatibility.** Old defNames (donor durasteels, donor beskars) are kept loadable until
stack, stuff and deep-grid migration is done; nothing is deleted in the first build.

## 8. Normalization process fit

The project already normalizes by **manifest CSV + generator**: the beast normalization
(`design/Jawa/worldbuilding/beast_normalization_spec.md`: *"Manifest-driven (`beast_norm_manifest.csv`
…) — patch a curated artifact, never re-derive"*), the stat-normalization census
(`design/Jawa/mods/stat_normalization_audit_2026-09-09.md`), research normalization. The mineral
registry joins as the **materials axis** of that process:

- It is a curated artifact: edited by hand at biome sittings, never re-derived from a census.
- **Coverage check** (the gate that makes "control, don't absorb" safe): the generator diffs the
  def dump's mineral set (every ThingDef with `building.mineableThing`, `deepCommonality > 0`, a
  MineralsFramework drop, or a Metallic/Gemstones stuff) against the registry's `defs` column, and
  fails listing any unregistered material. A new mod's ore cannot reach a map without a row.
- **Freshness**: the generator stamps the def-dump fingerprint it validated against
  (`dump_fingerprint`), per the fingerprint-not-timestamp rule.
- Each biome sitting reviews its column; that is where the GUESS cells become rulings.
- Downstream normalizations read it: market values (rarity should follow EPM + UPY), recipes that
  need duranium/doonium, trader stock tables.

## 9. GPT consult — taken and rejected

One consult, `gpt-6.1-sol`, effort high, via `src/RimMandrake/Utils/gpt_consult.py` with this doc and the
CSV inlined. GPT numbered its points; citations above use them.

**Taken.**
- 1.1 stochastic rounding of the attempted lump count, and "expected placed" measured by the
  functional script instead of claimed exact (§4).
- 1.2 a per-map "ore per 1,000 eligible rock cells" diagnostic; hilliness kept but labelled policy (§4).
- 1.3 deep and quarry get absolute units: units/find + finds per scanner-year; quarry units per 100
  jobs (new CSV column `quarry_per_100_jobs`). UPY redefined as *offered* at a stated encounter rate.
- 2.1 the absorption criterion is changed (§3): not only "materials we rename/merge" but also
  **"small subsets whose absorption retires a substantial integration burden"**, with per-file licence
  provenance. Applied: LK Mineable Outer Rim is retired outright; Biomes! Fossils' amber/fossil seams
  are an absorb candidate at the Flooded Canyon sitting if its LICENSE.md covers assets; Glowstone has
  no licence and stays controlled (or is replaced by our own crystal).
- 3.1 draft/emitted split, exact bindings, merged rows split at emission; components and durasteel
  rows now name every producer they disable.
- 3.2 deep scanner by **prefix** with an empty-pool path; quarry by **transpiler** on the one
  `TakeOne()` call with `singleSpawn` reset on fallback.
- 3.3 nomadic factor and gravship value rules applied explicitly.
- 3.4 unregistered minerals **suppressed by default**, not left vanilla.
- 3.5 one policy service with per-source adapters; pool caches by revision; sparse absolute overrides;
  keep old defNames until migration.

**Rejected.**
- A value-weighted unit (1.2 itself argues against it: it would tie abundance to the market-value
  normalization, a circular dependency).
- Making "ore per 1,000 rock cells" the player-facing unit: it does not cover nodules, crystals,
  salvage seams or sea floors, and is harder to reason about than "how much do I get from this map".
- Absorbing Jewelry's gems now: its crafting gameplay is still wanted, and NC-SA obligations follow
  any port. Revisit only if the jewellery mechanic is cut.
- Absorbing Minerals Framework/Rock/Sparkle: GPT agrees control wins for the full overhaul.

## 10. Open questions (cards)

`Transient/minerals_cards_2026-10-03.json` holds the cards: absorb-or-control (recommended: control,
absorb only small subsets that retire integration burden), the primary unit (recommended: EPM), what
happens to an unregistered mineral from a new mod (recommended: suppressed), and the quarry's
behaviour on a biome with no quarryable minerals (recommended: local rock chunks only).

## 11. Build waves (FOUNDRY, after the cards)

| wave | what | size |
|---|---|---|
| R1 | `gen_mineral_registry.py`: CSV validate, coverage check against the def dump, emit `RM_MineralRegistryDef` for RULED/BUILT rows | S |
| R2 | `RimMandrake.Minerals` policy service: startup zeroing, unregistered suppression, settings screen | M, C#, Opus |
| R3 | surface adapter: per-biome GenStep with stochastic lump counts + rock diagnostic | M |
| R4 | deep adapter (prefix) and quarry adapter (transpiler) | S each |
| R5 | MineralsFramework, meteorite, mineral-rich mutator, long-range scanner, VOE outpost adapters | M |
| R6 | durasteel donor consolidation (plasteel untouched); duranium/doonium defs and the large-build requirement | M |
| R7 | first functional script: stated vs placed EPM across seeds per biome; deep/quarry draws never leave the local pool; master toggle restores vanilla | S |
