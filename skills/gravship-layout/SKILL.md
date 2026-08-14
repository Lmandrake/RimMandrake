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

### The mid-game import button does not exist yet, and it is ours to build

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

That is a BRIDGE job, queued as **B-v2** in
`infrastructure/state/queue/BRIDGE.md`. Until it exists, a layout can only enter
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

## 🔴 What actually makes a gravship work — measured live 2026-08-13

A layout that builds is not a ship that flies. All of the below was measured on
a running game, not read from a wiki or a def dump.

### Capacity comes from the ENGINE and nowhere else

`Connected substructure: <used> / <cap>` on the engine's inspect panel is the
number that matters. The cap is **the engine's `SubstructureSupport` stat**.

| source | contributes |
|---|---|
| `GravEngine` | **all of it** — 632.7954 as shipped by Bigger Gravships |
| `GravFieldExtender` | **nothing**, at any distance — see the bug below |
| `VGE_GravFieldAmplifier` | **nothing** |
| a second `GravEngine` | **nothing, and it breaks the first** — panel reports *"Grav engine disabled: Multiple grav engines present"* and both engines go dead |

Ruled out by experiment, so nobody repeats them: **distance is not the gate**
(moved an extender from 22.0 to 15.0 tiles against a `maxDistance` of 34 — cap
unchanged); **power is not the gate** (same cap at 4,800 W and at 0 W);
**faction is not the gate** (the engine is already player-owned — its `Claim`
gizmo is disabled and the Claim designator refuses with *"Must designate
abandoned claimable structures"*).

### 🟢 The capacity dial, and it applies WITHOUT a restart

Bigger Gravships owns these numbers and exposes them as settings. **This is the
lever — not a hull redesign, not a new mod, not a Harmony patch.**

```
rimworld/get_mod_settings    {"modId":"redmattis.biggergravship"}
rimworld/update_mod_settings {"modId":"redmattis.biggergravship",
                              "values":{"gravEngineSupport":4500}}   # NOTE: dict
rimworld/open_mod_settings   {"modId":"redmattis.biggergravship"}
rimworld/get_ui_layout       -> find "Apply Settings Now!" -> click_ui_target
```

🔴 **`update_mod_settings` WRITES but does not APPLY.** After the call the
setting reads 4500 in memory and on disk, and the live def still reads 632.7954.
The mod's **"Apply Settings Now!"** button is what pushes settings into the
defs. Measured: engine `SubstructureSupport` went 632.7954 → **4500.0** with the
game running, and the panel went `4057/633` → `4057/4500`.

⚠️ `values` must be a **dict** — `{"gravEngineSupport": 4500}`. A list of pairs
returns *"At least one settings path/value pair is required."*
⚠️ The click returns *"UI state did not change"* even when it worked. Assert on
the def, not the message.

**Consequence worth more than the ship: gravship size experiments no longer
cost a game load.** Anything BG owns — engine support and radius, extender
count and radius, thruster counts, fuel tank sizes, shields — is a live edit.

### ⚠️ Bigger Gravships applies only SOME of its own settings

Two of its writes are broken. Both were mistaken for design facts before being
measured:

| setting | value | live def |
|---|---|---|
| `gravEngineSupport` | 632.7954 | ✅ 632.7954 |
| `gravExtenderSupport` | **500.0** | ❌ **no `SubstructureSupport` on the def at all** |
| `gravExtenderMaxDistanceFromEngine` | **85.0** | ❌ **34** — it gets the *engine's* number |

So BG intends 632.8 + 12×500 = 6,632 and delivers 633. **Nothing in the settings
window fixes this** — the slider is already at 500. And an XML patch cannot fix
it either: BG's Harmony prefix on `DefGenerator.GenerateImpliedDefs` runs after
all XML patching and is the last writer. Proof it clobbers others: Engines
Unlimited patches `maxSimultaneous` to 9000; the live defs read BG's 20 and 10.

⚠️ Probe caveat, stated because it caught this seat: `jawa/get_def` returned no
comps block for `GravFieldExtender`, so "the stat is absent" is *absent from the
probe*. The behaviour — 633 with eight extenders, four of them inside 34 — is
the finding that stands.

### Completeness is a separate check from capacity

Being under capacity does not make a ship fly. The engine panel also lists, in
red, **`Requires: Thruster, fuel tank, controls`**. Providers: `SmallThruster` /
`LargeThruster`, `ChemfuelTank` / `LargeChemfuelTank`, `PilotConsole`. A hull
with none of them builds, reports connected, and refuses to launch.

**And pathing is a launch requirement, not just a boarding one** — Ludeon's own
keyed strings include `NoPathToPilotConsole`, `PilotConsoleInaccessible` and
`NoPathToGravship`. A sealed hull cannot fly. Our v1 hull was 782 continuous
tiles with **no door anywhere**; doors were cut at (115,58) and (82,136) and are
now in the exported artifact.

⚠️ Cutting a hull tile drops its roof. `DoorBase` and `GravshipHull` both
`holdsRoof`, so spawn the door **in the same breath** as the destroy — a survey
between the two calls is long enough for a collapse.

## Why the file beats the build

Building the v1 ship live took 31 bridge steps, 4,057 foundation cells, 4,057
floor cells and 1,053 things — and even then the map contributed litter (32
river rocks and glacial ice swept into the first export) and refused two
foundation cells because of pre-existing ruins. Authoring the same ship as a
file has none of those failure modes: no map state, no substructure ordering,
no spawn collisions. The build path stays useful for *proving* a design in
game; the file path is how a design should be *made*.
