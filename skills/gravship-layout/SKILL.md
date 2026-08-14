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
| **how a layout is IMPORTED** | 🔴 **UNPROVEN — see "Loading" below** |
| `quality`, `compSettings`, `exportedStorageSettings` shapes | **NEVER OBSERVED POPULATED** — always `IsNull="True"` in our export |

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

## Loading a layout — 🔴 UNPROVEN, do not assume

**Everything above is measured. This is not.** What was checked, all negative:

- The grav engine's gizmos are Claim, Deconstruct, Select Blueprint, Selection
  tools, Edit item, Set Rotation, Place Blueprint, Deactivate Engine, Inspect,
  Export Gravship Layout. **There is no Import.** "Select Blueprint" opens
  nothing and is believed to belong to a different mod.
- `rimworld/search_debug_actions` for `gravship`, `layout` and `ship` returns
  **zero** hits.
- **`ShipLayoutDefV2` is not in the live def dump**, so it is not loaded as a
  Def at game start despite carrying `defName`/`label`. The mod reads these
  files at runtime from somewhere else.

Two hand-authored ships are already sitting in `Config/GravshipExport`
(`JawaTestSled.xml` 9×9, `JawaTestBarge.xml` 22×16) waiting for whoever settles
this. **The next step is to read Gravship Exporter's own source for its import
entry point** — CREATE has read it and has been asked.

⚠️ Until the import route is proven, **a hand-authored layout is an unvalidated
artifact.** Round-tripping through this library proves our parser agrees with
itself, *not* that RimWorld will accept the file. Do not ship a hand-written
ship as done until one has been loaded in-game and looked at.

## Why the file beats the build

Building the v1 ship live took 31 bridge steps, 4,057 foundation cells, 4,057
floor cells and 1,053 things — and even then the map contributed litter (32
river rocks and glacial ice swept into the first export) and refused two
foundation cells because of pre-existing ruins. Authoring the same ship as a
file has none of those failure modes: no map state, no substructure ordering,
no spawn collisions. The build path stays useful for *proving* a design in
game; the file path is how a design should be *made*.
