# RimBridge traps: debug actions, designators, dialogs and clicks

Part of the trap catalogue indexed in [../traps.md](../traps.md); its first law and admission test are there. Append a new trap to the topic file it belongs to.

## An armed architect designator swallows every later click, and nothing on the bridge disarms it
**Symptom:** after `select_architect_designator` + `click_cell`, all subsequent `click_cell` calls return `success: true` and select nothing — `list_selected_gizmos` returns `[]` forever, so no inspect panel can be read and no gizmo can be fired. Screenshots show the designator's "Shapes" palette still open with its refusal message pinned top-left.
**Cause:** the designator stays armed and consumes map clicks as designation attempts rather than selections. It is a *mode*, not a one-shot.
**Fix — none found from the bridge.** All of these were tried and all reported success while changing nothing: `press_cancel` ("Dispatched semantic 'cancel'… UI state did not change"), `right_click_cell` on empty ground, `clear_selection`, `close_context_menu`, `close_main_tab` ("No RimWorld main tab is currently open"), and `select_architect_designator` with a null id (errors). `get_designator_state` returned nothing useful. The owner clicking once in game clears it.
**Recurs when:** any use of `select_architect_designator`. ⚠️ **Treat arming a designator as a one-way door for the rest of your bridge session** — do every selection-based read you need FIRST, then designate last. Worth a companion tool that calls `Find.DesignatorManager.Deselect()` directly.

## A jammed UI does NOT block the companion route
**Symptom:** with an architect designator armed, every `click_cell` selects nothing and `list_selected_gizmos` returns `[]` — the click-driven route is dead for the session.
**Cause/scope:** the jam is a UI *mode*. It only affects click-and-select.
**Fix — work around it, do not wait it out.** `jawa/spawn_pawn` places by coordinate, `jawa/set_pawn_rotation` and `jawa/set_pawn_style` act by `pawnId`, `jump_camera_to_cell` and `take_screenshot` need no selection at all. **A full spawn-rotate-photograph pass runs fine with the UI jammed** — measured by a retired seat, four spawns and screenshots, designator still armed throughout. Only inspect panels and gizmos are lost.
**Recurs when:** any session that has touched `select_architect_designator`.

## 🔴 `search_debug_actions` walks the whole tree and FROZE the game — twice
**Symptom:** two `rimworld/search_debug_actions` calls each hung past a 120 s client timeout; the owner reported *"game appears frozen"*, then *"game is back"*. The answers eventually arrived and were worthless — six matches for "goodwill", all one `QuestPart` test entry.
**Cause:** it *"searches the full RimWorld debug-action tree globally by path, label, category and source metadata"* — with ~575 mods that tree is enormous, and `limit` caps the RESULT, not the WALK. This is the same enumeration livelock `SKILL.md` §4 forbids, arriving through a tool whose name sounds like a cheap lookup.
**Fix:** do not use it to answer *"does a debug action for X exist"*. Decide that from the engine instead — `ilprobe` on the type that would own the action — or accept the gap and build a companion tool. If it must be run, expect a stall and never fire a second one while the first is outstanding.
**Recurs when:** any global search tool on this bridge. ⚠️ **Generalises: `limit` bounds the answer, not the work.** A parameter that looks like a cost control is often only a truncation control, and the difference is invisible until the game stops rendering. Cost a real freeze 2026-08-14, on a seat that had this trap in its own file.

## ⚠️ `rimworld/search_debug_actions` timed out at 30 s even on a 13-mod list

The documented debug-discovery hang is **not** only a heavy-modlist problem. Do not call
the four `*_debug_action*` discovery tools as if they were reads.

## `Actions\Spawn Pawn...` reports success and places nobody on a blocked cell

CHECK, 2026-08-20. A 69-race lineup reported `ok=69 fail=0`; the map held **64**.
`execute_debug_action` returns `success: true` whether or not the pawn lands, so
five kinds — Chiss, Gamorrean, Herglic, Kaleesh, Kaminoan — vanished without a
word. Nothing was wrong with those defs: each spawned first try when given a free
cell, so the cause is the CELL, not the kind.

**Count what arrived, never what the spawner claimed.** `jawa/list_pawns` grouped by
`kindDef` and diffed against the requested list names the missing ones in one call.
Generalises to every `spawn`-family debug action.

## `jawa/clear_ui` defaults do NOT close an open info card

Same session, and it cost a screenshot: `clear_ui` with its defaults reported
`deselected 0 thing(s)` and `get_game_info` showed `selectedPawns: []`, yet the shot
came back with a full character card — Bio/Inventory/Health tabs — covering the frame.
`devWindows` covers `Window_Dev` descendants and `clearSelection` covers the bottom-left
pane; the info card is neither. **`{"all": true}` closes it.** Read back the pixels, not
the deselect count.

