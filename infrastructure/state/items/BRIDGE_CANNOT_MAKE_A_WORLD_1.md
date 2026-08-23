## spec

🔴 **The bridge cannot create a world, and therefore cannot create the 21,872-tile world
everything downstream needs.** Established 2026-08-23 10:1x by going to the main menu and
trying every route the tool list offers.

| route | result |
|---|---|
| `rimworld/start_debug_game` / `_ready` | ✅ works — but it is **RimWorld's built-in quick test only**. No world parameters at all; no coverage, no seed, no scale. Produces the default **119,904**-tile world |
| `rimworld/open_window_by_type` `RimWorld.Page_CreateWorldParams` | ❌ `NullReferenceException` — the page needs a `Game` that does not exist at the Entry scene |
| `rimworld/get_ui_layout` at the main menu | ❌ the only actionable elements are **nine 24×24 icon buttons at y=0** — the dev toolbar. **New colony, Load game and the rest are not exposed**: the Entry menu is immediate-mode GUI, not a `Window`, so nothing enumerates it |
| `rimworld/click_screen_target` / `click_ui_target` | ❌ both take a **targetId** from the layout. Neither takes screen coordinates, so a button that is not enumerated cannot be clicked |
| `rimworld/click_cell` | ❌ map space, and there is no map |

⇒ **No tool in the 107 `rimworld/*` and 121 `jawa/*` tools starts a normal new game.**

## What this blocks, and it is not small

- **The paint test** and `WORLD_PORT_SURVIVES_BRIDGE_1` — `ASHKARR_WORLDMAP_tiles.csv` is
  indexed to 21,872 tiles under MLP subcount 7; a quicktest world is 119,904, and every
  row would be written to an unrelated tile.
- `LAKE_LINT_NARROWED_NOT_OFF_1` — its lint needs the frozen CSV imported first.
- `PRESET_ONSCREEN_CHECK_UNVERIFIED_1` — its whole remaining half is *reading* Configure
  Planet, a page the bridge cannot open.

## The owner's five clicks

⭐ **This is genuinely his, not a permission problem.** New colony → scenario → Configure
Planet, and **while he is on that page the preset check happens for free**: it must read
**Scale 7** and **Coverage 100%**. 🔴 If Scale reads **10** the preset was not read —
abort rather than generate.

⚠️ The game is currently sitting at the main menu, one click from New colony. That was
left deliberately.

## Worth building, or worth not building

🔑 **A companion tool could do it** — `Page_CreateWorldParams` is reachable from C# once a
`Game` object exists, and Worldbuilder already pre-sets the sliders from the preset. But
weigh it honestly: world creation happens a handful of times in this project's life, and
`ONE MAP, NOT A GENERATOR` means we are never rolling worlds in bulk. **A tool that
automates five clicks the owner performs twice may not be worth an assembly.** File the
capability, do not assume it should be built.

## verify

- Either a bridge call creates a world at subcount 7 / coverage 1 and
  `jawa/world_cache_audit` reports `tilesScanned == 21872`, or this item is closed as
  WONT-BUILD with the owner's five clicks written down as the route.

## criteria

Nobody spends another session discovering the bridge cannot make a world.
