---
name: gravship-layout
description: Author, save and load RimWorld gravship layouts (ShipLayoutDefV2) as XML — write a ship directly with no map, no build and no game running, or export one from a live map. Use when creating, editing, sharing or inspecting a gravship design, when working with Gravship Exporter's files, or when a ship needs to be carried between saves.
---

# Gravship layouts — write the ship, don't build it

A gravship can be **authored as a file**. Gravship Exporter's `ShipLayoutDefV2`
XML is a plain grid of cells, and nothing about it requires a running game to
produce. That turns ship design from *"build it live on a map, then export"*
into *"write it, then load it"* — no bridge, no quicktest, no 25-minute load.

**The library is `src/RimMandrake/Utils/gravship_layout.py`.** It reads, writes
and validates layouts, and its `--roundtrip` mode is the proof the format is
understood rather than guessed.

```bash
python3 src/RimMandrake/Utils/gravship_layout.py --info      <file.xml>
python3 src/RimMandrake/Utils/gravship_layout.py --roundtrip <file.xml>
python3 src/RimMandrake/Utils/gravship_layout.py --demo      <out.xml>
```

## 🔴 What is measured here, and what is not

This project has been burned by trusting documentation — **the exporter's own
README says floors cannot be saved, and that is false**: our v1 export carries
4,057 `terrainDef` cells. So every claim below is labelled.

| claim | status |
|---|---|
| the XML schema in this file | **MEASURED** against `Gravship_v1.xml`, 2026-08-13 |
| floors survive the round trip | **MEASURED** — 4,057 cells out, 4,057 back |
| the grid carries a 1-cell margin | **MEASURED** — 86×133 hull exported as 88×135 |
| `gravEngineX/Z` are layout-local | **MEASURED** — map (126,149) → file (45,92) |
| the three export dialogs | **MEASURED** — driven live via the bridge |
| the file paths | **READ OFF THE GAME'S OWN POPUP**, not inferred |
| how a layout is IMPORTED | **READ AT SOURCE** — scenario-side only; see "Loading" |
| `quality`, `compSettings`, `exportedStorageSettings` shapes | **READ AT SOURCE** — declared in `ShipThingEntry.cs` / `StorageSettingsSnapshot.cs`, never populated in our own export |

**Do not restate what other skills own.** `.rws` anatomy and the grid codec are
`skills/rimworld-savegame/`; the bridge call surface and its traps are
`skills/rimbridge/`; what a quicktest result is worth is
`skills/rimworld-debug-testing/`. A layout file is ordinary uncompressed XML —
none of the savegame codec applies to it.

## The format

Root `<ShipLayoutDefV2>`. A `<rows>` list, one `<li>` per **row**, each holding
one `<li>` per **column**. Empty cells are `<li IsNull="True" />`.

```xml
<ShipLayoutDefV2>
  <rows>
    <li>                                     <!-- row z=0 -->
      <li IsNull="True" />                   <!-- empty cell -->
      <li>                                   <!-- populated cell -->
        <foundationDef>Substructure</foundationDef>
        <foundationStuff IsNull="True" />
        <terrainDef>MetalTile</terrainDef>
        <terrainStuff IsNull="True" />
        <things>
          <li>
            <defName>GravshipHull</defName>
            <stuffDef>Steel</stuffDef>
            <rotInteger>0</rotInteger>       <!-- 0=N 1=E 2=S 3=W -->
            <quality IsNull="True" />
            <plantToGrowDef IsNull="True" />
            <exportedStorageSettings IsNull="True" />
            <compSettings IsNull="True" />
          </li>
        </things>
      </li>
    </li>
  </rows>
  <width>88</width>  <height>135</height>
  <gravEngineX>45</gravEngineX>  <gravEngineZ>92</gravEngineZ>
  <defName>Gravship</defName>  <label>Gravship</label>
  <descriptionHyperlinks IsNull="True" />
  <ignoreIllegalLabelCharacterConfigError>False</ignoreIllegalLabelCharacterConfigError>
</ShipLayoutDefV2>
```

### Four things that will silently ruin a hand-written layout

1. 🔴 **The grid has a one-cell empty margin on every side.** Our 86×133 hull
   exported as `width` 88, `height` 135. Author the margin, or everything sits
   one cell off from where you think it is.