## `rimworld/search_debug_actions` times out; the walk it exists to replace does not

Its own description says it exists *"so callers do not need to walk one subtree at a time"*.
On this stack it timed out at 30s and again at 150s, with params verified against its schema,
while `jawa/map_zones` answered in seconds either side. `rimworld/list_debug_action_children`
walked the same **646** nodes in seconds. **Walk it. Do not wait on the search.**

## `visible: false` on a debug node is not "absent" — and `category` is not a tree level

Two separate traps that compound into one wrong conclusion:

- `Actions` reports **childCount 646, visibleChildCount 146.** `includeHidden` defaults to
  **false** on every discovery tool, so 500 children simply do not appear and a hidden node
  is indistinguishable from a missing one. A report of "146 children" is a report of the
  visible count.
- **`category` on a `[DebugAction]` is metadata on a LEAF, not a node.** All seven
  `Inhabited` actions are DIRECT children of `Actions`; there is no `Actions\Inhabited`
  node to descend into. Looking for one and not finding it proves nothing.

And the reason a node hides is usually boring: `AllowedGameStates.PlayingOnMap` evaluates
false while the session is on the **world view**. `jawa/world_view {"show": false}` returns
to the map and the node reappears with `supported: true`. Check the view before the def.

## 🔴 `rimworld/search_debug_actions` WEDGES the bridge on a full mod list

Measured 2026-08-26, seat CHECK, **582 active mods**, one map, game paused.

```
rimworld/search_debug_actions {"query": "generate map", "limit": 10}
  -> timed out after 30s
  -> every subsequent bridge call then timed out for ~11 MINUTES (measured: 04:07:30 -> 04:18:0x,
     four probe cycles at 45s each plus one 100s ping, all timing out, then a clean answer)
  -> RimWorldWin64.exe alive throughout, growing 7.12 -> 7.21 GB while it walked
```

🔑 **A `limit` on the RESULT does not limit the WORK.** The tool walks the whole dev-menu surface
before it filters, and on a 582-mod list that surface is enormous — §4 measures 1,119 matches for
"apparel" on a *three-mod* list. The call runs on the game's main thread, so **every other bridge
call queues behind it** and the bridge reads as wedged (stuck, not crashed; it frees when the call
finishes).

⛔ **Do not call it on a full mod list**, and do not assume a narrow `query` makes it cheap — the
query is applied after the walk. ✅ On the 13-mod minimal list it is affordable; that is where
debug-action work belongs.

⚠️ **If you have already fired it:** do not reconnect in a tight loop. Wait, with a long client
timeout (`RimBridge(..., timeout=120)`), and check `tasklist.exe | grep -i rimworld` to confirm the
process is alive rather than assuming a crash. The §4 warning that enumerating debug actions
"destroyed a 568-mod game" is the same failure at a larger scale.

## 🔑 A Dialog_NodeTree can absorb ALL input while ignoring its OWN buttons
BENCH, 2026-08-29, live with the owner. A faction comms offer (Dialog_NodeTree) sat
focused with `anyWindowAbsorbingAllInput: true` but `currentWindowGetsInput: false` —
so every map click died AND the owner's real mouse clicks on the dialog's own
Accept/Reject were ignored. The debug log drawn on top was a red herring; closing it
changed nothing. The route out, no restart: `rimworld/get_ui_state` (shows those two
flags and the window stack), `rimworld/get_ui_layout` (every button with a `targetId`
and its label — it read the whole offer text too), then
`rimworld/click_ui_target {"targetId": ...}` — which activated 'Reject' cleanly even
though the window was ignoring the mouse. Verify on `get_ui_state` afterwards:
`anyWindowAbsorbingAllInput` back to false is the independent read.
**Generalises to:** "the game ignores my clicks" is a WINDOW-STACK read, not a restart.
get_ui_state first; click_ui_target goes through the UI event system, not the mouse,
so it works where the physical cursor cannot.

## `select_pawn` and every `ToolMapForPawns` debug action require `IsColonist` — a bridge-spawned pawn, even faction PlayerColony, does not qualify

The vehicle case above ("Nothing reaches a `VehiclePawn`'s UI") already hit this same gate
in a narrower form and attributed it (correctly) to "filters on colonists". This entry
confirms the mechanism generalizes past vehicles to ordinary bridge-spawned humanlike pawns.

