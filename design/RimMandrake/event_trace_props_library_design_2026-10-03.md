# Event trace props library — design (2026-10-03)

Item: `EVENT_TRACE_PROPS_LIBRARY_1`, filed by the owner 2026-09-15: *"a new props library that's
all about blaster marks, burn marks, scorch marks, floor scrapings, and other 'signs of something
happening.' Specific creations to power and fill gaps identified in the first design exercise's
library."* DESIGN ONLY: no defs, code or art jobs come from this document. Building it is FOUNDRY's,
and §8 is sized for that.

**Scope source:** `design/RimMandrake/narrative_dictionary_pilot/GAPS.md` §1–§5 (gaps G1–G6, the
structural gaps S1–S7, and the blind-run gaps) and README "Blind test result" (PASS; B3 and B2
were the weakest claims).

Evidence tags: **MEASURED-SRC** = read in decompiled 1.6 source via RimSage this session ·
**MEASURED-REPO** = read in this repo · **UNMEASURED** = not checked; never assume it.

---

## 0. Findings that change the brief

1. **Directional filth is already a vanilla engine feature, so we need no new renderer for floor
   vectors.** (MEASURED-SRC) `Filth` carries `List<FilthInstance> drawInstances`, each with its own
   `drawPos` and `rotation`, set by `Filth.SetOverrideDrawPositionAndRotation(Vector3, float)` and
   saved in `ExposeData`. `Graphic_ClusterTight` draws one sprite per instance at that position and
   rotation. `Graphic_Cluster` uses the stored rotations only when the instance count equals
   the thickness. Two vanilla callers prove the path. `Pawn_HealthTracker.DropBloodSmear()` rotates
   each crawl smear to the crawler's heading, so **a downed crawler already leaves a heading in one
   cell**. `RoomPart_Gore.SpawnCorpseSmear` lays a 6–10-cell rotated smear chain away from a corpse
   at mapgen. ⇒ GAPS S1 ("direction only by chaining") is half wrong. Heading exists. What is
   missing is **sense**: the `CrawlSmear` sprite is symmetric end-to-end, so a reader cannot tell
   which way the body went. That matches the blind run exactly: room W got "trailing inward", and
   the crawl direction was never stated. **The fix is art plus placement: an asymmetric sprite with
   a heavy start and a tapering, hand-printed end. No mechanism is needed.**

2. **We already have a footprint and drag grid, and it is unwired.** (MEASURED-REPO)
   `src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_TrackGrid.cs`, `RM_TrackPool.cs`,
   `RM_SectionLayer_TrackPrints.cs` and `RM_TrackGridPatches.cs` (`FOOTPRINT_TRACK_GRID_1`, commit
   `84a377bf0`) form a capped per-map pool. Each record holds 8 headings, a size class, a source
   class (animal, humanlike or mech), a **drag bit for crawling pawns**, and the tick it was laid.
   The pool has a priority eviction order, an erase API (cell, rect, and a downwind sweep), and a
   section layer that rotates every print to the walker's heading. The art exists:
   `RM_TrackPrint_Human`, `_Animal`, `_Large`, `RM_TrackDrag`. **No XML consumer carries
   `RM_TrackSurfaceExtension` yet**, and the item is still `proposed`. ⇒ G4 (worn path) and the
   footprint half of S1 **extend this grid. Nothing is rebuilt.**

3. **Our wall-mark register renders a 1/16 crop of its texture, and nobody has looked at it in
   game.** (MEASURED-SRC, live effect UNMEASURED) Every `RM_Graffiti_*` def is a floor-cell
   `Filth_Mark` with `<linkType>CornerFiller</linkType>` linked to `Wall`.
   `GraphicData` wraps any linked graphic in `Graphic_Linked*`. `Graphic_Linked.LinkedDrawMatFrom`
   then calls `MaterialAtlasPool.SubMaterialFromAtlas`, which treats the texture as a **4×4 link
   atlas** and draws one 0.1875-scale tile, chosen by which cardinal neighbours are walls. The
   graffiti PNGs are single centred images (for example `scratches_0.png`, 640², a small claw
   motif in the middle). Under atlas sampling, a mark with one wall to the north (link index 1)
   draws the bottom-row tile, which is transparent canvas. The donor's full-bleed spray art
   (`vandal_0.png`) survives this because any crop of it is still paint. The one "verified" note
   (`GRAFFITI_FRAMEWORK_BUILD_1`) proved that *linking* needs no subclass, not what the linked mark
   *looks like*, and the walk's evidence is "confirmed by looking at the sprite". ⇒ **GAPS S3's
   "the framework already places them on walls" is not a safe foundation for wall traces.** This
   library does not use `CornerFiller` for wall traces (§2.2). One live screenshot of a placed
   `RM_Graffiti_Scratches` next to a wall settles the graffiti question; it is filed as a
   question for the Graffiti owner, not fixed here.

