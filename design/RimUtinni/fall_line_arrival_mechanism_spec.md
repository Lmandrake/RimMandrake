# Fall Line arrival mechanism — design spec

**Item:** `FALL_LINE_ARRIVAL_MECHANISM_1` (the item is the authority; this spec serves it).
**Status:** DRAFT, 2026-09-20. Design only — no def, mod or C# touched.

## 1. The hole this fills

`EXTREME_DESERT_UNRULED_VERMIN_1` (2026-09-20) removed 15 rows from the ambient
`wildAnimals` tables of `RUT_ExtremeDesert`, `RUT_Desert` and `RUT_AridShrubland`
on the owner's §8a ruling (`design/Jawa/worldbuilding/biomes/fall_line.md`):

> *"These falling injections should not be listed as 'sometimes appears' in the deep
> desert but rather arrive with injected content from inhabited from wreckage or,
> alternatively, if we pursue the generator option to produce the same. They are not
> part of 'the biome' there are simply events and subregions where you can meet them."*

The hole is deliberate. The deep desert is meant to be EMPTY; what you meet there
has to have *arrived*. Today nothing delivers any of the 17 species (15 pulled + 2
wreckage creatures that were never wired), so the Fall Line's signature content —
its named vermin, its walking salvage, the §8b "hunting ground, not a battlefield"
beat — does not exist in the game at all.

This spec designs the delivery. It does not touch `wildAnimals` (the rejected
mechanism), it does not roll a planet (there is no worldgen feature), and it must
work by arriving INTO an existing colony map on the already-frozen world.

**Design stance in one line:** every arrival is an **event with a wreck at its
centre**. The wreck is the visible cause; the creatures are what crawls out of it.
Nothing on the Fall Line ever "just appears" — if the player looks for where it came
from, there is always a hull to point at.

## 2. The 15 species, by band

Preserved from the item (the durable record; the roster's injection layer is
deleted). Old ambient commonalities are listed only as a RELATIVE weight for the
arrival tables in §4–§6 — they are never used as biome commonality again.

