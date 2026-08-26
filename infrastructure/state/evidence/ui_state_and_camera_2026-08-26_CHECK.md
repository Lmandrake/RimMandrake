# UI_STATE_MAP_READS_NULL_1 and CAMERA_CANNOT_AIM_AT_ANIMALS_1 — both settled live

2026-08-26, seat CHECK, full 582-mod list, `game_loaded`, one map, 72 pawns, `ticksGame 1174`.

## UI_STATE_MAP_READS_NULL_1 — the dangerous NULL is GONE, but read the right instrument

`rimworld/get_ui_state` no longer has a `currentMap` key **at all**. Its full top-level set is:

```
anySearchWidgetFocused anyWindowAbsorbingAllInput currentWindowGetsInput floatMenuOpen
focusedWindowTitle focusedWindowType hasCurrentGame inEntryScene mainTab mainTabOpen
mouseObscuredNow nonImmediateDialogWindowOpen openMainTabId openMainTabLabel
openMainTabType programState success topWindowTitle topWindowType windowCount windows
windowsForcePause windowsPreventCameraMotion windowsPreventSave
```

`currentMap`, `maps` and `mapCount` are **absent**, not null. ⇒ The specific hazard the item
was filed about — a caller reading `currentMap: None` and concluding "no map exists" — cannot
happen through this tool any more, because there is no field to misread.

🔑 **The instrument that answers "is there a live map" is `rimworld/get_game_info`.** Measured
on the same map in the same second: `{"status":"game_loaded","ticksGame":1174,"mapCount":1}`,
while `jawa/list_pawns` returned **72** pawns. `mapCount` is correct.

⇒ **`ASHKARR_WORLD_DEFINITION.md` §12.4's `Find.CurrentMap != null` guard must ask
`get_game_info.mapCount`, never `get_ui_state`.** `get_ui_state.hasCurrentGame` is `true` for a
loaded GAME and says nothing about a MAP — it would pass on the world-map screen with no map
instantiated.

## CAMERA_CANNOT_AIM_AT_ANIMALS_1 — FALSIFIED. It aims at animals fine.

The remaining half of this item ("`jump_camera_to_pawn` succeeds for a colonist and fails for
an animal, by name or by id") is **wrong on both halves**, and each was a different mistake.

**By name — it was AMBIGUITY, not species.** The animal originally tested was a `Qormot`, and
this map holds three of them. The tool says so:

```
pawnName=Qormot  -> success=False  "Ambiguous current-map pawn name 'Qormot'. Matches: qormot, qormot, qor…"
```

Uniquely-named animals aim immediately:

```
pawnName=Loth-cat        -> success=True
pawnName=Geralinura      -> success=True
pawnName=Fungal ferret   -> success=True
```

**By id — it is an ID-SPACE MISMATCH, and it hits humans exactly as hard.**
`jawa/list_pawns` / `jawa/pawn_get` return `Human335585`, `Qormot62098`.
`rimworld/jump_camera_to_pawn` wants the `rimworld/list_colonists` form, `Thing_Human922`.

```
pawnId=Qormot62098        -> False      pawnId=Thing_Qormot62098        -> True
pawnId=Qormot62099        -> False      pawnId=Thing_Qormot62099        -> True
pawnId=Human335585        -> False      pawnId=Thing_Human335585        -> True
pawnId=Human335595        -> False      pawnId=Thing_Human335595        -> True
```

🔑 **The conversion is `"Thing_" + id`.** With it, an ambiguously-named animal is addressable:
`Thing_Qormot62098 -> success=True`, followed by a successful `rimworld/take_screenshot`.

⚠️ **`rimworld/list_colonists` lists COLONISTS only** — 3 rows on this map against 72 pawns —
so an animal will never appear there. That is why the id space looked closed to animals. It is
not; the prefix is the whole of it.

**Also standing, from the item's own earlier correction:** `screenshot_cell_rect` at the
animal's `jawa/pawn_get` position works and wrote
`…\Screenshots\CHECK_animal_2026-08-26__cell_rect.png`. So there were always two working routes.
