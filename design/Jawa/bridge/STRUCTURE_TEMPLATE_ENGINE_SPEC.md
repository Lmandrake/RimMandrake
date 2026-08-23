<!-- status: draft — CHECK, 2026-08-22. Three approaches for downselect; nothing here is chosen yet. -->
# The structure template engine — building a dwelling from a file

**Owner, 2026-08-22:** *"Consider how to implement a generic 'build this template' capability
through the live bridge. Such that we could send a filename and you would be able to follow its
contents and replicate… This is the start of our ability to 'dynamically place items' into a
fresh tilemap."*

**The worked example he set:** a RimWorld home — *"a fairly simple call that can produce a one
room, two room, or three room domicile from a given faction in an area."*

This document is **three ways to build it, with tradeoffs, for a downselect.** It does not pick
one. It does argue that the three share a spine, and that choosing the spine first makes the
downselect cheap and reversible.

---

## 0. The one architectural claim this document makes

🔑 **Separate the FORMAT question from the GENERATION question. They are orthogonal, and
conflating them is what makes this look like a single hard choice instead of two easy ones.**

|  | what it decides | the options |
|---|---|---|
| **Generation axis** | how much the system *decides* | stamp a fixed thing · assemble from parts · solve for a goal |
| **Format axis** | what a template *is* | data (CSV/JSON/XML) · a declarative DSL · a scripting engine (Lua) |

A fixed template library written in Lua is possible and silly. A constraint solver driven by
CSV is possible and painful. But **the middle of each axis composes**, and — the point —
**every combination can emit the same intermediate representation.**

⇒ **Build the IR and its compiler first.** Then A, B and C differ only in what *produces* the
IR, and a downselect never throws away the half that was expensive to get right.

```
   ┌─ A. fixed library ──┐
   │                     │
   ├─ B. parts + rules ──┼──►  BuildPlan (IR)  ──►  planner  ──►  bridge calls  ──► map
   │                     │      pure data          groups by       build_batch
   └─ C. constraint solve┘      no game needed      stuff/def      set_terrain_batch
                                                                   set_roof_batch
                                                                   map_commit
```

**Everything left of the IR is testable with no game running.** That is the property worth
paying for: a 25-minute cold load is the scarce resource, and a generator that can only be
judged live will never get enough iterations to become good.

---

## 1. What the bridge can already do — MEASURED 2026-08-22, not remembered

Read out of `JawaBench.BridgeTools/*.cs` at commit `53fa7d2e`. **120 `jawa/` tools declared in
source**; two are `#if JAWA_GM_TOOLS` so a default deploy ships 118.

| tool | signature that matters | what it means for this design |
|---|---|---|
| `jawa/build_batch` | `ops`, `stuff`, `faction`, `quality`, `hitPoints`, `wipeExisting`, `readBack` | the workhorse. `ops` is `'ThingDef:x,z[,rot]'` joined by `;` |
| `jawa/build_check` | `def`, `rect`, `stuff`, `rot`, `godMode` | pre-flight a placement without placing it |
| `jawa/set_terrain_batch` | rect-based | floors |
| `jawa/set_roof_batch` | rect-based | **roofs are separate; see the trap below** |
| `jawa/prefab_capture` | `name`, `rect`, `copyAllThings`, `copyTerrain`, `overwrite` | capture a live rect into a `PrefabDef` |
| `jawa/prefab_place` | `name`, `pos`, `rot`, `faction`, `blueprint`, `checkOnly` | stamp one down — **and `blueprint=true` places blueprints instead of finished buildings** |
| `jawa/prefab_list` | — | what is captured |
| `jawa/designate_batch` | `action`, `designation`, `rect`, `onThings` | mine/deconstruct/plan |
| `jawa/connect_cells` | `from`, `to`, `thing`, `mode`, `dryRun` | runs a conduit/pipe along a path |
| `jawa/map_commit` | `regions`, `pathing`, `power`, `redraw`, `full` | **the invalidation recipe; nothing is visible without it** |

### 🔴 Four constraints from that surface that shape the whole design