4. **Walls already show generic damage, but doors never do.** (MEASURED-SRC)
   `SectionLayer_BuildingsDamage` prints corner and edge crumble overlays on any building below max
   HP. The overlay count is `count − floor(count × hp/max)`, so it scales with damage, and repair
   erases it. `Wall`'s `damageData` defines corners and edges but no `scratches`. `Door` sets
   `<damageData><enabled>false</enabled>`, so **a beaten door looks pristine until it dies**
   (G2). Scene tools can therefore show "this wall took a beating" today by spawning a wall at
   reduced HP. It cannot say *what* hit it, which is what this library adds.

5. **Sand that banks against walls exists outdoors only.** (MEASURED-REPO)
   `src/RimMandrake/MovingDunes` banks Odyssey sand behind walls and at roof lips, but it skips
   roofed cells, and its own patch notes that vanilla decays sand "unconditionally indoors" at about
   five days for a full drift. ⇒ G5's *interior* drift ("fanned in under a door", the abandoned
   room) cannot ride the sand grid. It needs a filth trace (§3, T9/T10).

6. **Art already exists for eight of the traces we need.** (MEASURED, `artpipe_state.py find` and
   `done/` listing) These are finished jobs: `RM_TrackPrint_Human/_Animal/_Large`, `RM_TrackDrag`
   (in CreatureBehaviors `Textures/Things/Tracks`), `RM_Filth_DragMark` and
   `RM_Filth_DisturbedSand` (shipped as defs in `RM_KillSigns_Filth.xml`), and
   `RM_Filth_SettledFilm`, `RM_Filth_SandWake`, `RSW_Filth_CrawlerTread` and `RUT_MendingWeldPlate`
   (art done, **no def in `src/`**). Check every new art row against this list before queuing
   anything (CLAUDE.md, 2026-09-20 rule).

---

## 1. Inputs

| gap | claim it starves | trace(s) in §3 |
|---|---|---|
| G1 | someone fought their way in | T1 bolt scar (wall), T2 scorch bloom (wall), T5 bolt pit (floor) |
| G2 | the door was forced | T6 breached doorway |
| G3 | smashed by people, not decayed | T7 strike marks, T8 shard spill |
| G4 | they come and go every day | T11 worn lane (TrackGrid wear) + footprints |
| G5 | the desert is coming in | T9 drift edge, T10 door fan |
| G6 | everything is mended | T14 mend plate, T15 lashing |
| S1 / B3 | crawled away, which way | T3 crawl trail (directional) + T4 drag trail |
| S2 / B2 | *long ago* | aged variant of every trace (§5) + T12 dust film + T13 dust ghost |
| S4 | tended, not squalid | T14–T16 (mend, lashing, sweep arcs) + T17 scrub ghost |
| S5 | cause misattribution | T7 is a *tool*-strike mark, distinct from claw `RM_Graffiti_Scratches` |
| S6 | dead torch, open safe | T18 soot ring; T8 doubles as "contents spilled" |
| B1 | looted *after* they left | T13 dust ghost (things removed from a dusty room) + T11 fresh prints over old film |
| B4 | wrecked *by Empire-haters* | T7 next to a graffiti motif; cause comes from adjacency, not one sprite |

Not in scope: A2/A4 child and bedroll cues (those are object rows, not traces) and the per-claim
density ceiling, which waits for a measured over-crowded case as GAPS says.

## 2. Engine mechanisms (measured)

Every trace uses one of five carriers, chosen per trace in §3.

### 2.1 Carrier F — floor filth, with optional heading (def-only)
- `thingClass` `Filth` (or a thin `RM_TraceFilth` subclass, §2.6), `category Filth`,
  `altitudeLayer Filth`, `drawerType MapMeshOnly`.
- **Undirected:** `Graphic_Random`, as vanilla `Filth_BlastMark` and `Filth_DriedBlood` do.
- **Directed:** `Graphic_ClusterTight`. The placer adds one `drawInstance` per sprite with a
  heading in degrees, exactly as `DropBloodSmear` does (MEASURED-SRC). Art is drawn pointing NORTH
  (0°), the same convention the TrackGrid uses.
