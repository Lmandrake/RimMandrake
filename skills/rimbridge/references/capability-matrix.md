# RimBridge capability matrix

Verified against a live 3-mod game (Harmony + Core + RimBridgeServer 2.1.0),
2026-08-11/12. "Works" means **observed changing the world**, not merely
returning `success: true`.

## Works

| capability | call | evidence |
|---|---|---|
| status | `rimbridge/get_bridge_status` | programState, paused, automationReady |
| game info | `rimworld/get_game_info` | ticksGame, mapCount |
| roster | `rimworld/list_colonists` | pawnId, position, job, drafted, downed, dead |
| select | `rimworld/select_pawn` | reflected in later calls |
| spawn thing | `rimworld/spawn_thing` | thingId, confirmed by get_cell_info |
| set material | `T: Set Stuff...` + thingId | steel to **plasteel**, stuffDefName changed |
| set quality | `T: Set Quality...` + thingId | normal to **legendary**, hitPoints 810 |
| spawn pawn | `Spawn Pawn...` + x/z | 68 races placed, 0 failures |
| wear apparel | `Wear apparel (selected)...` | Apparel_PowerArmor in the parsed save |
| strip | `Remove all apparel` | wornApparel empty in the save |
| kill a **colonist** | `T: Damage To Death` + pawnId | pawn gone from roster. ⚠️ colonists only — `ResolvePawn` refuses hostiles |
| build | `apply_architect_designator` | 9x9 room, then a 13x11 furnished room |
| validate placement | same, `dryRun: true` | rejects illegal footprints |
| site finding | `flood_fill_cells` + designatorId | footprint, anchor, reachability |
| clear vegetation | lay a **floor rectangle** | interior wiped clean |
| **damage anything, incl. hostiles** | `Actions\Explosion...\<DamageDef>` + `x`/`z` | `ToolMap`, so no pawn resolution. EMP on a droid gave `stunTicksLeft 1386`, `stunFromEMP True` |
| resolve an explosion while paused | `step_game_ticks` | advances it **without unpausing** — no raid risk |
| exact time | `step_game_ticks` | 130 to 190 exactly |
| wall-clock time | `play_for` | returned success:false once, unexplained |
| screenshot | `take_screenshot` | absolute path, readable by the agent |
| god mode | `set_god_mode` | placement becomes instant |
| save | `save_game` | 14.9 MB rws; **ignores fileName** |

### Added by our own companion, `JawaBench.BridgeTools`

These are not RimBridge tools — they exist because we wrote them, and they load
only at RimBridgeServer startup.

⚠️ **The ms figures in this first table were measured at 568 mods on a real
21-colonist colony.** Latency depends on how busy the main thread is, not on the
mod count — re-measured at 573 on a quiet quicktest map, reads were **3× faster**
(16.7 → 5.8 ms). Treat every number here as carrying its COLONY, not its tier.
See traps.md, "The 16.7 ms latency floor is workload".

| capability | call | evidence |
|---|---|---|
| paint natural terrain | `jawa/set_terrain` | grid read back per cell; median 16.7 ms on both 3-mod and 568-mod tiers |
| paint under-terrain | `jawa/set_terrain` `layer=under` | same tool, same read-back |
| paint a whole formation | `jawa/set_terrain_batch` | 421 cells / 124 rects in ONE call: **14.0 ms**, vs 1,611 ms per-rect — **115×**. `failedVerify=0` |
| capture a whole region | `jawa/get_terrain_batch` | 421 cells in ONE call: **17.5 ms**, vs 6,086 ms per-cell — **348×**. Answers in the paint tool's own grammar, so a capture replays as a restore |
| exact terrain revert | capture + repaint | 2,601 cells verified back, **0 wrong**, one call each way |
| clear vegetation | paint a terrain the plant cannot grow on | Sand / PackedDirt / rock / water destroy grass; **Gravel does not**; same-terrain is a no-op |

⚠️ **Restoring terrain is not undoing the paint** — destroyed plants do not come
back. Terrain is exactly restorable; the paint is not reversible. On a colony
that matters the save is the undo.

### ✅ PROVEN LIVE — all 16, the roof pair included

