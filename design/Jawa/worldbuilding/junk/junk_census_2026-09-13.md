# Junk census — 2026-09-13

`FASCINATING_WORLD_JUNK_1`, Phase 1 only (CENSUS). Owner's ask: know what wreck/junk/
ruin/debris ThingDefs the map generator scatters, before deciding what stays and what
gets reskinned. This document is that inventory. Phase 2 (donor ideas), Phase 3
(roster), Phase 4 (art/text) are NOT started.

## Method — what was actually measured, and against what

Per CHARTER's instrument order: **RimSage** (vanilla + all 5 DLCs, live source —
`mcp__rimsage__*`) for anything shipped by Ludeon, and the project's **live def
dump / `measure`** for every third-party and our-own mod, because RimSage's indexed
tree is `Defs/{Core,Royalty,Ideology,Biotech,Anomaly,Odyssey}` only — confirmed by
`mcp__rimsage__list_directory` — and does **not** cover a single third-party mod or
any `src/RimMandrake*` def. Searching RimSage for `VFE`, `KOTOR`, `AlphaBiomes`
returned nothing; that is RimSage's registered scope, not evidence those mods are
absent from the game.

The on-disk `defs.sqlite` was **stale** at the start of this session (`captured
2026-09-10T08:36:27Z`, `mods=577`) against a live `ModsConfig.xml` running **594**
active mods including three fresh captures from earlier today
(`captures/2026-09-12T22-49-15Z`). This is a dump that was already sitting there
from a prior game session — no bridge, no game load was invoked to produce it. I
rebuilt `defs.sqlite` from that latest capture (`measure build`, offline, reads an
already-captured `DefDump/`):

```
MEASURED 79522 defs built from .../DefDump/captures/2026-09-12T22:49:15Z
(533 types; absent=0 shadowed=0 ambiguous=0 orphan=0 partial=0 failed=0)
```

All counts below are `MEASURED … @ defs.sqlite mods=594/d4f85d2a9d785594
captured=2026-09-12T22:49:15Z` unless flagged otherwise. Raw `measure sql` rows
(needed for per-package breakdowns the CLI's built-in verbs don't offer) are marked
**RAW** — a real row count from the query, but not a `measure`-blessed Measurement,
per the skill's own distinction.

