---
name: gravship-layout
description: Author, save and load RimWorld gravship layouts (ShipLayoutDefV2) as XML — write a ship directly with no map, no build and no game running, or export one from a live map. Use when creating, editing, sharing or inspecting a gravship design, when working with Gravship Exporter's files, or when a ship needs to be carried between saves.
---

# Gravship layouts — write the ship, don't build it

You can **author a gravship as a file**. The `ShipLayoutDefV2` XML of the Gravship Exporter mod is a plain grid of cells.
You do not need a running game to write such a file. So ship design changes from *"build it live on a map, then export"* into
*"write it, then load it"*. You do not need the bridge, a quicktest or a cold load.

**The library is `src/RimMandrake/Utils/gravship_layout.py`.** The library reads, writes and validates layouts. Its
`--roundtrip` mode loads a file, saves the file, loads the result and compares the two. A clean round trip shows that the
library writes back all that it loaded. The comparison cannot see a field that the load drops. The library drops
`foundationStuff` and `terrainStuff`. Our exports hold a value in neither field. Boundary page: `design/specs/2026-11-23-gravship-layout-library/boundary.md`.

```bash
python3 src/RimMandrake/Utils/gravship_layout.py --info      <file.xml>
python3 src/RimMandrake/Utils/gravship_layout.py --roundtrip <file.xml>
python3 src/RimMandrake/Utils/gravship_layout.py --demo      <out.xml>
```

## What is measured here, and what is not

Do not trust the documentation of the mod. **The README of the exporter says that floors cannot be saved. The README
is false there.** Our v1 export carries 4,057 `terrainDef` cells. So the table gives a status to each claim. MEASURED means that a
run or a file showed the claim. READ AT SOURCE means that the code of the mod says so and no run showed the claim.

| claim | status |
|---|---|
| the XML schema in this file | **MEASURED** against `Gravship_v1.xml`, 2026-08-13 |
| floors survive the round trip | **MEASURED** — 4,057 cells out, 4,057 back |
| the grid carries a 1-cell margin | **MEASURED** — an 86×133 hull exported as 88×135 |
| `gravEngineX/Z` are layout-local | **MEASURED** — map (126,149) → file (45,92) |
| an export holds no `GravEngine` thing | **MEASURED** — zero in all 6 of our exports, 2026-11-23 |
| the three export dialogs | **MEASURED** — driven live through the bridge |
| the file paths | **read from the game's own popup**, not inferred |
| how a layout is imported | **READ AT SOURCE** — at scenario setup only; see "Loading a layout" |
| `quality`, `compSettings`, `exportedStorageSettings` shapes | **READ AT SOURCE** — declared in `ShipThingEntry.cs` / `StorageSettingsSnapshot.cs`. Our later exports hold the last two; see "Fields of the model classes" |

**Do not restate what other skills own.** A layout file is ordinary uncompressed XML. The savegame codec does not apply
to a layout file. These skills own the neighbouring topics:

- `.rws` anatomy and the grid codec: `skills/rimworld-savegame/`.
- The bridge calls and their traps: `skills/rimbridge/`.
- What a quicktest result is worth: `skills/rimworld-debug-testing/`.

Old measurements, and lines of this file that were wrong: `references/history.md`.

## The format

The root is `<ShipLayoutDefV2>`. The root holds a `<rows>` list, with one `<li>` per **row**. Each row holds one `<li>`
per **column**. An empty cell is `<li IsNull="True" />`.

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

1. **The grid has an empty margin of one cell on every side.** Our 86×133 hull exported as `width` 88, `height` 135.
   Author the margin. Without the margin, every thing is one cell away from where you think.
2. **`gravEngineX/Z` are layout-local and include that margin.** The engine stood at map `(126,149)`, in a footprint that
   starts at `(82,58)`. The engine exported as `(45,92)`, not `(44,91)`. If the layout holds a `GravEngine` thing,
   `Layout.validate()` reports coordinates that name a different cell. A layout with no `GravEngine` thing gives
   `validate()` nothing to compare. Then `validate()` reports only coordinates outside the grid, or on a cell with no
   foundation. So check the coordinates of an export yourself.