- Multi-cell: `size (3,3)` as on `Filth_BlastMark`. `FilthMaker.CanMakeFilth` tests the whole
  occupied rect (MEASURED-SRC).
- ⚠ `placementMask` is a REQUIREMENT the terrain's mask must cover (Graffiti def comment, measured
  live 2026-09-06). Use `Unnatural` for man-made marks, and `Natural`/`Terrain` only where the
  trace is earth (drag trough in sand).
- ⚠ `FilthMaker.TryMakeFilth` on a cell holding the same def **thickens** it and adds no new
  instance (MEASURED-SRC). A second heading in one cell therefore needs a direct
  `SetOverrideDrawPositionAndRotation` call on the existing filth. `RM_TraceUtility` (§2.6) owns
  that.

### 2.2 Carrier W — a wall-cell overlay filth (def-only, placed on the wall cell)
Wall traces are **not** linked graphics (finding 3). Instead:
- A filth def with `altitudeLayer BuildingOnTop`, `Graphic_ClusterTight`, spawned **on the wall
  cell itself**. Its single drawInstance is offset about 0.3 cells toward the face that was hit
  and rotated to the incoming angle, so the sprite sits on that face.
- Why this should work (MEASURED-SRC): `FilthMaker.CanMakeFilth` tests terrain only, not the
  edifice, and filth is not an edifice, so no wipe. `TorchWallLamp` proves that a `BuildingOnTop`
  thing drawn with an offset (`drawOffsetNorth (0,0,0.9)`) reads as on the wall.
- **UNMEASURED and the first thing the script checks:** whether `GenSpawn` / `TryMakeFilth`
  accepts a filth on a cell whose edifice is a wall. Other unknowns: whether the
  `MapMeshOnly` filth layer at `BuildingOnTop` draws above the wall's `Building`-altitude mesh, and
  whether `JobDriver_CleanFilth` can reach a wall cell. A wall scar should be *uncleanable*
  anyway: add no `cleaningWorkToReduceThickness` override and give it a large value, but have
  repair erase it (§5).
- **Fallback if the spawn is refused:** carrier A, below.

### 2.3 Carrier A — a wall attachment Building (def-only)
1.6's attachment system (MEASURED-SRC): `building.isAttachment`, `Placeworker_AttachedToWall`,
`Wall.supportsWallAttachments = true`, a thing in the floor cell facing the wall, and
`Graphic_Multi` with per-facing `drawOffset*` (the `TorchWallLamp` shape). When the wall goes, so
do its attachments (`GenConstruct` line ~972 matches `isAttachment` by rotation). Vanilla's
`RoomContentsWorker.TryPlaceWallAttachments` can place them at mapgen from a `LayoutRoomDef`.
- Costs: the thing is selectable and has HP; only one attachment per wall face per cell
  ("SomethingPlacedOnThisWall"); it needs 3 facings of art; and the player can hit it.
- Use: **hero placements** (the mapgen dressing of a famous fight), and the fallback for W.

### 2.4 Carrier G — a grid with no Things (C#, extends the TrackGrid)
For traces that are per-cell *quantities* rather than objects: worn lanes (T11). Same pattern as
`RM_TrackPool`: a packed per-cell array, its own `SectionLayer` (vanilla `Section` instantiates
every non-abstract `SectionLayer` subclass by reflection, MEASURED-SRC `Section.cs:48`), saved
packed, and capped. Not inspectable, so a reader sees it but cannot click it. Fine for wear, wrong
for anything that needs a label.

### 2.5 Carrier B — a replacement Building (C# hook + def)
For a *state* the engine will not draw (G2 breached door): a different ThingDef swapped in for the
original. Not filth.

### 2.6 The shared runtime: `RM_TraceUtility` + `RM_TraceRuleDef` + one aging component
- `RM_TraceUtility.Place(ThingDef trace, IntVec3 cell, Map map, float? headingDeg, float ageDays,
  Vector3? offset)` is the **only** placer. Scene tools, rimplace, RoomParts and gameplay hooks all
  call it. It handles thicken-vs-new-instance, the wall offset and the fresh-or-aged choice.
