---
name: rimworld-world-editing
description: Author RimWorld's PLANET from the bridge - tiles, biomes, elevation, rivers, roads, mutators, landmarks, named regions and settlements - whether the game sits at Page_SelectStartingSite or is already Playing, because the 33 jawa/world_* tools reach Find.WorldGrid from either. Covers the world_commit without which no edit is visible, the 100-row limit cap on every read, the gates the setters do not enforce, the category conflicts that make a correct write read as a failure, and the instruments here that report a clean number while being wrong. Use when editing biomes, rivers, roads, landmarks or settlements on the planet, auditing a generated faction roster before committing to a landing site, or automating anything a human would otherwise click tile by tile.
---

# Editing the world from outside, at the world screen

This skill holds facts that were measured on a live game, or read in code. The code is the 1.6 source or the companion.
Sections 0 to 2, 4 and 5 were mostly measured at `Page_SelectStartingSite`. The owner created a throwaway world for that.
Do not infer world-screen behaviour from map-screen behaviour. Almost none of the map-screen behaviour transfers.

Dates, measurements and corrected lines: [references/history.md](references/history.md).

In this skill, "the world screen" is `Page_SelectStartingSite`. "The bridge" is RimBridge with its companion DLL,
JawaBench. `rb` is the Python bridge client (`src/RimMandrake/Utils/rimbridge_client.py`). "NRE" means a null reference
exception.

## 0. Know which screen you are on — it changes everything

```python
rb.call("rimworld/get_ui_state", {})   # -> windows[]
```

The world screen looks like this:

```
programState      Entry          <- NOT "Playing"
inEntryScene      true
hasCurrentGame    true           <- a WORLD exists
windows           RimWorld.Page_SelectStartingSite
                  MapModeFramework.MapModeUI, MapPreview.MapPreviewToolbar
```

🔴 **`hasCurrentGame: true` with `programState: Entry` is the signature.** At this screen the window is
`Page_SelectStartingSite`. There is a planet, but no map. The rest of this skill follows from that one fact.

⚠️ **`rimworld/get_game_info` THROWS here.** `Find.MapUI` is null, so the tool fails with
*"Specified cast is not valid."* The failure is a bridge limitation at this screen. The world is not broken. **Do not use
`get_game_info` to test if the game is alive here.** Use `get_ui_state`.

---

More traps for this section: [references/traps.md](references/traps.md) § 0. Know which screen you are on — it changes everything.

## 1. What actually works

| goal | call | verified |
|---|---|---|
| planet-wide stats, **per-biome tile counts** | `jawa/world_stats` | ✅ 295,732 tiles, 16.67% water, and a biome histogram of the land tiles |
| the generated faction roster | `jawa/list_factions` | ✅ 43 factions: defName, name, hostility, `settlementCount` |
| what lives in a biome | `jawa/biome_probe` | ⚠️ NREs on ANY biome while Alpha Animals is loaded (its `CommonalityOfAnimal` postfix). The tool walks `AllWildAnimals` even with `animals:false`. Alpha Animals is a retired mod |
| run a debug action | `rimworld/execute_debug_action` | ✅ `Outputs\All Factions` returned real data |
| resolve a debug path without a run of it | `rimworld/get_debug_action` | ✅ |
| walk the debug tree | `rimworld/list_debug_action_children` | ✅ **except the `Actions` root** — see §2 |
| read the UI | `get_ui_layout` · `get_ui_state` · `get_screen_targets` | ✅ |
| click a checkbox | `rimworld/click_ui_target` | ✅ actionable elements only |
| close a window | `rimworld/close_window` | ✅ |
| screenshot | `rimworld/take_screenshot` | ✅ but read §4 first |

⭐ **`jawa/world_stats`' biome histogram is your measuring instrument.** The histogram is the only cheap way to prove
that a world edit did or did not land. Record the histogram before and after each attempt. A no-op edit that reported success was
caught that way.

---

## 2. 🔴 The `Actions` root NREs — but its children resolve anyway

```
list_debug_action_children("Actions")
  -> success: FALSE, "Object reference not set to an instance of an object"
```