**Not measured this pass, needs bridge**: live per-map counts (`jawa/list_things` at
Zeddo's Yard and a Fall Line map). That is bridge-driving and explicitly out of scope
for this offline session. Whoever runs Phase 3/verify owes those two counts.

**The dump drops `texPath`/`graphicData` and patch-time xpaths entirely** (project
fact `def-dump-has-no-statbases`) — every texPath and description below came from
`mcp__rimsage__get_def_details` (vanilla/DLC) or a direct read of the mod's own XML
on disk (third-party and our own), never from the dump.

---

## 1. Vanilla + DLC — the actual "crashed 21st-century motorway" mechanism

This is the owner's complaint, precisely located. **`AncientJunkClusters`**
(`GenStepDef`, `Defs/Ideology/MapGeneration/CommonMapGenerator.xml`) is wired into
`Defs/Core/MapGeneration/CommonMapGenerator.xml` under `MayRequire="Ludeon.RimWorld.
Ideology"` — and Ideology is an active `knownExpansion` in this campaign, so **this
GenStep runs on every ordinary outdoor map the game generates** (colony start,
caravan encounter, quest site — anything using the common map generator), at
`countPer10kCellsRange: 0.2~0.5`, `minSpacing: 85`. It is a `GenStep_ScatterGroup`
with 9 weighted "junk group" tables; the vehicle/machine table is group 4 and 5:

| defName | label | texPath |
|---|---|---|
| `AncientRustedCar` | ancient car | `Things/Building/Ruins/RustedCars` |
| `AncientRustedCarFrame` | (car frame) | — |
| `AncientPodCar` | (pod car) | — |
| `AncientRustedTruck` | ancient truck | — |
| `AncientRustedJeep` | ancient troop carrier | — |
| `AncientWheel` / `AncientGiantWheel` | (wheel) | — |
| `AncientRustedEngineBlock` / `AncientLargeRustedEngineBlock` | (engine block) | — |
| `AncientTank` | ancient ruined tank | `Things/Building/Ruins/RuinedTank` |
| `AncientTankTrap` | ancient tank trap | `Things/Building/Ruins/AncientTankTrap` |
| `AncientAPC` | ancient ruined APC | `Things/Building/Ruins/RuinedAPC` |
| `AncientWarwalkerClaw/Leg/Foot/Torso/Shell` | (mech walker remains) | — |
| `AncientWarspiderRemains` / `AncientMiniWarwalkerRemains` | — | — |
| `AncientJetEngine` / `AncientDropshipEngine` / `AncientRustedDropship` | — | — |

Full text for the two headline defs (from `get_def_details`, `merged`):

- **`AncientTank`** — *"ancient ruined tank"* — "The remains of an ancient tank
  which was destroyed by some kind of heavy weapon. All the useful components were
  looted or deteriorated long ago." `ChunkSlagSteel×6` on kill, `MaxHitPoints 2000`.
- **`AncientRustedCar`** — *"ancient car"* — "An ancient, broken car. Everything
  that isn't rusted away was looted long ago." `ChunkSlagSteel×2`.

The other clusters in the same GenStep scatter suburban-earth furniture, not
vehicles — `AncientVendingMachine`, `AncientATM`, `AncientShoppingCart`,
`AncientRefrigerator`, `AncientStove`, `AncientOven`, `AncientWashingMachine`,
`AncientAirConditioner`, `AncientMicrowave`, `AncientToilet`, `AncientPostbox`,
crate/barrel/container piles, and (indoor-ruin flag) `AncientOperatingTable`. This
is where "flavours of ice cream to a Jawa" is least earned right now — none of it
reads as anything but a dead American strip mall.

**Sibling/fallback GenSteps** (same shape, different biome gating):

- **`ScarlandsJunkClusters`** (Odyssey) — the non-Ideology equivalent;
  `preventsGenSteps: AncientJunkClusters` so the two never double-stack. Wired into
  `Defs/Odyssey/BiomeDefs/Scarlands.xml` and `GlacialPlain.xml`, and into the
  generic **`TileMutators_Modifiers.xml`**. Adds cranes (`AncientCraneBase/Arm/
  Column`), a forklift (`AncientIndustrialTruck`), and chemtruck/chembarrel piles.
- **`ScarlandsJunkPrefabs`** — `GenStep_ScatterGroupPrefabs`, drops whole multi-cell
  prefabs: `Exterior_CrashedCrane`, `Exterior_AncientContainerForklift`,
  `Exterior_MilitaryBlockade`, `Exterior_AncientRoad_Short/Long`.
- **`AncientPollutionJunk`** (Biotech, `minPollution: 0.25`) — `AncientToxifierGenerator`,
  `AncientBandNode`.
- **`Mechhive_JunkClusters`** / **`OrbitalRelay_JunkClusters`** — mech-cluster and
  orbital-relay maps only, scatter `ChunkMechanoidSlag` on `MechanoidPlatform`
  terrain — this is the "mech cluster debris" the item asked about; it is a single
  chunk-type, not a roster of distinct wrecks.
- **`Junkyard`** (`TileMutatorDef`, Odyssey) — *"An old dumping ground for various
  kinds of junk."* `chanceOnNonLandmarkTile: 0.01`, `junkDensityFactor: 15` (15× the
  normal rate), and its `extraGenSteps` are exactly `ScarlandsJunkClusters` +
  `ScarlandsJunkPrefabs` — **this is a ready-made "designated junkyard tile" flavor
  already in the engine**, worth flagging for Phase 3 as a candidate to retexture
  wholesale for Zeddo's Yard rather than building a new mutator from scratch.

**Other vanilla/DLC wreck families, not GenStep-scattered the same way:**

