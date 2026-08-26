---
name: rimworld-world-editing
description: Drive RimWorld's WORLD screen from the bridge - the planet map at Page_SelectStartingSite, after a world is generated and before a map exists. Covers what the bridge can read and change about a generated world, the debug-menu route that works there, the map-scoped tools that all refuse, and the 25 jawa/world_* companion tools that read, write and validate every element of the planet - tiles, biomes, elevation, rivers, roads, mutators, landmarks, settlements, named regions and world info - plus the world_commit without which no edit is visible. Use when editing biomes or landmarks on the planet, auditing a generated faction roster before committing to a landing site, or automating anything a human would otherwise click tile by tile.
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
| what lives in a biome | `jawa/biome_probe` | ✅ |
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
   so this cannot be checked offline at all.
4. **`AddLandmark` does not enforce `IsValidTile`.** It will happily stack a landmark on a
   settlement and say nothing. Ordering is ours to police.

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

---

## 7. Where the detail lives

This file is the map. The parts that earned their own page:

| read this | when |
|---|---|
| `references/generating-a-world.md` | a world is about to be GENERATED — the settings no offline edit can undo, the measured tile-count anchors, why Worldbuilder overwrites My Little Planet's Scale slider and the one-line fix, and how to verify a generated world entirely from its `.rws` |
| `references/savegame-editing.md` | you are about to READ the planet in a `.rws` — the array layouts, what each field means, and the calibrated scalar encodings with the technique that produced them. ⛔ Its WRITE half is tombstoned: savegame writing was deleted 2026-08-19 |
| `references/debug-surface.md` | you need a debug action — the 139 in-game actions vs the NRE at the world screen, and why a mod setting read at INITIALISATION silently does nothing |
| `references/river-networks.md` | you are editing RIVERS, or anything beside one — the 100-row `limit` cap on every `world_*_get`, the category conflicts that make a correct write read as a failed one, the mutator gates the setter does not enforce, the five graph diagnostics that find real damage, and why meandering a river put 828 m of uphill water into it |
| `references/tidally-locked.md` | the planet is tidally locked — the substellar point, where the terminator actually is in lat/lon, the liveable ring, and how to select the planet type |
| `references/curation-and-looks.md` | curating what appears on the planet (WHITELIST posture, the frozen element list) or making it look right (which beautification mods, and which are hard-incompatible) |

## 8. Keep this skill learning

Anything measured at the world screen goes here rather than into `rimbridge`, because the
two screens behave so differently that mixing them is how the wrong tool gets reached for.
~~If a world-tile targeting tool ever lands, §3 is what has to be rewritten first.~~
✅ It landed 2026-08-19 and §3 was rewritten. The next thing that would invalidate this
file is a change to the `jawa/world_*` surface itself.
