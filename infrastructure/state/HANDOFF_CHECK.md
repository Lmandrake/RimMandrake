# CHECK handoff — 2026-08-21, session ended for a context-losing restart

Everything below is measured this session on the live game, not inferred.
All work is committed AND pushed; `git log origin/main..HEAD` is empty.

## 🔴 Read this first: the thing the board was wrong about

**The 578-stack load blocker is GONE.** `LOADS_ARE_BLOCKED_NEEDS_YOU_1` said no save loads
on the owner's full list. It does now: `thereallemon.factioncontrol` is absent from
`ModsConfig.xml`, a world generated, and the game is up. `game.json` had been sitting at
`DOWN` carrying that stale blocker note all session; corrected.

⇒ **Do not re-derive this. Do not plan around a load blocker.**

## Live state as of ~11:00 PDT

| | |
|---|---|
| game | **UP, PAUSED at ticksGame 3250** |
| mods | **583 active** (`grep -o "<li>" ModsConfig.xml \| wc -l` — the `<li>`s are on ONE line, so `grep -c` returns 6 and is a trap) |
| bridge | answers, **244 tools**, held by CHECK in the ledger (`rimflow bridge take` already done) |
| world | `Ash'karr`, seed **`grasshopper`**, 21,872 tiles, coverage 1.0, 21 factions |
| keeper? | **NO.** Owner: *"Use the world for testing purposes. It's still not keeper, but you are free to clear testing items ad nauseum."* |
| map | scratch colony, one colonist (Zozo), 16 spawned vehicles, 200 RawPotatoes at (142,141) |

⛔ **WSL cannot reach the bridge** — RimBridge binds Windows loopback and WSL2 is NAT.
Every call goes through `python.exe`, never `python3`:

    python.exe src/RimMandrake/Utils/rimbridge_client.py --call <tool> --json '<args>' \
               --timeout 130 --yes-i-know-this-is-live

A helper that wraps this is at `/tmp/claude-1000/br.py` — **scratch, will be gone after a
reboot.** Rewrite it, it is ten lines.

## What the owner said, and what is next

🔴 **"We are changing how we store and access dump files to avoid problems."** That is the
next topic. **Nothing was started on it.** Ask him what the new scheme is before touching
`refresh.py`, the def dump, or anything that reads it.

🔴 **"Remove all Neolithic vehicle testing from the queue… release those items completely
and mark done."** Done — see below. ⛔ Do not reopen any of it.

## Closed this session

| item | result |
|---|---|
| `INHABITED_ACTION_BRIDGE_CONFIRM_1` | PASS `1a54377` |
| `WORLD_PAINT_IS_PRESENT_1` | PASS `a02cb3c` |
| `VEHICLE_RESKIN_LIVE_LOOK_1` | partial, closed `6d96714` |
| `VEHICLE_FUEL_LIVE_PROOF_1` | partial, closed `3777935` |
| `THE_SCALD_LOST_ITS_WATER_1` | run recorded, **left open, `needs: owner`** |

Evidence for all of them is in `observed/bridge/`, one file per run.

## Open, and it needs the OWNER not a seat

**`THE_SCALD_LOST_ITS_WATER_1`.** Option 2 was already in force in the frozen CSV
(`bd5dad0`) before the item deliberated it, and it is now measured live: water
6.71% → **8.14%**, 2 bodies → 3, `lakesAboveSeaLevel` 312 → **0**. The one remaining
criterion is *the owner looks at the relief around the Scald and does not name it a defect*.
No seat can discharge that.

## Filed for BUILD

**`LINT_EXCLUDE_LAKE_SUBMERGED_1`** (`infrastructure/state/items/`, needs offline, companion
change ⇒ game DOWN). `JawaBenchWorldTools.cs:2385` leaves `Lake` out of `biomeIsWater`, so
line 2392's `!biomeIsWater` sweeps the 312-tile Scald at −30 into `landBiomeSubmerged`.
Sinking the Scald moved 312 findings from the check that scores zero into the one that
scores. The comment right above 2385 fixed the *positive*-elevation direction on
2026-08-20 and never came back for this one.

## 🪤 Four bridge traps found the hard way — none of these is documented anywhere else

1. **`rimworld/search_debug_actions` TIMES OUT** on this stack — 30s and again at 150s, with
   params checked against its own schema, while the bridge was healthy either side.
   `rimworld/list_debug_action_children` walks the same 646 nodes in seconds. Use the walk.
   (`SEARCH_DEBUG_ACTIONS_TIMES_OUT_1`)
2. **`rimworld/screenshot_cell_rect` captures the SCREEN, including whatever window is on
   top.** It returned `success: true` four times for four different cell rects and wrote
   four **byte-identical** PNGs of the open Debug log. Check `rimworld/get_ui_state`
   (`topWindowType`) and `rimworld/close_window` FIRST, every time.
   (`SCREENSHOT_CAPTURES_OPEN_WINDOW_1`)
3. **`visible: false` on a debug node is not "absent".** `Actions` has **childCount 646 but
   visibleChildCount 146**; `includeHidden` defaults to false on every discovery tool. And
   `category` on a `[DebugAction]` is metadata on a LEAF, not a level in the tree — all
   seven `Inhabited` actions are direct children of `Actions`. A node declared
   `AllowedGameStates.PlayingOnMap` hides itself while the session is on the WORLD view;
   `jawa/world_view {"show":false}` returns to the map and it reappears.
4. **No bridge route reaches a `VehiclePawn`'s UI or its comps.** `rimworld/select_pawn`
   refuses one by id and by name (*"Could not find player-controlled colonist"*) even when
   `set_pawn_faction` confirms it is already PlayerColony; `jawa/get_defs` flattens
   `components` to `["VehicleComponentProperties" × 5]`; no tool anywhere mentions fuel; and
   `rimbridge/run_lua` only orchestrates existing capabilities, it does not reflect into
   game objects. (`VEHICLE_HEALTH_TAB_UNREACHABLE_1`, `VEHICLE_FUEL_LEVEL_UNREADABLE_1` —
   both recorded, both released with the vehicle work.)

## The instrument that settled the world question, worth reusing

⛔ Not a grep of the `.rws`, and **not a biome histogram either** — a histogram agrees on a
total while disagreeing tile by tile. Use **`jawa/world_tile_validate`**, which compares the
live world to a CSV row by row and reads RAW fields, never the lazily-cached properties:

    jawa/world_tile_import  {"path":"D:\\...\\ASHKARR_WORLDMAP_tiles.csv","apply":true,"expectTiles":21872}
    jawa/world_commit
    jawa/world_tile_validate {"path":"D:\\...\\ASHKARR_WORLDMAP_tiles.csv","maxRows":0}

That round trip is proven: **21,872 / 21,872, mismatched 0**, in about a second of engine
time. The whole planet reaches a running game in three calls.

🔑 **And the lesson underneath it.** The world looked unpainted — `AB_OcularForest` read 0
where the spec said 3, `rain_mm 0` read 0 rows where the spec said 20,113 — and both of the
spec's own signatures said "bare regeneration, say so loudly". They were right about the
fact and **wrong about the cause**. The world was three CSV commits behind: the last save is
08:25, the three hand edits land at 08:34, 08:59, 09:03. **A regeneration disagrees
everywhere; a stale world disagrees only on the edits.** Count the fields before raising an
alarm.
