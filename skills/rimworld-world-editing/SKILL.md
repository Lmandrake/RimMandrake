---
name: rimworld-world-editing
description: Author RimWorld's PLANET from the bridge - tiles, biomes, elevation, rivers, roads, mutators, landmarks, named regions and settlements - whether the game sits at Page_SelectStartingSite or is already Playing, because the 33 jawa/world_* tools reach Find.WorldGrid from either. Covers the world_commit without which no edit is visible, the 100-row limit cap on every read, the gates the setters do not enforce, the category conflicts that make a correct write read as a failure, and the instruments here that report a clean number while being wrong. Use when editing biomes, rivers, roads, landmarks or settlements on the planet, auditing a generated faction roster before committing to a landing site, or automating anything a human would otherwise click tile by tile.
---

# Editing the world from outside, at the world screen

Every claim here was **measured on a live game at `Page_SelectStartingSite`** on
2026-08-15, on a throwaway world the owner created for the purpose. Nothing is
inferred from the map-screen behaviour, because almost none of it transfers.

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

🔴 **`hasCurrentGame: true` with `programState: Entry` is the signature.** There is
a planet but no map. Everything below follows from that one fact.

⚠️ **`rimworld/get_game_info` THROWS here** — `Find.MapUI` is null, so it dies with
*"Specified cast is not valid."* That is a bridge limitation at this screen, not a
broken world. **Do not use it as your are-we-alive probe**; use `get_ui_state`.

---

## 1. What actually works

| goal | call | verified |
|---|---|---|
| planet-wide stats, **per-biome tile counts** | `jawa/world_stats` | ✅ 295,732 tiles, 16.67% water, full biome histogram |
| the generated faction roster | `jawa/list_factions` | ✅ 43 factions, defName + name + hostility |
| what lives in a biome | `jawa/biome_probe` | ⚠️ NREs on ANY biome while Alpha Animals is loaded (its `CommonalityOfAnimal` postfix) — it walks `AllWildAnimals` regardless, even with `animals:false` (2026-09-21) |
| run a debug action | `rimworld/execute_debug_action` | ✅ `Outputs\All Factions` returned real data |
| resolve a debug path without running it | `rimworld/get_debug_action` | ✅ |
| walk the debug tree | `rimworld/list_debug_action_children` | ✅ **except the `Actions` root** — see §2 |
| read the UI | `get_ui_layout` · `get_ui_state` · `get_screen_targets` | ✅ |
| click a checkbox | `rimworld/click_ui_target` | ✅ actionable elements only |
| close a window | `rimworld/close_window` | ✅ |
| screenshot | `rimworld/take_screenshot` | ✅ but read §4 first |

⭐ **`jawa/world_stats`' biome histogram is your measuring instrument.** It is the
only cheap way to prove a world edit did or did not land. Record it before and
after every attempt — that is how the no-op in §3 was caught.

---

## 2. 🔴 The `Actions` root NREs — but its children resolve anyway

```
list_debug_action_children("Actions")
  -> success: FALSE, "Object reference not set to an instance of an object"
```

**It returns `0` children and a failure.** If you print only the count you will
read that as "there are no debug actions at the world screen" and be wrong — that
mistake was made and corrected on 2026-08-15. **Always check `success`, never the
count alone.**

The tree is fine underneath. Every one of these resolved:

```
get_debug_action("Actions\Set biome (mod)...")      -> success TRUE
get_debug_action("Actions\Clear Landmark (mod)")    -> success TRUE
get_debug_action("Actions\World noise visualizer")  -> success TRUE
list_debug_action_children("Actions\Set biome (mod)...")     -> 54 biomes
list_debug_action_children("Actions\Set landmark (mod)...")  -> 113 landmarks
```

### The route that works: read the leaf names off the SCREEN

Since you cannot enumerate the root, get the names from the open debug dialog and
prefix them:

```python
rb.call("rimworld/execute_debug_action", {"path": "Actions\\..."})  # opens nothing
lay = rb.call("rimworld/get_ui_layout", {})          # with Dialog_Debug OPEN
labels = re.findall(r'"label"\s*:\s*"([^"]{2,60})"', json.dumps(lay))
#   -> 'Set biome (mod)...', 'Set landmark (mod)...', 'Clear Landmark (mod)',
#      'World noise visualizer', 'Show more actions', 'Open Tweak Editor'
path = "Actions\\" + label          # this composes correctly at this screen
```

🔑 A bare label without the `Actions\` prefix fails: *"Could not find debug action
'Set biome (mod)...'"*. A section HEADER is not an action — `Actions\More debug
actions` does not resolve, while `Actions\Show more actions` does.

🔑 **A submenu refuses to execute, and says so usefully:** *"This debug node is a
submenu. Browse its children instead of executing it directly."* That message is
how you tell a branch from a leaf without listing anything.

⛔ **Debug-menu rows are NOT clickable.** In `get_ui_layout` they come back as
`kind: "label", actionable: false`, and `click_ui_target` refuses with *"is not
actionable"*. `execute_debug_action` is the only route to them.

---

## 3. ✅ THE WALL IS GONE — world-tile targeting landed 2026-08-19

**This section used to say "there is no way to target a world tile" and that was true for
four days.** It is now false. CHECK built 25 companion `[Tool]` methods that reach
`Find.WorldGrid[tile]`, `Find.World.landmarks`, `Find.WorldObjects` and
`Find.World.features` directly, with no cursor involved. Tile-by-tile world editing is no
longer a human clicking.

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

⚡ **Writing all 21,872 tiles takes 0.1 seconds.**

🔴 **`success: true` still does not mean the planet changed** — that law is unrepealed, and
it is now enforceable rather than merely warned about. Every writer here has a matching
`*_validate` that reads RAW FIELDS, and `jawa/world_stats`' biome histogram remains the
independent second instrument. Use both.

🔴 **Two more traps, measured 2026-08-25, that make a correct result look wrong and a
wrong one look right:**
* ⛔ **Every `world_*_get` returns at most 100 rows.** Pass `limit`; `max` and `count` are
  silently ignored and report `requested: N` as though nothing were capped.
* ⛔ **`AddMutator` resolves category conflicts**, so `Headwater`/`RiverConfluence`/
  `RiverDelta` displace plain `River` and `CaveLakes` displaces `Caves`. Ask whether the
  tile carries ANY def from the family, never whether it carries the exact one you wrote.
* ⛔ **The setter does not enforce a mutator's own gates** (`needs no river`, `requires
  coastline`, hilliness, biome). They live in the roster's `note`, and an illegal write
  lands and then misbehaves. Full treatment: `references/river-networks.md`.

### The four traps that replaced the wall

1. **Nothing is visible until `jawa/world_commit` runs.** RimWorld has no per-tile visual
   invalidation except pollution; everything else needs a whole `WorldDrawLayer` mesh
   regeneration.
2. **`Tile`'s private caches never invalidate.** `HillinessLabel`, `MinTemperature`,
   `MaxTemperature` and `Biomes` are lazily cached with **no reset method anywhere in
   RimWorld**. A validator built on them confirms writes that never landed.
3. **`SurfaceTile.Roads`/`Rivers` are biome-FILTERED views.** A biome with
   `allowRivers=false` hides links without deleting them — 20+ such tiles on an untouched
   world. And `BiomeDef.allowRivers`/`allowRoads` are **absent from the offline def dump**,
   so this cannot be checked offline at all. 🔑 **`allowRoads` is a claim about OUR def
   vs. the DONOR def, and the donor answers it in one query.** A handoff once flagged a
   roads ruling as resting on a false premise; the live dump showed both donors (`ExtremeDesert`,
   `AB_PropaneLakes`) actually carry `allowRoads=True`, and the ban arrived with OUR OWN
   defs — the ruling was right and the doubt was the error. Check the donor before
   retracting a ruling about what we changed (2026-09-19).
4. **`AddLandmark` does not enforce `IsValidTile`.** It will happily stack a landmark on a
   settlement and say nothing. Ordering is ours to police.
5. **The same raw-vs-filtered split applies to mutators, and it can report something the
   engine will never run.** `jawa/world_mutators_get` reads the RAW `mutatorsNullable`
   field, while the engine's gensteps iterate the `Tile.Mutators` PROPERTY — Geological
   Landforms Harmony-postfixes that property to filter out its own
   `Odyssey_DisabledTileMutators`. So the bridge can report a mutator (e.g. `River`) the
   engine has actually disabled. Check the raw-vs-filtered pair before blaming either side
   for a missing effect (2026-09-18).

### 🔴 Five more, measured 2026-08-26 across ~11,000 mutator and 150 landmark writes

Full evidence in `references/mutators-and-objects.md`; these are the ones that cost a repair.

1. **`world_landmarks_set`'s `isValidTile` is evaluated AFTER the add** — it reports the
   landmark you just placed, never blocks anything, and is worthless as a pre-check.
   Success is `added >= 1` **plus** the read-back showing your def.
2. **The landmark and the mutator often have different defNames.** `AncientRuins` is the
   mutator; the landmark is `Ruins`. `sw_Sarlacc` has no mutator at all.
3. **A landmark's `mutatorChances` rolls bypass any category guard you wrote** — they go
   through `AddMutator` and displace. Diff whole-planet LOSSES after every landmark pass.
   ⚠️ And a **remove does not restore** what an add displaced; probes are destructive.
4. **The 45 `GL_*` defs cannot be written and that is correct** — Geological Landforms
   computes them at display time; they never enter `mutatorsNullable`, so a "never used"
   count over them measures nothing. Landforms are assigned at MAP generation from
   hilliness/topology/elevation, and never appear on the world-tile pane.
5. **`elevation <= 0` is water and generates NO ROCK** (`GenStep_RocksFromGrid` returns on
   `WaterCovered`), and a land tile's elevation is clamped to >= 1 m on save. A chasm's
   depth is the MAP elevation grid, not the world tile — you deepen it with hilliness.
6. **A mutator's own biome whitelist can silently block a LANDMARK's auto-rolled
   companion mutator, even on a biome the whitelist patch already covers.** `Tile.AddMutator`
   (the direct API call a landmark placement uses) bypasses the gate that the normal roll
   enforces. Also: a spec's own tile-count header can be stale — one claimed 236 tiles of a
   biome where a fresh `world_tile_export` measured 223 (2026-09-18).

Full element census and every signature:
`design/Jawa/worldbuilding/WORLDMAP_BRIDGE_SURFACE.md`. Live facts: `LIVE.md`.

📌 **The debug-menu route in §2 is now the slow path**, not the only path. It still works
and the `Actions` root still NREs, so keep §2 — but reach for a `jawa/world_*` tool first.

⛔ **`rimworld/search_debug_actions` timed out at 30 s even on a 13-mod list.** The
documented debug-discovery hang is not only a heavy-modlist problem. Do not call it.

## 4. ⚠️ An open dialog blanks the screenshot

With `LudeonTK.Dialog_Debug` open, `take_screenshot` returned **the dialog on pure
black** — no planet at all. Closing it restored the full world view immediately:

```python
rb.call("rimworld/close_window", {"windowType": "LudeonTK.Dialog_Debug"})
```

This is the same family as the map-screen trap where a modal froze and
false-coloured the frame (`skills/rimbridge/references/traps.md`). **Rule: close
every dialog before you photograph anything, and never diagnose a visual defect
from a frame taken with one open.**

⚠️ **The world view can wedge open under bridge driving, and every UI-reset call refuses
to close it.** After a generated-map cull plus a run of world edits, `jawa/world_view
{show:false}` can refuse (`wantedMode` reasserts `Planet`, `worldSelected` stays `true`),
and `clear_selection`/`select_pawn`/`jump_camera_to_cell`/any main-tab call all fail the
same way. **Save and reload is the reset that actually works** (2026-09-18).

🔑 `jawa/clear_ui` does not close these — it reports `closedCount: 0` and lists the
window under `remaining`. Use `close_window` with the exact type.

---

## 5. Auditing a generated world before you commit

This is the one job the bridge does well here, and it is worth doing every time,
because the landing-site page is the last moment before the world is fixed.

```python
fs = rb.call("jawa/list_factions", {})["factions"]
names = [f["defName"] for f in fs]
missing = [w for w in WANTED if w not in names]      # did ours generate?
unwanted = [n for n in names if n in FICTION_BREAKERS]
```

Measured on the 2026-08-15 world: **43 factions**, all eight `Jawa_*` factions
present. ⚠️ Presence is not a settlement count — `jawa/list_factions` returned
`settlements: None` for every faction at this screen, so it answers "does this
faction exist in the world", **not** "how many bases does it hold".

📌 **The Configure Factions page is already behind you at
`Page_SelectStartingSite`.** If the roster is wrong here, the fix is regenerating,
not editing. Audit early.

---

## 5a. A BiomeDef with no `workerClass` crashes ALL worldgen, not just its own tiles

A `BiomeDef` that is `implemented` + `generatesNaturally` but ships no `workerClass`
throws per-tile inside `WorldGenStep_Terrain.BiomeFrom` — and because that genstep runs
for every tile on the planet, one bad biome kills the whole worldgen pass, not just the
tiles that would use it. **Set `generatesNaturally=false` on any hand-placed,
frozen-world biome that has no worker** (2026-09-17).

🔑 **And even WITH a `workerClass`, it is inert on the frozen world.**
`BiomeDef.Worker.GetScore` is called only from `WorldGenStep_Terrain` (MEASURED,
RimSage), and this campaign runs no worldgen — the planet is authored, not
generated (see CLAUDE.md's "world remake is the last step" ruling). A
self-placing BiomeDef can never actually paint itself here; that is not a
defect in the def, it is the standing fact about how this world gets painted
(2026-09-20).

## 5b. Sparse is correct — a landmark-density pass is not owed to every biome

Deserts, wasteland and seas SHOULD read barren on the worldmap; blanket-landmarking
everything is the defect, not the fix. Only dense/dramatic biomes want a
landmark-density pass (2026-09-08).

## 6. Repainting biomes — measured 2026-09-07, closing out two vanilla survivors

Ash'karr had been "fully repainted" for weeks and still carried 262 vanilla `SeaIce`
and 10 vanilla `Lake` tiles. Everything here is why they survived and what the engine
actually reads.

### 🔴 A `(region, biome)` selector silently skips every pair it does not enumerate

The paint script chose tiles like this:

```python
SELECTORS = [('Scald','Lake','RUT_TheScald'), ('Twilight Sea','Ocean','RUT_TwilightSea'), ...]
moved = [r for r in rows if r['region']==region and r['biome']==from_biome]
```

The 262 `SeaIce` tiles were **inside** the two sea regions and were skipped only for not
being `Ocean`; the 10 `Lake` tiles were in a region no selector named. **And nothing
caught it, because the script printed 442 and 381 — exactly the numbers its own plan
predicted.** A count that matches your plan only proves the plan was self-consistent.

✅ **Assert coverage against the INVENTORY, not against the expected number.** After any
regional repaint, ask what is left in that region that you did not touch:
`Counter(r['biome'] for r in rows if r['region']==R)` must contain nothing you did not
intend to leave. Same family as *zero rows is a failure, not a footnote*.

### 🔴 Water NEVER freezes from temperature. Ice comes from the biome, and only the biome.

Do not assume a cold sea will look frozen. Two independent mechanisms, both measured in
source:

1. **Map-gen** — `MapGenUtility.TerrainFrom()` resolves every cell through
   `biomeDef.terrainsByFertility`. **There is no temperature term anywhere in it.**
   Vanilla `SeaIce` looks frozen purely because its `terrainsByFertility` maps everything
   to `Ice`. `BiomeDef` has no ice or freezing field at all.
2. **Runtime** — Odyssey's `FreezeManager.DoWaterFreezing` lays `ThinIce` at ≤ −7 °C, but
   only where `terrain.canFreeze`. `WaterDeepBase` (parent of `WaterDeep` **and**
   `WaterOceanDeep`) sets `canFreeze=false`, as does `WaterOceanShallow`. **Ocean terrain
   is hard-excluded by def flag.** Only freshwater shallows freeze.

⇒ A custom sea biome mapping to `WaterOceanDeep` stays liquid at any temperature, forever.
**Visible ice requires a variant BiomeDef whose `terrainsByFertility` maps to `Ice`** —
there is no other lever.

### Plant density — the formula, and how to census it fast

`WildPlantSpawner`'s desired cover per cell is `min(plantDensity * fertility^2, 1)` —
fertility multiplies TWICE, so `plantDensity` above 1 is the real coverage knob, and
`wildPlantsCareAboutLocalFertility=false` makes the budget whole-map/uniform instead of
per-cell (2026-09-18). To census a biome's regrow behaviour without burning real time,
the debug setting `Settings\Fast Ecology Regrow Rate Only` runs `WildPlantSpawner` 2000x
per game tick — a full regrow census costs ~1000 ticks instead of a million (2026-09-21).

### Measure the planet before normalising anything against it

Before stripping or reformatting names in bulk — leading articles, spelling, plurals —
check what the live data actually does first. 68 of Ash'karr's 71 features carry no
leading article, but three genuinely do (`The Abandoned Mines`, `The Breaks`, `The
Verge`); two other painter divergences turned out to be a SPELLING difference
(Gray/Grey Sea) and a plural (Ashen Waste/Wastes), not articles at all. A blanket strip
rule would have written three new wrong names (2026-09-21).

### ⭐ Only ten fields are real. Everything else in your authoring CSV is bookkeeping.

`jawa/world_tile_export` returns exactly:
`tile · lat · long · biome · elevation · temperature · rainfall · hilliness · swampiness · pollution`

A `water` column, an `arc`, a `region` — those are **yours**, not the engine's. ⛔ The
engine's water test is `elevation <= 0` and nothing else. Ash'karr's `water` column had
silently disagreed with `elev_m` on 153 tiles; invisible to the game, but a live landmine
for the next `(region, water)` selector. **Reconcile a derived column against the field
the engine actually reads, or delete the column.**

### ⚠️ Sibling CSVs exported "together" are not the same vintage

Check each file's own export date before joining two CSVs that live side by side.
`ASHKARR_WORLDMAP_tiles.csv` carries the 2026-09-12 frozen marker while
`ASHKARR_WORLDMAP_landmarks.csv` beside it is dated 2026-08-23 — a different
lineage whose def mix shares almost nothing with the live one (2026-09-19).

### ⚠️ Two encodings that make a correct diff look like total failure

* **`hilliness` round-trips as an ENUM NAME, not an int.** A naive compare of an authoring
  CSV (`2`) against a live export (`SmallHills`) reports a mismatch on **every tile**. Map
  `0..5` → `Undefined · Flat · SmallHills · LargeHills · Mountainous · Impassable`.
* **`jawa/world_stats`' biome histogram covers LAND ONLY.** Water is counted separately, so
  the histogram total will not equal the tile count — 20,465 + 1,407 = 21,872. That is
  correct, not a truncation.

### ✅ Decide a landform per adjacency CLUSTER, not per tile

Voting each ex-lake tile independently by neighbour majority scattered **three biomes
across one five-tile basin** and left a **117 m lump** inside it, because each tile saw a
different rim. Flood-fill the patch first, pool the land neighbours of the WHOLE cluster,
and give the cluster one biome and one elevation. For a drained basin, set elevation to the
cluster's lowest **land** neighbour minus ~10 m (floored at 1 m) so it still reads as a
depression rather than a bump.

⚠️ **Exclude water biomes from any neighbour-majority vote**, or a fill paints the sea onto
dry land — nearly done here twice.

### 📌 Signatures that are not what you would guess

* `jawa/world_view` takes **`centerTile`**, `altitude`, `northUp`, `show` — **not** lat/lon.
* `jawa/world_neighbors` takes **`path`** and writes the whole adjacency CSV; it does not
  answer a single tile. Dump it once, then read it offline.
* `jawa/world_landmarks_get` takes **`limit`**, not `range`.
* `world_features` objects key the id as **`uniqueID`**, not `featureId` — and
  `world_features_set` assign/update/delete needs that `uniqueID`. A wrong name returns
  `None` silently, same as any other unknown-param drop (2026-09-08).

Both were caught by `rimbridge_client`'s param guard, which refuses an undeclared name
rather than letting the bridge discard it and report success. Drive the bridge through that
client, never raw.

---

## 7. Where the detail lives

This file is the map. The parts that earned their own page:

| read this | when |
|---|---|
| `references/generating-a-world.md` | a world is about to be GENERATED — the settings no offline edit can undo, the measured tile-count anchors, why Worldbuilder overwrites My Little Planet's Scale slider and the one-line fix, and how to verify a generated world entirely from its `.rws` |
| `references/savegame-editing.md` | you are about to READ the planet in a `.rws` — the array layouts, what each field means, and the calibrated scalar encodings with the technique that produced them. ⛔ Its WRITE half is tombstoned: savegame writing was deleted 2026-08-19 |
| `references/debug-surface.md` | you need a debug action — the 139 in-game actions vs the NRE at the world screen, and why a mod setting read at INITIALISATION silently does nothing |
| `references/mutators-and-objects.md` | you are placing MUTATORS, LANDMARKS or SETTLEMENTS — the audit histogram that omits defs, the `marineChecked` scope that invents offenders, `CoastDirectionAt` recognising `Ocean` and nothing else, why the mutator form beats the landmark form, `world_objects_add` and the null-faction settlement that is destroyed on load, and the whole-planet displacement diff without which a pass destroys other work and reports 100% |
| `references/road-networks.md` | you are editing ROADS — why the penalty belongs on HOLDING A BEARING rather than on turning, the five RoadDefs being gameplay-identical so the class is free story, the barren country where no weight can steer and waypoints must, the three cost-model mistakes, and the `allowRoads=false` biomes that store a road and draw nothing |
| `references/river-networks.md` | you are editing RIVERS, or anything beside one — the 100-row `limit` cap on every `world_*_get`, the category conflicts that make a correct write read as a failed one, the mutator gates the setter does not enforce, the five graph diagnostics that find real damage, and why meandering a river put 828 m of uphill water into it |
| `references/tidally-locked.md` | the planet is tidally locked — the substellar point, where the terminator actually is in lat/lon, the liveable ring, and how to select the planet type |
| `references/curation-and-looks.md` | curating what appears on the planet (WHITELIST posture, the frozen element list) or making it look right (which beautification mods, and which are hard-incompatible) |

## 8. Keep this skill learning

Anything measured at the world screen goes here rather than into `rimbridge`, because the
two screens behave so differently that mixing them is how the wrong tool gets reached for.
~~If a world-tile targeting tool ever lands, §3 is what has to be rewritten first.~~
✅ It landed 2026-08-19 and §3 was rewritten. The next thing that would invalidate this
file is a change to the `jawa/world_*` surface itself.