**Latest run: 2026-08-12 on the 574-mod stack — 23 passed, 0 failed, 2 skipped**
(the 2 are opt-in: `--letter` writes to the player's pane, `--pawns` spawns).
Census read **16 of 16**, 141 tools on the bridge overall. The earlier 20/20 run
at 573 proved the first 14; this one adds `jawa/set_roof_batch` and
`jawa/get_roof_batch`, which had never run.

Run on a **dev quicktest colony** started through the bridge itself
(`rimworld/start_debug_game_ready`), so nothing was proven against a colony that
matters. Harness: `src/RimMandrake/bridgetools/prove_new_tools.py`.

⚠️ **`start_debug_game_ready` exceeds the 30 s client timeout and succeeds
anyway** — the response is merely late. Do not retry (the connection is desynced)
and do not re-issue it (you get a second map). Fresh connection, then poll
`jawa/list_pawns` until it stops saying *"No current map"*. Full entry in
`traps.md`.

| capability | call | evidence |
|---|---|---|
| spawn many things | `jawa/spawn_batch` | 3 ops in one call = 3 spawned; `count` sets **stackCount** (`Steel:x,z,50` → one thing labelled `Steel x50`), NOT a rect fill |
| destroy many things | `jawa/destroy_batch` | 9 plants destroyed, `pawnsSkipped=0`; params are **`rects`/`categories`** |
| enumerate every pawn | `jawa/list_pawns` | **35 on map vs 3 colonists** — hostiles and animals included. `includeHealth` returns the full hediff list |
| plant vegetation | `jawa/set_plants` | `planted=9 cleared=0 rejected=0`, with `rejectionReasons` per refusal |
| damage **hostiles** | `jawa/damage` | reached a hostile the stock bridge cannot resolve; hediffs 8→10. ⚠️ `amount` is a request — 400 landed as 32 |
| read a **resolved** def | `jawa/get_def` | 10 `statBases` for a def the offline dump shows bare |
| read tick-time logs | `jawa/drain_log` | `errorsOnly` filtered 149 of 200 |
| spawn a **hostile** pawn | `jawa/spawn_pawn` | genuinely hostile, faction Insect, `isPlayer:false` — the debug menu always spawns player-side |
| fire an incident | `jawa/fire_incident` | `dryRun` returned `canFireNow=true` and **`fired=false`** |
| write to the letter pane | `jawa/send_letter` | letters visible in the notification pane in-screenshot |
| dirty the mesh alone | `jawa/refresh_rect` | ⚠️ **data half only** — accepts a rect, refuses a malformed one. The VISIBLE half is unproven and the obvious test cannot work: moving the camera to photograph a stale mesh repaints it. See traps.md |

### ⏳ BUILT, COMPILES, NEVER RUN — four more, as of 2026-08-13

**Nothing below has been driven in a live game.** They are in the repo artifact,
0 errors 0 warnings, and that is the whole claim. `jawa/list_factions` was
deployed at **10:05 on 2026-08-13**, one minute *after* the last session's
`Player.log` stopped writing, so even the deployed one has never registered in a
running game. The other three were written offline the same day with the game
down. Verified against `Assembly-CSharp.dll` with `src/RimMandrake/Utils/ilprobe`,
not from memory.

| capability | call | what would decide it |
|---|---|---|
| enumerate **every** faction | `jawa/list_factions` | `countAllIncludingHidden` > `countReturned` with `includeHidden` false. The visible subset once read **34** against a true **54** |
| turn a pawn and hold it | `jawa/set_pawn_rotation` | `applied: true` from a read-back of `pawn.Rotation`, `locked: true`, and a **second** turn while locked still applying — `Thing.set_Rotation` returns silently on a locked pawn, so a wrong clear→set→lock order is a silent no-op |
| restyle a pawn | `jawa/set_pawn_style` | the requested `HairDef` reads back off `pawn.story` **and** the pawn redraws — `Notify_StyleItemChanged()` is what dirties the graphics |
| convert a pawn's xenotype | `jawa/set_pawn_xenotype` | `pawn.genes.Xenotype` reads back as the def asked for and is **not Baseliner** — `get_Xenotype` returns `XenotypeDefOf.Baseliner` for a pawn that was never converted, so Baseliner cannot distinguish success from a no-op |
| force a xenotype at spawn | `jawa/spawn_pawn` `xenotype=` | the row's `xenotypeApplied: true` — `PawnGenerationRequest.ForcedXenotype` returns first out of `GetXenotypeForGeneratedPawn` (IL_0000), ahead of every chance roll |

⚠️ **`jawa/spawn_pawn` used to report `success: true` for a batch in which every
pawn threw during generation** — rows are added for failures too and `success`
was `rows.Count > 0`. Fixed 2026-08-13; the response now carries `spawnedCount`
and `failedCount`, and `success` counts only pawns that really landed.

🔴 **`jawa/fire_incident` remains a different class from everything else here.**
Proven only through `dryRun`. Firing one for real is a deliberate act; the owner
ruled on 2026-08-12 that the tool ships, and it stays behind the `--gm`
compile-time flag so that is reversible in one shutdown window.

## Does not work

| capability | call | evidence |
|---|---|---|
| graduated damage | `Apply damage...` | 45 applications, 0 injuries — **inert through `pawnName`**, and hostiles are unreachable by pawn anyway. Use `jawa/damage`, which is proven against hostiles (2026-08-12), or `Actions\Explosion...` |
| paint terrain via vanilla | `Set terrain (rect)` | success, terrain unchanged. Drag tool. **Superseded — use the companion** |
| destroy directly | `Clear area (rect)` | success, plant survived. Drag tool. **superseded by `jawa/destroy_batch`**, proven 2026-08-12 |
| synthetic drag | `drag_cell` | timeout — PROVISIONAL, mouse interference |
| spawn with material | `spawn_thing` | no stuff parameter; fix on the next call |
| **bounded discovery** | `search_debug_actions` q+limit | ⛔ **DANGEROUS.** The old "12 of 119, truncated" evidence is from the **3-mod** tier. On 568 it livelocked the game and cost a cold reload — `limit` bounds the response, not the search. Never call it on the full stack |

## Not yet explored

Zones and areas, mod settings read/write, UI targeting and clicking, camera
beyond jump/zoom/frame, saves beyond save_game, language, `dpa_*`, `run_script`
versus `run_lua`, companion SDK tools.

_(Letters and alerts left this list on 2026-08-12 — `jawa/send_letter` is
deployed and proven.)_

## The Lua front-end is a lowered DSL

`rimbridge/run_lua` describes itself as a small Lua-shaped front-end over the
shared script runner, **not general-purpose Lua**. Call `get_lua_reference`
before writing any.

- `local` is required before assignment.
- Only `rb.call`, `rb.poll`, `rb.print`, `rb.assert`, `rb.fail`, `print`, `ipairs`.
- **Static indexes only** — `names[1]` is fine, **`names[i]` is rejected in v1**.
- Host calls only as a statement or the sole right-hand side.
- Use `compile_lua` to inspect the lowering before executing mutations.

Batch from the client instead of looping in Lua.