2. 🔴 **`gravEngineX/Z` are LAYOUT-LOCAL and include that margin.** The engine
   at map `(126,149)`, in a footprint starting `(82,58)`, exported as `(45,92)`
   — not `(44,91)`. `Layout.validate()` catches the off-by-one by checking that
   a `GravEngine` actually sits in the cell those coordinates name.
3. **A multi-cell building appears ONCE**, in its position cell, not in every
   cell it covers.
4. **`IsNull="True"` is how this format writes "absent".** An empty element is
   a different thing and RimWorld's scribe will read it as a value.

## Authoring a ship from nothing

```python
import sys; sys.path.insert(0, "src/RimMandrake/Utils")
from gravship_layout import Layout

lay = Layout(9, 9, defName="JawaTestSled", label="Jawa test sled")
for z in range(1, 8):
    for x in range(1, 8):
        lay.floor(x, z, "MetalTile")            # terrain + Substructure
for x in range(1, 8):
    lay.put(x, 1, "GravshipHull", "Steel", terrain="MetalTile")
    lay.put(x, 7, "GravshipHull", "Steel", terrain="MetalTile")
lay.put(4, 4, "GravEngine", terrain="MetalTile")
lay.gravEngineX, lay.gravEngineZ = 4, 4

print(lay.validate())      # [] means nothing obviously wrong
lay.save(".../Config/GravshipExport/JawaTestSled.xml")
```

`validate()` reports the failures that are silent rather than fatal: no engine
coordinates, coordinates outside the grid, coordinates that do not point at a
`GravEngine`, and things sitting on cells with no foundation (they will not be
part of the ship).

⚠️ **A layout the library accepts is not a layout the GAME accepts.** The
validator checks internal consistency, not defNames — a typo'd `defName` is a
def lookup that fails at load, and this project's rule stands: never guess a
defName, read it off the def or the live dump.

## Saving from a live map

Requires the bridge; see `skills/rimbridge/SKILL.md` for the call surface.
**It is a THREE-dialog flow, and the third one blocks every later screenshot
until it is dismissed.**

```
1. rimworld/click_cell            {x,z}  on the grav engine
2. rimworld/list_selected_gizmos         find label "Export Gravship Layout"
3. rimworld/execute_gizmo         {"gizmoId": "<the id field>"}
4. rimworld/get_ui_layout                find "Export"  -> click_ui_target
5.   (only if description is blank)      find "Confirm" -> click_ui_target
6. rimworld/get_ui_layout                find "Close"   -> click_ui_target
```

🔴 **`execute_gizmo` takes `gizmoId`, not `index`.** Passing `index` returns
`"A gizmo id is required."` The id looks like
`selection-gizmo:sel-<fingerprint>:12:<hash>` and **changes every time the
selection changes** — always re-list, never cache it.

The dialogs, in order:

| # | title | what it wants |
|---|---|---|
| 1 | *Name and Describe Your Ship* | name (pre-filled `Gravship`), optional description → **Export** |
| 2 | *No description has been entered…* | appears only when the description is blank → **Confirm** |
| 3 | *Ship Export Complete!* | ⚠️ **the annoying one.** Purely informational, but it sits over the map and every screenshot taken while it is open shows the popup, not the ship → **Close** |

Popup 3 states the output location itself, which is where these paths come from:

```
C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\GravshipExport
  <name>.xml    the layout
  <name>.png    a preview image, same basename
```

**Read the screen before searching the disk.** The popup names the folder; a
`find` across the user profile is slower and less certain.

### What an export does NOT carry — design the ship to these

Floors **do** survive (§"What is measured here"); these five do not, and each one
changes how a ship must be authored rather than how it is exported.

- 🔴 **Pawns and items are not exported. The ship arrives empty.** Confirmed
  against the exported data, not just the README blurb.
- **Include Shelves — possibly vanilla ones — or starting items may not spawn.**
  Storage is what the arrival code has to put things into; a ship with no
  shelving can silently land with nothing in it.
- **Any room with no pawn in it spawns under unexplored fog.** A large authored
  ship opens half-fogged. Cosmetic, but it reads as a bug in a demo, so put the
  starting pawns where the ship should be visible.
- **Every mod used in the ship becomes a hard dependency of the exported mod.**
  Free for us — one stack, one machine — and a landmine only if a ship is ever
  shared. Authoring with vanilla parts is the only thing that keeps it portable.