1. **`stuff` is per-CALL, not per-op.** One `build_batch` paints one material. A house with
   wooden walls, a steel door and stone furniture is **≥3 calls**. ⇒ The planner's core job is
   **grouping the plan by `(def, stuff, faction, quality)` into the fewest calls**, and the
   IR must carry material per-cell so that grouping is possible.
2. **`⚠️ WALLS CREATE NO ROOF`** — the tool says so itself. Roofing is a separate pass over a
   *derived* region, not a property of a wall. ⇒ The IR needs an explicit roof layer, and the
   compiler must be able to *derive* it (flood-fill the enclosed area) rather than make the
   template author enumerate it.
3. **`MaxOps = 4096` per call.** A 30×30 dwelling is ~900 cells, so a single house is
   comfortably inside one call; a **settlement is not**. ⇒ Chunking belongs in the planner from
   day one, not bolted on when the first village fails.
4. **`map_commit` is mandatory and is its own call.** ⇒ The planner emits it once at the end,
   never per-room. (`connect_cells` documents the same pattern.)

### What is NOT built, and is directly relevant

From `BRIDGE_CAPABILITY_ROSTER.md` (reconciled 2026-08-22: 56 built · 10 partial · 37 open),
the open §7 rows that bear on this exact problem:

- `layout_generate` — *"a whole multi-room complex"*, `layoutDef.Worker.GenerateStructureSketch`
- `sketch_spawn` — `SketchGen.Generate(SketchResolverDef, params)` → `Sketch.Spawn(...)`
- `kcsg_place` — place a VE (KCSG) structure layout
- `place_blueprint_batch`, `frame_complete`, `minify`/`uninstall`
- `set_thing_props` — quality/HP/faction/style on **already-spawned** things

🔑 **Three of those are RimWorld's own structure engines.** Approach C leans on them; A and B
do not need them. That is a genuine fork and it is priced in §6.

---

## 2. Two precedents already in this repo — do not reinvent either

**`skills/gravship-layout` + `src/RimMandrake/Utils/gravship_layout.py`.** This project has
already solved "author a RimWorld structure as a file, offline, with no game running" once, for
`ShipLayoutDefV2`. It reads, writes and validates, and it has a **`--roundtrip` mode that is the
proof the format is understood rather than guessed.**

⇒ **Steal the shape wholesale:** a grid format, a Python library that owns it, a `--roundtrip`
that re-emits byte-for-byte, an `--info` that summarises, and a `--demo` that produces a valid
artifact from nothing. That library is the single best model in the repo for what the template
library should look like.

**`src/Jawa/Jawa_Patches/Defs/PrefabDefs/JawaGroundHulk.xml`.** We already ship an authored
`PrefabDef` — 619 stamped cells cropped out of a real gravship export. So `PrefabDef` as a
delivery format is **proven in this stack**, not theoretical.

⚠️ **But note what that file's own header records:** the crop was chosen by hand because it was
*"the one slice of the ship that reads as a room rather than as a slice."* **A human made the
aesthetic call.** That is the honest baseline for how much judgement Approach A externalises to
an author — and how much Approach C would have to encode.

Also in the family: `design/Jawa/bridge/LIVING_NPC_TEMPLATES.md` (the population half of the
same idea — who lives in the thing we just built). The two specs should stay separate and meet
at a documented seam; §8 proposes one.

---

## 3. The call, and its parameters

The owner asked specifically to *"consider the parameters that might be passed."* This is the
proposed surface, and it is **deliberately the same for all three approaches** — that is what
makes them interchangeable behind the IR.

```
jawa/structure_build
    template     "dwelling"                 a name in the library, or a file path
    rect         "120,80,24,18"             where. x,z,w,h
    faction      "Jawa_Junkers"             palette + aesthetics + tech ceiling
    rooms        2                          1 | 2 | 3, or an explicit role list
    occupants    4                          drives bed count and room sizing
    wealth       "modest"                   destitute | poor | modest | comfortable | rich
    techLevel    null                       override; default inherits from faction
    defended     "none"                     none | fence | walled | fortified
    seed         12345                      determinism. same seed + same site = same house
    condition    "kept"                     pristine | kept | weathered | derelict | ruin
    rot          0                          entrance facing
    blueprint    false                      true = leave blueprints for colonists to build
    dryRun       true                       ⭐ DEFAULT TRUE — see below
    stuffOverride null                      force a material
    climate      "auto"                     auto | none | cool | warm  (see §5, the Jawa case)
```