- **`AncientFence`** — *"An ancient fence made of reinforced concrete posts joined
  by concrete panels."* `texPath: Things/Building/Linked/AncientFence_Atlas`. Scattered
  by its own `GenStep_ScatterAncientFences` (`AncientFences` GenStepDef, Ideology,
  wired into Core's `CommonMapGenerator.xml`) **and** used as the `perimeterWallDef`
  of several Odyssey ancient-ruins `TileMutatorDef`s (`TileMutators_AncientStructures.xml`).
- **`AncientMechDropBeacon`** — *"The broken shell of a mech drop beacon."*
  `texPath: Things/Building/Ruins/DestroyedMechDropBeacon`. Placed via
  `spawnAtCenter` in `Defs/Ideology/MapGeneration/CommonMapGenerator.xml` (a fixed
  single spawn, not a `ScatterGroup`).
- **`AncientTerminal`** (+ `_Worshipful`, `AncientEnemyTerminal`, `AncientSecurityTerminal`)
  — *"An ancient computer terminal. It can be hacked to reveal long-forgotten
  information."* `texPath: Things/Building/Misc/AncientTerminal/AncientTerminal`.
  Placed inside Anomaly/Odyssey `LayoutRoomDef`s (dungeon interiors), not outdoor
  scatter.
- **`ShipChunk`** / **`ShipChunkIncoming`** — *"A chunk of a spacecraft… Having
  landed not long ago, it still contains useful resources."* `texPath:
  Things/Building/Exotic/ShipChunk`. Spawned by the **`ShipChunkDrop`** `IncidentDef`
  (a skyfaller event, `ShipChunkIncoming` falls then rests as `ShipChunk`), not a
  GenStep — this is a live *event*, and its wreckage is "fresh," structurally the
  same register as the Fall Line's "nothing here is old."
- **`CrashedShipPartIncoming`** — a second, separate crashed-ship skyfaller event
  (own `SoundDef` ambience), Anomaly-side.
- **Ancient Ruins dungeon system** (`AncientRuins*` `LayoutRoomDef`/`StructureLayoutDef`/
  `TileMutatorDef`, ~45 room types, Odyssey/Anomaly) — the interior "vault" crawl
  content: reactors, cryptosleep caskets, insect hives, frozen labs. This is where
  `AncientTank`, `AncientMilitaryBarrier` etc. also get placed as **`PrefabDef`**
  furniture inside a dungeon room, in addition to outdoor scatter. 177 total
  `Ancient*` `ThingDef`s exist in vanilla+DLC (`search_defs` count, RimSage);
  most are indoor dungeon furniture (workbenches, beds, lockers) rather than
  outdoor scatter junk, per the traps section below.

---

## 2. Third-party mods — MEASURED per package, `defs.sqlite`

| package_id | mod | ThingDefs (RAW) | shape |
|---|---|---:|---|
| `xmb.ancienturbanruins.mo` | Ancient urban ruins | 735 | **Whole hand-authored city maps** (`CustomMapDataDef`×42, entered via `SitePartDef`/`WorldObjectDef` world sites), not random GenStep scatter. Building-block ThingDefs include `AM_AbandonedBus`, `AM_AbandonedForklift`, `AM_Amublance`, `AM_AVendingMachine`, plus re-declared `AM_Ancient*` furniture matching the vanilla junk roster. **Named for retirement in the item** — this is the prime Phase 2 donor. |
| `meteores.ancienturbanruinsalldeconstructible.aurad` | (patch add-on) | 0 | Patch-only (makes AURuins defs deconstructible); no defs of its own. |
| `meteores.ancienturbanruinsvanillaloot.aurvl` | (patch add-on) | 0 | Patch-only (vanilla loot tables on AURuins containers); no defs of its own. |
| `sarg.alphabiomes` | Alpha Biomes | 467 total; 7 `AB_Derelict*` | `AB_Derelict*` is **not** vanilla-earth junk — it's ancient-alien-luxury: `AB_DerelictArchotechTower`, `AB_DerelictArchonexusCore`/`Alpha`/`Beta`/`Gamma`/`Delta` (`PrefabDef` + `StructureLayoutDef` "derelict resort" sites), `AB_DerelictSwimmingPool`/`Recliner`/`BeachUmbrella`/`PoolLadder`. Reads much closer to the roster's "Rakatan megastructure, ancient and mostly not junk at all" register than to the Hutt-yard register. |
| `guy762.mm.kotorcore` | Star Wars KotOR Resources and Materials | 532 | **Negative finding**: zero defs match `wreck/salvage/scrap/debris/rubble`. It's a materials/weapons/apparel/sound resource pack (285 `SoundDef`, 136 `RecipeDef`, 43 `HediffDef`, 29 `ColorDef`), not a wreck-scatter mod. |
| `neronix17.outerrim.core` | Outer Rim: Core | 707 | **Negative finding** for scatter defs — only hit was `OuterRim_ScrapperWorksuit`/`Helmet` (apparel, not map junk). |
| `neronix17.outerrim.furnitureanddecor` | Outer Rim: Furniture and Decor | 1051 | Not checked line-by-line this pass (owed, Phase 2) — furniture catalog, likely a `vfepropsanddecor`-shaped no-GenStep set. |
| `neronix17.outerrim.galacticempire` / `.rebelalliance` | Outer Rim faction content | 160 / 61 | Not surveyed this pass — faction gear/pawns, not terrain junk. |
| `vanillaexpanded.vfepropsanddecor` | VFE — Props and Decor | 1805 (1795 are `PropDef`) | **No `GenStepDef`/`TileMutatorDef` of its own** (def_type breakdown: `ThingDef` 1805, `PropDef` 1795, `PropCategoryDef` 40, `HiddenDesignatorsDef` 1) — it is a **player-buildable decoration catalog**, not a map scatterer. 113+ of its ThingDefs directly re-declare the vanilla junk roster as placeable decor: `VFEPD_AncientRustedCar` ("ancient car"), `VFEPD_AncientRustedTruck` ("ancient truck"), `VFEPD_AncientTank`, `VFEPD_AncientAPC`, `VFEPD_AB_Derelict*` (re-declares Alpha Biomes' set too), plus mech-wreck decor (`VFEPD_AB_Mech_Ruined{Activator,Assembler,Turret,Mortar,Shield}`). Whether any other mod's KCSG layout spawns these as symbols is unconfirmed — flagged for Phase 2. |
| `mlie.dungeonpack` | Dungeon Pack | 55 ThingDef, 11 `CustomMapDataDef`, 11 `QuestScriptDef` | Own hand-authored dungeon maps entered by quest/incident, same shape as Ancient Urban Ruins. **Zero `GenStepDef` of its own** in this package — no confirmed mechanism for its furniture "landing outdoors" on an ordinary map; the item's warned trap did not reproduce from the dump alone (a patch injecting it elsewhere would not show here — Phase 2/3 should re-check with a live map, not just the dump). |
| `gmmp.dungeon` | GMMP: Dungeon | 60 ThingDef, 57 `PropDef` | Same shape as Dungeon Pack — quest-site dungeon crawl furniture, no `GenStepDef` in-package. |
| `moja.salvagerubble` | Salvage Rubble | 0 | Patch/behavior-only mod (no defs) — likely changes rubble/chunk salvageability, not a content source. |

---

## 3. Our own mods (`mandrake.*`)

| package_id | mod | relevant defs | status |
|---|---|---|---|
| `mandrake.rm.injections` | RimMandrake: Structure Injections | **0 defs** | Pure C# engine (`GenStep_RimplacePlan`) — the replay mechanism, no content of its own. Active. |
| `mandrake.rsw.injections` | RimStarWars: Structure Injections | 26 defs (2 ThingDef, 12 GenStepDef, 12 TileMutatorDef) | **Active.** Two are direct wreck content: **`RSW_CrashedShip`** (`TileMutatorDef`) — *"A one-deck starship broken open on the ground, bow furrow still scored into the sand… whoever was aboard didn't all make it out."* Template `crashed_ship.txt` places vanilla `ShipChunk`, `AncientLamp`, `AncientMetalCrate`, `Ship_Engine`, `Ship_ComputerCore`, `Ship_CryptosleepCasket`, `LargeThruster`/`SmallThruster`, plus two `SpaceRefugee` skeleton corpses — **but its own source comment says "NOT YET PLACED on any Ash'karr tile."** **`RSW_PodracerWreck`** (`TileMutatorDef` + template) — same status, not yet placed. The other 10 mutators (`KraytGraveyard`, `BanthaGraveyard`, `MynockRoost`, `HuntingLodge`, `BeastPens`, `DeadCaravan`, `GarrisonTiny`, `MiningSite`, `MoistureFarm`, `RoadWarehouse`, `TradingPost`) are not wreck-flavored. |
| `mandrake.rut.injections` | RimUtinni: Structure Injections | n/a | **NOT in the active mod list** (verified against `ModsConfig.xml`'s 594 `<li>` entries and the fresh dump's mod table — absent from both). The repo has it at `src/RimUtinni/StructureInjectionsRUT/`, with `Templates/broken_ring.txt`, `dead_beacon.txt`, `moisture_farm_ruined.txt`, `rakatan_trace.txt` etc. and its own About.xml says its batch-3 content (Oasis Shrine, Rakatan Trace, Cistern, Toll Gap) is "None … yet placed on any Ash'karr tile." Repo-only right now — cannot be counted as live game content. |
| `mandrake.rm.wreckedmachines` | RimMandrake: Wrecked Machines | 15 defs | **Not a scatter-junk mod** — a single restorable-machine mechanic: `RM_WM_AutomatedSmelter_{Wrecked,Kludged,Repaired}` + a `ResearchProjectDef`/`Techprint` to restore it. This IS the shape the item's roster wants (yields/risks/restoration), just scoped to one machine — good template for Phase 3, not itself a source of map junk. |
| `mandrake.rm.graffiti` / `mandrake.rm.sacredgraffiti` | Graffiti Framework / Sacred Marks | 13 / 3 | Wall markings (`RM_Graffiti_Vandal/Scratches/TallyMarks/WarningGlyph`, `RM_SacredMark_Ishko`) — decor/flavor-text layer, not physical wreckage. |
| `mandrake.rut.scavengerevents` | Jawa Scavenger Events | 8 defs | `RUT_PodCrash`, `RUT_ShipBreak` `IncidentDef`s — our own crash-event triggers. Worth cross-referencing in Phase 3: these are candidate hooks for spawning the ruled roster's "fresh wreck" register directly, without waiting on the Fall Line TileMutator. |

**"Fall Line deposition set" — not yet a spawner.** `design/Jawa/worldbuilding/
biomes/fall_line.md` (FROZEN, owner+BENCH 2026-09-05) is a fully-written design
doc describing the Fall Line's fresh/renewable wreckage register in prose, but no
GenStepDef/TileMutatorDef implementing it was found under that name in any active
mod. The nearest live mechanism is `RSW_CrashedShip`/`RSW_PodracerWreck` above —
same register (fresh, active, Star-Wars-flavored), same caveat (not yet placed).
Building the actual Fall Line injection is Phase 3/4 work, not something this
census found already shipping.

---

## 4. What Phase 2 needs (handoff)

1. **Donor mining priority**: `xmb.ancienturbanruins.mo` (735 ThingDefs, the primary
   target the owner named) and its two patch add-ons (`meteores.*`) retire together.
   `neronix17.outerrim.furnitureanddecor` (1051 defs) and `mlie.dungeonpack` /
   `gmmp.dungeon` were not mined line-by-line this pass — do that before ruling them
   in or out as donors.
2. **Re-check "dungeon furniture landing outdoors" against a live map, not the
   dump** — the dump shows no `GenStepDef` for either dungeon mod, but a patch that
   injects one elsewhere would not show here (a patch matching nothing logs
   nothing, and the dump has no xpath provenance). This is the item's own trap,
   unresolved by Phase 1.
3. **Confirm whether any GenStep/KCSG symbol actually spawns VFE Props and Decor's
   113 junk-flavored `PropDef`s** as map content, vs. player-placed-only. If none
   does, VFEPD is decoration reference, not a scatter source, and Phase 3's roster
   should treat it as an art donor rather than a spawner to repoint.
4. **Live counts owed**: `jawa/list_things` at the Zeddo's Yard arrival map and one
   Fall Line map, whole-map, by def — needs the bridge, explicitly out of scope for
   this FOUNDRY offline pass.
5. **Contact sheet of real sprites is owed, not attempted this pass** — it needs
   `rimworld-content-moderation` (render straight from defs) and
   `reading-rimworld-graphics` (loose-PNG-vs-AssetBundle), and meaningfully more
   session time than a CENSUS phase should spend. Build it alongside/after Phase 2's
   donor mining so both draw on the same texPath list.
6. Note for the owner: **`AncientTruck` and `AncientCar` (as literally named in the
   item's own ask) do not exist** — vanilla's names are `AncientRustedCar`/
   `AncientRustedTruck`/`AncientPodCar`; VFE Props and Decor separately declares
   `VFEPD_AncientRustedTruck` ("ancient truck") as buildable decor. Any Phase 3/4
   defName references should use the real names above, not the shorthand in the
   original ask.

## Phase 2 — ideas mined from retiring donors

Read-only pass, per the item spec: no new defs, no XML edits, no Cherry Picker or
`ModsConfig` changes. Goal: borrow *shapes/silhouettes/naming patterns* from mods on
their way out, before the art is gone for good. Method: read each donor's own XML on
disk directly (`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/
<workshop id>/1.6/Defs/...`) — RimSage doesn't index these, per Phase 1.

### 1. `xmb.ancienturbanruins.mo` — the confirmed prime donor

Already Cherry-Picker-**cut** live (`ANCIENT_RUINS_FAMILY_CUT_1`, 2026-09-09 — 559 of
1005 defs cut, the rest fall out of use with the 5 kill-switch QuestScriptDefs gone),
but the mod is still installed and its XML still readable on disk for reference,
which is exactly what this phase needs. A prior deep audit already exists —
`design/Jawa/mods/ancient_ruins_mod_audit.md` — and ruled the *content* uniformly
non-Star-Wars ("modern firearms, LEGO loot, credit cards, mall guards") while flagging
its `ComplexLayoutDef`/`LayoutRoomDef` procedural-dungeon technique (not its assets)
as the one reusable pattern. That audit did not, however, look at shape/silhouette
value independent of the earth-flavor text — which is this phase's actual ask, since
Phase 4 replaces every label/description/texPath anyway. Read directly from
`ThingDef_NonfunctionalBuilding.xml`:

| source def | size (cells) | drawSize | current label/desc | texPath | SW reskin idea |
|---|---|---|---|---|---|
| `AM_AbandonedBus` | (3,8) | (3.3,9) | "abandoned bus" / "Damaged ancient buses." | `Things/Building/AbandonedBus` | a beached repulsor-bus or troop transport hull — long, single-orientation, big enough to anchor a Zeddo's Yard "avenue" the way `AM_MALL` maps anchor a mall |
| `AM_FireTruck` | (7,3) | (9,4) | "ancient fire truck" | `Things/Building/FireTruck` | a crashed light freighter or gunboat fuselage — wide, squat, cab-plus-tank silhouette reads as an armored vehicle hull without new art logic |
| `AM_AncientTruckCarriages` / `AM_FreightTrainCarriages` | (3,5) | (4.8,6.9) | "ancient truck carriages" / "freight train carriages" | `Things/Building/AncientTruckCarriages`, `.../FreightTrainCarriages` | a snapped-off cargo module or shipping-crawler carriage — same footprint works for both a Hutt hauler wreck (Zeddo's Yard) and a derelict cargo skiff (Fall Line, if reskinned "fresh") |
| `AM_Amublance` | (5,2) | (6.6,3.5) | "ancient amublance" (sic) | `Things/Building/Amublance` | a downed medbay speeder or evac pod — smaller vehicle silhouette, single-piece `Graphic_Single`, easy retexture target |
| `AM_AbandonedForklift` | (2,4) | (2,4) | "abandoned forklift" | `Things/Building/AbandonedForklift` | a wrecked cargo-loader droid chassis or repulsor pallet-lifter — good small/medium filler between the bigger hulls above |
| `AM_AVendingMachine` | (1,1) | (2.5,2.5) | "ancient vending machine" | `Things/Container/AVendingMachine` | a dead astromech charging alcove or ration dispenser — smallest tier, good for interior/kiosk dressing rather than open-field scatter |

**Explicit rejects** (confirms the prior audit rather than repeating its work):
`ThingDef_Ruins.xml`/`ThingDef_SalvagePoint.xml` (86 defs of generic concrete rebar
rubble — no silhouette distinct enough to read as anything but rebar), the 83
`ThingDef_NonfunctionalBuilding.xml` mall shells (vending-machine *variants* aside,
arcade cabinets/escalators/ATMs read as contemporary retail, not vehicle or tech
wreckage), `RangedIndustrial.xml`'s 48 modern-firearm defs, `ThingDef_HighValueItem.xml`'s
48 defs (CPU/GPU/credit-card/LEGO loot — the single clearest "not Star Wars" evidence
in the whole mod), the `AM_PlayerColony`/`SafeHouse` alternate-scenario defs, and the
`AncientMallGuards`/`AM_RampageParasite` body-horror faction — none of these have a
shape or concept worth reskinning; they're earth-flavor dead weight straight through,
same verdict the prior audit already reached from the content side.

### 2. `mlie.dungeonpack` — negative finding

`Defs/Buildings/Buildings.xml` carries exactly 7 `ThingDef`s:
`DP_Embrasure`/`DP_HiddenExplosive`/`DP_HiddenFire`/`DP_HiddenSpike`/
`DP_GenPowerUnit`/`DP_MinigunTurret`/`DP_Automortar` — traps and turret/power-node
mechanics for its own quest-triggered dungeon maps (Area 50, Area 52, Grand Walls,
Ninja, Pirate Bay, Private, Sun Cult, Thrumbo Valley — all `QuestScriptDef`-entered
hand-authored maps, same "prefab floor-plan" shape as Ancient Urban Ruins' technique
(a)). **No wreck, vehicle, or debris ThingDef exists in this mod at all** — nothing
to mine. The item's own trap ("re-check dungeon furniture landing outdoors against a
live map, not just the dump") is now moot for the *donor-mining* question: even if a
patch injects `DP_GenPowerUnit` outdoors somewhere, it's a turret/power prop, not a
junk silhouette worth a card.

### 3. `gmmp.dungeon` (GMMP: Dungeon) — negative finding

`Defs/ThingDefs_Props/Buildings_DungeonProps*.xml` is a fantasy-dungeon prop catalog:
gibbet cages (`GM_PropGibbet*`, 4 variants × top styles), bone piles
(`GMMP_DankPyon_RuinedBonePile*`), and generic wood/stone debris
(`GMMP_DankPyon_WoodenDebris`, `StoneDebris(Small)`). This reads as sword-and-sorcery
dungeon dressing, not tech wreckage — cages and bone piles have no Star Wars register,
and the "debris" defs are undifferentiated rubble piles with no silhouette distinct
enough to be worth a card over what vanilla `AncientRuins*` rubble already provides.
**No shapes worth borrowing.**

### 4. `neronix17.outerrim.furnitureanddecor` — out of scope for THIS phase, not mined

Per `STARWARS_DONOR_SUNSET_1`, this mod is Wave-3 (entangled with `DROID_SYSTEM_BUILD_1`'s
port plan, gated on `neronix17.outerrim.core` staying active), not a near-term
retirement, and — more to the point for Phase 2 — it is **already Star-Wars-themed**
content (Outer Rim furniture/decor). Mining an SW mod for "ideas to reskin as SW
wreckage" is circular; it belongs to the droid-porting items' own audit if anything,
not this donor-ideas pass. Phase 1's open question #3 (does any GenStep/KCSG symbol
actually spawn its 113 junk-flavored `PropDef`s as map content, vs. player-placed-only)
remains genuinely unresolved and is **not** answered here — it's a spawn-mechanism
question, not a shape-mining one, and belongs to Phase 3's roster-building pass if it
turns out to matter.

### 5. Non-mod references (owner's ask, Phase 2 spec)

One line each, tied to the three registers `FASCINATING_WORLD_JUNK_1` already
distinguishes (Fall Line fresh/Imperial, Zeddo's Yard Hutt-accumulation, Rakatan
ancient-alien):

- **Jawa sandcrawler yards** (OT concept art / Tatooine) — the reference for **Zeddo's
  Yard** itself: junk sorted into rough piles by kind, nothing catalogued, scale
  ranging from single droid parts to whole vehicle hulls in the same frame.
- **Jakku's Starship Graveyard** (*The Force Awakens*) — half-buried capital-ship
  hulls, dune-scoured, huge single silhouettes rather than piles; the register for a
  "wreck too big to haul" landmark-scale piece, not a scatter object.
- **Raxus Prime** (Legends) — an entire *planet* of junk; useful less as a shape
  reference and more as the naming-convention reference: Raxus content is named for
  function-before-damage ("crashed freighter," "discarded droid foundry"), which is
  the register the roster's "what it was / what it yields / what it risks" naming
  already follows.
- **Bracca / the Scrapper Guild** (*Star Wars Jedi: Fallen Order*) — the reference for
  **fresh, active salvage work**: cables, gantries, and half-stripped hulls mid-cut,
  not decades-settled — closer to the Fall Line's "nothing here is old" register than
  to Zeddo's Yard.
- **Lotho Minor** (Legends, "the Slop") — a world literally made of compacted garbage;
  reference for texture/ground-cover treatment (a junk-compacted terrain look) more
  than for individual object shapes — worth flagging for Phase 4's terrain work, not
  Phase 3's roster of discrete things.

### Phase 2 handoff

The roster material for Phase 3 is: 6 named shapes from Ancient Urban Ruins (table
above, with real def sizes/texPaths a reskin can bind to), plus the five non-mod
references above as tone/naming/terrain guides. Two donor mods (`mlie.dungeonpack`,
`gmmp.dungeon`) are confirmed negative — no further mining owed there. One donor
(`neronix17.outerrim.furnitureanddecor`) is explicitly out of scope for idea-mining
(already SW-flavored) and its spawn-mechanism question is deferred, not answered.

## status

**Phase 1 (CENSUS) — complete, 2026-09-13.** Rebuilt `defs.sqlite` from the latest
already-captured `DefDump/` (594 mods, offline, no bridge/game load used) before
measuring, since the on-disk sqlite was stale by 17 mods and two days. Findings:
the vanilla/DLC `AncientJunkClusters` GenStep family (wired into every common-map
generation via Ideology) is the actual source of "crashed motorway" junk on every
map; `xmb.ancienturbanruins.mo` is the correctly-identified prime donor; KOTOR
core and Outer Rim core are negative findings (no wreck-scatter content); VFE
Props and Decor is a decoration catalog with no scatterer of its own;
`mandrake.rut.injections` (StructureInjectionsRUT) is **not currently active** in
the live mod list despite being fully authored in the repo; `RSW_CrashedShip` /
`RSW_PodracerWreck` are active but explicitly "not yet placed" per their own
source comments. Item left `doing` per FOUNDRY instructions (multi-phase, not
closed). Next FOUNDRY/BENCH pass on this item should start Phase 2 (donor ideas)
using section 4 above as the punch list.
