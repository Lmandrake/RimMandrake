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

---

## 7. Tidally locked worlds — the geometry, solved

`7f.alienworlds.tidallylocked` (workshop **3631364335**, ACTIVE) on top of
`7f.alienworlds` (**3626210061**, ACTIVE). Both ship **full C# source**; everything below
was read out of `Source/PlanetTypeDef.cs` and `Defs/PlanetTypes.xml`, not inferred.

### 🔑 The substellar point is at latitude 0, longitude 0

The mod transpiles `WorldGenStep_Terrain.GenerateTileFor` so temperature stops being a
function of latitude and becomes a function of **great-circle distance from (0,0)**:

```csharp
effectiveLat = Acos( Cos(long) * Cos(lat) ) * Rad2Deg;   // pos.x = LONGitude, pos.y = lat
return AvgTempByLatitudeCurve.Evaluate(effectiveLat / 90f);
```

⚠️ `Find.WorldGrid.LongLatOf()` returns `Vector2(longitude, latitude)` — **x is longitude**.
Read that backwards and every calculation you build on it is wrong but plausible.

So the curve's x-axis is **(degrees from the substellar point) / 90**, and its published
0.0→2.0 range is exactly 0°→180°:

| x | angle from substellar | avg temp | what it is |
|---|---|---|---|
| 0.0 | 0° | **+70 °C** | substellar point — permanent noon, lethal |
| 0.44 | 40° | +21 °C | inner edge of the liveable ring |
| 0.5 | 45° | +14 °C | |
| 0.64 | 57° | **0 °C** | outer edge of the liveable ring |
| **1.0** | **90°** | **−37 °C** | 🔴 **THE TERMINATOR** |
| 1.33 | 120° | −70 °C | |
| 2.0 | 180° | −80 °C | antistellar point — permanent midnight |

### ⇒ Where the terminator actually is, in lat/lon

The terminator is the great circle **90° from (0,0)**, i.e. every tile where
`cos(long)·cos(lat) = 0`. In practice that means:

* **longitude = ±90°, at any latitude** — the two meridians that run pole to pole, and
* **the poles themselves** (latitude ±90°, any longitude).

**Day side = |longitude| < 90°. Night side = |longitude| > 90°.** It is a LONGITUDE
split, not the latitude split every other RimWorld world uses. Any tool that reasons
about "north is colder" is wrong on this planet.

🔑 **The liveable ring is a circle of radius ~40–57° around (0, 0)** — that is the
"habitable sliver" the mod's description promises, and it sits **well inside the day
side**, not at the terminator. The terminator itself is −37 °C.

Compute it per tile straight off `jawa/world_tile_export`:
```python
import math
d = math.degrees(math.acos(math.cos(math.radians(lon)) * math.cos(math.radians(lat))))
# d  <  40  scorched   |  40..57 liveable  |  57..90 cold  |  >90 night side
```

### 🔴 How you SELECT it — two backends, auto-detected

`AlienWorldsFramework.cs` picks its UI at `[StaticConstructorOnStartup]`:

