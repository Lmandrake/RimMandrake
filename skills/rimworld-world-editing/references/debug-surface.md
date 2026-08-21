# The debug surface, and init-gated settings

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
(`Hali.ModifyLandingTile`) · ~~`Toggle Reveal World`~~ (Exploration Mode — **REMOVED 2026-08-15**)
· `Get Map Information` / `Generate Custom Map Data` / `Get Custom Map Data Information`
(map-preview/landform family — attribution not verified) · `World noise visualizer` ·
`Run Map Generator...` · `Generate Map With Caves` · `Regenerate Current Map Stepped`

### 🔑 Which of these the BRIDGE can actually fire

**Targetless — callable right now, no mouse:**
`Retroactively Add Landmarks To World` · `Regenerate Map Features` · `Regen WorldGrid` ·
`Regen WorldReachability` · `RegenerateFactionLeaders` · `World noise visualizer`

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

⛔ **The mod this was learned on is GONE.** `TheLastBulletBender.RWExploration`
(Rimworld Exploration Mode) was **removed from the mod list 2026-08-15 by owner ruling**
— its fog wrecked the world-map view, and the planet must read as a world seen from
space. **Do not re-enable it and do not reach for `Actions\Toggle Reveal World`; neither
exists any more.** The lesson below is general and outlives the mod.

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
* ⭐ a debug action that resets the thing directly, if the mod ships one. The removed
  Exploration Mode had `Actions\\Toggle Reveal World`, which fixed it in ONE call where a
  reload would have cost a whole load. **Always look for that action before reloading.**

**Generalises to:** when a mod setting "does nothing", check whether it is read at
initialisation before calling it broken. Look for `Initialize`/`FromSave` in the
assembly's method names — `python3 src/RimMandrake/Utils/ilprobe/meta.py <ClassName>`
prints every method on a type (repoint `DLL` in a copy of `meta_core.py` for a mod's own
dll). ⛔ Not `strings -a <dll> | grep -i init`: the blind-scan hook refuses it, and a byte
scan of a .NET assembly sees a minority of names, so finding nothing tells you nothing.
And prefer a debug action over a reload; a reload here costs a load, the action cost one
call.

📌 Also useful: the in-game world **tile inspector prints lat/long directly**
(`39.40°N 4.97°E`). Free cross-check against `jawa/world_tile_export` once it deploys.

---

## ⛔ You cannot reach the WORLD VIEW from a loaded map — measured 2026-08-16

Once `rimworld/load_game_ready` puts you on a colony map, **nothing in the bridge can
switch to the planet view.** Every route was tried:

| route | result |
|---|---|
| `open_main_tab` `mainTabId: "World"` | ❌ **NullReferenceException** |
| `open_main_tab` `mainTabId: "main-tab:World"` | ❌ same NRE |
| `click_ui_target` on `main-tab:World` | ❌ *"is not a UI element target"* |
| `click_screen_target` on it | ❌ *"Main-tab targets are descriptive only"* |
| `open_window_by_type` `MainTabWindow_World` / `WorldInterface` | ❌ no such Window type |

🔑 **The NRE is the diagnosis, not a bug to route around.** RimWorld's World button is a
`MainButtonDef` whose **`TabWindow` is null** — it toggles the world camera instead of
opening a window — so a generic open-the-tab call dereferences null. There is no window
to open and no clickable target, because the bottom bar is drawn immediate-mode.

⚠️ **There is no arbitrary-screen-coordinate click anywhere in the bridge.** `click_cell`
is map-space, the other two take target ids.

⇒ **CHECK cannot self-review any world-map change once a game is loaded.** A screenshot
taken here shows the colony, not the planet. Either a human presses World, or the
companion gains a verb — `MainButtonWorker_ToggleWorld.Activate()` /
`CameraJump.TryShowWorld()` is the call — which needs a game-down window to deploy.
📌 Loading a save at the **main menu** still reaches `Page_SelectStartingSite`, where the
world IS on screen; it is only the map-loaded state that traps you.
