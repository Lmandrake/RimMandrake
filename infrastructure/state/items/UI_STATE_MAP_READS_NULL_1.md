🔴 **CLOSED 2026-08-26 by seat CHECK — read this before the spec below.**
Evidence: `infrastructure/state/evidence/ui_state_and_camera_2026-08-26_CHECK.md`.

`rimworld/get_ui_state` has **no `currentMap` key at all** in the current build — absent, not
null — so the misreadable field the item was filed about no longer exists. The concern behind it
stands and now has an answer: **`rimworld/get_game_info` → `mapCount`** is the instrument
(`mapCount: 1` measured on a map carrying 72 pawns). ⛔ `get_ui_state.hasCurrentGame` is NOT a
substitute — it is true for a loaded game with no map. §12.4 of `ASHKARR_WORLD_DEFINITION.md` has
been corrected in place to name the right call.

---

## spec

`rimworld/get_ui_state` reports **`currentMap: None` on a map that plainly exists.**
Measured 2026-08-23 00:2x on a live dev quicktest:

```
rimworld/get_ui_state   ->  programState: Playing   currentMap: None   maps: None
jawa/list_pawns         ->  success, "8 pawn(s), 21 beyond the limit."
                            Jet | PlayerColony | Colonist
                            Minty | PlayerColony | Colonist
                            Pena | PlayerColony | Colonist
                            Sharkey | PlayerColony | BMT_Glowtail
```

29 pawns are standing on the map `currentMap` says is not there. `programState` is
correct; the map fields are not.

## Why this is worth an item rather than a shrug

🔴 **It is a NULL that reads as an answer.** `currentMap: None` is exactly the value a
caller uses to decide "no map exists yet" — and several things in this repo do:

- `ASHKARR_WORLD_DEFINITION.md` §12.4 requires the planet importer to **refuse if
  `Find.CurrentMap != null`**, because painting a planet underneath an instantiated map
  destroys that colony. A guard that
  asks the bridge instead of the engine would read `None` here and **proceed against a
  live map** — the precise thing the guard exists to prevent.
- Any wait-for-map loop of the shape `while st['currentMap'] is None` never exits, even
  though the map arrived. One was written during this session and had to be abandoned.

⚠️ **`programState: Playing` is NOT a substitute.** It was `Playing` here with the map
fields null, and it is `Playing` on the world screen before a map exists at all.

## What is NOT yet known

- Whether `currentMap` is null only when the camera has not settled on the map, or
  always on a bridge-started debug game, or always full stop. **One reading is not a
  population** — check it on a normally-started colony and on a loaded save before
  concluding anything about the cause.
- Whether the field is meant to be an index, a name or an object, and what it returns
  when it does work. Nobody in this session has seen it non-null.

⛔ **Do not "fix" this by making callers ask `jawa/list_pawns` instead.** A pawn census
is not a map existence test — a map with nothing on it is still a map, and the §12.4
guard must refuse that one too.

## verify

- On a live map, `rimworld/get_ui_state` returns a non-null `currentMap`, and it agrees
  with what the engine's own `Find.CurrentMap` holds.
- Re-measured on all three routes: a bridge-started debug game, a normally-started
  colony, and a loaded save. A row per route, not one reading generalised.

## criteria

A caller can tell "no map exists" from "a map exists and I cannot see it" using this
tool alone. Until then, anything guarding on map existence reads the engine, not the
bridge.

---

## 🔑 RESOLVED IN THE PART THAT MATTERED — 2026-08-23 10:3x

**There IS a correct instrument, and it is not this one.** `rimworld/get_game_info`
returns **`mapCount`**, and on a map holding 29 pawns it reads **`mapCount: 1`** while
`get_ui_state` on the same game still reads `currentMap: None`.

Confirmed on **two independent game states** — the original dev quicktest, and the
reloaded `rimbridge_save_20260823_002929` — so it is not a one-off of a bridge-started
game.

⇒ **Anything guarding on map existence must read `get_game_info.mapCount`, not
`get_ui_state.currentMap`.** That includes `ASHKARR_WORLD_DEFINITION.md` §12.4's
"refuse if a map is instantiated" rule, which was the whole reason this item was filed as
urgent. ⭐ `w9_run.py` already gets this right — its guard is `mapCount > 0`.

**What remains is cosmetic but still wrong:** `get_ui_state` reports `currentMap: None`
and `maps: None` on a game with one live map. A field that is null when the answer is
"one" is a wrong answer rather than a missing one, and it should either be populated or
removed. It is no longer blocking anything.

## ALMOST CERTAINLY A NON-BUG — CHECK, 2026-08-23 11:5x, game DOWN

🔑 **`currentMap` is not a field `get_ui_state` emits.** The original reading was a Python
`dict.get("currentMap")` on a key that was never in the response — the same shape of reading
as `st.get("banana")` returning None. Nothing in the tool is broken.

**The tool is upstream, not ours.** `get_ui_state` belongs to RimBridgeServer
(`brrainz.rimbridgeserver`), not to JawaBench. Its documented purpose is *"the current
RimWorld window stack and input state"* —
`vendor/mod_sources/RimBridgeServer-main/docs/tool-reference.md:579-583`. Upstream's own smoke
test asserts on `mainTabOpen` / `openMainTabId` / `openMainTabType`
(`Tests/RimBridgeServer.LiveSmoke/SmokeScenarioCatalog.cs:1176-1181`) and on no map field.
`get_game_info` has no map object either — its shape is `{status, ticksGame, mapCount,
selectedPawns}`, which is why `reload_check.py:116-119` already takes `mapCount` from there
and only `programState`/`hasCurrentGame` from `get_ui_state`.

⇒ The item's closing demand — *"a field that is null when the answer is one should either be
populated or removed"* — is about a field that does not exist.

**`Find.CurrentMap` was not the mechanism either.** `Find.cs:114` is
`Current.Game?.CurrentMap`; `Game.cs:118-127` returns null iff `currentMapIndex < 0` (default
`-1`, `Game.cs:17`). ⛔ **Opening the WORLD view does not null it** —
`MainButtonWorker_ToggleWorld.cs:16` only sets `wantedMode`, and the only non-load
`CurrentMap = null` in the entire decompile is `Game.cs:753`, the last map being removed.
The engine treats "maps exist, current is null" as a defect it repairs at load
(`Game.cs:596-600`).

**✅ The right guard, for anyone who needs one.** `rimbridge/wait_for_game_loaded`
(`docs/tool-reference.md:730-745`) returns a `state` carrying **`currentMapIndex`**, which is
`Game.currentMapIndex` verbatim — `-1` IS the engine's null. That, not `mapCount`, is the
true `Find.CurrentMap != null` test.

### ⚠️ Why this is "almost certainly" and not "settled"

RimBridgeServer ships **no C# source** — the vendored tree's `1.6/Assemblies` is empty and the
only binary is
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3727949765\1.6\Assemblies\RimBridgeServer.dll`.
The field list above was recovered by a literal-string read of that DLL. 🔴 **A byte scan can
prove a name is PRESENT; it can never prove one is ABSENT** — .NET keeps strings in metadata
blobs a scan never reaches. So the "there is no `currentMap` key" half rests on a scan plus
the docs plus the upstream test, not on a decompile.

### The one observation that closes this, next load — seconds, not a test

Call `rimworld/get_ui_state` and print **`sorted(resp.keys())` raw**, not `.get("currentMap")`.
If there is no `currentMap` key, this item is a non-bug and closes; if there IS one and it
reads null on a populated map, the original finding stands and nothing above applies.