- `RM_TraceRuleDef` (data, not code) maps an event to a trace, for example
  `{ targetKind: Wall, damageDefs: [RSW_Blaster_Damage, …], trace: RM_Trace_BoltScar, chance: 0.35,
  maxPerCell: 2 }`. The census of every blaster-type damage def in the live 628-mod set is
  UNMEASURED; in-repo there are `RSW_Blaster_Damage` (9 uses), `Bullet`, `Flame`, `Bomb`, `Beam`
  and `Burn`.
- `RM_MapComponent_TraceAging` does a rare sweep (about every 2,500 ticks) over a registered list.
  It swaps fresh to aged after `ageAfterDays`, copying `drawInstances`, sources and thickness. A
  MapComponent is used because vanilla filth sets no ticker and has **no fresh→aged conversion
  anywhere**: `Filth_DriedBlood` is only ever *spawned* aged, by `GenStep_ScatterCaveDebris`,
  `SymbolResolver_AncientComplex` and `GenStep_ScatterAncientTurret` (MEASURED-SRC).
- `disappearAfterTicks` counts from the last thicken (`SteadyEnvironmentEffects`, MEASURED-SRC). An
  aged trace meant to persist sets `disappearsInDays` to zero, which means never.

## 3. Trace catalogue

Every row gets a **fresh** and an **aged** def unless marked. Ids: `RM_Trace_<Name>` and
`RM_Trace_<Name>_Aged`. All rows are RM_ tier except T19 (RSW).

