> 🔴 **CORRECTED 2026-08-23 by the owner — read `PAINT_UNDER_MAP_DESTROYS_GAME_1` before
> acting on anything below about painting under a live map.** His words: *"painting under
> a player colony is actually fine to do... it just destroys the player colony. So you must
> create a new one... let's please not record that we cannot paint into an existing game."*
> ⇒ Losing the COLONY is real and expected. "The game becomes unstable / cannot make a new
> colony / the UI breaks" is ONE unreproduced session and he believes it is false. ⛔ Do not
> cite this file as evidence that painting into an existing game is impossible.

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
  is what destroyed the save twice (`PAINT_UNDER_MAP_DESTROYS_GAME_1`). A guard that
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