Measured 2026-08-30. Spawned a `DW_OuterRim_GNKDroid` via `jawa/spawn_pawn` with
`faction: "PlayerColony"` — the response showed `faction: PlayerColony, hostile:
False`. `rimworld/select_pawn {pawnId: <id>}` still refused: *"Could not find
player-controlled colonist id"*. `Actions\Add Hediff...\Restraining bolt`
(`actionType: ToolMapForPawns`) then reported `success: true` with an empty
`effects.logs` and changed nothing — `jawa/pawn_get` afterward showed no new
hediff at all, an old backstory scar unrelated to the call. Same silent
no-op on `Actions\Add Prisoner` (`actionType: Action`, acts on "current
selection" — which was nothing, since selection had already failed).

⇒ **`ResolvePawn`'s "player colonists only" restriction (§4) means literally
`Pawn.IsColonist`**, which tracks colony membership (join pipeline, `playerSettings`
being set, etc.), not merely `faction == PlayerColony`. A pawn dropped straight
into the faction via `spawn_thing`/`spawn_pawn`/a debug spawn is NOT a colonist
by this test, and every `ToolMapForPawns` action — `Add Hediff...`, `Add
Prisoner`, `T: Enslave`, `T: Turn into prisoner` and siblings — silently
no-ops on it exactly like it does on a hostile.

**Generalises to:** any test that needs to arrest, imprison, enslave, or hand-add
a hediff to a bridge-spawned NON-colonist pawn (a captured droid, a downed
rogue, anything not part of the starting colonist trio). `ToolMap` actions
targeting by `x`/`z` or `thingId` (e.g. `jawa/damage`) are unaffected — they
work on any target regardless of faction/colonist status, per §3's own
distinction. **Workaround, unproven:** none found this session; a real fix
would need either a genuine colonist-join path exposed on the bridge, or a
new `jawa/` tool that bypasses `ResolvePawn` for hediff-adding the way
`jawa/damage` already does for damage.


## ✅ ToolMap debug actions DO honour the bridge's x/z, even ones reading UI.MouseCell() (2026-09-02, BENCH)

`StructureInjectionsDebugActions` is registered `DebugActionType.ToolMap` and its body
calls `UI.MouseCell()` directly — no parameter plumbing. Passing `x`/`z` to
`rimworld/execute_debug_action` still placed it at exactly the named cell
(`origin=(60, 0, 60)` for `x:60, z:60`). So the bridge sets the cell the tool reads,
and a ToolMap action written for a human mouse needs no adaptation to be driven.
Confirmed twice, at two different cells, one of them 120 cells from the other.

## The debug menu's `Actions\Spawn Pawn...\<kindDef>` does not reliably spawn that kindDef — use `jawa/spawn_pawn`

Measured 2026-09-18, FOUNDRY, live campaign map, BAREHANDED_MELEE_FALLBACK_1's 5
undiagnosed kinds. Two separate calls to `execute_debug_action {"path":
"Actions\Spawn Pawn...\RUT_Jawa_Deepwater_Leader", "x":.., "z":..}` each returned
`success: true`, zero logs, and DID spawn a pawn at the named cell — but the
resulting pawn's `kindDef` (confirmed independently via both `jawa/list_pawns` and
`jawa/pawn_get`) was **`Colonist`**, not the requested kind, and one of the two had
Shooting AND Melee both `disabled: true` (incapable of violence) while dressed for
a faction it could never fight for.

Root cause (read via RimSage, `Verse/PawnGenerator.cs` `GenerateOrRedressPawnInternal`):
unless the generation request forces a fresh pawn, vanilla `PawnGenerator` first
rolls a chance (`ChanceToRedressAnyWorldPawn`) to **reuse an existing WORLD PAWN**
or the map has one to reuse. The debug menu's own request does not set
`ForceGenerateNewPawn`, so it can grab any matching-race world pawn — including a
long-retired civilian backstory pawn — and "redress" it into the new role via
`RedressPawn`/`ChangeKind`. Whatever broke `ChangeKind`'s kindDef update in this
path, the practical result is: **the debug menu is not a reliable source of "does
this PawnKindDef generate correctly."**

⇒ **Use `jawa/spawn_pawn {"kindDef":..., "faction":..., "x":.., "z":..}` instead.**
Its response reports `kindActual` and `kindSubstituted` explicitly, and 30/30 test
spawns across 5 kinds this way matched the requested kind with zero substitution —
the debug menu route is the confound, not the game's real generation path used by
raids/quests/`jawa/spawn_pawn` itself.