| # | trace | event that leaves it (gameplay) | carrier · render | dictionary / scene placement | lifetime |
|---|---|---|---|---|---|
| **T1** | **bolt scar (wall)**: a glassy pit with a radial scorch halo, 3 variants | a ranged hit on a wall whose damageDef is in the "energy" rule set | **W** (fallback A) · ClusterTight, 1 instance offset to the hit face, rotated to `dinfo.Angle` | `PlaceWallScars(door, side, count)`: 2–4 at either side of a door, on the room-facing faces | fresh 10 d → aged; aged persists; **repair to full HP erases it** |
| **T2** | scorch bloom (wall): a soot fan rising off the face | Flame/Burn damage on a wall, or a `Fire` dying on a cell adjacent to a wall | W · rotated *away* from the fire | above any brazier, torch or burnt room | fresh 15 d → aged, persists |
| **T3** | **crawl trail with sense**: a heavy start smudge, a tapering streak, a handprint at the leading end | vanilla `DropBloodSmear` already runs; we add **art only**: retexture `Filth_BloodSmear`'s `CrawlSmear` set as asymmetric (patch `texPath` to our folder) | F directed · vanilla ClusterTight, vanilla rotation | `PlaceCrawl(from, to)`: one instance about every 0.6 cells along the path, heading = segment angle | vanilla 35–40 d; `Filth_DriedBlood` already covers aged |
| **T4** | drag trail: two parallel heel furrows, or a body-width scrape | TrackGrid drag bit (a crawling pawn on a track surface), plus carrying a downed pawn: **UNMEASURED** whether the carrier's path is recorded; the draft adds a postfix on the carry job | F directed (floor) / G (on a track surface) | `PlaceDrag(from, to, width)` | 20–25 d (matches `RM_Filth_DragMark`) |
| **T5** | bolt pit (floor): a small fused crater plus a scorch tick | a ranged energy *miss* landing on a floor (`Bullet.Impact` with `hitThing == null`, MEASURED-SRC: that branch exists) | F undirected · Graphic_Random, 0.5 drawSize | scatter 3–6 near the fight line | fresh 10 d → aged |
| **T6** | **breached doorway**: a door frame with a buckled or holed leaf, passable | a door destroyed by damage from a hostile instigator; replaces vanilla's `filthLeaving Filth_RubbleBuilding`-only outcome | **B** · new building `RM_BreachedDoorway` (stuffable, `holdsRoof`, standable, `Graphic_Multi`, 2 facings since `Door` is not rotatable but the frame orientation is read from its wall neighbours) | `PlaceBreach(doorCell, kind=blown/cut/buckled)` | permanent until deconstructed; rebuild a door over it |
| **T7** | strike marks on equipment: dents, a star-crack, a tool scrape | melee Blunt/Cut damage on a non-wall Building of `buildingSizeCategory` small/medium, or with a `CompPowerTrader` (consoles) | F at BuildingOnTop on the building's cell · Graphic_Random, 2–3 variants | next to `AncientDestroyedConsole` and the like | fresh → aged, persists while the building stands |
| **T8** | shard spill: screen glass and plastic chips fanned one way | same event as T7 (spawned in the adjacent cell the blow came from) | F directed | "contents spilled" beside a closed safe (S6) | 20 d, then gone (debris) |
| **T9** | **drift edge (interior)**: sand banked against wall feet | rare tick in roofed rooms that **touch a door to outdoors** on a sandy biome, while no pawn has entered for N days (`RM_MapComponent_TraceAging` doubles as the counter) | F **linked, used correctly**: `Graphic_Linked` (Basic) with linkFlags Wall, **authored as a real 4×4 link atlas**, so sand piles toward whichever sides are walls (finding 3, inverted) | `PlaceDrift(room, depth)`: every floor cell with a cardinal wall | grows 3 thickness steps over ~30 d; a pawn walking through drops thickness by 1 (cleaning removes it) |
| **T10** | door fan: a sand tongue spreading inward from a door | same as T9, on the cell inside each outer door | F directed · ClusterTight, heading = into the room | `PlaceDoorFan(door)` | as T9 |
| **T11** | **worn lane**: a scuffed, polished track | TrackGrid extension: per-cell `wear` counter, +1 per step, slow decay | **G** · extra SectionLayer, 3 wear tiers, edges blended by the neighbours' wear | `PlaceWear(path, tier)` | decays one tier per ~20 d without traffic |
| **T12** | dust film: a settled grey layer that takes footprints | rare tick on roofed cells with no step for N days; reuse **`RM_Filth_SettledFilm` art** (Warscar), carrying `RM_TrackSurfaceExtension` so walking through it *prints* | F undirected + TrackGrid surface | `PlaceDust(room, age)`; then `PlaceTrackRun` across it for "someone came back" | grows with absence; cleaning removes it |
| **T13** | dust ghost: a clean outline where something stood | a building despawned (deconstructed, minified, stolen) from a cell under dust film | F · Graphic_Single sized to the footprint (1×1, 1×2, 2×2 sets) | B1 "looted after they left": ghosts in fresh-dust rooms | refills with dust at the T12 rate |
| **T14** | mend plate: a riveted patch or weld bead | `JobDriver_Repair` completes on a building that had dropped below 50% HP | F at BuildingOnTop on the building cell; reuse **`RUT_MendingWeldPlate` art if the owner allows it to be generic**, otherwise RM_ art (Q3) | next to salvage furniture in "competent poor clan" rooms | permanent while the host stands (aging subclass checks the host) |
| **T15** | lashing: cord or wire binding | same event, for Woody/Fabric stuff | as T14 | as T14 | as T14 |
| **T16** | sweep arcs: fan-shaped broom strokes | `JobDriver_CleanFilth` finishes a cell | F directed (heading = cleaner's facing) | "tended" rooms | 2–3 d, never aged (freshness is the point) |
| **T17** | scrub ghost: a lighter rectangle where a mark was removed | a `Filth_Mark` (graffiti) cleaned or gone over | W (same carrier as the mark's replacement) | a "regime changed" room: a ghost beside a fresh stencil | 60 d |
| **T18** | soot ring: a black halo on the floor | a fuelled light (`TorchLamp`, `TorchWallLamp`, our gaslamp) runs out of fuel and stays out for 3 d | F undirected under the lamp | stand-in for "unlit torch", which the engine will not place (S6) | until relit + 5 d |
| **T19** | **saber cut** (RSW): a molten glowing seam on a wall or door, cooling to a dark weld line | `TakeDamage` on wall/door with an RSW lightsaber damageDef (census UNMEASURED; the rule row ships empty until a def name is measured) | W/B; on a door it leads straight to T6 `kind=cut` | iconic SW breach staging | glow 1 d (fresh), seam persists (aged) |

**Footprint runs** are not a new trace. They are the existing TrackGrid prints, laid by real walking
on any surface carrying `RM_TrackSurfaceExtension`, or by `PlaceTrackRun(from, to, source, ageDays)`.
That needs one new write path on `RM_MapComponent_TrackGrid`, since the record already stores a
tick. **Tracked filth** (G4's "tar does not read as tracked"): vanilla `Pawn_FilthTracker` already
carries filth off a cell, but drops it undirected. The library adds `RM_TrackSurfaceExtension` to
`RM_Filth_Tar`, blood pools and T9/T12, so stepping *in* them prints with a heading. It does not
modify the carried-filth system.

### 3a. Gameplay hooks: three postfixes cover every row
1. `Thing.TakeDamage(DamageInfo)` postfix, filtered first on `thing is Building`, then a rule
   lookup keyed `(targetKind, dinfo.Def)`. This covers T1, T2, T7, T8 and T19. The angle comes
   from `dinfo.Angle` (Bullet passes `ExactRotation.eulerAngles.y`, MEASURED-SRC). TakeDamage is hot
   in combat: the filter must cost one type check and one dictionary lookup. That per-hit cost is
   UNMEASURED.
2. `Bullet.Impact` postfix with `hitThing == null` → T5.
3. `Building.Destroy` / `Kill` with the door case → T6. `JobDriver_Repair` and
   `JobDriver_CleanFilth` completion → T14/T15/T16. Graffiti scrub → T17. Fuel-out → T18.
   Building despawn under film → T13.

Interior accumulation (T9, T10, T12) and aging run in the one MapComponent sweep.

### 3b. Mapgen placement (beside the scene tools)
- **rimplace**: one new plan row, `TRACE defName x z heading_deg age_days` (the existing `THING`
  row has only `Rot4`, MEASURED-REPO `RimplacePlan.cs:16`), and `GenStep_RimplacePlan` calls
  `RM_TraceUtility.Place`.
- **Vanilla layout rooms**: `RoomPartWorker` subclasses (the `RoomPart_Gore` shape) such as
  `RM_RoomPart_FirefightAtDoor` (T1 + T5 + T3 + T6) and `RM_RoomPart_LongAbandoned` (T9 + T10 + T12 +
  aged variants), so ancient complexes and our StructureInjections rooms get them from data.
- **Dictionary rows** (`objects.jsonl`) gain `heading: none|required|optional`,
  `age: fresh|aged|both`, `carrier: F|W|A|G|B` and `cause` (from S5), so the composer can request
  "a crawl trail from X toward Y, aged" and the validator can refuse a vector claim placed
  without a heading.

## 4. Placement summary

| | dictionary / scene tools | real gameplay |
|---|---|---|
| every F/W trace | `RM_TraceUtility.Place` through a JawaBench `[Tool]` and the rimplace `TRACE` row | rule table + 3 postfixes |
| T6 breach | `PlaceBreach` | door death hook |
| T11 wear, prints | `PlaceWear` / `PlaceTrackRun` on the TrackGrid | the existing TrackGrid postfix, plus the wear counter |
| T9/T10/T12/T13 | `Place*` with `ageDays` | the aging sweep (absence-driven) |

Both columns go through the same placer, so a scene-authored trace and a gameplay one are
**byte-identical in the save**. That is what lets a blind reader's verdict on an authored room
transfer to play.

## 5. Lifetime and decay

- **Fresh → aged** after `ageAfterDays` (per def; default 10). The aged def is darker, lower
  saturation and slightly smaller. Aged wall and equipment traces never expire.
- **Rain** (`rainWashes`) applies only to fresh outdoor floor traces. Aged ones are "baked in".
- **Repair erases damage traces on its host**: a wall scar or strike mark goes when its host
  returns to full HP. This keeps base-building gameplay clean: if you fix it, the history goes.
  Players who want permanent history can turn it off (§6).
- **Cleaning**: floor traces are cleanable. Wall traces (W) are cleaned only by repair, and
  whether the clean job reaches a wall cell is UNMEASURED (§2.2).
- **Absence traces** (T9, T10, T12) grow only while no pawn of any faction steps in the room.
  The first step starts printing into the dust, which is the "someone came back" cue.
- **Caps:** per map, one FIFO ring of trace Things (default 600). The TrackGrid keeps its own cap
  (`trackPoolCap`, already a setting).

## 6. Mod Settings (`mandrake.rm.traces`)

| setting | default | note |
|---|---|---|
| Combat traces on walls (T1, T2, T19) | on | |
| Floor impact traces (T5, T8) | on | |
| Breached doorways (T6) | on | off = vanilla rubble only |
| Strike marks on equipment (T7) | on | |
| Upkeep traces (T14–T17) | on | |
| Abandonment accumulation (T9, T10, T12, T13) | on | **affects map dressing at generation** (labelled as such, per CLAUDE.md) |
| Worn lanes (T11) | on | lives with the TrackGrid settings in CreatureBehaviors |
| Repair erases damage history | on | |
| Days until a trace ages | 10 | slider 2–60 |
| Trace chance multiplier | 1.0 | 0–2; 0 turns every gameplay hook off and leaves scene placement intact |
| Max traces per map | 600 | |

All-off degrades to vanilla. The scene tools keep working, because authored rooms are content and
not behaviour.

## 7. Art briefs

General rules: RimWorld top-down, painterly to match vanilla filth, **real alpha**, drawn
**pointing NORTH** for every directed sprite (the engine rotates it), and the motif centred and
filling ≥60% of the canvas for undirected sprites. Palette: the warm desert-ruin set (sand ochres,
soot near-black `#1b1612`, scorched umber, glassy blue-white for energy-fused centres). The aged
variant is the same shape: about 35% less saturated, darker, softer edges, with a dust tint over it.
Check `artpipe_state.py find <name>` first for each row.

| # | canvas | variants | brief |
|---|---|---|---|
| T1 | 256² | 3 | a 0.35-cell pit, a glassy blue-white fused core, a cracked rim, a radial soot halo stretched **north** (the direction of travel), a few molten drips south |
| T2 | 256² | 2 | a soot plume shaped like a fan narrowing to the south (the fire side), wispy and tarry at the base |
| T3 | 256²; texPath patch over `Things/Filth/CrawlSmear` | 3 | a dense blot at the **south** end, smeared streaks running north, ending in a smeared handprint and finger drags at the north tip. **Must read as asymmetric when shrunk to 64 px.** |
| T4 | 256² | 2 | two parallel heel furrows 0.25 cells apart, deeper at the south; one body-width scrape |
| T5 | 128² | 3 | a small fused crater + a single scorch tick |
| T6 | 2 facings (east-west and north-south frames) × 3 kinds, 128×128 per cell | 6 | blown (leaf peeled outward, blackened), cut (glowing seam cooled, leaf slumped), buckled (leaf folded off its track) |
| T7 | 128² | 3 | a star-crack on a dark screen, two round dents, a bright tool scrape. **Must not resemble claw marks** (S5) |
| T8 | 128² | 2 | a wedge of glass chips widening to the north |
| T9 | **512² link atlas, 4×4 tiles of 128**, laid out as a vanilla wall atlas (`Things/Building/Linked/Wall` order) | 1 + aged | sand banked against the linked sides, feathering toward the open sides. Get the tile order wrong and it piles against air: validate offline |
| T10 | 256² | 2 | a tongue of sand, wide at the south (the door), feathering north |
| T11 | 128² × 3 tiers | 3 | scuff → dull → polished lane; tileable, low contrast |
| T12 | reuse `RM_Filth_SettledFilm` | — | (exists) |
| T13 | 1×1, 1×2, 2×2 | 3 | a crisp clean rectangle inside dust, with scuffed corners where feet stood |
| T14 | 128² | 3 | a riveted plate, a weld bead line, a bolted bracket |
| T15 | 128² | 2 | cord wraps; wire twists |
| T16 | 256² | 2 | 3–4 curved broom strokes fanning from the south |
| T17 | 256² | 1 | a lighter blotchy rectangle with a few residual paint flecks |
| T18 | 128² | 1 | a soot ring with a dead-ash centre |
| T19 | 256² | 2 | a hot orange seam (fresh) / a dark rippled weld line (aged), a vertical stroke with a melted lip |

## 8. Build plan for FOUNDRY

New mod: `src/RimMandrake/Traces` (packageId `mandrake.rm.traces`, namespace
`RimMandrake.Traces`), depending on `mandrake.rm.creaturebehaviors` for the TrackGrid. T19 goes in
a RimStarWars patch beneath it. Order is chosen so that each step is provable before the next costs
anything:

| step | what | proves | size |
|---|---|---|---|
| 0 | **Spike, no art:** spawn a placeholder Carrier W filth on a wall cell, and a Carrier F ClusterTight filth with two headings, on the minimal mod list | §2.2's three UNMEASUREDs; directed render | ½ day |
| 1 | `RM_TraceUtility`, `RM_TraceRuleDef`, `RM_MapComponent_TraceAging`, settings, the JawaBench `[Tool]` `traces/place` | one placer, aging swap keeps instances | 1 day |
| 2 | T1, T5, T3 (CrawlSmear art patch), T6. The B3 fight family | blind B3 re-run can use them | 1 day + art |
| 3 | T9, T10, T12 (+ film as track surface), T13, aged variants. The B2/B1 abandonment family | B2 "for years" | 1 day + art |
| 4 | the TakeDamage, Impact and door hooks + rule table | gameplay leaves the same Things | 1 day |
| 5 | T11 wear in CreatureBehaviors; `PlaceTrackRun`; the rimplace `TRACE` row; the RoomPartWorkers | A3 un-refused | 1½ days |
| 6 | T7, T8, T14–T18, T19 | upkeep / motive | 1 day + art |

**Re-run the blind test after step 3** with the same answer key and bar. B3 Room W must state crawl
direction, and B2 must state "years" or "desert getting in". That re-run is the library's own
pass bar.

### 8a. First script (`debug_process.md` §2)
`src/RimMandrake/Traces/validation.py` (a modcheck `Suite`) and the walk
`design/validation_walks/RimMandrake/Traces.md` `## must be true`:

```
- A wall-cell trace spawns on a wall and is present after spawn        → place.wall_spawn   (list_things on the wall cell; foundCount==1)
- A directed trace keeps its heading through save/load                 → place.heading_roundtrip (read drawInstances[0].rotation before/after save_game+load)
- A fresh trace becomes its aged def after ageAfterDays                → aging.swap (step_game_ticks ageAfterDays*60000+2500; def==*_Aged, instance count unchanged)
- A blaster hit on a wall leaves RM_Trace_BoltScar on the hit face     → hook.wall_bolt (spawn wall + shooter, force N shots, count scars ≥1, offset sign matches shooter side)
- A miss leaves a floor bolt pit                                       → hook.floor_pit
- A destroyed door under hostile fire becomes RM_BreachedDoorway       → hook.breach
- Repairing the wall to full erases its scars                          → aging.repair_erases
- A roofed outer-door room with no visitors accumulates drift/dust     → aging.absence (step 30 d; thickness>1 on wall-adjacent cells)
- Walking through dust film lays a TrackGrid print with heading        → tracks.dust_prints (pool record at cell, Angle within 45° of walk)
- Each Mod Settings toggle off removes its effect                      → suite.toggles (one per §6 row)
- Scene and gameplay placements are byte-identical in the save         → UNCOVERED: needs a save-diff tool (file as item)
- Traces read as their claim to a viewer                               → UNCOVERED: §4 boundary, owner/blind-reader judgement
```
Seed the anti-guessing notes with: `RULED OUT: wall marks via CornerFiller filth show the whole
texture — Graphic_Linked samples one 4×4 atlas tile (MaterialAtlasPool.SubMaterialFromAtlas)`.
Add a guard component: if any `RM_Trace_*` def is ever given a `linkType` other than T9's, go red.
Selftest under `--mock` first.

## 9. Questions for the owner

**Q1. When a colonist repairs a wall, should its battle scars go away?**
- **(a) Yes, repair erases them, with a setting to keep them (recommended).** Your base stays
  clean if you maintain it. Ruins and abandoned rooms keep their history because nobody repairs
  them.
- (b) Never erase. Every fight leaves a permanent record. This is richer storytelling, but a
  well-defended colony slowly gets covered in scars and there is no way to tidy it.
- (c) Erase only the fresh ones; old scars stay. A middle path, but players won't understand
  why some scars vanished and others didn't.

**Q2. How should a door look after it is broken through?**
- **(a) Leave a broken doorway: a passable, roof-holding frame with a blown or buckled door
  (recommended).** It tells the story at a glance and you rebuild a door over it. It needs about 6
  new pieces of art.
- (b) Keep vanilla: the door just disappears and leaves rubble. No art cost, but the "door was
  forced" story stays invisible.
- (c) Only in pre-made ruins (scene tools), never in live play. It costs the art without the
  gameplay hook, so your own colony never shows it.

**Q3. The mending weld-plate art was made for the Rust Cathedral rite. Can a generic version be
used for everyday "this was repaired" marks?**
- **(a) Yes, reuse it as the plain repair mark, and the rite gets a fancier variant later
  (recommended).** No new art job, and "repaired" shows up everywhere straight away.
- (b) No, keep it special to the rite and make new plain repair art. The rite keeps a look nobody
  else has, at the cost of one more art job.

**Q4. Should rooms nobody visits slowly fill with sand and dust during play, or only in pre-made
ruins?**
- **(a) Both: abandoned rooms in your own map gather drift and dust, and walking through leaves
  prints (recommended).** "Nobody has been here in years" becomes something you can see and read
  footprints in, and there is a setting to turn it off.
- (b) Pre-made ruins only. Cheaper, and it never touches your colony, but a storeroom you forget
  for a year looks the same as the day you left it.
- (c) Play only, with no pre-placed dust in ruins. This throws away the main reason the blind
  test asked for it.
