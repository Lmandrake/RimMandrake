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