⚠️ **Cleanup note:** these redressed/spawned test pawns are NOT colonists
(`select_pawn` refuses them, §"IsColonist" trap above) and `jawa/destroy_batch`
never touches pawns. Kill them with `rimworld/execute_debug_action
{"path":"Actions\T: Damage To Death","pawnId":"Thing_<id>"}` (note the `Thing_`
prefix even though `jawa/list_pawns`/`jawa/spawn_pawn` report the bare id) — but it
NRE'd silently on 2 of 34 pawns in this session ("Object reference not set", no
kill). Fall back to `jawa/damage {"thingId":<bare id>,"amount":large,"damageDef":
"Bomb"}` looped until `dead:true` in the response — `amount` is a request, not a
result (§ elsewhere in this file), so one call is not enough evidence of a kill.

## 🔴 `logCount: 0` from a debug action can mean LOGGING IS OFF, not "the action never ran"
**Symptom:** `execute_debug_action` on our `Actions\Forge cycle: report state (current map)` returned `success: true`, `effects.logCount: 0`, and Player.log held no line from a method that calls `Log.Message` unconditionally. It was read as "mod debug actions are no-ops" (BRIDGE_MOD_DEBUGACTIONS_NOOP_1, 2026-09-30).
**Cause:** `Verse/Log.cs` stops ALL managed logging after **10,000** messages (`Reached max messages limit. Stopping logging to avoid spam.`, and it also sets `Debug.unityLogger.logEnabled = false`). After that, `Log.Message`/`Warning`/`Error` return immediately, so the in-game log, RimBridge's LogJournal and Player.log all go silent. In that session **8,994** of the 10,000 were our own plants' `must have plant.MaxMeshCount that is a perfect square` (`Plant.cs:1000`, which accepts only 1/4/9/16/25).
**Fix:** before trusting a silent debug action, grep Player.log for `Reached max messages limit`. The only reset is the Debug log window's **Clear** button (`EditWindow_Log` → `Log.Clear` → `ResetMessageCount`), and no bridge tool calls it. Keep `maxMeshCount` a perfect square (all 15 offenders fixed 2026-09-30).
**Recurs when:** any long session on the full list with a per-frame or per-print error spammer. Every log-based verdict after the cap is blind.

## `rimworld/click_ui_target` can report success and do nothing — drive the real OS mouse
- **A bridge click that reports `success: true` with a correct target-to-rect mapping can still change nothing.** Proven by before/after screenshots on two controls of one heavily custom-IMGUI dialog (the semantic click's `changed` field only reflects window open/close, not a control's internal effect); consistent with a synthetic MouseDown/MouseUp not resolving against the same control id through nested `GUI.BeginGroup`/`EndGroup`. Do not keep retrying it or escalate to a human: drive the REAL Windows mouse via `ctypes`/`user32.dll` from `python.exe` (not WSL, it needs the Windows session). Call `ctypes.windll.shcore.SetProcessDpiAwareness(2)` FIRST, or `GetWindowRect`/`GetClientRect`/`GetSystemMetrics` return virtualized 96-DPI coordinates on a scaled or multi-monitor setup and every click lands nowhere without an error. Then `FindWindowW` the RimWorld window, `ClientToScreen` for the client origin, add the `get_ui_layout` `screenRect` coordinates (1:1 once DPI-aware), and `SetCursorPos` + `mouse_event(MOUSEEVENTF_LEFTDOWN)` + `mouse_event(MOUSEEVENTF_LEFTUP)`. `get_ui_layout` target ids embed a frame number that expires in well under a second, so fetch the target immediately before the click or `click_ui_target` times out for an unrelated reason that looks like the same failure.

## VEF Dialog_NewFactionSpawning windows stack after a donor-free save load
- **After the donor-free save loads on a short tier, VEF `Dialog_NewFactionSpawning` windows stack:** close each with `rimworld/close_window`. `go_to_main_menu` then NREs, so restart the game (~80 s on 21 mods) rather than fight it.

## 4. Debug actions are the real surface
- **Selection ids carry a `Thing_` prefix.** `rimworld/get_selection_semantics` names a thing `Thing_<def><idNumber>` (`selectedObjects[].id`, `details.thingId`) while `jawa/list_things` names it `<def><idNumber>`. Code binding a selection to a listed thing must strip `Thing_` (or compare `details.thingIdNumber`); a selftest stub that invented a bare-id shape passed 660/660 while the live read was blind.
- **`jawa/clear_ui` defaults `hideHud=true`:** it switches on vanilla screenshot mode for 20 s, and in screenshot mode RimWorld draws no gizmo grid, no inspect tabs and no tooltips, so `get_ui_layout` returns only an empty Inspect surface. A probe that clears the UI before reading gizmos, tabs or hover text must pass `hideHud:false` and wait out a lease still on (reply `hudHidden`). Before calling a proof_or_site NO VERDICT an environment fault, read the probe's own call log (`result_*.json` calls) for `hudHidden`. Guarded by `bridgetools/selftest_hover_probe_hud.py`.