🔴 **`dryRun` defaults to TRUE, and this is the single most important line in the spec.**
The companion's own design rules require destructive defaults off (`fire_raid` does the same).
A dry run returns **the full BuildPlan and the validation report without touching the map** —
which means the entire generator can be exercised, reviewed and regression-tested against a
running game **without ever mutating one.** It also makes the failure mode legible: you see the
plan that *would* have been built.

### The parameters that are load-bearing, and why

| parameter | what it actually changes | why it is not cosmetic |
|---|---|---|
| `faction` | palette, stuff preference, furniture whitelist, floor tier, aesthetic tags | the difference between a Jawa nest and an Imperial billet is *entirely* here |
| `wealth` | quality roll, material tier, decoration density, floor tier | RimWorld already models wealth; a rich shack reads wrong |
| `techLevel` | hard ceiling on the palette | a Neolithic faction with an autodoor is a bug, not a variation |
| `occupants` | bed count → room count → footprint | this is what makes `rooms` and `occupants` interact rather than conflict |
| `defended` | perimeter, chokepoints, turret/trap slots | changes the *topology*, not the furnishing |
| `condition` | `hitPoints`, missing walls, filth, whether the roof holds | the cheapest source of visual variety, and it makes ruins free |
| `seed` | everything stochastic | **without it nothing is reproducible and no bug is ever diagnosable** |

⚠️ **`rooms` and `occupants` can contradict each other** (1 room, 9 occupants). The engine must
have a stated precedence rule rather than silently picking. Proposed: **`rooms` is a hard
constraint on layout; `occupants` is a hard constraint on beds; if they cannot both hold, the
call REFUSES and says which to relax.** Silent accommodation is how a generator starts lying.

---

## 4. The IR — `BuildPlan`

Pure data. No game, no bridge. This is what all three approaches emit and what the planner
consumes, and it is the thing to get right first.

```jsonc
{
  "meta": {
    "template": "dwelling/two_room",
    "seed": 12345,
    "faction": "Jawa_Junkers",
    "generator": "B:parts+rules@0.3.1",   // which approach produced it — provenance in the artifact
    "footprint": [120, 80, 24, 18]
  },
  "terrain":  [ {"rect":[121,81,10,8], "def":"TileSandstone"}, … ],
  "things":   [ {"def":"Wall", "x":121, "z":81, "rot":0, "stuff":"BlocksSandstone"}, … ],
  "roof":     [ {"rect":[121,81,10,8], "def":"RoofConstructed"} ],
  "rooms":    [ {"id":"r1", "role":"Bedroom", "rect":[122,82,8,6], "door":[126,81]} ],
  "notes":    [ "cooled nursery: eggs ruin above 32C (jawa_society §4.3a)" ]
}
```

**Why an IR earns its place, concretely:**

1. **It is lintable offline.** Sealed-room check, roof-support check, door reachability,
   overlap, tech-level violations, stuff availability — all decidable from this object with no
   game. That converts most of the test burden off the scarce resource.
2. **It is diffable.** Two seeds, two factions, or a template before and after an edit produce
   comparable artifacts. Regression testing a *generator* is otherwise nearly impossible.
3. **It is the natural unit of review.** A human can read a BuildPlan; nobody can read a
   sequence of 900 `build_batch` ops.
4. **It decouples the downselect.** A→B→C changes the producer only.
5. **It survives the bridge changing.** If `build_batch` gains per-op stuff tomorrow, the
   planner changes and nothing upstream does.

⚠️ **The IR must carry `stuff` per-thing even though the bridge takes it per-call.** Do not
pre-flatten to the bridge's shape — that is the planner's job, and baking the tool's current
limitation into the format would be exactly the kind of decision that is expensive to undo.

---

## 5. What the site and the world impose