3. **A multi-cell building appears ONCE**, in its position cell. Do not write the building in every cell that it covers.
4. **`IsNull="True"` is how this format writes "absent".** An empty element is a different thing. RimWorld's scribe reads
   an empty element as a value.

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

`validate()` reports the failures that are silent. A fatal failure shows itself. The silent failures are:

- The layout has no engine coordinates.
- The coordinates are outside the grid.
- The coordinates point away from the `GravEngine` thing, or at a cell with no foundation.
- A thing sits on a cell with no foundation. That thing will not be part of the ship.

**A layout the library accepts is not a layout the GAME accepts.** The validator checks internal consistency. The
validator does not check defNames. A wrong `defName` is a failed def lookup at load. Never guess a defName. Read the
defName from the def or from the live dump.

**The library loads loose files only.** A file in `Config\GravshipExport` has the root `<ShipLayoutDefV2>`. A layout
inside a mod is a `<GravshipExport.ShipLayoutDefV2>` element under a `<Defs>` root. The library refuses that root by name.

## Saving from a live map

You need the bridge. `skills/rimbridge/SKILL.md` holds the bridge calls. **The export has THREE dialogs. The third dialog
blocks every later screenshot until you close the dialog.**

```
1. rimworld/click_cell            {x,z}  on the grav engine
2. rimworld/list_selected_gizmos         find label "Export Gravship Layout"
3. rimworld/execute_gizmo         {"gizmoId": "<the id field>"}
4. rimworld/get_ui_layout                find "Export"  -> click_ui_target
5.   (only if description is blank)      find "Confirm" -> click_ui_target
6. rimworld/get_ui_layout                find "Close"   -> click_ui_target
```

**`execute_gizmo` takes `gizmoId`, not `index`.** A call with `index` returns `"A gizmo id is required."` The id looks
like `selection-gizmo:sel-<fingerprint>:12:<hash>`. The id **changes every time the selection changes**. So list the
gizmos again before each call. Never keep an old id.

The dialogs, in order:

| # | title | what it wants |
|---|---|---|
| 1 | *Name and Describe Your Ship* | name (pre-filled `Gravship`), optional description → **Export** |
| 2 | *No description has been entered…* | appears only when the description is blank → **Confirm** |
| 3 | *Ship Export Complete!* | gives information only. The popup covers the map, so each screenshot shows the popup and not the ship → **Close** |

Popup 3 states the output location. These paths come from that popup:

```
C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\GravshipExport
  <name>.xml    the layout
  <name>.png    a preview image, same basename
```

**Read the screen before you search the disk.** The popup names the folder. A `find` across the user profile is slower
and less certain.

### What an export does NOT carry — design the ship to these

Floors **do** survive (§"What is measured here"). Each item below changes how you author a ship.

- **Pawns and items are not exported. The ship arrives empty.** The exported data confirms this, and so does
  `GravshipExporter.BuildLayout`.
- **Include shelves, or the starting items may not spawn.** The README gives this hint and adds that vanilla shelves
  might be needed. The arrival code puts the items into storage. A ship with no shelves can land with nothing in it, and
  no error appears.
- **Fog on arrival: the README and the code disagree.** The README says that each room with no pawn in it shows as
  unexplored. The code (`HarmonyPatch_DoGravship.UnfogEntireMap`) clears the fog of the whole map. No live run here
  tested which one is true. If a demo opens under fog, put the starting pawns where the ship must be visible. The fog is
  cosmetic, but it reads as a bug.
- **Every mod used in the ship becomes a hard dependency of the exported mod.** This costs us nothing while we use one
  mod list on one machine. A shared ship costs the other player every mod. Only a ship of vanilla parts stays portable.
- **A preview image is written beside the XML by the export** (`ShipPreviewRenderer.Capture`). The README says that the
  author could not automate the preview. That line is older than the code. A hand-written layout has no preview until
  somebody puts a PNG beside the XML, with the same basename.