- **Preview screenshots must be placed by hand.** The exporter's author could not
  automate them, so a shipped layout has no preview until someone drops the PNG
  in beside the XML.

The starting platform extends around the ship, so large ships are supported
"obviously with a limit" — **the map edge is the bound, and we have not tested
where it bites.**

## Loading a layout

🔴 **Stop looking for an import gizmo. There is none, and that is deliberate.**
Import happens **only at new-game setup**, and the author says so in his README:
*"I won't be adding any major features like delayed ship spawning etc."*

Source, at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3576790938\1.6\Source\GravshipExport\`
(read directly — the mod ships its source, and its licence permits use and
adaptation):

| what | where |
|---|---|
| scenario page inserted | `Setup/Patch_Scenario_GetFirstConfigPage.cs:9` — Postfix on `Scenario.GetFirstConfigPage` puts `Page_ChooseGravship` **after** `Page_CreateWorldParams`, only when the scenario's arrival method is gravship |
| your pick materialised | `HarmonyPatch_DoGravship` on `ScenPart_PlayerPawnsArriveMethod.DoGravship` |
| where files are read | `Settings/ShipManager.cs:14` — `Path.Combine(GenFilePaths.ConfigFolderPath, "GravshipExport")` |
| how they are read | `:41` `Directory.GetFiles(ExportFolder, "*.xml")` → `:45` `DirectXmlLoader.ItemFromXmlFile<ShipLayoutDefV2>(file)` |
| floors re-applied on arrival | `Exporter/GravshipExporter.cs:182-184` captures non-substructure terrain; `HarmonyPatch_DoGravship.cs:~157` re-applies via `terrainGrid.SetTerrain` |

**This is why `ShipLayoutDefV2` is absent from the def dump and that absence was
correct evidence, not a failed search** — it is never registered as a Def. It is
deserialised from loose files at runtime, which is also why dropping a
hand-written XML into that folder is enough to make it selectable: no mod, no
`About.xml`, no restart-into-Defs dance. Just the file.

**So the round trip is: author → drop in `Config/GravshipExport` → start a new
game with a gravship-arrival scenario → the ship appears on the choose page.**

### ⭐ SUPERSEDED 2026-08-27 — a layout CAN be stamped onto a live map today

**`src/RimMandrake/Utils/print_gravship.py` does it, and it never touches
`ShipSketchBuilder`.** Foundation, floors and buildings are three batch calls the
bridge already has, so the Sketch route below stays unwritten and stops being the
blocker. Measured on a cleared 250×250 map: `Gravship_Cradle` — 4,034
foundation cells, 4,034 floors, 1,571 things — went down in ~15 calls and
verified **1,571 of 1,571 by cell-by-cell read-back**, every building
`PlayerColony`.

```
python.exe src/RimMandrake/Utils/print_gravship.py <layout.xml> --center 125,125 --apply
```

🔴 **The gate nobody predicts: `SetFoundation` is refused on any cell that has an
UNDER layer**, per cell, as *"cell has under-terrain; strip the floor first"* —
and a natural top terrain **cannot be removed at all**, because
`CanRemoveTopLayerAt` reads `Removable` and natural soil is not. The way through
is two calls: paint a **removable** floor (`MetalTile`) over the footprint, then
`jawa/set_terrain_layer layer='removeTop'`. `SetTerrain` pushes the natural
terrain down into `under`; `RemoveTopLayer` pops it back up and **nulls
`under`** — and only then is the cell eligible. Order is
**strip → foundation → terrain → things, largest footprint first.**

⚠️ **The export contains NO `GravEngine`** — verified zero in both of ours. The
mod's importer places it from `gravEngineX/Z`, and so does the script.
⚠️ **Map litter rides along**: `Gravship_Cradle` carries 2 `SteamGeyser`
and 1 `VHGE_GasGeyser` swept in from the original map. The script skips them.
🔑 **The FOUR GATES below are untouched by any of this.** A printed ship is
geometry: the engine reads `Gravship range: 0` and every thruster reads
*"Not connected to grav engine"* until it is powered, fuelled and inspected.

### Dressing a printed ship — floors, signage, damage

`print_gravship.py` puts the geometry down. Three more tools carry it from geometry
to something that reads as a thousand-year-old ship, and they are all offline-first:

| tool | does |
|---|---|
| `src/RimMandrake/Utils/gravship_floor_v2.py` | assigns a TerrainDef and a ColorDef to every deck cell from a seeded noise field, renders the result offline using swatches cut from live captures, and `--emit-plan` writes the whole scheme in MAP coordinates |
| `src/RimMandrake/Utils/apply_floor_plan.py` | lays that plan on the live map — holes, floors, per-cell colour |
| `src/RimMandrake/Utils/repaint_hull.py` | paints the HULL with the vanilla paint system (`jawa/paint_building`, one call per colour chunk; persistent, savegame-scribed). `--census` reads back; plan format `{"wallColor": {"<ColorDef>": [[x,z],...]}}` |
| `src/RimMandrake/Utils/ship_dress.py` | Aurebesh word signage, landing pads, gutted bays, design notes as letters |

🔑 **Three rules that came out of doing it**, each measured and each expensive:

* **Cut the holes BEFORE painting the floors.** Painting writes an `under` layer and
  that is exactly what the foundation operations refuse. Full ordering in
  `skills/rimbridge/references/map-authoring.md`.
* **Colour the hull with STUFF, not paint.** The dev `T: Set Color` tool runs out at
  roughly 380 invocations per GAME session and no reconnect clears it. `GravshipHull`
  takes any Metallic stuff and stuff carries colour, so one `jawa/build_batch` per
  material does permanently what 2,300 dev-tool calls could not. ⚠️ Rebuilding a wall
  cell wipes the conduits sharing it — re-place them from the layout, which is the
  authority for where they were.
* **The floor is the ship's autobiography, so label it.** Outer Rim ships 36 Aurebesh
  word decals — 2×1, `Standable`, `altitudeLayer Floor`, so they lie on the deck and
  pawns walk over them. Naming each bay for what it USED to be, and leaving the sign
  standing after the bay is gutted, says more about the ship than any amount of rust.

### The mid-game import button does not exist yet, and it is ours to build

⚠️ **Overtaken by the section above — read that first.** This route was never
built and no longer needs to be.

`Importer/ShipSketchBuilder.cs:14` is a **`public static class`** and `:24`
exposes **`public static Sketch BuildFromLayout(ShipLayoutDefV2 layout)`**
(verified: the file also holds `public static ShipLayoutDefV2 CurrentLayout` and
`public static Sketch CurrentSketch`). A `Sketch` spawns onto a live map. So
mid-game import is a small companion tool calling one public method — not a
reimplementation of anything.

**Is it reachable outside a scenario start? YES — checked, not assumed.**
`BuildFromLayout`'s file contains **zero** references to `Find.`, `Current.`,
`GameInitData`, `Scenario` or `Map`. It is a pure function: layout in, `Sketch`
out, resolving defs through `DefDatabase` and its own caches. The scenario page
is its only *caller*, not a constraint on it. So the difference between a
one-shot and an offline design loop is a call we have not written yet.

⚠️ **One real catch for a mid-game spawn.** Terrain is not re-applied by
`BuildFromLayout`. Floors land during arrival via
`HarmonyPatch_DoGravship.cs:~157` (`terrainGrid.SetTerrain`), and **that patch
does not run when you spawn a Sketch mid-game** — so a mid-game import would
produce the structure with no floors. Fix is already in our hands: replay the
layout's `terrainDef` cells through `jawa/set_terrain_batch` after the spawn.
`gravship_layout.py` can emit those ops straight from the file.

That is a CHECK job, queued as **B-v2** in
`infrastructure/state/queue/CHECK.md`. Until it exists, a layout can only enter
the game at world creation.

### Fields this project has never seen populated

Declared in the mod's own model classes rather than inferred from our one
export, where all of them are `IsNull="True"`:

- `ShipThingEntry.cs` — `string defName`, `string stuffDef`, `int rotInteger`,
  `string quality`, `string plantToGrowDef`,
  `StorageSettingsSnapshot exportedStorageSettings`,
  `List<CompSettingsSnapshot> compSettings`
- `StorageSettingsSnapshot.cs` — `string priority`, `List<string>
  allowedThingDefs / allowedCategories / allowedStuffCategories`,
  `FloatRange? hitpointsRange`, `FloatRange? mentalBreakRange`,
  `QualityRange? qualityRange`, `Dictionary<string,bool> specialFilterStates`
- `ShipCell.cs` — `foundationDef`, `foundationStuff`, `terrainDef`,
  `terrainStuff`, `List<ShipThingEntry> things`

⚠️ **A layout this library accepts is still not one the game has accepted.**
Round-tripping proves our parser agrees with itself. Do not call a hand-written
ship done until one has been through the choose-gravship page and looked at.

## Capacity, and the dial that changes it

`Connected substructure: <used> / <cap>` on the engine is the number that matters.
The cap comes from the engine's `SubstructureSupport` stat — **plus +500 per
`GravFieldExtender`, but only once that extender is claimed and powered** (see
THE FOUR GATES below; the extenders are worth an order of magnitude — measured
`4,680 -> 51,480`). A second `GravEngine` contributes nothing **and disables the
first**: *"Grav engine disabled: Multiple grav engines present"*.

The cap is also a **mod setting** on Bigger Gravships (`gravEngineSupport`), which
applies without a restart. Full numbers, the settings-dialog flow, and the
2026-08-13 experiments — including two conclusions later found to be confounded —
are in `references/measured-2026-08-13.md`.

## 🔴 The FOUR GATES — why a printed gravship never flies (measured live 2026-08-15)

A ship written by this skill, stamped onto a map and spawned through the bridge is
**geometrically perfect and completely inert.** Owner drove the fix by hand; every
line here is a before/after read off `jawa/inspect_string`.

Result: `Gravship range: 0 -> 40`, all four thrusters GREEN, all nine extenders
connected, engine capacity `4,680 -> 51,480`.

**The gates, in dependency order. Each one silently blocks everything after it.**

1. **CLAIM EVERY PART.** Bridge-spawned buildings arrive `faction: None`, and a
   factionless part does not join the gravship. ⚠️ **The engine being
   `PlayerColony` proves nothing about the rest** — on the measured ship the
   engine was player-owned while the console, tank, hull, extenders and thrusters
   were all `None`. Claim is per-thing.
2. **RUN CONDUIT TO EVERYTHING.** Not "conduit exists on the map" — an actual
   connected run reaching each consumer, through the floor.
3. **ADD BATTERIES.** The extenders draw more than the engine alone will carry.
   After the fix the engine reads `Power output 4,424 W`, `Grid excess -2,216 W`
   with `5,990 Wd stored` — i.e. it runs **at a deficit**, off batteries.
4. **PIPE ASTROFUEL** from the tank to the thrusters **and to the grav engine**.
   A console reading `Stored astrofuel: 250 / 250` while thrusters read
   `Astrofuel net excess/stored in network: 0 l/d / 0 l` means fuel exists and is
   not plumbed to them.

### 🔴 The error string lies about the cause

Every unmet gate above reports the **same** message on the part:

```
Not functional: Not connected to grav engine
Must be placed within range of a grav engine
```

It reads like geometry and it is almost never geometry. On the measured ship it
meant, in turn: unclaimed, then unpowered, then unfuelled. **Do not move a part in
response to this message until all four gates are satisfied** — I relocated a
whole thruster bank chasing it, and the bank was never the problem.

### Red herrings, so nobody spends the hours again

- **Substructure connectivity was intact the whole time.** 4,037 cells, 4,034
  linked to the engine — matching the engine's own `Connected substructure: 4034`
  exactly. All eight thruster cells were substructure AND connected. Verify this
  cheaply with a 4-way flood fill from the engine over the `foundation` layer and
  compare to the engine's own number; if they agree, substructure is not your bug.
- **Distance is not the gate.** Thrusters 40 tiles out work once claimed and fed.
- **`onlyRequiresLooseConnection`** differs between parts (`GravFieldExtender`
  true, `SmallThruster` false) and is a genuine def difference — but it is not
  what was blocking, and reading it as the cause sends you to geometry again.
- **A colonist must INSPECT the grav engine** before anything binds to it, and an
  uninspected engine makes every part report the same "not connected" line. That
  is a real gate, and it is upstream of all four above. Reaching the engine needs
  a door: on the measured hull the engine chamber had **none**, and the whole ship
  has 2 doors for an 86x133 hull.

⇒ **A gravship cannot be printed.** The layout file gets you a hull and correct
placement. Claiming, wiring, powering, fuelling and inspecting are colonist work,
and the ship is inert until they are done.

## Validation plan — what you owe whoever holds the game

`validate()` returning `[]` and `--roundtrip` passing prove the file agrees with
itself. Neither is the game accepting the ship. So an authored layout ships with
a validation plan **in the same commit** — because a load costs 23–30 minutes,
and without one the seat holding the game invents a check that carries none of
your predictions.

**1. The observable — what a player SEES when it works.**
🔴 **A positive observation, never "no error".** A ship that fails placement
mostly fails *silently* — nothing red, nothing logged. Name the thing on screen:
the layout's label on the choose-gravship page, `Connected substructure: 49 /
4500` on the engine panel, a floor tile that is `MetalTile` and not dirt.

**2. The route — the exact call, click path or spawn that produces it.**
The filename in `Config\GravshipExport`, the scenario, the cell to `click_cell`,
the gizmo. ⚠️ **If the route needs a tool that does not exist yet, say so and
file it as blocked on the tool** — mid-game import is queued as **B-v2** and does
not exist, so any item routed through a Sketch spawn is blocked, not queued.

**3. The prediction — written BEFORE the look.**
A number or a specific string: `49 / 4500`, two thrusters with no warning, 4,057
`terrainDef` cells back. A layout is all counts; predict them.

**4. The threshold — what CLOSES it, and what is explicitly out of scope.**
⭐ **Usually one observation, not a battery.** Name the minutia you are skipping
— the fog in unoccupied rooms, the missing preview PNG, the open questions in
`gravship_flight_invariants.md` §9.

**5. Batch or solo.**
A layout file rides with anything else on the same new game — it enters at world
creation and costs nothing extra. **A new assembly goes solo** (the B-v2 importer
when it lands), because if the load comes up wrong nobody can separate the DLL
from the ship beside it.

**6. What a FALSE PASS looks like.**
The way this particular check lies. Four measured here:
- **Geometrically valid, still unplaceable.** A thruster must **STAND on
  substructure while its exclusion zone contains NO substructure** — 1×5 behind a
  `SmallThruster`, 2×7 behind a `LargeThruster`. `validate()` checks foundations
  and engine coordinates and never looks at that rectangle, so a clean validator
  run is not a clearance check (`gravship_flight_invariants.md` §5).
- **Floors that survive export and vanish on a Sketch spawn.** Terrain is
  re-applied by the arrival Postfix (`HarmonyPatch_DoGravship.cs:~157`), *not* by
  `BuildFromLayout` — so a mid-game import lands the structure bare and **nothing
  errors**. Export→import passing says nothing about the Sketch path (§"One real
  catch"; invariants §9 q9).
- **The surplus was silently disconnected.** `maxSimultaneous` (ours: 20 small,
  10 large, read live) **drops the excess with no warning**. Counting thrusters in
  the XML is not counting connected thrusters; read the engine panel (§5, §6).
- **Under capacity read as flight-ready.** Completeness is a separate check from
  capacity: the engine panel's red `Requires: Thruster, fuel tank, controls`, and
  pathing (`NoPathToPilotConsole`, `PilotConsoleInaccessible`) — a sealed hull
  connects fine and refuses to launch (invariants §1, §2).

### The shape to hand over

```
PROVE    <exact call / defName / click path>
EXPECT   <number or string, written before the look>
LIES     <how this check produces a false pass>
```

Three lines. If it does not fit, the item is really two items.

Worked, for a hand-authored sled's first import:

```
PROVE    Drop JawaTestSled.xml in Config\GravshipExport -> new game, gravship- arrival scenario -> choose page -> pick "Jawa test sled" -> click_cell each thruster, then the GravEngine
EXPECT   Both SmallThrusters show a plain inspect panel with NO red "will be blocked by gravship substructure" warning · 0 blocked warnings; engine panel reads "Connected substructure: 49 / 4500"
LIES     validate() returns [] for this file: it checks foundation and engine coords, never the 1x5 exclusion rectangle. A clean validator is not a check.
```

## Why the file beats the build

Building the v1 ship live took 31 bridge steps, 4,057 foundation cells, 4,057
floor cells and 1,053 things — and even then the map contributed litter (32
river rocks and glacial ice swept into the first export) and refused two
foundation cells because of pre-existing ruins. Authoring the same ship as a
file has none of those failure modes: no map state, no substructure ordering,
no spawn collisions. The build path stays useful for *proving* a design in
game; the file path is how a design should be *made*.