**The call returns `0` children and a failure.** If you print only the count, you read "there are no debug actions at the
world screen". That reading is false. **Always check `success`, never the count alone.**

The tree below the root works. Each of these calls resolved:

```
get_debug_action("Actions\Set biome (mod)...")      -> success TRUE
get_debug_action("Actions\Clear Landmark (mod)")    -> success TRUE
get_debug_action("Actions\World noise visualizer")  -> success TRUE
list_debug_action_children("Actions\Set biome (mod)...")     -> 54 biomes
list_debug_action_children("Actions\Set landmark (mod)...")  -> 113 landmarks
```

### The route that works: read the leaf names off the SCREEN

You cannot list the children of the root. So get the names from the open debug dialog, and put the prefix before each
name:

```python
rb.call("rimworld/execute_debug_action", {"path": "Actions\\..."})  # opens nothing
lay = rb.call("rimworld/get_ui_layout", {})          # with Dialog_Debug OPEN
labels = re.findall(r'"label"\s*:\s*"([^"]{2,60})"', json.dumps(lay))
#   -> 'Set biome (mod)...', 'Set landmark (mod)...', 'Clear Landmark (mod)',
#      'World noise visualizer', 'Show more actions', 'Open Tweak Editor'
path = "Actions\\" + label          # this composes correctly at this screen
```

🔑 A bare label without the `Actions\` prefix fails: *"Could not find debug action
'Set biome (mod)...'"*. A section HEADER is not an action. `Actions\More debug
actions` does not resolve. `Actions\Show more actions` does.

🔑 **A submenu refuses to execute, and its message says so:** *"This debug node is a
submenu. Browse its children instead of executing it directly."* That message tells you that the node is a branch, without
a list of anything.

⛔ **Debug-menu rows are NOT clickable.** In `get_ui_layout`, each row is
`kind: "label", actionable: false`. `click_ui_target` refuses the row with *"is not
actionable"*. `execute_debug_action` is the only route to a row.

---

## 3. ✅ THE WALL IS GONE — world-tile targeting landed 2026-08-19

An older form of this section said "there is no way to target a world tile". That statement is false now. The companion
`[Tool]` methods (25 at the first landing) reach `Find.WorldGrid[tile]`, `Find.World.landmarks`, `Find.WorldObjects` and
`Find.World.features` directly. These methods use no cursor. No person has to click tile by tile.

```
READ      world_layers · world_tile_get · world_links_get · world_mutators_get
          world_landmarks_get · world_objects_get · world_features_get · world_info_get
WRITE     world_tile_set/import · world_links_set/clear/import · world_mutators_set
          world_landmarks_set · world_objects_set · world_features_set · world_info_set
VALIDATE  world_tile_validate · world_links_validate · world_objects_validate
          world_mutators_audit · world_lint