The starting platform extends around the ship. So large ships are supported. The README says *"obviously there will be a limit"*.
**The map edge is the limit. We did not test where the limit is.**

## Loading a layout

**Do not look for an import gizmo. There is none, and that is deliberate.** The mod imports **only at new-game setup**.
The author says so in the README: *"I won't be adding any major features like delayed ship spawning etc."* To put a
layout on a live map, use our script (see "A layout can be stamped onto a live map").

The source is at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3576790938\1.6\Source\GravshipExport\`.
The mod ships its source. Its licence puts the source in the public domain.

| what | where |
|---|---|
| scenario page inserted | `Setup/Patch_Scenario_GetFirstConfigPage.cs:9` — a Postfix on `Scenario.GetFirstConfigPage` puts `Page_ChooseGravship` **after** `Page_SelectStoryteller` and **before** `Page_CreateWorldParams`, only when the scenario's arrival method is gravship. The log line and a comment of the mod say "after Page_CreateWorldParams". The code does not do that |
| your pick materialised | `HarmonyPatch_DoGravship` on `ScenPart_PlayerPawnsArriveMethod.DoGravship` |
| where files are read | `Settings/ShipManager.cs:14` — `Path.Combine(GenFilePaths.ConfigFolderPath, "GravshipExport")` |
| how they are read | `:41` `Directory.GetFiles(ExportFolder, "*.xml")` → `:45` `DirectXmlLoader.ItemFromXmlFile<ShipLayoutDefV2>(file)` |
| floors re-applied on arrival | `Exporter/GravshipExporter.cs:182-184` captures non-substructure terrain; `HarmonyPatch_DoGravship.cs:~157` re-applies via `terrainGrid.SetTerrain` |

**A loose file in that folder is never registered as a Def.** The mod reads the file at runtime. So you can put a
hand-written XML in the folder, and the choose page offers the ship. You need no mod, no `About.xml` and no restart. A
def dump does not list a loose file, and that absence is correct evidence. The class `ShipLayoutDefV2` is a Def: the mod
ships its 4 built-in ships as Defs, and an exported mod ships its ship as a Def.

**So the full route has four steps:**

1. Author the layout.
2. Put the file in `Config/GravshipExport`.
3. Start a new game with a gravship-arrival scenario.
4. Pick the ship on the choose page.

### The landing chain can wedge forever under bridge automation — save first

This section is about a ship that flies and then lands. Vanilla's landing chain runs camera-pan callbacks and captures.
Under automation, that chain can hang **before the ship is even placed**. When the chain starts, the landing marker is
**consumed**. Then no retry and no cancel exist. Only a save reload recovers the game.

- **Save the game before you drive any landing test.** Do this always. Do not wait until the landing looks stuck
  (2026-08-28).
- Land with `jawa/gravship_land`. Its default, `skipCutscene=true`, places the ship directly and does not run the chain.
  `skipCutscene=false` runs the chain and is for a player at the screen only. The tool leaves the game paused. Read the state with `jawa/gravship_status`.

### A layout can be stamped onto a live map

**`src/RimMandrake/Utils/print_gravship.py` stamps a layout onto a live map (2026-08-27).** The script never touches
`ShipSketchBuilder`. Foundation, floors and buildings are three batch calls of the bridge. One print of
`Gravship_Cradle` on a cleared 250×250 map was measured:

- The print laid 4,034 foundation cells, 4,034 floors and 1,571 things, in ~15 calls.
- A cell-by-cell read-back verified **1,571 of 1,571**. Every building was `PlayerColony`.

```
python.exe src/RimMandrake/Utils/print_gravship.py <layout.xml> --center 125,125 --apply
```

**The gate that nobody predicts: `SetFoundation` is refused on any cell that has an UNDER layer.** The refusal comes per
cell, as *"cell has under-terrain; strip the floor first"*. A natural top terrain **cannot be removed at all**:
`CanRemoveTopLayerAt` reads `Removable`, and natural soil is not removable. The way through is two calls:

1. Paint a **removable** floor (`MetalTile`) over the footprint. `SetTerrain` pushes the natural terrain down into
   `under`.
2. Call `jawa/set_terrain_layer layer='removeTop'`. `RemoveTopLayer` pops the natural terrain back up and **nulls
   `under`**. Only then can the cell take a foundation.

The order of the whole print is **strip → foundation → terrain → things, largest footprint first.** The script obeys
this order.

- **An export contains NO `GravEngine` thing.** The exporter skips the def of the engine. The mod's importer places the
  engine from `gravEngineX/Z`, and so does the script. If a hand-written layout also holds a `GravEngine` in that cell,
  the importer keeps one engine: its `AddThing` call refuses a thing that collides.
- **An export carries map litter.** `Gravship_Cradle` carries 2 `SteamGeyser` and 1 `VHGE_GasGeyser` from the original
  map. The script skips these two defs and no other litter.
- **The FOUR GATES below still apply.** A printed ship is geometry. The engine reads `Gravship range: 0` and every
  thruster reads *"Not connected to grav engine"* until somebody powers, fuels and inspects the ship. The script closes
  gate 1 only: its default `--faction PlayerColony` gives every building to the player.

### Dressing a printed ship — floors, signage, damage

`print_gravship.py` puts the geometry down. Four more tools turn the geometry into a ship that looks a thousand years
old. The first three plan before they write. `ship_dress.py` has no dry run, so each phase writes to the map at once:

| tool | does |
|---|---|
| `src/RimMandrake/Utils/gravship_floor_v2.py` | gives a TerrainDef and a ColorDef to every deck cell from a seeded noise field, and renders the result offline with swatches cut from live captures. `--emit-plan` writes the whole scheme in MAP coordinates |
| `src/RimMandrake/Utils/apply_floor_plan.py` | lays that plan on the live map — holes, floors, per-cell colour |
| `src/RimMandrake/Utils/repaint_hull.py` | paints the HULL with the vanilla paint system (`jawa/paint_building`, one call per colour chunk; persistent, savegame-scribed). `--census` reads back; plan format `{"wallColor": {"<ColorDef>": [[x,z],...]}}` |
| `src/RimMandrake/Utils/ship_dress.py` | Aurebesh word signage, landing pads, gutted bays, design notes as letters |

Three rules came out of this work. Each was measured, and each was expensive:

* **Cut the holes BEFORE you paint the floors.** A painted floor writes an `under` layer, and the foundation operations
  refuse a cell with that layer. The full order is in `skills/rimbridge/references/map-authoring.md`.
* **Paint the hull; do not choose the hull material for its colour.** The owner disliked a hull whose material was chosen
  for its colour: *"I'm not super happy that my ship's walls are made of megabone."* (quoted in a commit of 2026-08-28.)
  - Paint with `repaint_hull.py`. `repaint_hull.py` has no budget per game session. The dev `T: Set Color` tool stops at
    roughly 380 invocations per GAME session. No reconnect clears that count.
  - **Paint does not survive an export.** `ShipLayoutDefV2` carries no colour field: `ShipThingEntry` has `stuffDef` and
    no other field with a colour. A re-export after a `jawa/paint_building` repaint measured **zero** colour matches
    (2026-09-02). So paint the hull again after each import or print. Keep the paint plan beside the layout.
  - Stuff is the only colour that a layout round trip keeps. `GravshipHull` takes any Metallic stuff, and stuff carries
    colour. One `jawa/build_batch` per material did permanently what 2,300 dev-tool calls could not.
  - If you rebuild a wall cell, the rebuild wipes the conduits in that cell. Place the conduits again from the layout.
    The layout is the authority for where the conduits were.
* **Label the floor: it tells what the ship was.** The Outer Rim mods have 36 Aurebesh word decals. Each decal is 2×1,
  `Standable`, `altitudeLayer Floor`, so the decal lies on the deck and pawns walk over it. Name each bay for what the
  bay USED to be, and leave the sign when the bay is gutted. The sign says more about the ship than any amount of rust.
  The decals come from `Neronix17.OuterRim.FurnitureAndDecor`. That mod was not in ModsConfig on 2026-11-23, so read
  the defs before you run the `labels` phase.

### The mod's own Sketch builder, if you ever need it mid-game

Nobody built this route, and `print_gravship.py` makes it unnecessary. Read this only if a Sketch is the point.
`Importer/ShipSketchBuilder.cs:14` is a **`public static class`**. Line `:24` exposes **`public static Sketch
BuildFromLayout(ShipLayoutDefV2 layout)`**. The file also holds `public static ShipLayoutDefV2 CurrentLayout` and
`public static Sketch CurrentSketch`. A `Sketch` can spawn onto a live map.

- **The call works outside a scenario start, by its source.** The file holds **zero** references to `Find.`, `Current.`,
  `GameInitData`, `Scenario` or `Map`. The method resolves defs through `DefDatabase` and its own caches. The scenario
  resolver is only its caller. No live run here tested this call.
- **The method is not a pure function.** `BuildFromLayout` sets `CurrentLayout` and `CurrentSketch`. The call raises the footprint radius of
  the `GravEngine` def to 79 when the radius is smaller. Only the arrival Postfix calls `RestoreGravEngineRange()`. So call that method yourself
  after a mid-game spawn, or every grav engine keeps the larger radius.
- **`BuildFromLayout` does not lay the floors.** The floors land during arrival, through
  `HarmonyPatch_DoGravship.cs:~157` (`terrainGrid.SetTerrain`). **That patch does not run when you spawn a Sketch
  mid-game.** So a mid-game import gives the structure with no floors. Send the `terrainDef` cells of the layout through
  `jawa/set_terrain_batch` after the spawn. `gravship_layout.py` reads those cells straight from the file.

### Fields of the model classes

The mod's model classes declare the fields below. Our first export had `IsNull="True"` in `quality`,
`exportedStorageSettings` and `compSettings`. Our later exports hold `exportedStorageSettings` and `compSettings` blocks,
and some hold one `plantToGrowDef`. None of our exports holds a `quality`. The library carries each block whole.

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

**A layout this library accepts is still not one the game has accepted.** A round trip proves that our parser agrees with
itself. Send a hand-written ship through the choose-gravship page and look at the result. Until then the ship is not done.

## Capacity, and the dial that changes it

`Connected substructure: <used> / <cap>` on the engine is the number that matters. The cap comes from the
`SubstructureSupport` stat of the engine. **Each `GravFieldExtender` adds to the cap, but only after that extender is
claimed and powered** (see THE FOUR GATES below). Nine extenders raised a measured cap `4,680 -> 51,480`, which is an
order of magnitude. A second `GravEngine` contributes nothing **and disables the first**: *"Grav engine disabled: Multiple
grav engines present"*.

The cap also depends on **mod settings** of Bigger Gravships. `gravEngineSupport` applies without a restart. On
2026-11-23 the settings file held `BG_gravEngineSupport` 4500 and `BG_gravExtenderSupport` 5000. Read the file before you
predict a cap. The full numbers, the settings-dialog flow and the experiments of 2026-08-13 are in
`references/measured-2026-08-13.md`. Two conclusions of those experiments were later found to be confounded.

## The FOUR GATES — why a printed gravship never flies (measured live 2026-08-15)

A ship that this skill writes, and that somebody stamps onto a map through the bridge, is **geometrically perfect and
completely inert.** The owner drove the fix by hand. Every line here is a before/after read from `jawa/inspect_string`.

Result: `Gravship range: 0 -> 40`, all four thrusters GREEN, all nine extenders connected, engine capacity
`4,680 -> 51,480`.

**The gates, in dependency order. Each gate silently blocks everything after it.**

1. **CLAIM EVERY PART.** A building that the bridge spawns with no faction arrives `faction: None`. A part with no faction
   does not join the gravship. **If the engine is `PlayerColony`, that proves nothing about the rest.** On the measured
   ship, the player owned the engine. The console, tank, hull, extenders and thrusters were all `None`. Claim each thing.
2. **RUN CONDUIT TO EVERYTHING.** The test is not "conduit exists on the map". A connected run must reach each consumer,
   through the floor.
3. **ADD BATTERIES.** The extenders draw more than the engine alone can carry. After the fix the engine reads
   `Power output 4,424 W`, `Grid excess -2,216 W` with `5,990 Wd stored`. So the ship runs **at a deficit**, from
   batteries.
4. **PIPE ASTROFUEL** from the tank to the thrusters **and to the grav engine**. Fuel can exist with no pipe to the
   thrusters. Then a console reads `Stored astrofuel: 250 / 250` and the thrusters read
   `Astrofuel net excess/stored in network: 0 l/d / 0 l`.
   - **On the VGE modlist (Vanilla Gravship Expanded) this gate is enforced, not cosmetic.** A `CanBeActive` postfix keeps
     a thruster inactive until its astrofuel **pipe net** holds fuel. Vanilla's own inspect string still shows the generic
     "Not connected to grav engine" and does not name the fuel gate.
   - `ChemfuelTank` is the astrofuel storage. `VGE_AstrofuelPipe` connects the tank into the network. A tank near a
     thruster is not piped to the thruster (measured 2026-08-29).

### The error string lies about the cause

Every unmet gate in the list reports the **same** message on the part:

```
Not functional: Not connected to grav engine
Must be placed within range of a grav engine
```

The message reads like geometry. The cause is almost never geometry. On the measured ship the message meant, in turn:
unclaimed, then unpowered, then unfuelled. **Do not move a part because of this message until all four gates are
satisfied.** One agent moved a whole thruster bank because of the message. The bank was never the problem.

### Red herrings, so nobody spends the hours again

Substructure connectivity, thruster distance and `onlyRequiresLooseConnection` were each ruled out live. The cheap check
that rules each one out is in [references/validation-plan.md](references/validation-plan.md). One real gate sits before
all four: **a colonist must INSPECT the grav engine** before anything binds to the engine. An uninspected engine makes
every part report the same "not connected" line. A colonist needs a door to reach the engine.

**So a gravship cannot be printed.** The layout file gives you a hull and correct placement. Claiming (unless the print
script gave the faction), wiring, powering, fuelling and inspecting are colonist work. The ship is inert until that work is done.

## Validation plan — what you owe whoever holds the game

`validate()` returning `[]` and `--roundtrip` passing prove that the file agrees with itself. Neither one proves that
the game accepts the ship. So an authored layout ships with a validation plan **in the same commit**. A load on the full mod
list takes many minutes. Without a plan, the seat that holds the game invents a check that carries none of your
predictions. Write three lines per check. If a check does not fit in three lines, the item is really two items:

```
PROVE    <exact call / defName / click path>
EXPECT   <number or string, written before the look>
LIES     <how this check produces a false pass>
```

What to predict for each gate, and a worked example for a sled's first import:
[references/validation-plan.md](references/validation-plan.md).

## Why the file beats the build

Building the v1 ship live took 31 bridge steps, 4,057 foundation cells, 4,057 floor cells and 1,053 things. The map then
contributed litter: 32 river rocks and glacial ice went into the first export. The map also refused two foundation cells,
because ruins already stood there. A ship authored as a file has none of those failure modes: no map state, no
substructure order, no spawn collisions. Use the build path to *prove* a design in game. Use the file path to *make* a
design.

## Landing rotation

When a ship turns to land, each thing turns by these rules (1.6 `Gravship.GetPlacementValues`):

- A rotatable thing turns with the ship.
- A `rotatable=false` SQUARE thing keeps `defaultPlacingRot` and never turns.
- A `rotatable=false` NON-square Building is FORCED to the ship's rotation anyway.

Audit and lint with `src/RimMandrake/Utils/gravship_rotation_audit.py --check`.