*(This section is filled from measured research — the world docs, the biome palette, and the
current mod stack's actual build palette. See §5.2–5.4.)*

### 5.1 Site constraints the planner must check before it builds anything

A dwelling dropped on the wrong ground is worse than none. **The planner reads the site first
and either adapts or refuses:**

| check | why | failure mode if skipped |
|---|---|---|
| terrain buildability | water, marsh, deep water refuse foundations | walls that cannot be placed, half a house |
| existing things | rock, trees, other buildings | `wipeExisting=true` silently destroys them |
| elevation / roof | already-roofed cells, overhead mountain | a room that cannot be roofed, or one that already is |
| flatness of the footprint | mixed terrain looks accidental | a house half on salt crust, half on dune |
| reachability | a door that opens onto rock | a building nothing can enter |
| **the fog** | building in unfogged territory photographs as nothing | a "successful" test with no evidence |

🔑 **Refusing is a first-class outcome.** The companion's design rules are explicit that a tool
must report refusals rather than swallow them, and the zone-builder incident (a 6×6 stockpile
that took 11 of 36 cells and reported success) is exactly the failure this must not repeat.
⇒ `structure_build` returns `cellsRequested`, `placed`, `refusedCount` and a `refused[]` list
with a reason per entry — never a bare `success: true`.


### 5.2 The world this builds on — Ash'karr

**Tidally locked desert planet, 21,872 tiles.** The lock is a **point, not a latitude band**:
temperature correlates −0.98 with *arc* (angular distance from the substellar point). Noon is
+70 °C, the terminator +14, the antistellar −80. **The habitable ring is arc 40–57.**

⚠️ `canon.yml > planet.status: remaking` — every planet number is being replaced, and
`check_canon` currently downgrades planet rules to ADVISORY. **Cite arc bands, not absolute
tile numbers**, and treat the biome mix below as current-not-frozen.

**Biomes actually painted** (25 of 36 survivors; top of the distribution): `AB_RockyCrags` 20.3 %
· `ExtremeDesert` 16.4 · `AridShrubland` 11.0 · `Desert` 9.8 · `AB_MycoticJungle` 8.9 ·
`Wasteland` 7.9 (salt plains) · `Ocean` 6.7 · `PoisonForest` 2.8 · `AB_PropaneLakes` 2.5 ·
`ZBiome_Badlands` 2.5 · `BMT_FungalForest` 1.9 · `ZBiome_Grasslands` 1.07 (the Pyrelands).

**Ground you will actually build on:** `Sand`, `SoftSand`, `Gravel`, rare `Soil`/`SoilRich`,
`Mud`/`Marsh` at river edges; plus Alpha Biomes' `AB_FineSand`, `AB_CompactedSand`,
`AB_ForsakenSand`, `AB_CrackedMud`, `AB_ParchedEarth`, `AB_VolcanicGravel`, `AB_SolidifiedLava`,
`AB_Obsidian`, `AB_BlackPebbles`, `AB_Tar`, `AB_MycoticSoil`.

**Scarcity, and it drives materials directly:**
- 🔴 **Water is the master scarce resource.** *Every potable tile is defended.* This is why so
  many faction dwellings below are organised around a **cistern** — that is not decoration, it
  is the settlement's reason for existing.
- **Deep desert is rich in salvage, scrap, buried wrecks and surface metal** and poor in food,
  water and components. **Steel, ore and obsidian come from the volcanic province only.**
- ⚠️ **Wood scarcity is a genuine documentation gap.** No doc rules on it. Inferable only:
  trees carry a ×2.5 growth multiplier *"because trees are a wood economy"*, the Mycotic Jungle
  offers a *"wood-substitute"*, and wooded tiles are called rare and hard-sited to one faction.
  ⇒ **The palette cannot currently answer "may this faction build in wood?" from canon.** Flagged
  in §9 as a decision the owner or DECIDE owes before 🅑 or 🅒 can pick materials honestly.

### 5.3 🔴 The cold nursery — the one constraint that makes this architectural

`jawa_society.md` §4.3a, owner's ruling 2026-08-22, verbatim:

> *"That would mean Jawa MUST build deep cave-like homes in the wild or (in modern days) build
> refrigerated egg chambers in order to reproduce. That's fantastic."*

Measured, not asserted: a laid egg carries `CompProperties_TemperatureSensitiveHumanEgg` with
`maxSafeTemperature 32`; above it the egg becomes `SEX_HumanEgg_Ruined` — no hatch, no child.
**6,276 of 21,872 tiles (29 %) exceed 32 °C on their annual mean**, and an annual mean
*understates* summer peaks. `MandrakeJawa` adults are comfortable to **46 °C**.

> *"There is a fourteen-degree window in which the clan is perfectly comfortable and its own
> clutch cooks… The nursery is not a precaution against a hostile world; it is a precaution
> against a world the adults find pleasant."*

⛔ **Do not "fix" the 32 °C ceiling — it is the pillar.**

🔑 **Why this belongs in a template spec, and why it is the best argument in the whole document:**
*"keep one room below 32 °C"* is **a goal, not a shape.** It cannot be expressed as a fixed
template, because whether a room holds 32 °C depends on the tile's arc, the season, the wall
material, the roof, and whether the room is buried. Satisfying it requires reading the site.

⇒ **This single requirement is the cleanest illustration of the A/B/C fork:**

| approach | how it handles the nursery | honest verdict |
|---|---|---|
| 🅐 Stamp | author a "Jawa dwelling **with cold room**" variant; the cold room contains a cooler and is walled in stone | works, but the template *asserts* the room is cold without checking |
| 🅑 Assembler | a `Nursery` room role whose rules require a cooler + insulation when `faction=Jawa` | works, and scales — but still does not verify the result |
| 🅒 Solver | takes `hold ≤32 °C` as a constraint, reads the tile's arc and season, and decides burial depth / cooler count / wall material to satisfy it | **the only one that can be wrong loudly instead of quietly** |

⚠️ **And note what none of them can do offline: prove the room actually holds temperature.**
That is a live measurement, and it belongs in the acceptance test in §8 — not in the linter.

### 5.4 Faction architecture — what the docs actually say

🔴 **Correction worth stating plainly, because this spec would have been built on the error.**
`canon.yml > factions.count: 13` = **8 authored by us (all carrying the `Jawa_` prefix) + 5
vanilla/mod vessels we patch.** ⛔ **That is not eight *Jawa* factions.** The `Jawa_` prefix is a
**namespace, not a claim about who the faction is** (`FACTION_SPEC` R18) — the Geonosians, the
Hutts and the Free Droids are not Jawa. Precisely: **two factions are Jawa peoples** (Trade Moot,
the Junkers), and **exactly one GENERATES Jawa pawns** — `faction_world_spec.md:48`, *"No faction
generates Jawa except the Trade Moot — the player race is not a common sight."* The fourteenth,
the Unbound Hive, is **cut**; docs still saying "14 factions" are stale.

| faction | defName | tech | what its dwelling IS, per the docs |
|---|---|---|---|
| Galactic Empire | `Empire` *(patch)* | Ultra | *"heavily fortified installations"*, perimeter turrets, kill corridors, **water condensers and reservoir bunkers**; *"wide sterile scars visible from orbit"* |
| Hutt Cartel | `Jawa_HuttCartel` | Industrial | drug labs, prisons, barracks, throne room, warehouse, **walled cistern**; sited *beside* an oasis, never on it |
| Homestead Defense League | `OutlanderCivil` *(patch)* | Industrial | **vaporator arrays and cistern storage — *"the faction's defining infrastructure"***; ⭐ **sandbags rather than full walls**; ⛔ no spacer chrome |
| Deep Desert Tribes | `TribeCivil` *(patch)* | ⚠️ **Neolithic vs Industrial — contested** | **stone huts, caves, bedrolls, animal pens, concealed cisterns**; *"traps and natural chokepoints instead of turret grids"*; fire answer is **move** — *"no permanent structures at all"* |
| Jawa Trade Moot | `Jawa_IndigenousTribes` | ⚠️ **Neolithic vs Industrial — contested** | **subterranean**; *"canyon fortresses, sandcrawler circuits, salvage markets"*; condensers on the crawler spine, buried cisterns at circuit nodes; **never sites on open water** |
| the Junkers | `Jawa_Junkers` | Industrial, degraded | **warrens** dug into wreck fields and tailings; squatters who *"manufacture nothing"*; wealth is *"in what they are wearing"* |
| Geonosian Foundry Hive | `Jawa_GeonosianFoundryHive` | Spacer | **subterranean** — *"ancient factories under the rock"*; fabrication halls, arena; fire answer is **burrow**: *"surface entrances only"* |
| Deepwater Compact | `Jawa_DeepwaterCompact` | Industrial | **layered walls, sandbags, turrets, EMP traps**; purification and cistern halls. *"Inside our walls no one raises a hand."* |
| Wildsteam Clan | `Jawa_WildsteamClan` | Industrial | ⭐ **open, tree-integrated, unwalled**; communal halls, animal shelters; *"minimal turrets due to ideology; defenders fight directly"* |
| Blackstar Company | `Pirate` *(patch)* | Industrial | *"small high-security compounds"*; food and water **bought in** |
| Free Droid Enclaves | `Jawa_FreeDroidEnclaves` | Spacer | charging hall, fabrication, battery bunker; ⭐ **no food stores and no beds** |
| Ascendant Helix | `Jawa_AscendantHelix` | Spacer | *"sterile labs and secure vaults; no large food or textile economy"*; cryptosleep, gene banks |
| the Forgotten Arsenal | `Mechanoid` *(label patch)* | — | ⛔ **deliberately no settlements at all** — `settlementGenerationWeight 0` |

⚠️ **Two tech levels are genuinely contested between docs** — the Deep Desert Tribes and the
Trade Moot each read Neolithic in the faction spec and Industrial (salvage-grade) in the roster.
🔴 **`techLevel` is a HARD palette ceiling in this design**, so an unresolved tech level is an
unresolved *palette*. Both are listed in §9 as blocking decisions: a generator cannot honestly
choose between a torch and a standing lamp until someone rules.

🔑 **Read that table as a test suite, not as flavour.** It already falsifies a naive generator
four times over, and each is a cheap unit test on the BuildPlan:

1. **Free Droid Enclaves must produce a dwelling with no beds and no kitchen.** A generator that
   always places one bed per occupant is wrong for an entire faction.
2. **Wildsteam must produce an *unwalled* dwelling** — `defended` must be able to reach zero, and
   ideology forbids the turrets a "defended" flag would otherwise add.
3. **Deep Desert Tribes' canonical answer to fire is to have no permanent structure at all**, so
   "build a house here" is sometimes the wrong request for that faction.
4. **Three factions are subterranean** (Trade Moot, Geonosians, Junkers). A surface-rectangle
   generator cannot express them; they need excavation — `designate_batch` mining, or placement
   under existing overhead mountain.

⚠️ **The gaps, stated so nobody mistakes silence for permission.** No doc names a **stuff
material**, a wall/roof/floor def, or a room-programme size for **any** faction, and **there is
no Jawa dwelling spec of any kind** — the phrase *"rag nest"* appears nowhere in
`jawa_society.md`; it exists only as `JAWA_RAG_NEST_1` in `V2_DREAMS.md`, and that is a
**furniture def, not a dwelling.** ⇒ The per-faction *palette* in §7's plan is **new design
work**, and it is DECIDE's or the owner's to approve, not this seat's to invent.

### 5.5 Neighbouring specs — the seams

Two documents already occupy adjacent ground and this spec must not duplicate either:

- **`design/Jawa/worldbuilding/tile_augmentation_catalogue.md`** — 30 rows of what is *placed on*
  a world tile (derelict refineries, abandoned moisture-farm homesteads, fortified toll posts,
  junkyards), with defNames, rarity and defenders. **That catalogue is the demand side; this
  spec is the supply side.** Several of its rows are flagged as needing an authored structure
  layout — those rows are this engine's first real customers.
- **`design/Jawa/bridge/INHABITED_DESIGN.md`** (which architecturally supersedes
  `LIVING_NPC_TEMPLATES.md`) — the *population* layer: `TileMutatorDef.extraGenSteps` → a GenStep
  → `LordMaker`. **The seam: this engine builds the place; `Inhabited` puts people in it.** They
  meet at a rect and a faction, and neither should know how the other works.

---

## 6. THE THREE APPROACHES

All three emit `BuildPlan`. They differ only in **who decides where the walls go.**

---

### 🅐 THE STAMP — a library of fixed, authored templates

**Mechanism.** A template is an artifact on disk: a grid of cells carrying def, stuff, rotation,
terrain and roof, plus metadata (faction tags, room count, footprint, entrance side). The call
selects one matching `(template|faction, rooms, wealth)`, translates and rotates it onto the
target rect, validates against the site, and emits the plan.

**Three authoring routes, all already possible:**
1. **Hand-write the grid file** — the `gravship_layout.py` model exactly.
2. **Build it in-game and capture it** — `jawa/prefab_capture` on a rect, then export. *This is
   the killer route: the aesthetic judgement happens by building, which is the medium a human is
   actually good at.*
3. **Crop it from an existing artifact** — how `JawaGroundHulk.xml` was made.

**Cheap variety multipliers that cost almost nothing:**

| lever | multiplier | how |
|---|---|---|
| rotation + mirroring | ×8 | free, geometric |
| material substitution | ×3–5 | template says `WALL`, faction palette says `BlocksSandstone` |
| `condition` | ×4 | `hitPoints`, knocked-out walls, filth, roof holes |
| **furniture slots** | ×3–10 | template marks `BED_SLOT`; palette fills it |

⇒ **~20 authored templates can present as several hundred distinct buildings.** That is the
number that decides whether A is viable, and it is much better than the naive count suggests.

**Pros**
- ✅ **Cheapest to build by a wide margin**, and partially exists today (`prefab_capture`/`place`).
- ✅ **Every output was approved by a human.** No uncanny phase, ever.
- ✅ Deterministic, diffable, reviewable. A template is linted once and trusted forever.
- ✅ Captures judgement no rule can state — *"reads as a room rather than a slice"*.
- ✅ Failure is local and obvious: a bad template is one bad file.

**Cons**
- ❌ **Authoring is combinatorial.** 13 factions × 3 sizes is 39 before wealth or defence.
- ❌ **Does not adapt to the site.** A fixed 12×10 needs a flat, clear 12×10.
- ❌ **Repetition is visible at volume.** Forty houses from six templates reads as six houses.
- ❌ Every new faction is new authoring, forever.

**Best when:** the count of placements is low-to-medium and art direction matters more than
variety. **Worst when:** populating a whole planet.

---

### 🅑 THE ASSEMBLER — authored parts plus furnishing rules

**Mechanism.** Two passes.

1. **Layout.** Either subdivide the footprint (BSP or a room-graph), or instantiate an authored
   *skeleton* whose dimensions are parameterised. Produces rooms, walls, and door positions.
2. **Furnish.** Fill each room from rule tables keyed by `(role, faction, wealth, tech)`.

```yaml
room Bedroom:
  size:     { min: [3,3], prefer_per_occupant: [5,5] }
  require:  [ BED × occupants ]
  prefer:   [ LIGHT, DRESSER, END_TABLE ]
  when wealth >= comfortable: [ RUG, SCULPTURE ]
  when tech <= neolithic:     forbid [ LAMP ]  # torch instead
```

🔑 **Make the room roles match RimWorld's own `RoomRoleDef`s.** If the generated room satisfies
the game's own bedroom scorer, the game *labels it a bedroom* — the output is validated by the
engine rather than by us, which is a far stronger guarantee than any linter we write.

**Pros**
- ✅ **Variety from few assets.** One dwelling template serves every faction and size.
- ✅ **Parameters map onto rules directly** — `wealth`, `tech`, `occupants` are literally
  conditions. This is the approach the owner's parameter list *wants*.
- ✅ **Adapts to the footprint given**, so placement is far less fussy than A.
- ✅ **A new faction is a palette entry**, not three new buildings.
- ✅ Scales to volume without visible repetition.

**Cons**
- ❌ Needs a real engine: subdivision, door placement, furniture packing, reachability.
- ❌ **There is an uncanny phase** — output is plausible-but-wrong until the rules are tuned, and
  tuning needs many evaluations.
- ❌ **Art direction is indirect.** You tune a rule and hope; you cannot nudge one wall.
- ❌ A bad house is a *rule interaction*, which is harder to diagnose than a bad file.

**Best when:** many placements across many factions — i.e. tilemap enrichment, the actual goal.

---

### 🅒 THE SOLVER — goal-directed and site-aware, riding RimWorld's own generators

**Mechanism.** Input is a **goal**, not a shape: *shelter 6, hold ≤32 °C in one room, defensible
to level 2, spend ≤400 resources, on this terrain.* The system searches layouts satisfying the
constraints, reading real site geometry — elevation, rock, water, existing buildings, roof cover.

**And it has the option to delegate.** RimWorld ships three structure engines (`LayoutDef` /
`LayoutWorker`, `SketchGen` / `SketchResolverDef`, `BaseGen` symbol stack) that already generate
multi-room complexes and faction bases. `layout_generate`, `sketch_spawn` and `kcsg_place` are
**named, anchored, and unbuilt** in the capability roster.

⚠️ **The open question that prices this whole approach: those engines are map-GENERATION code.
Whether they can be invoked against a rect on an already-generated live map is the thing to
settle before committing.** If yes, C gets dramatically cheaper and its output matches
vanilla-generated bases for free. If no, C means writing a solver from scratch.

**Pros**
- ✅ **The most powerful and the most general.** One system does houses, settlements, ruins,
  outposts, defended camps.
- ✅ **Genuinely site-aware** — builds into a cliff, around rock, along a river.
- ✅ **Goals compose.** "Defended + cooled nursery + 6 occupants" is a constraint set, not a new
  template. Every other approach needs a new asset for that.
- ✅ If it can ride the engine's generators, output is vanilla-consistent by construction.

**Cons**
- ❌ **By far the most expensive**, and the estimate is soft until the live-map question is
  answered.
- ❌ **Solver output reads as *solved*, not *lived in*.** This is the deep aesthetic risk and it
  is not fixable by more constraints — irregularity has to be injected deliberately.
- ❌ **Graceful degradation is mandatory and hard.** An unsatisfiable constraint set must produce
  a worse house, never no house and never a wrong one.
- ❌ Slowest iteration: each tuning pass needs evaluation, and evaluation wants a game.

**Best when:** the site is irregular and the goal matters more than the look. **Worst when:** you
need a specific building to look a specific way.

---

## 7. Comparison, and the recommendation

| | 🅐 Stamp | 🅑 Assembler | 🅒 Solver |
|---|---|---|---|
| build cost | **low** | medium | **high** (soft) |
| already partly exists | ✅ `prefab_*` | — | ✅ 3 engines, unbuilt |
| art direction | **total** | indirect | weak |
| variety at volume | poor | **good** | **good** |
| site adaptation | none | footprint only | **full** |
| new faction cost | high | **low** | **low** |
| failure mode | obvious, local | rule interaction | subtle |
| offline testable | **fully** | **fully** | mostly |
| serves settlements later | no | partly | **yes** |

### 🔑 The recommendation, and it is not one of the three

**Build the IR and planner first. Ship 🅐. Grow it into 🅑. Keep 🅒 gated behind one measurement.**

1. **IR + planner + offline linter.** Everything expensive and reusable lives here, and none of
   it needs a game. This is the real deliverable.
2. **🅐 immediately**, because `prefab_capture`/`prefab_place` already work — so the *first*
   version is mostly plumbing, and it produces reviewable output on day one.
3. **Add slots and palettes to 🅐** — the moment a template says `BED_SLOT` instead of
   `Bed`, it is already halfway to 🅑, and no authored template is invalidated.
4. **🅑 when repetition becomes the complaint.** The trigger is observable, not a guess.
5. **🅒 only after settling whether `LayoutWorker`/`SketchGen`/`BaseGen` run on a live map.**
   That single measurement swings its cost by a large factor, and it is answerable in one bridge
   session.

⚠️ **The trap to avoid: starting at 🅒 because it is the most impressive.** It is the only one
whose cost is unknown, the only one whose aesthetic risk cannot be fixed by more work, and the
only one that cannot show the owner a house this week.

🔑 **And the composition nobody should miss: 🅐 and 🅑 are not rivals.** Authored skeletons
(🅐's strength — a floorplan a human approved) filled by rule-driven furnishing (🅑's strength —
variety and parameter response) is strictly better than either alone, and it is the natural
end state of steps 2–4 above.