COMMIT    world_commit          <- nothing you write is visible without it
CAMERA    world_view            <- the only bridge route to the planet at all
```

The code also registers these tools:

- Read: `world_stats`, `world_tile_export`, `world_neighbors`, `world_cache_audit`.
- Write: `world_objects_add`, `world_objects_remove`, `world_settlements_import`, `world_features_import`,
  `world_landmark_rename`, `world_tile_cache_reset`, `world_tile_map_generate`.
- Display: `world_map_mode`.

The live tool list is the truth, not this page.

⚡ **Writing all 21,872 tiles takes 0.1 seconds.**

🔴 **`success: true` still does not mean the planet changed.** Use two instruments to prove each write. First, call the
family's `*_validate` tool, or `world_mutators_audit`. A family with no such tool has its `world_*_get`. All of them read
RAW FIELDS. Then compare `jawa/world_stats`' biome
histogram. The histogram is independent of the writer.

🔴 **Three more traps make a correct result look wrong, or a wrong result look right:**

* ⛔ **A `world_*_get` returns only `limit` rows.** The default is 100 rows (200 for `world_tile_get`). Pass `limit`. `max` and
  `count` are not parameters: a guard refuses them, or the raw bridge silently ignores them (§6). Then compare the rows that you got with the total:
  * `world_links_get` and `world_mutators_get` report `limitHit` and `unexaminedAfterLimit`.
  * `world_tile_get` reports `truncated`.
  * In `world_landmarks_get`, `world_objects_get` and `world_features_get`, `count` is the total and `returned` is the
    number of rows.
* ⛔ **`AddMutator` resolves category conflicts.** `Headwater`/`RiverConfluence`/`RiverDelta` displace plain `River`, and
  `CaveLakes` displaces `Caves`. Ask whether the tile carries ANY def from the family. Never ask whether the tile carries
  the exact def that you wrote.
* ⛔ **The setter does not enforce a mutator's own gates** (`needs no river`, `requires
  coastline`, hilliness, biome). The gates are in the `note` field of the mutator roster (`world/_organic/_mutator_roster.json`). An illegal write lands and then misbehaves. Full
  treatment: `references/river-networks.md`.

### The four traps that replaced the wall

(The list has five entries now.)

1. **Nothing is visible until `jawa/world_commit` runs.** RimWorld has no per-tile visual
   invalidation except for pollution. Each other change needs a whole `WorldDrawLayer` mesh regeneration.
2. **RimWorld never invalidates `Tile`'s private caches.** `HillinessLabel`, `MinTemperature`,
   `MaxTemperature` and `Biomes` are lazily cached, with **no reset method anywhere in
   RimWorld**. A validator that reads them confirms writes that never landed. Read the raw fields. To clear the caches, run `jawa/world_cache_audit` with `includeTemps=true`. Then run
   `jawa/world_tile_cache_reset` with the tiles or `all=true`. Then run the audit again. A reload also clears them.
3. **`SurfaceTile.Roads`/`Rivers` are biome-FILTERED views.** A biome with
   `allowRivers=false` hides links and does not delete them. An untouched world had 20+ such tiles. A current def dump
   holds `BiomeDef.allowRivers` and `BiomeDef.allowRoads`. The donor is the original biome def that ours
   replaced. 🔑 **`allowRoads` is a claim about OUR def vs. the DONOR def. The donor answers it in one query.** A handoff
   once doubted a correct roads ruling of this kind. The live dump showed that both donors (`ExtremeDesert`,
   `AB_PropaneLakes`) carry `allowRoads=True`. The ban came with OUR OWN
   defs. Check the donor before you retract a ruling about what we changed.
4. **`AddLandmark` does not enforce `IsValidTile`.** `AddLandmark` puts a landmark on a
   settlement and says nothing. So we must keep the order: landmarks before settlements.
5. **The same raw-vs-filtered split applies to mutators. A tool can report a mutator that the
   engine never runs.** `jawa/world_mutators_get` reads the RAW `mutatorsNullable`
   field. The engine's gensteps iterate the `Tile.Mutators` PROPERTY. While Geological
   Landforms is loaded, its Harmony postfix removes its own
   `Odyssey_DisabledTileMutators` from that property. Then the bridge can report a mutator (e.g. `River`) that the
   engine has disabled. Before you blame either side for a missing effect, compare the raw list with the filtered list.
   Geological Landforms is not on `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` now.

### 🔴 Five more, measured 2026-08-26 across ~11,000 mutator and 150 landmark writes

(The list has six entries now.) Full evidence is in `references/mutators-and-objects.md`. Each entry here cost a repair.

1. **`world_landmarks_set`'s `isValidTile` is not a gate.** The tool computes `isValidTile` for each tile just before the
   add, in the same call. The tool then adds the landmark whatever the verdict says. A landmark that is already on the
   tile also makes the verdict false. Success is `added >= 1` **plus** the read-back that shows your def. Also read
   `overwroteLandmarks` and `displacedMutatorCount` (the `displacedMutators` list stops at 25).
2. **The landmark and the mutator often have different defNames.** `AncientRuins` is the
   mutator. `Ruins` is the landmark. `sw_Sarlacc` has no mutator at all of that name (its mutator is `sw_SarlaccLair`).
3. **A landmark's `mutatorChances` rolls bypass any category guard you wrote.** The rolls go
   through `AddMutator` and displace other mutators. After each landmark pass, diff the LOSSES of the whole planet.
   ⚠️ A **remove does not restore** what an add displaced. So a probe that adds and removes is destructive.
4. **The 45 `GL_*` defs of Geological Landforms cannot be written, and that is correct.** Geological Landforms
   computes them at display time. The `GL_*` defs never enter `mutatorsNullable`. So a "never used"
   count over them measures nothing. Landforms are assigned at MAP generation from
   hilliness/topology/elevation. A landform never appears on the world-tile pane.
5. **`elevation <= 0` is water and generates NO ROCK** (`GenStep_RocksFromGrid` returns on
   `WaterCovered`). A save clamps a land tile's elevation to >= 1 m. The depth of a chasm is in the MAP elevation grid,
   not in the world tile. To deepen a chasm, change the hilliness of the tile.
6. **A mutator's own biome whitelist can silently block a LANDMARK's auto-rolled
   companion mutator.** This happened even on a biome that the whitelist patch already covered. `AddLandmark` tests `IsValidTile` of each
   companion mutator. `AddLandmark` skips that test only for a required companion with `forced`. A direct `Tile.AddMutator` call has
   no such test. Also, the tile count in the header of a spec can be stale. One spec claimed 236 tiles of a
   biome. A fresh `world_tile_export` measured 223.

Full element census and every signature:
`design/Jawa/worldbuilding/WORLDMAP_BRIDGE_SURFACE.md`. Live facts: `observed/LIVE.md`.
📌 **The debug-menu route in §2 is the slow path now.** The route still works, and
the `Actions` root still NREs, so §2 stays. Use a `jawa/world_*` tool first.

⛔ **`rimworld/search_debug_actions` timed out at 30 s even on a 13-mod list.** So the
documented debug-discovery hang is not only a problem of a heavy mod list. Do not call this tool.

## 4. ⚠️ An open dialog blanks the screenshot

With `LudeonTK.Dialog_Debug` open, `take_screenshot` returned **the dialog on pure
black**, with no planet. When the dialog was closed, the full world view came back at once:

```python
rb.call("rimworld/close_window", {"windowType": "LudeonTK.Dialog_Debug"})
```

The map screen has a similar trap: a modal froze the frame and gave it false colours
(`skills/rimbridge/references/traps.md`). **Rule: close
every dialog before you photograph anything. Never diagnose a visual defect
from a frame that was taken with a dialog open.**

⚠️ **The world view can stick open under bridge driving, and then every UI-reset call refuses
to close it.** The case came after a generated-map cull plus a run of world edits. `jawa/world_view
{show:false}` can refuse: `wantedMode` goes back to `Planet`, and `worldSelected` stays `true`.
`clear_selection`/`select_pawn`/`jump_camera_to_cell`/any main-tab call all fail the
same way. **Save and reload is the reset that works.**

🔑 **Do not rely on `jawa/clear_ui` to close a dialog.** A measurement at the world screen read `closedCount: 0`, with the
window under `remaining`. In the code today, the default call closes windows of type `Window_Dev`. `Dialog_Debug` is one.
A page or a game dialog is not one. `remaining` lists every window that is still open, the landing page included. Close
only the dialog that you opened, with `close_window` and its exact type. ⛔ Never close `Page_SelectStartingSite`.
⛔ Never use `clear_ui {all:true}` at the world screen. That call closes the landing page, and the world is lost.

---

## 5. Auditing a generated world before you commit

The bridge does this audit well. Do this audit each time that a world is generated. The
landing-site page is the last moment before the world is fixed.

```python
fs = rb.call("jawa/list_factions", {})["factions"]
names = [f["defName"] for f in fs]
missing = [w for w in WANTED if w not in names]      # did ours generate?
unwanted = [n for n in names if n in FICTION_BREAKERS]
```

One measured world had **43 factions**, with all eight `Jawa_*` factions of that date present. ⚠️ Presence is not a
settlement count. The field for the count is `settlementCount`, and `settlementsTotal` covers the planet. `settlements` is
not a field, so a script that reads `settlements` gets `None` for every faction. `list_factions` skips hidden
factions unless you pass `includeHidden`. Read `isCompleteList`.

📌 **The Configure Factions page is already behind you at
`Page_SelectStartingSite`.** Audit early. If the roster is wrong at this screen, an edit of the page is no longer
possible. Regenerate, or add a missing faction with `jawa/faction_create`. The "audit the roster" step (row S7) of
`design/RimMandrake/world_remake_2026-10-19/06_remake_runbook.md` says who decides.

---

More traps for this section: [references/traps.md](references/traps.md) § 5. Auditing a generated world before you commit.

## 5a. A BiomeDef with no `workerClass` crashes ALL worldgen, not just its own tiles

A `BiomeDef` that is `implemented` + `generatesNaturally` but has no `workerClass`
throws in `WorldGenStep_Terrain.BiomeFrom`, for each tile. That genstep runs
for every tile on the planet. So one bad biome stops the whole worldgen pass, not only the
tiles that would use that biome. **Set `generatesNaturally=false` on any hand-placed,
frozen-world biome that has no worker.**

🔑 **Even WITH a `workerClass`, the worker does nothing on the frozen world.**
`BiomeDef.Worker.GetScore` is called only from `WorldGenStep_Terrain` (MEASURED,
RimSage). This campaign runs no worldgen. The planet is authored, not
generated. The rule is `CLAUDE.md` §A biome with zero tiles is not a defect. A
self-placing BiomeDef can never paint itself here. The def has no
defect. The world gets its biomes from our paint.

## 5b. Sparse is correct — a landmark-density pass is not owed to every biome

Deserts, wasteland and seas must read barren on the worldmap. Landmarks
everywhere are the defect, not the fix. Only dense or dramatic biomes want a
landmark-density pass.

## 6. Repainting biomes — measured 2026-09-07, closing out two vanilla survivors

Our planet, Ash'karr, was recorded as "fully repainted". Ash'karr still carried 262 vanilla `SeaIce`
and 10 vanilla `Lake` tiles. The next two parts say why those tiles survived, and what the engine
reads.

### 🔴 A `(region, biome)` selector silently skips every pair it does not enumerate

The paint script chose tiles like this:

```python
SELECTORS = [('Scald','Lake','RM_TheScald'), ('Twilight Sea','Ocean','RM_TwilightSea'), ...]
moved = [r for r in rows if r['region']==region and r['biome']==from_biome]
```

The 262 `SeaIce` tiles were **inside** the two sea regions. The script skipped them only because they were not
`Ocean`. The 10 `Lake` tiles were in a region that no selector named. **Nothing
caught the skip. The script printed 442 and 381, exactly the numbers that its own plan
predicted.** A count that matches your plan proves only that the plan agrees with itself.

✅ **Assert coverage against the INVENTORY, not against the expected number.** After any
regional repaint, ask what is left in that region that you did not touch.
`Counter(r['biome'] for r in rows if r['region']==R)` must contain nothing that you did not
intend to leave. The same rule says: *zero rows is a failure, not a footnote*.

### 🔴 Sea water NEVER freezes from temperature. Sea ice comes from the biome.

Do not assume that a cold sea will look frozen. Two independent mechanisms, both read in the
source:

1. **Map generation.** `MapGenUtility.TerrainFrom()` takes the terrain of each cell from the biome's `terrainPatchMakers`,
   then from gravel or rock by map elevation, then from
   `biomeDef.terrainsByFertility`. **There is no temperature term anywhere in it.**
   Vanilla `SeaIce` looks frozen because its `terrainsByFertility` maps everything
   to `Ice`. `BiomeDef` has no freezing field.
2. **Runtime.** Odyssey's `FreezeManager.DoWaterFreezing` lays `ThinIce` at ≤ −7 °C, but
   only where `terrain.canFreeze`. `WaterDeepBase` (parent of `WaterDeep` **and**
   `WaterOceanDeep`) sets `canFreeze=false`, as does `WaterOceanShallow`. **A def flag excludes ocean terrain.**
   Fresh water that is not `WaterDeep` can freeze: shallow, moving or chest-deep water, and marsh. Hot springs cannot.

⇒ A custom sea biome that maps to `WaterOceanDeep` stays liquid at any temperature, forever.
**Visible sea ice requires a variant BiomeDef whose `terrainsByFertility` maps to `Ice`.** (Its `terrainPatchMakers` can
also lay `Ice`.) There is no other lever: no temperature setting does it.

### Plant density — the formula, and how to census it fast

`WildPlantSpawner`'s desired cover per cell is `min(plantDensity * fertility^2, 1)`. The engine also multiplies by a
density factor: the tile mutators' `plantDensityFactor` and the game conditions.
Fertility multiplies TWICE. So `plantDensity` above 1 is the real control of coverage.
`wildPlantsCareAboutLocalFertility=false` makes the budget uniform over the whole map instead of
per cell. To census a biome's regrow behaviour fast, use
the debug setting `Settings\Fast Ecology Regrow Rate Only`. The setting runs `WildPlantSpawner` 2000x
per game tick. A full regrow census then costs ~1000 ticks instead of a million.

### Measure the planet before normalising anything against it

Before you strip or reformat names in bulk, check what the live data does. Examples are leading articles, spelling and plurals. 68 of Ash'karr's 71 features carry no
leading article. Three carry one (`The Abandoned Mines`, `The Breaks`, `The
Verge`). Two other differences between the paint script's names and the live names were a SPELLING difference
(Gray/Grey Sea) and a plural (Ashen Waste/Wastes), not articles. A blanket strip
rule would write three new wrong names.

### ⭐ Only ten fields are real. Everything else in your authoring CSV is bookkeeping.

By default, `jawa/world_tile_export` returns exactly:
`tile · lat · long · biome · elevation · temperature · rainfall · hilliness · swampiness · pollution`

`extended=true` adds ten more columns. `world_tile_import` does not need them.

A `water` column, an `arc`, a `region`: those are **yours**, not the engine's. ⛔ The
engine's water test is `elevation <= 0` and nothing else. Ash'karr's `water` column
silently disagreed with `elev_m` on 153 tiles. The game did not see the difference. The
next `(region, water)` selector would have used the wrong column. **Reconcile a derived column against the field
that the engine reads, or delete the column.**

### ⚠️ Sibling CSVs exported "together" are not the same vintage

Two CSVs that lie side by side can have different export dates. Check each file's own export date before you join them.
`world/ASHKARR_WORLDMAP_tiles.csv` is a frozen record (marker: `ASHKARR_WORLDMAP_tiles.csv.frozen.json`), last changed 2026-09-12.
`ASHKARR_WORLDMAP_landmarks.csv` beside it was last changed 2026-08-23. The landmarks file comes from a different
lineage, and its def mix shares almost nothing with the live one.

### ⚠️ Two encodings that make a correct diff look like total failure

* **`hilliness` round-trips as an ENUM NAME, not an int.** A naive compare of an authoring
  CSV (`2`) with a live export (`SmallHills`) reports a mismatch on **every tile**. Map
  `0..5` → `Undefined · Flat · SmallHills · LargeHills · Mountainous · Impassable`.
* **`jawa/world_stats`' biome histogram covers LAND ONLY.** The tool counts water separately. So
  the histogram total is not the tile count: 20,465 + 1,407 = 21,872. That is
  correct, not a truncation.

### ✅ Decide a landform per adjacency CLUSTER, not per tile

A vote for each ex-lake tile alone, by neighbour majority, scattered **three biomes
across one five-tile basin**. The vote also left a **117 m lump** inside the basin. Each tile saw a
different rim. So:

1. Flood-fill the patch first.
2. Pool the land neighbours of the WHOLE cluster.
3. Give the cluster one biome and one elevation.

For a drained basin, set the elevation to the
cluster's lowest **land** neighbour minus ~10 m (floored at 1 m). The basin then reads as a
depression, not as a bump.

⚠️ **Exclude water biomes from any neighbour-majority vote.** Otherwise a fill paints the sea onto
dry land. That nearly happened here twice.

### 📌 Signatures that are not what you would guess

* `jawa/world_view` takes **`centerTile`**, `altitude`, `northUp`, `show`. `world_view` does **not** take lat/lon.
* `jawa/world_neighbors` takes **`path`** and writes the whole adjacency CSV. `world_neighbors` does not
  answer for a single tile. Dump the CSV once, then read it offline.
* `jawa/world_landmarks_get` takes **`limit`** (and `def`), not `range`.
* `world_features_get` objects hold the id as **`uniqueID`**, not `featureId`. `world_features_set`
  assign/update/delete needs that `uniqueID` value. Pass the value in the parameter `featureId`. A wrong field name in a
  read returns `None` silently.

`rimbridge_client`'s parameter guard caught the `world_view` fault and the `world_neighbors` fault. The guard refuses an undeclared name. The raw bridge
discards an undeclared name and reports success in two cases. One is the first `jawa/` call of a session. The other is a
tool that is not a `jawa/` tool. Other `jawa/` calls refuse an undeclared name (`JawaBenchArgGuard.cs`). Drive the bridge through that
client, never raw.

---

More traps for this section: [references/traps.md](references/traps.md) § 6. Repainting biomes — measured 2026-09-07, closing out two vanilla survivors.

## 7. Where the detail lives

This file is the map. These parts have their own page:

| read this | when |
|---|---|
| `references/generating-a-world.md` | a world is about to be GENERATED. Contents: the settings that no offline edit can undo; the measured tile-count anchors; why Worldbuilder overwrites My Little Planet's Scale slider and the one-line fix; how to verify a generated world entirely from its `.rws` |
| `references/savegame-editing.md` | you are about to READ the planet in a `.rws`. Contents: the array layouts; what each field means; the calibrated scalar encodings with the technique that produced them. ⛔ Its WRITE half is tombstoned: savegame writing was deleted 2026-08-19 |
| `references/debug-surface.md` | you need a debug action. Contents: the 139 in-game actions vs the NRE at the world screen; why a mod setting that is read at INITIALISATION silently does nothing |
| `references/mutators-and-objects.md` | you are placing MUTATORS, LANDMARKS or SETTLEMENTS. Contents: the audit histogram that omits defs; the `marineChecked` scope that invents offenders; `CoastDirectionAt` recognising `Ocean` and nothing else; why the mutator form beats the landmark form; `world_objects_add` and the null-faction settlement that is destroyed on load; the whole-planet displacement diff, without which a pass destroys other work and reports 100% |
| `references/road-networks.md` | you are editing ROADS. Contents: why the penalty belongs on HOLDING A BEARING and not on a turn; the five RoadDefs being gameplay-identical, so the class is free story; the barren country where no weight can steer and waypoints must; the three cost-model mistakes; the `allowRoads=false` biomes that store a road and draw nothing |
| `references/river-networks.md` | you are editing RIVERS, or anything beside one. Contents: the 100-row `limit` cap on every `world_*_get`; the category conflicts that make a correct write read as a failed one; the mutator gates that the setter does not enforce; the five graph diagnostics that find real damage; why meandering a river put 828 m of uphill water into it |
| `references/tidally-locked.md` | the planet is tidally locked. Contents: the substellar point; where the terminator actually is in lat/lon; the liveable ring; how to select the planet type |
| `references/curation-and-looks.md` | curating what appears on the planet (WHITELIST posture, the frozen element list) or making it look right (which beautification mods, and which are hard-incompatible) |
| `references/traps.md` | you work in §0, §5 or §6: more traps, by section |
| `references/history.md` | you need the date or the measurement behind a line here |

## 8. Keep this skill learning

Put anything measured at the world screen here, not in `rimbridge`. The
two screens behave very differently. When their facts are mixed, an agent reaches for the wrong tool.
A change to the `jawa/world_*` tools can make this file false. When those tools change, check this file.
