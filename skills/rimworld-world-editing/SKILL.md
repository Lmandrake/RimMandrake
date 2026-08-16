---
name: rimworld-world-editing
description: Drive RimWorld's WORLD screen from the bridge - the planet map at Page_SelectStartingSite, after a world is generated and before a map exists. Covers what the bridge can read and change about a generated world, the debug-menu route that works there, the map-scoped tools that all refuse, and the one missing primitive (world-tile targeting) that makes bulk tile editing impossible today. Use when editing biomes or landmarks on the planet, auditing a generated faction roster before committing to a landing site, or automating anything a human would otherwise click tile by tile.
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

## 3. 🔴 THE WALL: there is no way to target a world tile

**This is the single most important fact in this file.** The world editors exist,
resolve, and execute — and then do nothing, because nothing tells them WHICH TILE.

Measured, end to end:

```
world_stats -> IceSheet 6070
execute_debug_action("Actions\Set biome (mod)...\ice sheet") -> success TRUE, no message
world_stats -> IceSheet 6070          # UNCHANGED. Nothing happened.
effects.debugToolActiveAfter = False  # and no tool was even armed
```

`execute_debug_action`'s whole parameter set is `path`, `pawnId`, `x`, `z`,
`thingId` — **every targeting parameter is map-scoped**, and at this screen they
are all meaningless. There is no `tile` parameter and no world-selection call.

Everything map-shaped refuses cleanly, which is at least honest:

```
click_cell        -> "No current map is active."
get_cell_info     -> "Architect tools require an active map."
```

⚠️ **`success: true` here means the node ran, not that the planet changed** — the
one law, in its most expensive form. A world edit that silently no-ops looks
exactly like a world edit that worked. **Diff the `world_stats` biome histogram or
you have measured nothing.**

⛔ The page's own buttons — **Back / Select random site / Factions / Next** — are
drawn immediate-mode and are **not exposed as targets**. `get_screen_targets`
offers only `window-dismiss:*` ids. `press_accept` / `press_cancel` exist and map
to Enter/Escape, and on this page Enter means **Next**, which COMMITS the site and
leaves the world screen. Do not fire it while exploring.

### ⇒ What would unblock bulk tile work

A companion `[Tool]` that takes a **tile id** — `jawa/set_world_biome`,
`jawa/set_landmark`, `jawa/world_tile_info` — reaching `Find.WorldGrid[tile]` and
`Find.World.landmarks` directly, no cursor involved. Extending the companion is a
documented, supported path; see `skills/rimbridge/references/extending.md` §9.
Until that exists, **tile-by-tile world editing is a human clicking, and the
bridge cannot help.**

The other route, when the world is already saved: edit the world data in the
`.rws` offline — see `skills/rimworld-savegame`. That is post-hoc, not interactive.

---

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

## 6. Keep this skill learning

Anything measured at the world screen goes here rather than into `rimbridge`,
because the two screens behave so differently that mixing them is how the wrong
tool gets reached for. If a **world-tile targeting tool** ever lands, this file's
§3 is what has to be rewritten first.