* **If `ferny.Worldbuilder` is ACTIVE** — the framework writes a Worldbuilder preset
  folder at runtime and you choose *"tidally locked world"* on **Worldbuilder's world
  preset screen**. The mod-settings radio buttons are **disabled** in this mode.
  (This is almost certainly what created the empty `…\Worldbuilder\` folder on this
  machine — the framework expecting a companion that is switched off.)
* **If Worldbuilder is INACTIVE — our current state** — choose it at
  **Mod Settings → "Alien Worlds Framework" → "Planet type for new worlds"**, a radio
  button, **before you create the world**.

⛔ It is **not** a dropdown on the Create World page and **not** a scenario setting. If
you are looking for it at worldgen you will not find it. Framework + Harmony are hard
`modDependencies`.

### ⚠️ It applies NO biome restriction — this is the trap

The mod leaves the framework's `<biomes>` and `<biomeConfigs>` **empty**, and
`PlanetTypeManager.cs` treats an empty list as "no restriction". So **vanilla BiomeWorkers
run unchanged against the rewritten temperature field** — which produces jungle and
savanna at ~64 °C on the day side. That is the top complaint on its Workshop page, and it
is a real problem for any world meant to read as a desert.

⇒ The temperature model is excellent and the biome placement is not curated. If we want a
desert planet we constrain biomes ourselves — `Mlie.ChooseBiomeCommonality` (ACTIVE) is
the blunt lever, and per-tile repainting from `jawa/world_tile_export` is the precise one.

### What else the mod changes, from the patches

* **`SunPositionPatch`** pins `dayOfYear = 0`, `dayPercent = 0.5` — the sun never moves.
  **There is no day/night cycle anywhere on the planet.**
* **`SunGlowPatch`** rotates the sun vector by the tile's LONGITUDE, so in-map light
  level is set by longitude. Day-side maps are permanently lit, night-side permanently
  dark. Plan solar power and growing light accordingly.
* **`OutdoorTemperaturePatch`** forces `includeDailyVariations = false` — **no day/night
  temperature swing**, anywhere.
* **`NoIslandPatch` + `SeaIceEdgesPatch`** push sea ice right to the world edge, and
  `ungeneratedPlanetPartsTexture` is `World/Biomes/IceSheetOcean` — the unrendered
  remainder of the planet reads as ice ocean rather than blank.
* `seasonalTempVariationCurve` is 15 / 15 / 5 across the same axis — mild seasons on the
  day side, almost none on the night side.
* `difficulty: 3`. Ships an Alpha Biomes compat patch
  (`Mods/sarg.alphabiomes/Patches/UngeneratedPlanetParts.xml`).
* Ships `Textures/TidallyLockedWorld/Worldbuilder/{Thumbnail,Flavor}.png` — i.e. it is
  **built to be presented through Worldbuilder**, which is currently disabled here.

### ⭐ Coverage: the mod tells you itself

Its own description: *"Generating at least 50% of the planet is recommended."* That is an
independent confirmation of the **0.5 coverage** choice — and it is not arbitrary: below
that you clip away the latitude range that gives the liveable ring its land area.

⚠️ **Known issues.** `Realistic Planets` also rewrites `WorldGenStep_Terrain`
temperature and would collide — not installed here, keep it that way. The author's own
TODO warns the 15° sun-tilt correction may drift after ~half an in-game year. Caravan
travel is untouched (no patch). Solar panels run permanently on the day side and never on
the night side, because sun *glow* is permanent even though `sunlightFactor` is 1.0.

⚠️ **It defines NO biomes of its own.** `Defs/` holds one `PlanetTypeDef` and nothing
else. Biome placement is still vanilla + whatever biome mods are loaded, re-scored
against the new temperature field. So a "terminator biome" is not something this mod
provides — if we want one it is ours to author.

---

## 8. 🔴 IN-GAME is a different, far richer debug surface than the world screen

Measured 2026-08-15 on a live colony (`programState: Playing`), against the same calls
that fail at `Page_SelectStartingSite`:

| | world screen | in game |
|---|---|---|
| `list_debug_action_children("Actions")` | **NRE, 0 children** | ✅ **139 children** |
| vanilla `Set biome...` / `Set landmark...` | ❌ absent | ✅ present |
| `get_game_info` | ❌ throws | ✅ works |

⇒ **Load a save and work from inside the game.** Everything the world screen refuses,
the in-game debug tree offers. This is the strongest argument for the
load-savegame-then-god-mode workflow over editing at world creation.

### The world-touching actions that exist in game (32 of the 139)

**Vanilla 1.6 — these do NOT appear at the world screen:**
`Set biome...` (**54** biome leaves) · `Set landmark...` (**113** landmark leaves) ·
`T: Clear Landmark` · **`Retroactively Add Landmarks To World`** ·
`Regenerate Map Features` · `Regen WorldGrid` · `Regen WorldReachability` ·
`T: Spawn World Object...` (**132** leaves, incl. `Settlement`, `AbandonedSettlement`,
`DestroyedSettlement`, `EscapeShip`, `Caravan`, `Ambush`) · `T: Spawn Random Faction Base`
· `T: Spawn Random Caravan` · `RegenerateFactionLeaders` ·
`Repair stale Lord/world-pawn ownership`

**From mods:** `Set biome (mod)...` / `Set landmark (mod)...` / `Clear Landmark (mod)`
(`Hali.ModifyLandingTile`) · **`Toggle Reveal World`** (`TheLastBulletBender.RWExploration`)
· `Get Map Information` / `Generate Custom Map Data` / `Get Custom Map Data Information`
(map-preview/landform family — attribution not verified) · `World noise visualizer` ·
`Run Map Generator...` · `Generate Map With Caves` · `Regenerate Current Map Stepped`

### 🔑 Which of these the BRIDGE can actually fire

**Targetless — callable right now, no mouse:**
`Retroactively Add Landmarks To World` · `Regenerate Map Features` · `Regen WorldGrid` ·
`Regen WorldReachability` · `RegenerateFactionLeaders` · `Toggle Reveal World` ·
`World noise visualizer`

**Still blocked — `T:`-prefixed world tools and the leaves under `Set biome...` /
`Set landmark...` arm a cursor and read `GenWorld.MouseTile`.** `execute_debug_action`
offers only `pawnId`/`x`/`z`/`thingId`, and `x`/`z` are MAP cells even in game. So §3's
wall stands on both screens: **enumeration and execution work; world-tile TARGETING does
not.** A companion tool taking a tile id is still the only fix.

⚠️ `Retroactively Add Landmarks To World` rewrites landmarks across the whole planet with
no confirmation and no undo. **Never fire it on a world anyone cares about without asking
first.**

---

## 9. ⚠️ A mod setting that gates on INITIALISATION will silently do nothing

Owner toggled **Disable Fog-of-War** in Rimworld Exploration Mode's settings and the map
stayed fogged. The setting was correct; it simply could not take effect.

**Why:** the mod builds fog as two *draw layers* — `WorldDrawLayer_Fog` and
`WorldDrawLayer_UngeneratedFog` — created when the world grid initialises. The giveaway is
in its own method names: `Grid_InitializeDrawLayersFromSave_RWE` and
`GridInitializeDrawLayersFresh_RWE`. `DisableFogOfWar` is read **at that moment**. Flipping
it mid-session changes a flag that nothing re-reads, so the already-built layer keeps
drawing.

**Two fixes, one of them free:**
* reload the save — the layers rebuild and read the new flag; or
* ⭐ `execute_debug_action("Actions\\Toggle Reveal World")` — **instant, no reload**, and
  verified live: the whole planet rendered immediately.

**Generalises to:** when a mod setting "does nothing", check whether it is read at
initialisation before calling it broken. Look for `Initialize`/`FromSave` in the
assembly's method names — `strings -a <dll> | grep -i init` is usually enough. And prefer
a debug action over a reload; a reload here costs a load, the action cost one call.

📌 Also useful: the in-game world **tile inspector prints lat/long directly**
(`39.40°N 4.97°E`). Free cross-check against `jawa/world_tile_export` once it deploys.