| band | defName (verify live before wiring) | old weight | note |
|---|---|---|---|
| A ship-vermin | `RSW_Scavrat` | 0.6 | "the name is the job — eats what falls" |
| A ship-vermin | `RSW_WompRat` | 0.4 | icon; nests under hulls |
| A ship-vermin | `RSW_Mynock` | 0.3 | icon; hull parasite — literal canon niche |
| A ship-vermin | `RSW_Cindermite` (ex `VFEI2_Fuelmite`; mid-rebuild in our C# as of 2026-09-20 — confirm defName exists as a spawnable PawnKindDef) | 0.3 | eats fuel |
| A wreckage creatures (never live) | `BMT_BunkerBug` | 0.5 | owner: "Superb for the Fall wreckage creature" |
| A wreckage creatures (never live) | `BMT_Megapleura` | 0.5 | "wreckage-based creature for the Fall" |
| B feral droid | `RSW_DW_OuterRim_MSEDroid` | 0.10 | |
| B feral droid | `RSW_DW_OuterRim_SalvageAssistDroid` | 0.10 | |
| B feral droid | `RSW_DW_OuterRim_DUMDroid` | 0.08 | |
| B feral droid | `RSW_DW_OuterRim_GNKDroid` | 0.08 | |
| B feral droid | `RSW_DW_OuterRim_FX7Droid` | 0.05 | |
| B feral droid | `RSW_DW_OuterRim_MuckrakerDroid` | 0.05 | |
| B feral droid | `RSW_DW_OuterRim_DestroyerDroid` | 0.02 | rare dangerous fall; still flee-prone per §8b |
| B feral droid (roster only, never wired) | `OuterRim_AstromechDroid` | 0.08 | UNMEASURED whether dropped on purpose; this spec INCLUDES it so it is not lost twice |
| C the joke | `Rat` (Core) | 0.1 | ruled in for the joke; must fall out of a ship, white-lab-rat framing |

Bands are not just taxonomy — they are three different EXPERIENCES:

- **A** is *infestation*: the wreck is a nest. You approach a hull and things come
  out of it. Food-web participants (they eat what falls, and each other).
- **B** is *pursuit*: the wreck is cover. Something mechanical breaks from it and
  RUNS. §8b's hunting ground. Invisible to the food web.
- **C** is *comedy*: one white rat, one crate, one message. Once in a long while.

## 3. Engine mechanisms available (measured)

Every def type and class below was read from the decompiled 1.6 engine via RimSage
or from our own source on 2026-09-20. Nothing here is guessed; where a thing was not
verified it is marked UNMEASURED in §12.

### 3.1 What already exists in OUR mods (reuse, do not rebuild)

| piece | where | what it does today | fitness for this item |
|---|---|---|---|
| **`RM_CompVerminNest`** (`RM_CompProperties_VerminNest`) | `src/RimMandrake/ShipVermin/Source/` | A ThingComp for any wreckage ThingDef: every 2–4 days spawns ONE wild pawn from `ShipVerminSettings.PickEnabledNestSpecies()` within radius 4, gated by the shared `RM_MapComponent_VerminPopulation` pool (tag `ShipVermin`, hard cap 12). Roster today: `RSW_Mynock`, `RSW_Scavrat`, `RSW_WompRat`, `VFEI2_Fuelmite` (stale name), `Rat`. | **The Band A engine, already built.** Owner-ruled 2026-09-12 (*"Yes vermin should be able to spawn from wreckage"*). Needs its roster updated (Cindermite rename, BMT pair added, Rat removed to Band C) and a real wreck to sit on. |
| **`WreckVerminNest_ShipChunk.xml`** | `src/RimUtinni/UtinniPatches/Patches/` | Attaches the nest comp (+`tickerType Normal`) to Odyssey's `ShipChunk_Mech`. | The campaign-side wiring half. Today it makes every `ShipChunk_Mech` on ANY map a nest — including the six on the start-map hulk. See §4 for why that is the wrong anchor for the Fall Line. |
| **`RUT_Jawa_GroundHulk`** (PrefabDef) + `RUT_Jawa_StampGroundHulk` (GenStepDef, `GenStep_ScatterGroupPrefabs`, order 940) + `JawaGroundHulk_Register.xml` | `src/RimUtinni/UtinniPatches/Defs/PrefabDefs/`, `Defs/MapGeneration/`, `Patches/` | Stamps ONE 73×16 hull (caskets + 6× `ShipChunk_Mech`) on `Base_Player` maps only. | Proves the PrefabDef → GenStep → map pipeline end to end. The Fall Line wreck is a smaller sibling of this. |
| **`GenStep_RimplacePlan`** + `TileMutatorDef.extraGenSteps` pattern | `src/RimMandrake/StructureInjections/`, `src/RimUtinni/StructureInjectionsRUT/Defs/TileMutatorDefs_Batch*.xml` | A TileMutatorDef whose `extraGenSteps` replay a rimplace BuildPlan when a map generates on that tile. `MapGenerator.cs:158` concatenates mutator `extraGenSteps` into the real pipeline — no Harmony. | **The subregion "place you walk into" mechanism**, already proven. A Fall Line wreck-field mutator is one more def in this family. |
| **`RSW_DW_WildDroidCrash`** (IncidentDef) + `IncidentWorker_WildDroidCrash` + `WildDroidCrashExtension` | `src/RimStarWars/Droidworks/Defs/IncidentDefs/`, `Source/Droidworks/` | ONE factionless droid from a weighted pool walks in from the map edge in `ManhunterPermanent`; baseChance 0.7, minRefireDays 20; capture → `RSW_DW_DataSpike_Wild` overwrites its core. Mod-setting gated. | **Band B's skeleton.** Same worker shape, but §8b wants *flee*, not manhunter — see §5. The DataSpike_Wild capture→memwipe path is already the §8b payoff and needs nothing new. |
| **`GameComponent_GizkaStowaway`** | `src/RimStarWars/GizkaStowaway/Source/` | A found-aboard event: Harmony postfix on `Scenario.PostGravshipLanded` (35 %), `TradeDeal.TryExecute` (5 %), `Quest.End`, salvage `Thing.Destroy`. Never a storyteller roll. | **Band C's model.** The white rat is a stowaway joke, and this mod already knows how to tell one. |
| `RUT_ShipBreak`, `RUT_SurvivalPod`, `RUT_PodCrash` (ScavengerEvents) | `src/RimUtinni/ScavengerEvents/` | Drop-pod incidents via `DropPodUtility.DropThingsNear`; pods carry pawns and cargo. | Reference for "something falls and opens"; not reused directly. |
| **Gravship Crashes** (`Arcjc007.GravshipCrashes`, donor, installed) | workshop `3578515873/1.6/Defs/` | `CrashedGravshipIncident` → `IncidentWorker_CrashedGravship`; `CrashedGravshipSite` WorldObjectDef + `CrashedGravshipSitePart` SitePartDef; `BrokenGravEngine`; `GravshipCrashLoot` ThingSetMaker; `BrokenSubstructure` terrain. | The only installed "crash creates a SITE on another tile" mechanism. A dependency our hulk already takes. Its internals are UNMEASURED (assembly only, not read) — §12. |

### 3.2 Vanilla mechanisms, read from the engine

| mechanism | def / class (verified) | what it does | verdict for arrivals |
|---|---|---|---|
| **Ship chunk drop** | `IncidentDef ShipChunkDrop`, `IncidentWorker_ShipChunkDrop`, skyfaller `ShipChunkIncoming` → `ShipChunk`; `SkyfallerMaker.SpawnSkyfaller(ThingDefOf.ShipChunkIncoming, ThingDefOf.ShipChunk, pos, map)`. 1–4 chunks within 5 cells; count decays over game time; a `Messages.Message`, not a letter. | Something visibly FALLS from the sky onto the colony map and lands as a haulable chunk. | **The Band A delivery verb.** Our incident copies this shape: a skyfaller lands a wreck *that is a nest*. |
| **Skyfaller properties** | `Verse.SkyfallerProperties`: `ticksToImpactRange`, `explosionRadius/Damage`, `metalShrapnelCountRange`, `rubbleShrapnelCountRange`, `spawnThing`, `cameraShake`, `impactSound`, `anticipationSound`, `shadowSize`, `speed`, `movementType`. | Fully data-driven fall: shrapnel, shake, sound, what spawns on impact. | The wreck's own skyfaller ThingDef is pure XML. |
| **Drop pods with contents** | `DropPodUtility.DropThingsNear(IntVec3, Map, IEnumerable<Thing>, openDelay=110, …)` (`RimWorld/DropPodUtility.cs:27`). | A pod that opens and releases any Things, pawns included. | **Band C**: one pod, one rat, one opening delay. |
| **Walk-in from map edge** | `IncidentWorker_HerdMigration` (`RCellFinder.TryFindRandomPawnEntryCell` + `LordJob_ExitMapNear`), `IncidentWorker_WildManWandersIn` (`CellFinder.TryFindRandomEdgeCellWith(CanReachColony)`, `pawn.SetFaction(null)`). | Pawns enter at an edge and either cross the map or stay factionless. | **Band B's walk-in variant** (the survivor that has been out there for years and drifts into your map). HerdMigration itself draws from `map.Biomes[].AllWildAnimals`, so it can NEVER pick our species now — good; that is the ruling working. |
| **Incident biome gating** | `IncidentDef.allowedBiomes` / `disallowedBiomes` (`IncidentDef.cs:41,43`), checked in `IncidentWorker.cs:62–73` against the map's primary biome. | Restricts an incident to biomes. | Necessary but NOT sufficient: the Fall Line is 82 % `RUT_ExtremeDesert`, which is also the deep desert. Biome gating cannot tell the Fall Line from the rest of the sand — a REGION gate is needed (§3.3). |
| **Tile mutator** | `RimWorld.TileMutatorDef`: `extraGenSteps`, `preventGenSteps`, `animalDensityFactor`, `junkDensityFactor`, `chunkDensityFactor`, `biomeWhitelist`, `categories`/`priority`, `chanceOnNonLandmarkTile`, `workerClass` (`TileMutatorWorker`), `additionalGameConditions`, `blacklistedRaidStrategies`. No incident table, no wild-animal list. | Per-tile map-generation modifiers plus extra gensteps. | **The subregion mechanism**: a wreck-field mutator stamps wrecks at map-gen. `animalDensityFactor` on it lets the Fall Line be *emptier* than the biome, which is the ruling's other half. ⚠️ It has no per-tile *incident* hook — incidents must read the tile's mutators themselves (§3.3). |
| **Sites** | `SitePartDef.ExtraGenSteps` (`SitePartDef.cs:136`), `Site.cs:131`; `QuestNode_Root_Site` with `allowedBiomes` + `allowedLandmarks` (`FastTileFinder.Query`). | A WorldObject on an existing tile whose map generates when visited. | A "go to the wreck" quest is legitimate on the frozen world (it places an object on a tile that already exists; it never rolls a planet). Deferred to v2 (§9) — v1 is all on the colony map. |
| **Flee AI** | `JobGiver_AnimalFlee` (`RimWorld/JobGiver_AnimalFlee.cs`) for animals. For HUMANLIKE factionless pawns there is no vanilla "flee everyone" state: `WildMan` wanders; `ManhunterPermanent` attacks. `Pawn_MindState.Fleeing` — UNMEASURED (search returned nothing under that name). | | §5 needs a small custom `ThinkNode`/`JobGiver` for the feral droids; it is the one piece of new C# on the critical path. |

### 3.3 The one gap the engine leaves: "is this map ON the Fall Line?"

Nothing vanilla answers that. The region is a named `feature_id` in
`world/ASHKARR_VIVIFIED_2026-08-24_tiles.csv` (308 tiles, `region == "The Fall Line"`);
in-game it is a `WorldFeature`. Three ways to gate, in order of preference:

1. **A Fall Line TileMutatorDef present on the tile** (`map.TileInfo.Mutators.Contains(RUT_FallLineWreckField)`) — placed by hand on the frozen world through the bridge (`world_*` tools + `world_commit`), exactly like every other authored mutator. This is authoring THE map, not generating one. Deterministic, saveable, inspectable in the tile tooltip, and the same flag the map-gen genstep reads. **Chosen.**
2. The tile's `WorldFeature` name — fragile (string match on a label).
3. Arc/coordinate box — UNMEASURED whether `PlanetTile` exposes what we need cheaply; and it duplicates the CSV in code. Rejected.

So every arrival incident in this spec has a `CanFireNowSub` that returns false unless the
map's tile carries the Fall Line mutator (or the player has the "anywhere" setting on, §10).


## 4. Band A — ship-vermin: how they arrive

**Mechanism: a new IncidentDef, `RUT_FallArrival`, whose worker drops a WRECK skyfaller
onto the colony map; the wreck is a building carrying `RM_CompVerminNest`; the vermin
crawl out of it.** Nothing in this band ever spawns without a hull to point at.

🔑 **The colony is already on the Fall Line.** Start tile 17007 is region `Fall Line
Barrens` (MEASURED from `world/ASHKARR_VIVIFIED_2026-08-24_tiles.csv`: `Fall Line` 155
tiles + `Fall Line Barrens` 153 = the 308 in `fall_line.md` §0). So "arrive into an
existing colony's map" is not a corner case — it is the main case, from the first day.

### 4.1 The pieces (all data unless marked C#)

| piece | def type | notes |
|---|---|---|
| `RUT_FallWreck_Hull`, `RUT_FallWreck_Cargo`, `RUT_FallWreck_Tank` | `ThingDef` (building, `ParentName` a sibling of Odyssey's `ShipChunkBase`; size 2×2 in v1; `Graphic_Random`; `tickerType Normal` — the trap `WreckVerminNest_ShipChunk.xml` already hit; deconstructible for steel/plasteel/components so a wreck is also SALVAGE; not haulable, not minifiable) | Three wreck *kinds* so the species mix reads as a story: a hull rib is where mynocks cling; a cargo section is where rats and womp rats nest; a fuel tank is where cindermites feed. v1 may reuse `ShipChunk_Mech`'s texPath set (Odyssey art) and diverge later. |
| `RUT_FallWreckIncoming_*` | `ThingDef` with `thingClass Skyfaller` and `<skyfaller>` (`Verse.SkyfallerProperties`): `spawnThing` = the wreck; `explosionRadius 0` (it is a wreck, not a bomb — no fire on the deep desert); `metalShrapnelCountRange 3~6` (slag chunks = the "debris scar upwind"); `cameraShake`; `impactSound`, `anticipationSound`; `ticksToImpactRange 240~360` so the shadow is SEEN growing. | Same shape as `ShipChunkIncoming` → `ShipChunk` (`IncidentWorker_ShipChunkDrop.SpawnChunk`). |
| **`RM_CompVerminNest` on each wreck** (`RM_CompProperties_VerminNest`, existing) | comp | Interval 2~4 days, radius 4, tag `ShipVermin`, hard cap 12 — the owner's "nuisance unless there are many" ceiling, shared with the mynock breeder. Per-wreck species weighting is the one addition owed: today the comp picks uniformly from the settings roster. **Owed C# (small):** an optional `speciesWeights` list on `RM_CompProperties_VerminNest`, falling back to the roster when empty. |
| `IncidentDef RUT_FallArrival` | `IncidentDef`: `category Misc`, `targetTags Map_PlayerHome`, `letterDef NeutralEvent`, `baseChance` per §8, `minRefireDays` per §8, `allowedBiomes` = `RUT_ExtremeDesert`, `RUT_Desert`, `RUT_AridShrubland` (belt-and-braces; the real gate is the mutator) | Copies `ShipChunkDrop`'s shape (Core `baseChance 3`, `category ShipChunkDrop`); ours has its own category so storyteller weighting is separable. |
| `IncidentWorker_FallArrival` | **C#** | `CanFireNowSub`: Fall Line gate (§3.3) + `CellFinderLoose.TryFindSkyfallerCell` for the wreck def's `terrainAffordanceNeeded`. `TryExecuteWorker`: pick a wreck kind by weight → `SkyfallerMaker.SpawnSkyfaller(incoming, wreck, pos, map)` → after impact (a `CompSpawnOnImpact`-style hook or simply the nest comp's first tick set to `Rand(600, 2400)` ticks instead of 2–4 days) spawn the **initial burst**: 2–4 pawns from that wreck's species weights, standing within radius 4, all wild, faction null → send the letter. |

### 4.2 Species weights per wreck kind (relative, from the old commonalities — §2)

| wreck | `RSW_Mynock` | `RSW_Scavrat` | `RSW_WompRat` | `RSW_Cindermite` | `BMT_BunkerBug` / `BMT_Megapleura` |
|---|---|---|---|---|---|
| Hull rib | **6** | 2 | 1 | 0 | (deferred, §9) |
| Cargo section | 1 | **6** | **4** | 0 | (deferred) |
| Fuel tank | 1 | 1 | 0 | **6** | (deferred) |

Weights are drafted numbers for the owner to tune at quicktest, per this kit's convention.

### 4.3 What must change in what already exists

- `ShipVerminSettings.NestSpeciesRoster` (`src/RimMandrake/ShipVermin/Source/RM_ShipVerminMod.cs:44–50`): `"VFEI2_Fuelmite"` → `"RSW_Cindermite"` (MEASURED 2026-09-20: `RSW_Cindermite` exists as PawnKindDef `zhakka` + ThingDef in SWBestiary; `VFEI2_Fuelmite` also still exists, as the donor's own def, so the stale entry silently spawns the DONOR mite today). **`"Rat"` comes OUT of the nest roster** — under §8a's exception the rat arrives only through Band C. `GetNamedSilentFail` means a missing name costs nothing, so `BMT_*` names may be listed ahead of their port.
- `WreckVerminNest_ShipChunk.xml` (the `ShipChunk_Mech` wiring) **stays**. The owner's 2026-09-12 ruling stands, `ShipChunk_Mech` only reaches a map through a hulk or a crash, and the start hulk IS a Fall Line wreck. It is not the Fall Line gate, and it does not need to be.
- The live-verify owed on `WRECKAGE_VERMIN_SPAWN_1` (About.xml: "quicktest verify … has not yet been run live") is inherited by this item — the `tickerType` fix landed but the "vermin attributable to a placed wreck" test is still unrun.


## 5. Band B — feral droids: how they arrive

**Mechanism: a new IncidentDef, `RUT_FallSurvivor`, sharing `IncidentWorker_WildDroidCrash`'s
skeleton (factionless droid, weighted pool in a `DefModExtension`, mod-setting gate) but
with the OPPOSITE behaviour: it runs.** Two spawn routes, one worker:

| route | when | where it appears | why |
|---|---|---|---|
| **Breaks from the wreck** | rider on `RUT_FallArrival` (§4), chance per §8 | at the wreck, the moment the first colonist comes within ~25 cells of it (a `CompProperties`-driven trigger on the wreck: `RUT_CompFeralLurker`, C#) — NOT at impact | "the wreckage matters — it is the cover they break for" (§8b). The player walks up to loot a wreck and something mechanical bolts from under it. |
| **Drifts in** | its own storyteller roll | map edge, `RCellFinder.TryFindRandomPawnEntryCell` (as `IncidentWorker_WildDroidCrash` does) | a survivor that has been out there for years and wandered onto your map |

### 5.1 The pool (all MEASURED present in the 2026-09-20 dump unless noted)

`RSW_DW_OuterRim_MSEDroid` 10 · `RSW_DW_OuterRim_SalvageAssistDroid` 10 ·
`RSW_DW_OuterRim_DUMDroid` 8 · `RSW_DW_OuterRim_GNKDroid` 8 ·
`RSW_DW_OuterRim_RSeriesDroid` 8 (this is the roster's `OuterRim_AstromechDroid` — that
name was a RACE-side guess and never a PawnKindDef, which is why it was never wired; the
kind's race is `RSW_DW_Race_OuterRim_AstromechDroid`) · `RSW_DW_OuterRim_FX7Droid` 5 ·
`RSW_DW_OuterRim_MuckrakerDroid` 5 · `RSW_DW_OuterRim_DestroyerDroid` 2.

All eight are Humanlike-intelligence droids on `RSW_DW_FleshType_Droid` (Droidworks
`Races_Base.xml`), every one carrying the `combatPower 99999` keep-out-of-raids sentinel —
so, exactly as `IncidentWorker_WildDroidCrash` documents, the pick is a flat weighted
choice, never points-scaled, and it is **ONE droid per event**.

### 5.2 Behaviour — "wily, flee-prone" (§8b), the one genuinely new C# piece

Vanilla offers no "factionless humanlike that flees everyone": `WildMan` wanders,
`ManhunterPermanent` attacks, `PanicFlee` recovers in ~0.3 days (`MentalStateDef PanicFlee`,
`recoveryMtbDays 0.3`, MEASURED). So Band B needs a **think-tree insert** — the pattern
Droidworks already ships as `RSW_DW_RechargeInsert` (`ThinkTreeDefs_DWRecharge.xml`):

- `RUT_FeralDroidInsert` (`ThinkTreeDef` with `insertTag`, subtree gated on a
  `RUT_Hediff_Feral` hediff — the hediff is the flag, so the state survives save/load and
  is removed cleanly by the memwipe).
- `JobGiver_FeralFlee`: if any colonist/colony animal within 18 cells → `FleeUtility.FleeJob(pawn, threat, 24)` (the exact call `JobGiver_AnimalFlee` makes, MEASURED), preferring a destination within 6 cells of a wreck (`RUT_FallWreck_*` or `ShipChunk_Mech`) when one is reachable — cover-seeking is what makes it a *hunt*.
- `JobGiver_FeralLurk`: otherwise wander near the nearest wreck; at night stand still under it.
- **Cornered** (no flee cell found): melee/shoot the nearest threat — the only time it fights. The Destroyer droid is the exception that makes the rule felt: it flees like the rest, but cornered it is dangerous.
- Faction stays **null** for its whole life (§8b: no affiliation). Nothing here touches goodwill; a factionless pawn's death fires no `GoodwillSituation` in vanilla — **UNMEASURED**, listed in §12, because the "no droid hatred" carve-out depends on it.

### 5.3 Capture → memwipe — already built, needs no new work

Down it (the campaign's ion weapons; Droidworks' `IonBuildup_PowersDownDroid.xml` patch
makes ion damage power a droid down), arrest it, and `RSW_DW_DataSpike_Wild` ("built for a
droid with no faction ownership … only works on one you have already taken prisoner")
grinds its resistance to zero. The `RUT_Hediff_Feral` hediff is removed by the wipe recipe
(one line in the existing recipe's worker, or a `HediffComp` that removes itself when
`pawn.Faction == Faction.OfPlayer`). §8b's "restoration is clean" then holds by construction.

### 5.4 Reconciling with `RSW_DW_WildDroidCrash`

Two owner rulings, both live: DROID_UNIFIED_FRAMEWORK ruling 2 ("gone crazy … after
crashing" → manhunter) and `fall_line.md` §8b ("wily, flee-prone"). They are two different
animals and both stay: the **wild droid** is the mad one that attacks, anywhere in the
desert; the **feral survivor** is the Fall Line's own, and it runs. Same pool overlap is
fine — the behaviour, letter and location tell them apart. `RSW_DW_WildDroidCrash` is not
touched by this item.


## 6. Band C — the deliberate vanilla Rat

> *"actual terrestrial rats might be fun to fall from a ship as a white lab rat. That is all.
> So keep it."*

**Mechanism: a `PawnKindDef` and one drop pod.**

- `RUT_LabRat` — `PawnKindDef` with `race Rat`, label "lab rat", `lifeStages[*].bodyGraphicData.color` white (Core `Rat`'s kind sets `(110,95,82)` on the shared `Things/Pawn/Animal/Rat/Rat` texture, MEASURED via RimSage; a colour on the same texture IS the white rat — no art). Core `Rat` race stats stand: `Wildness 0.5`, `petness 0.15`, `MoveSpeed 4`, tameable, `trainability None`. It is NOT a new race and it is never in any `wildAnimals` table.
- `IncidentDef RUT_LabRatFalls`, `category Misc`, `letterDef NeutralEvent`, gated on the Fall Line like everything else, rate per §8. Worker: one `RUT_LabRat` pawn, faction null, in one pod via `DropPodUtility.DropThingsNear(cell, map, [pawn], openDelay: 180)` (`RimWorld/DropPodUtility.cs:27`, MEASURED) — the pod is the "fell from a ship" the owner asked for, and a lone pod on the sand with a rat in it is the whole joke.
- Rider: 1 in 10 `RUT_FallArrival` cargo sections includes one `RUT_LabRat` in the initial burst — a lab rat among the scavrats, for the player who looks closely.
- Letter (draft): **"Specimen"** — *"A single escape pod has come down on the flats. It contains one white rat, ear-tagged, in good health, and nothing else. Whatever it was part of, it is not any more."*

Guard for future sweeps: `RUT_LabRat` carries a `<description>` naming the §8a ruling, and
the linter exemption in `fall_line.md` §8a covers it. It is the one Earth animal on the belt,
by design.


## 7. What the player sees and feels, first time

The owner judges by experience, so this is the acceptance test, in order:

**Band A — the fall.** Mid-afternoon, day 4 or so. A low rising sound (`anticipationSound`,
~100 ticks before impact) and a shadow on the hardpan that is too big and getting bigger.
The camera shakes once; slag chunks skitter out in a line (the shrapnel range) and the
dust settles on a scorched hull section, 2×2, smoking, throwing the only hard black shade
for a hundred cells. A neutral message, not a letter: *"Something has come down on the
flats."* The player pauses, looks, goes back to work. Twenty to forty seconds later the
first scavrat noses out from under it. Then a second. The letter arrives now, on the first
spawn, not on impact: **"Wreck: hull section"** — *"A piece of somebody else's ship has come
down within sight of the colony. It is throwing shade, and things have already moved in
under it. It can be stripped for metal — if you want to be the one standing next to it."*
The tension the owner asked for is exactly here: salvage you want, in shade you need, with
an infestation ceiling you do not know yet. Leave it a season and there are twelve of them.

**Band B — the flush.** Later, the player sends a hauler to strip a cargo section. As the
pawn closes to ~25 cells, something the size of a dog breaks from the shadow and RUNS —
flat-out, small, mechanical, away across the open pan toward the next wreck (§9's "nothing
moves but heat shimmer and, occasionally, something small going flat-out from one shadow to
the next" — the art-theme line is now a mechanic). Letter: **"Fall survivor"** — *"A salvage
droid has been living under that wreck. Nobody owns it and it is not stopping to talk. It
will not fight unless it has nowhere left to run. Bring it down intact and it can be wiped
and made whole."* The player learns in one look that the verb is pursuit, that ion weapons
matter, and that the wrecks are cover.

**Band C — the rat.** Once a year, if that. A single pod, no wreck, no vermin. Opens on a
white rat with an ear tag that sits up and looks at the colonist. The letter is one line.
Everyone who plays it tells someone.

**What the player must NEVER see:** a scavrat on the open sand with no wreck within 30
cells; a vermin count climbing past 12 per map; a feral droid attacking first; a rat that
did not come out of something.


## 8. Frequency and pacing

Calibrated against installed neighbours: Core `ShipChunkDrop` `baseChance 3`, own
category; `RSW_DW_WildDroidCrash` 0.7 / 20 days; ScavengerEvents `RUT_ShipBreak` 1 / 15,
`RUT_SurvivalPod` 1.5 / 25. Arrival must feel like an event: **never more than one wreck a
week, a droid every couple of weeks, a rat every year or two.**

| incident | `baseChance` | `minRefireDays` | `earliestDay` | riders | ceiling |
|---|---|---|---|---|---|
| `RUT_FallArrival` (Band A) | 2.0 | 6 | 2 | 30 % carries a Band B lurker; 10 % of cargo sections carries a lab rat | vermin pool hard cap 12 (`ShipVermin` tag); wrecks themselves uncapped — stripping them is the player's answer |
| `RUT_FallSurvivor` (Band B, drift-in) | 0.8 | 12 | 5 | — | one droid per event; no more than 3 feral droids alive per map (worker refuses above it) |
| `RUT_LabRatFalls` (Band C) | 0.15 | 90 | 10 | — | one |

All three carry a frequency multiplier from Mod Settings (§10) applied in
`CanFireNowSub`/`TryExecuteWorker` the way `ShipVerminSettings.wreckSpawnRateMultiplier`
already is. Nests keep the existing 2–4 day interval; the initial burst is the only thing
that fires fast.

Pacing note: because the start colony is on the belt, the first wreck lands inside the first
week by design (`earliestDay 2`) — the belt introduces itself. The deep desert beyond it
stays empty, which is the ruling.


## 9. v1 versus deferred

### v1 — minimum shippable delivery for every species that is INSTALLED (13 of 15 + 1)

| # | piece | kind | owner-side risk |
|---|---|---|---|
| 1 | `RUT_FallLine` `TileMutatorDef` (no gensteps in v1; `animalDensityFactor` 0.5 so the belt reads emptier than its biome; label/description so the tile tooltip says "the Fall Line") placed on the 308 region tiles through the bridge (`world_*` + `world_commit`) and saved into the start save | data + one world-authoring pass | the frozen start save changes; back it up per the savegame rules; the tile edit is authoring THE map |
| 2 | `RUT_FallWreck_{Hull,Cargo,Tank}` + `RUT_FallWreckIncoming_*` skyfallers | data | art: reuse `ShipChunk_Mech`'s texPath set; check `infrastructure/artpipe/done/` before commissioning anything |
| 3 | `RM_CompProperties_VerminNest.speciesWeights` + initial-burst hook | small C# in ShipVermin (RM tier, generic) | |
| 4 | `ShipVerminSettings` roster: Cindermite rename, Rat removed, `BMT_*` names pre-listed | one-line C# | |
| 5 | `IncidentDef RUT_FallArrival` + `IncidentWorker_FallArrival` + letters | data + C# | |
| 6 | `RUT_Hediff_Feral`, `RUT_FeralDroidInsert` think tree, `JobGiver_FeralFlee`/`_FeralLurk`, `RUT_CompFeralLurker` | C#, the critical-path piece | the flee/cornered logic needs a quicktest with ≥5 droids (one pawn's result is RNG) |
| 7 | `IncidentDef RUT_FallSurvivor` + worker + letter; memwipe removes the hediff | data + C# | |
| 8 | `RUT_LabRat` kind + `RUT_LabRatFalls` incident + letter | data + tiny C# | |
| 9 | Mod Settings screen (§10) | C# | |
| 10 | Home: a new RimUtinni-tier mod **`FallLineArrivals`** (`mandrake.rut.falllinearrivals`, namespace `RimMandrake.Utinni.FallLineArrivals`) depending on `mandrake.rm.shipvermin` and `mandrake.rsw.droidworks`; generic engine bits (#3, #4) land in ShipVermin, the feral think tree in Droidworks if it is species-agnostic, else here | | naming per `NAMING_SCHEME_PLAN.md`; a mod is deployable only with `About.xml` + packageId |

### Deferred (named, not lost)

- **`BMT_BunkerBug`, `BMT_Megapleura`** — MEASURED ABSENT from the 618-mod dump (`measure find`, every slice complete). They belong to *Biomes! Polluted Lands* (`biomesteam.biomespollutedlands`, per `design/Jawa/fauna/animal_census.csv`), which is not loaded. Two routes, needs a card: load that mod (a Charter expensive-list action) or port the two defs to `RSW_`/`RUT_` names the way Cindermite was. v1 lists their names in the roster so wiring is a rename when they land.
- **Wreck-field map generation** — `extraGenSteps` on the `RUT_FallLine` mutator scattering 2–5 `RUT_FallWreck_*` (with nests) on any NEW Fall Line map via `GenStep_ScatterGroupPrefabs` (the hulk's proven pipeline). Cheap, but it only affects maps generated after it ships (gravship relocation, caravan stops), never the frozen start map — so it is v1.1, not v1.
- **The live wreck** — a Gravship-Crashes-style site (`WorldObjectDef` + `SitePartDef.ExtraGenSteps`, 12–20 day timeout, "something still runs") on a neighbouring Fall Line tile: the tile's prize from `fall_line.md` §8. Needs the `rimworld-quests` skill and its validator; v2.
- **Feral RACES** (§8b's "normally sentient races gone feral") — not in this item's 15; the flee think-tree and lurker comp are written species-agnostic so they carry over. Capture-to-slave with the permanent mental-scar hediff is its own item.
- **Mental treatment** at Helix / deep-water holdings — owner: v2 only, do not build.
- Wreck art variants, a scar/gouge terrain patch upwind (`terrainPatchMakers` on the mutator), aiming the breach at the colony.


## 10. Mod Settings surface

Per CLAUDE.md every mod ships a real settings screen; defaults are the shipped behaviour;
all-off degrades to "the Fall Line is just empty desert", which is a legal state.

| section | control | default | note |
|---|---|---|---|
| **Where** | "Only on Fall Line tiles" | ON | OFF lets every arrival fire on any desert map — labelled *changes which maps get events*, not worldgen |
| **Wreck falls (Band A)** | on/off | ON | |
| | frequency ×0.25–×4 | ×1 | |
| | initial burst 0–6 | 2–4 | 0 = the wreck lands silent and only the nest produces |
| | wreck kinds: hull / cargo / tank checkboxes | all ON | |
| | species roster | inherits `ShipVermin`'s per-species checkboxes — one roster, not two; this screen links to it | the nest engine already owns the roster |
| **Fall survivors (Band B)** | on/off | ON | |
| | frequency ×0.25–×4 | ×1 | |
| | chance a wreck hides one, 0–100 % | 30 % | |
| | allow the Destroyer droid | ON | the one dangerous pull |
| | max feral droids per map 1–10 | 3 | |
| | behaviour: flee (ruled) / attack like a wild droid | flee | for players who want the old wild-droid feel on the belt too |
| **The specimen (Band C)** | on/off | ON | |
| | frequency ×0.25–×4 | ×1 | |
| **Debug** | "Drop a wreck here" / "Spawn a survivor at edge" / "Drop the rat" dev actions | — | so the owner can LOOK without waiting a season; `RM_ShipVerminDebugActions` is the pattern |

No setting alters a `wildAnimals` table. There is deliberately no "also spawn ambiently"
option — that is the mechanism the owner rejected.


## 11. Constraints honoured

- **No worldgen.** Nothing rolls a planet or a variant. The one world touch is placing a
  mutator on 308 existing tiles of THE map, by hand, through the bridge, and freezing it into
  the start save — the same act as every road and landmark already authored there.
- **Works on the frozen world, into an existing colony map.** All three v1 incidents target
  `Map_PlayerHome` and the colony is on the belt from tick 0.
- **Not a spawn table with extra steps.** Every species enters through a visible cause
  (skyfaller, lurker flush, pod) with a letter, a ceiling, and a way for the player to end it
  (strip the wreck, capture the droid).
- **No `wildAnimals` rows, no `wildBiomes` dicts.** `RSW_Scavrat.xml` / `RSW_WompRat.xml`
  still carry dead pre-rename `wildBiomes` keys (item watch-out); they are inert today and
  should be deleted in the build so a future rekey cannot reopen ambient spawning.
- **§8b not foreclosed.** Factionless, flee-first, capture → `DataSpike_Wild` → clean
  restoration; the feral flag is a removable hediff, so the slave/mental-scar path for races
  can reuse the same insert with a different hediff.
- **Naming.** Everything new is `RUT_`/`mandrake.rut.*`/`RimMandrake.Utinni.*`; generic engine
  additions stay `RM_` inside ShipVermin.


## 12. UNMEASURED and open

| claim | status | how to measure |
|---|---|---|
| A factionless humanlike's death or capture fires no faction goodwill change ("no droid hatred", §8b) | **UNMEASURED** | RimSage: `GoodwillSituationManager` / `Faction.Notify_MemberDied` paths for `pawn.Faction == null`; then a quicktest kill |
| `Pawn_MindState` exposes a usable "fleeing" flag for humanlikes | **UNMEASURED** — search for `public bool Fleeing` returned nothing; the spec routes round it with a hediff-gated think insert | not needed if the insert is used |
| Gravship Crashes' `IncidentWorker_CrashedGravship` internals (site tile choice, defenders, loot) | partially read: creates a site via `GravshipSpawnUtility.TryFindSiteTile`/`CreateSite`, timeout 12–20 days, positive letter | read `GravshipSpawnUtility.cs` before v2's live-wreck site |
| The exact `Tile` accessor for mutators from a `Map` | `Tile.mutatorsNullable` field MEASURED; `tile.Mutators` property used by `TileMutatorDef.IsValidTile` (so it exists); `map.TileInfo` → that `Tile` is the expected route | confirm with RimSage `read_file Planet/Tile.cs` at build |
| `ShipChunk_Mech` nest wiring actually produces a pawn live | the `tickerType` fix landed 2026-09-12; the attributable-spawn quicktest is still owed (ShipVermin About.xml) | run it as this item's first quicktest — it is the engine v1 rides on |
| `BMT_BunkerBug`, `BMT_Megapleura` | MEASURED ABSENT from the dump (mod not loaded) | card: load *Biomes! Polluted Lands* or port |
| Whether the 209 mutators already on the belt (`Dunes` 61, `Mountain` 45, `VEE_MineralDevoid` 22 … per `ASHKARR_VIVIFIED_2026-08-24_mutators.csv`) conflict with a new category-less `RUT_FallLine` mutator | expected none (no `categories` → no priority collision in `IsValidTile`), UNVERIFIED live | place on one tile via bridge, read back |
| A filth/scar def for the debris line | not chosen; skyfaller `metalShrapnelCountRange` gives slag chunks without any filth def | pick at build if the owner wants the gouge |

Open for the owner (cards, not prose): (1) load or port the two BMT creatures; (2) tune the
§8 numbers after the first quicktest season; (3) whether the wreck-field map-gen scatter
ships in v1 or v1.1.


---

## 🔴 CORRECTION — the region name in this spec, checked by BENCH 2026-09-20

This spec (and `fall_line.md` before it) names the start tile's region
**`Fall Line Barrens`**. That name is real, but it comes from a **stale** worldmap
artifact. MEASURED, both files, same 21,872 tiles:

| | `world/ASHKARR_WORLDMAP_tiles.csv` (canonical) | `world/ASHKARR_VIVIFIED_2026-08-24_tiles.csv` (stale) |
|---|---|---|
| tile 17007's region | **`The Breaks`** | `Fall Line Barrens` |
| that region's size | 153 tiles | 153 tiles |
| the adjacent `Fall Line` region | 155 tiles | 155 tiles |
| biome key on tile 17007 | `RUT_ExtremeDesert` | `ExtremeDesert` (pre-rename) |

- **Region name differs on 1,136 of 21,872 tiles.**
- **Biome key differs on 21,660 of 21,872 tiles** — the vivified CSV predates the
  `RUT_` rename entirely.

⇒ The *geography* in this spec is right: tile 17007 IS in the 153-tile region
abutting the 155-tile `Fall Line`, and the 308-tile figure is 155 + 153. What is
wrong is the **name to build against**. The canonical worldmap — the one
`WORLD_REMAKE_FINAL_STEP_1` says survives the remake — calls those 153 tiles
`The Breaks`.

⛔ **Do not write `Fall Line Barrens` into a TileMutatorDef, a def, or a gate.**
Build against `ASHKARR_WORLDMAP_tiles.csv`'s names, or the gate matches nothing.
