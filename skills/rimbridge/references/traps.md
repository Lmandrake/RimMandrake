# RimBridge traps

Symptom, cause, fix, **recurs when**. Every entry cost a real cycle. Promote into
`SKILL.md` anything that should change default behaviour, and delete it from here
when you do. Admission test and entry format:
`skills/rimworld-modding/references/traps.md`.

**First law — most entries below are a special case of it: `success: true` means
the tool RAN, not that the game CHANGED.**

**The entries marked 🔴 have each destroyed something real.** Read those before
your first mutation, whatever else you skip.

---

## Contents

Skim this, open what matches your task — do not read them all.

- [`success: true` is not evidence](#success-true-is-not-evidence)
- [`debugToolChanged: false` means nothing](#debugtoolchanged-false-means-nothing)
- [`designatorId` is a UI path, not a defName](#designatorid-is-a-ui-path-not-a-defname)
- [A screenshot taken while paused can be the previous frame](#a-screenshot-taken-while-paused-can-be-the-previous-frame)
- [`ThingMaker.MakeThing` builds a wreck for any def whose framework wires it elsewhere](#thingmakermakething-builds-a-wreck-for-any-def-whose-framework-wires-it-elsewhere)
- [The debug log window sits on the middle of every screenshot](#-the-debug-log-window-sits-on-the-middle-of-every-screenshot) 🔴
- [Shell quoting eats debug action paths](#shell-quoting-eats-debug-action-paths)
- [Enumeration can livelock the game — and `limit` does not save you at 568](#enumeration-can-livelock-the-game--and-limit-does-not-save-you-at-568) 🔴
- [`runInBackground` is off by default, and it starves the bridge silently](#runinbackground-is-off-by-default-and-it-starves-the-bridge-silently)
- [One timeout desyncs the client for every later call](#one-timeout-desyncs-the-client-for-every-later-call)
- [Batching only pays when the SHAPE packs, and generator output does not](#batching-only-pays-when-the-shape-packs-and-generator-output-does-not)
- [A companion DLL cannot be deployed while the game is running — at all](#a-companion-dll-cannot-be-deployed-while-the-game-is-running--at-all)
- [Restoring the terrain is NOT undoing the paint](#restoring-the-terrain-is-not-undoing-the-paint)
- [The optimisation that made the number better made the picture wrong](#the-optimisation-that-made-the-number-better-made-the-picture-wrong)
- [A field missing from the def dump is not proof the patch failed](#a-field-missing-from-the-def-dump-is-not-proof-the-patch-failed)
- [WSL cannot reach the bridge at all — it binds to Windows loopback](#wsl-cannot-reach-the-bridge-at-all--it-binds-to-windows-loopback)
- [`get_cell_info` does not report pawns, so a spawn looks like a no-op](#get_cell_info-does-not-report-pawns-so-a-spawn-looks-like-a-no-op)
- [A debug-action leaf path embeds a TAB and the display label](#a-debug-action-leaf-path-embeds-a-tab-and-the-display-label)
- [Screenshots overwrite by filename, so a stale image reads as a failed action](#screenshots-overwrite-by-filename-so-a-stale-image-reads-as-a-failed-action)
- [Unpausing with freshly-spawned HOSTILES on the map wiped half a colony](#unpausing-with-freshly-spawned-hostiles-on-the-map-wiped-half-a-colony) 🔴
- [`Apply damage...` reports success and applies nothing — only a CONTROL caught it](#apply-damage-reports-success-and-applies-nothing--only-a-control-caught-it)
- [Verifying a compiled-out tool: attribute names are UTF-8 blobs, not UTF-16 literals](#verifying-a-compiled-out-tool-attribute-names-are-utf-8-blobs-not-utf-16-literals)
- [The companion DLL changes on every commit, by anyone, with no source change](#the-companion-dll-changes-on-every-commit-by-anyone-with-no-source-change)
- [`token=NO` during a load is the game still loading, not the WSL bug](#tokenno-during-a-load-is-the-game-still-loading-not-the-wsl-bug)
- [Do not quote a single bridge latency number](#do-not-quote-a-single-bridge-latency-number)
- [You cannot photograph a stale mesh — moving the camera repaints it](#you-cannot-photograph-a-stale-mesh--moving-the-camera-repaints-it)
- [`amount` is a request; RimWorld decides what lands](#amount-is-a-request-rimworld-decides-what-lands)
- [Every tool is named `rimworld/…`, so a topic grep matches all 139](#every-tool-is-named-rimworld-so-a-topic-grep-matches-all-139)
- [The `jawa/` prefix says WHO SUPPLIES the tool, not what it does — it cannot be inferred](#the-jawa-prefix-says-who-supplies-the-tool-not-what-it-does--it-cannot-be-inferred)
- [A prediction is only a test if the instrument can read its TERMS](#-a-prediction-is-only-a-test-if-the-instrument-can-read-its-terms) 🔴
- [`jawa/list_pawns` returns `kind`, not `kindDef`](#jawalist_pawns-returns-kind-not-kinddef)
- [A long call times out, succeeds anyway, and retrying does it TWICE](#a-long-call-times-out-succeeds-anyway-and-retrying-does-it-twice)
- [Foundation can only be laid on BARE ground — a floor blocks it permanently](#foundation-can-only-be-laid-on-bare-ground--a-floor-blocks-it-permanently) 🔴
- [Multi-cell things spawn CENTRED on the cell you name](#multi-cell-things-spawn-centred-on-the-cell-you-name)
- [You cannot enslave a pawn in your own faction — and `T: Enslave` says `success: true`](#you-cannot-enslave-a-pawn-in-your-own-faction--and-t-enslave-says-success-true) 🔴
- [`Thing.set_Rotation` returns SILENTLY on a locked pawn, and the lock is saved](#thingset_rotation-returns-silently-on-a-locked-pawn-and-the-lock-is-saved)
- [The renderer ignores `Rotation` for any laying pawn, so turning a downed one is a no-op](#the-renderer-ignores-rotation-for-any-laying-pawn-so-turning-a-downed-one-is-a-no-op)
- [Fixed in the companion — one line each](#fixed-in-the-companion--one-line-each)
- [A correct measurement of the WRONG predicate — and a null baseline is the only thing that catches it](#-a-correct-measurement-of-the-wrong-predicate--and-a-null-baseline-is-the-only-thing-that-catches-it) 🔴
- [The bridge answering is NOT the game being reactive — ~40 seconds of it](#-the-bridge-answering-is-not-the-game-being-reactive--40-seconds-of-it) 🔴
- [`python.exe` vs `python3` is a PER-SCRIPT choice, and the rule you carry points the wrong way half the time](#-pythonexe-vs-python3-is-a-per-script-choice-and-the-rule-you-carry-points-the-wrong-way-half-the-time) 🔴
- [`?.` guards the RESULT, not the CALL — the whole companion is dead at a main menu](#--guards-the-result-not-the-call--the-whole-companion-is-dead-at-a-main-menu) 🔴
- [A parameter you PASS is not a parameter that SURVIVES — the raid faction is rewritten by ref](#-a-parameter-you-pass-is-not-a-parameter-that-survives--the-raid-faction-is-rewritten-by-ref) 🔴
- [A tool built to break a conflation can INHERIT that conflation from the API it reads](#-a-tool-built-to-break-a-conflation-can-inherit-that-conflation-from-the-api-it-reads) 🔴
- [The reflective def reader is blind to properties and privates, and says nothing about it](#the-reflective-def-reader-is-blind-to-properties-and-privates-and-says-nothing-about-it)
- [A gate that greps "the source tree" greps the prose about it too](#a-gate-that-greps-the-source-tree-greps-the-prose-about-it-too)
- [`search_debug_actions` walks the whole tree and FROZE the game — twice](#search_debug_actions-walks-the-whole-tree-and-froze-the-game--twice) 🔴
- [Identify a thing by its accompanying signature, not by its own defName](#identify-a-thing-by-its-accompanying-signature-not-by-its-own-defname)
- [An instrument can be blind to the exact branch that fails](#an-instrument-can-be-blind-to-the-exact-branch-that-fails) 🔴
- [The denominator is the population that EXERCISED the rule](#the-denominator-is-the-population-that-exercised-the-rule) 🔴

---

## `success: true` is not evidence
**Symptom:** `spawn_thing` returns a real `thingId` and a sensible label while a red error window opens in game; `Set terrain (rect)` returns success on every call and changes no cell.
**Cause:** the bridge reports that the *tool ran*. Whether RimWorld accepted the result is a different question it does not answer.
**Fix:** verify on an independent channel — `effects.logs` on the response, `get_cell_info`, or `save_game` parsed from disk.
**Recurs when:** every bridge tool, every time. This is the file's first law.

## `debugToolChanged: false` means nothing
**Symptom:** `effects.debugToolChanged: false` read as proof that `execute_debug_action` had done nothing; a confident bug report was filed against the mod for an unimplemented code path.
**Cause:** it is `false` on calls that demonstrably work, including one that killed a pawn outright. The bridge applies these directly without arming a UI tool, so the flag says nothing about success.
**Fix:** judge by world state. Calibrate any diagnostic against a known-good case before trusting its negative.
**Recurs when:** `effects.debugToolChanged` and `effects.logCount` — response metadata that describes the dispatcher, not the game.

## `designatorId` is a UI path, not a defName
**Symptom:** `apply_architect_designator` with `designatorId: "Floor_Concrete"` returns `success: false`, `Could not find architect designator 'Floor_Concrete'` — inside an envelope that says `Success: true`, because the *tool* ran fine.
**Cause:** the id is a scoped path built from the live architect menu: `architect-designator:floors:build-concrete`. `list_architect_designators` requires a `categoryId` from `list_architect_categories`, and returns dropdown parents alongside leaves.
**Fix:** resolve at runtime by matching the trailing segment; never hardcode. See `find_designator` in `src/RimMandrake/Utils/bridge_latency.py`.
**Recurs when:** any id carrying a positional index (`highlight-designator-tutortagnotset-3`) — those renumber as mods add architect entries, so a path captured on the 3-mod tier is not safe at 568.

## A screenshot taken while paused can be the previous frame
**Symptom:** `screenshot_cell_rect` before and after a verified 36-cell terrain change produced **byte-identical** PNGs, same md5 — indistinguishable from the "terrain changed in the grid but does not redraw" failure.
**Cause:** the game was paused, so no new frame had been rendered between the two captures. The crop was real, the change was real, the image was stale.
**Fix:** `step_game_ticks` a few ticks before capturing, and `frame_cell_rect` on the target first — zoomed out over dense canopy a 6×6 patch is too small to see anyway.
**Recurs when:** `screenshot_cell_rect` with `set_time_speed` at 0. A screenshot is evidence about the *renderer*, not about game state; settle state with a data read and let the picture cover only what data cannot show.

## `ThingMaker.MakeThing` builds a wreck for any def whose framework wires it elsewhere
**Symptom:** `jawa/spawn_batch AV_DogSled` returned `NullReferenceException: Obje…` with nothing else in it, and the row was read as a verdict on the ART — "the sled does not spawn" — when it was a gap in the spawning tool.
**Cause:** `AV_DogSled` is a `Vehicles.VehicleDef`, and `VehiclePawn::.ctor` initialises collections only. `vehiclePather`, `ignition`, `drawTracker`, `statHandler` and `kindDef` are all written by `Patch_Components::CreateInitialVehicleComponents` — Vehicle Framework's Harmony hook on `PawnComponentsUtility.CreateInitialComponents`, which `MakeThing` never calls. `VehiclePawn::SpawnSetup` then `callvirt`s all three nulls (IL_007b, IL_0094, IL_00f8). Read with `ilprobe`, not recalled.
**Fix:** route through the framework's own public static factory — `Vehicles.VehicleSpawner.SpawnVehicleRandomized(def, cell, map, faction, rot, autoFill)`, which generates, wires, refuels and spawns. Reached by **reflection** (`GenTypes.GetTypeInAnyAssembly`), never a compile-time reference: a companion that hard-references a mod's DLL refuses to load for anyone without that mod. Pass a non-null Faction — `null` is tolerated by `SetFactionDirect` and then `SpawnSetup` takes the not-player branch and the vehicle auto-drafts.
**Recurs when:** any def type a framework mod introduces — vehicles, mechs, some animals. **Generalises to: `MakeThing` constructs the OBJECT, not the object's WORLD.** If a mod adds a def class, assume it also adds a factory, and find it before assuming the def is broken. And a bare NRE from a spawn is a statement about the TOOL until proven otherwise.

## 🔴 The debug log window sits on the middle of every screenshot
**Symptom:** twelve art screenshots from one live session, every one filed `NEEDS EYES` with a real path to a real 1878x1312 PNG — and in `p5_004.png` and `p13_012.png` **the photographed subject is not in the frame at all.** No error, no failed call, no clue in the ledger.
**Cause:** `look()` does its job — `jump_camera_to_cell` puts the subject dead centre — and RimWorld's **Debug log window is also dead centre**, ~940x650 px of scrolling text. The pawn inspect pane covers the bottom-left, the dev palette the top-left. Between them the middle of the screen is the one place a subject must not stand.
**Fix:** `jawa/clear_ui` before every capture — it removes every `LudeonTK.Window_Dev` and clears the selection (the inspect pane is drawn from the *selection*, not from a window, so nothing else closes it). `rimbench.core.look()` and `.frame()` call it automatically. ⚠️ Closing the log by hand does not hold: **auto-open-on-error reopens it**, and a 568-mod startup throws errors all session.
**Recurs when:** any instrument that captures a VIEW rather than a value. The check that passed was "did a file get written"; the question was "is the subject in it". **Generalises to: a capture tool must be told what to EXCLUDE, and the only way to know it obeyed is to look at the output — the twelve rows say `NEEDS EYES`, which reads as *collected, awaiting judgement*, and they were collected and empty.** Nothing in the response, the ledger or the log distinguishes a good frame from a photograph of a debug log.

## Shell quoting eats debug action paths
**Symptom:** a path containing backslashes passed through `--json` dies with a JSON decode error.
**Cause:** bash strips one backslash layer, then JSON rejects the result as an invalid escape.
**Fix:** drive `rimbridge_client` as a Python library; in heredocs use `chr(92)`, never a doubled backslash.
**Recurs when:** any `--json` payload holding a Windows path or a regex. Bash heredocs also corrupt ordinary prose — use the Write tool when the content is documentation.

## 🔴 Enumeration can livelock the game — and `limit` does not save you at 568
**Symptom:** `search_debug_actions {"query":"EMP","limit":12}` timed out at 30 s three calls running, then the game wedged: CPU at 43–96% of a core, `Player.log` stopped growing entirely, process had to be killed. `rimbridge/ping` and `rimworld/get_game_info` had both answered in ~7 ms moments earlier. Cost: a cold reload plus another thread's unsaved terrain work.
**Cause:** `limit` truncates the **returned list**, not the **search**. The response carries `totalMatchCount`, and computing that walks the entire debug-action tree however few rows you asked for. ~119 entries on three mods; enormous at 568 — SKILL.md's own figure is 1,119 matches for "apparel" on the *three-mod* list.
**Fix:** never call `search_debug_actions` on the full stack. Discover paths on the 3-mod tier (`modset_builder.py --tier bridge`), record them, then `execute_debug_action` with the known path at 568. `list_debug_action_children` is the safe discovery call on the full stack — one bounded level.
**Recurs when:** any `limit` paired with a total or "truncated" flag — the total implies a full traversal, same shape as SQL `LIMIT` over an unindexed `COUNT(*)`. A "verified safe" note inherits the tier it was measured on: "12 of 119" was a 3-mod number read as a guarantee.

## `runInBackground` is off by default, and it starves the bridge silently
**Symptom:** every main-thread call times out at 30 s while `rimbridge/ping` answers in 0.5 ms. `get_bridge_status` returns after ~5 s with **every field null**, including `version`, which has nothing to do with game state. Looks exactly like a hung game or an unloaded map.
**Cause:** RimWorld ships `<runInBackground>False</runInBackground>`. Unfocused it stops running its main loop — measured at **0.5% of one core** against 79% with the pref on — and the bridge dispatches every game-touching call through `ctx.MainThread.InvokeAsync`.
**Fix:** Options → Run in background, set **in the game's menu**: prefs live in memory and `Prefs.xml` is rewritten on exit, so a disk edit while the game runs is discarded. Verify with a main-thread call while unfocused. `src/RimMandrake/Utils/game_focus.py` has a `preflight()`; every unattended run needs this pref.
**Recurs when:** an all-null response. If fields that *cannot* depend on your question are also null, the answer is degraded, not a negative — "no map is loaded" was diagnosed from this and the map was loaded throughout.

## One timeout desyncs the client for every later call
**Symptom:** after one call times out, the next fails with `unexpected response id '<guid>'`, and numbers after that are quietly wrong rather than absent.
**Cause:** the timed-out call's response arrives late and sits in the socket buffer; the next request reads that frame as its own reply.
**Fix:** treat a timeout as fatal to the connection. Open a fresh `RimBridge` per measurement group so a stall is contained — `src/RimMandrake/Utils/frame_lock_probe.py` does this deliberately.
**Recurs when:** `rimbridge_client` after any 30 s timeout. Resync or reconnect; never continue on the same socket.

## Batching only pays when the SHAPE packs, and generator output does not
**Symptom:** a 6×6 rect paints 36 cells in 15.2 ms (0.42 ms/cell), so batching looks like a ~30× win. A real 411-cell dithered crater takes 5.15 s (12.59 ms/cell) — a ~1× win over painting one cell at a time.
**Cause:** cost tracks **call count**, not cell count. A dithered boundary is interlocked on purpose, and greedy rect decomposition yields ~4 cells per rect, so 411 cells become 103 calls at ~50 ms each in a tight sequence. Ruled out: map and mod stack (the 6×6 control re-ran at 15.2 ms) and mesh refresh (~10%).
**Fix:** batch at the layer that knows the whole cell set — `jawa/set_terrain_batch`. Until a multi-rect API exists, budget ~20 bridge calls per second and design generators around that.
**Recurs when:** quoting a per-unit cost taken from a best-case batch. Measure the shape the system will actually be given.

## A companion DLL cannot be deployed while the game is running — at all
**Symptom:** `src/RimMandrake/bridgetools/build.py --apply` dies with `OSError: [WinError 1224] The requested operation cannot be performed on a file with a user-mapped section open`. Reads like a permissions problem and sends you to folder ACLs.
**Cause:** RimWorld keeps the companion assembly **memory-mapped** for the life of the process, and Windows refuses to overwrite a file with a mapped section. The copy is impossible, not merely ineffective.
**Fix:** close RimWorld, `--apply`, then start the game. `build.py` now detects WinError 1224 and says so instead of a traceback. The build and the artifact are unaffected; only the copy fails.
**Recurs when:** any companion change — it is gated on a game *shutdown*, not a startup. Treat "the repo artifact is ahead of the deployed copy" as the normal mid-session state, not as drift.

## Restoring the terrain is NOT undoing the paint
**Symptom:** a crater captured, painted and restored: 2,601 cells verified back to their original TerrainDef, **0 wrong**, in one call — and the map still did not look as before. The 11×11 core held 10 vegetated cells before the restore and 10 after.
**Cause:** `SetTerrain` destroys the plants on a cell whenever the new terrain cannot support them. Measured: grass dies on Sand, PackedDirt, rock and water, **survives Gravel**; painting a cell its own terrain is a no-op and kills nothing. The capture only ever recorded terrain.
**Fix:** say "terrain is exactly restorable", never "the paint is reversible". A full undo needs the plant list — `get_cell_info` per cell, then respawn. On a colony that matters, **the save is the undo**; reloading restores both.
**Recurs when:** any capture/restore whose write has side effects outside the field being diffed. "0 wrong" measures only the axis you captured.

## The optimisation that made the number better made the picture wrong
**Symptom:** `--defer-refresh` passed `refresh=false` on every terrain call but the last, cutting per-cell cost 13.99 → 12.59 ms (~10%). It was recorded as a clean win and became the quoted baseline (5,150 ms / 411 cells).
**Cause:** not an equivalent operation. `RefreshRect` dirties only the rect it was handed, and RimWorld caches the map mesh in **17×17 sections**. A radius-12 crater spans ~3×3 sections, so refreshing on the final rect dirties **one** and leaves eight stale — correct in the grid, unpainted on screen. The 10% saved was redraws that never happened.
**Fix:** flag deprecated; the honest per-rect baseline is **13.99 ms/cell**. `jawa/set_terrain_batch` collects every changed cell in a `HashSet` and flushes once, so it gets the saving *and* refreshes completely.
**Recurs when:** invalidating a cache whose granularity is coarser than your write unit — nothing errors, the stale region simply looks fine until it does not. Ask which *sections* you touched, not which cells.

## A field missing from the def dump is not proof the patch failed
**Symptom:** `drawSize` absent from all three of our eye GeneDefs in a fresh `RimDefDump`, while its siblings in the same XML block (`texPath`, `shaderTypeDef`, `layer`) were all present — a very believable partial-patch failure.
**Cause:** the dumper cannot serialise every type. It writes `"<skipped:Vector3>"` / `"<skipped:Color>"`, and `drawSize` is a Vector2 — it appeared 7 times across the sampled files, always as `"<skipped:Vector2>"`. A screenshot showed the eyes rendering correctly; the patch had applied all along.
**Fix:** before reading absence as a negative, test whether the dumper emits that key *anywhere*, and in what form. If every occurrence is `<skipped:...>`, the instrument cannot see it and the only honest answer says so.
**Recurs when:** `RimDefDump` on any Vector2, Vector3 or Color field. A tool that cannot represent an answer reports nothing, and nothing looks exactly like no.

## WSL cannot reach the bridge at all — it binds to Windows loopback
**Symptom:** `resolve_endpoint()` returns `127.0.0.1:5174` with **no token** and connecting raises `ConnectionRefusedError`, while the game is up and `Player.log` plainly says `GABP server running standalone on port 5174`. Reads exactly like a dead game or a disabled RimBridgeServer.
**Cause:** two independent problems wearing one error. (1) `netstat.exe -ano | grep 5174` shows `TCP 127.0.0.1:5174 LISTENING` — Windows loopback **only** — and WSL2 is a separate network namespace, so neither WSL's `127.0.0.1` nor the default gateway (`172.22.176.1`) has a route. (2) `resolve_endpoint()` scrapes the token from `Player.log` via a native Windows path that does not resolve from WSL, so it silently returns `DEFAULT_TOKEN` and the failure also looks like auth.
**Fix:** move the *client*, not the server binding. `python.exe` (3.13.14) is on `PATH` from WSL and lives in the right namespace; with cwd under `/mnt/` relative paths still translate. Otherwise `python.exe "$(wslpath -w /path/script.py)"` plus `sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")`. Pass the token explicitly — grep `[RimBridge] Bridge token:` out of `Player.log`. `python3` reaches the filesystem and never the bridge.
**Recurs when:** diagnosing the game's health from a connection error. Settle it off-socket: `tasklist.exe | grep -i rimworld`, `Player.log` mtime against the clock, `grep -a 'GABP server running' Player.log`. All three said healthy while the socket said refused.

## `get_cell_info` does not report pawns, so a spawn looks like a no-op
**Symptom:** `execute_debug_action` on `Actions\Spawn Pawn...\Jawa_Spawn_Hutt` returned `success: true`, and `get_cell_info` on the exact target cell returned `things: []` — which against this file's first law reads as the documented no-op failure.
**Cause:** it had worked; a screenshot showed the pawn on that cell. `get_cell_info`'s `things` list simply does not include pawns.
**Fix:** verify pawn spawns with `screenshot_cell_rect`, `list_colonists` / `jawa/list_pawns`, or `save_game` + parse. `screenshot_cell_rect` refuses a rect that will not fit the viewport and names `requiredRootSize` vs `appliedRootSize` — pass `rootSize` and retry rather than guessing.
**Recurs when:** any verification channel that cannot observe the *class* of object you changed. The false negative is indistinguishable from a real failure, and here it was "confirmed" by the tool's own most-quoted warning.

## A debug-action leaf path embeds a TAB and the display label
**Symptom:** `execute_debug_action` on `Actions\Colonist of Xenotype...\BTD_Jawa` returned `success: false` eight times, with **no log line and no error message**. The defName was correct and the xenotype exists.
**Cause:** the node key is `"<defName>\t (<label>)"` — `list_debug_action_children` returns `Actions\Colonist of Xenotype...\BTD_Jawa\t (Jawa)`. A path built from the defName alone resolves to nothing. `Actions\Spawn Pawn...\<PawnKindDef>` takes the bare defName, so the convention is per-node, not global.
**Fix:** never construct a leaf path — read it and use it verbatim: `next(c["path"] for c in ch if c["path"].split(chr(92))[-1].startswith("BTD_Jawa"))`, where `ch` is `list_debug_action_children`'s `children`. Browse down from `list_debug_action_roots`; `Actions` has 596 visible children and returns in about a second.
**Recurs when:** `success: false` with no message — that means the path did not resolve, not that the action refused. `get_debug_action` returns `actionType: null` for both working and failing leaves, so it is not a usable diagnostic; compare against a known-good sibling instead.

## Screenshots overwrite by filename, so a stale image reads as a failed action
**Symptom:** eight Jawas spawned, `success: true` on all eight, and the screenshot showed **empty ground** — which against the first law reads as a confirmed no-op. `list_colonists` showed all eight at exactly the requested cells.
**Cause:** the screenshot call reused the `fileName` of an earlier, genuinely failed attempt, and the older image was read.
**Fix:** give every screenshot a unique name, or verify with `list_colonists` / `get_camera_state` before believing a picture. Treat an image file as a cache, not as an observation.
**Recurs when:** any tool writing to a caller-chosen path — `screenshot_cell_rect`, `save_game`. When the action reports success and the check says nothing happened, suspect the check first.

## 🔴 Unpausing with freshly-spawned HOSTILES on the map wiped half a colony
**Symptom:** `OuterRim_BattleDroid` and `JDSCIS_B1_Battle_Droid` spawned three cells from the colony for an EMP test, then `set_time_speed` to Normal for an *unrelated* voice test. ~2 in-game hours later: `Colonists need rescue`, `Medical emergency`, `Colonist left unburied`, `Death: Gwenevere (bengal cat)`; 16 pawns → 14 with several more downed. ~7,000 ticks elapsed during ordinary tool calls.
**Cause:** neither the spawn nor the unpause was wrong alone — each was correct for its own test. Together they are a raid, and the game runs in real time whether or not the agent is paying attention.
**Fix:** spawn hostiles at the map edge, not next to pawns; keep hostile tests **paused**, since debug damage applies with time frozen; list what is on the map before any `set_time_speed(>0)`; re-pause the moment the timed test ends.
**Recurs when:** `set_time_speed` — the most consequential call on the bridge, because it hands the whole simulation permission to act on everything you spawned earlier. Verify the pause like a mutation: read `ticksGame` twice a few seconds apart.

## `Apply damage...` reports success and applies nothing — only a CONTROL caught it
**Symptom:** `Actions\Apply damage...\EMP` with `pawnName` returned `success: true` three times and the droid showed no stun — a clean, publishable *"EMP does nothing to `OuterRim_BattleDroid`"*. An earlier round had produced zero injuries across 45 applications, five targeting variants and a paused/unpaused test.
**Cause:** the positive control settled it — `Bullet` ×4 on the same pawn also did **nothing**, with byte-identical saves at 29,553k and Gunshot 4 / Stun 0 / Bruise 1 across baseline, 3× EMP and 4× Bullet. `Apply damage...` is inert through `pawnName`/`pawnId`, not "needs an amount". Separately `RimBridgeServer.ResolvePawn` accepts player-controlled colonists only — *"A player-controlled colonist name or id is required."* — so no `ToolMapForPawns` action can target a hostile at all.
**Fix:** for damage to anything including hostiles, use a `ToolMap` action with `x`/`z`: `Actions\Explosion...\<DamageDef>`. `T: Damage To Death` kills a colonist in one call; `T: Set Stuff...` and `T: Set Quality...` work by `thingId`. The class is not broken — test a second member before condemning it.
**Recurs when:** any negative result from a mutation tool. Without a positive control whose effect is impossible to miss, "X had no effect" and "the tool had no effect" are indistinguishable. Compare whole-file save size and a global count, not a parsed segment.

## Verifying a compiled-out tool: attribute names are UTF-8 blobs, not UTF-16 literals
**Symptom:** a byte-scan of the deployed companion for its fourteen tool names reported a confident **0/14** — on a DLL containing all fourteen. Reads as "the deploy did not land", and the next hour goes to a deploy problem that does not exist.
**Cause:** the scan searched UTF-16, because .NET string *literals* live in the `#US` metadata heap as UTF-16. A tool name is a `[Tool("jawa/...")]` **custom attribute argument**, stored in the metadata **blob heap as length-prefixed UTF-8**. Different heap, same source text.
**Fix:** `verify_gm_gate()` in `src/RimMandrake/bridgetools/build.py` tests `name.encode("utf-16-le") in blob or name.encode("utf-8") in blob`. It was proven by building both ways and confirming it flips — 115,712 B "verified absent" against 125,440 B "in DLL" — and it `sys.exit`s if gated tools appear, so every way it can be wrong ends in "do not deploy". It gates `jawa/fire_incident`, the one tool that can drop a raid on the colony the owner is playing.
**Recurs when:** a build flag that flips `DefineConstants` without `--no-incremental` — MSBuild keys incrementality off timestamps, not properties, so a `--gm` run can hand back the previous non-GM DLL. Also: an XML comment cannot contain `--`, so documenting a `--flag` inside a csproj comment is an `MSB4025` build failure; name the property (`/p:JawaGmTools=true`).

**⚠️ The mirror image bit again on 2026-08-13, with this entry already written.** `strings -a "<dll>" | grep -F "No target. jawa/damage takes"` came back **ABSENT** on a DLL that contained it, because plain `strings` scans 7-bit ASCII and a method-body literal is UTF-16LE. The same command found `jawa/order_pawn`, `spawnedCount` and `countAllIncludingHidden` — attribute blobs and metadata member names, both UTF-8 — so the scan **looked** like it was working, and the false ABSENT was read as "the damage fix never deployed". **So: `strings -a` proves a tool NAME present; only `strings -a -el` proves a MESSAGE present, and a mixed check must run both.** The heap a string lives in is decided by whether it is an attribute argument or a literal, never by what you are trying to verify.

## The companion DLL changes on every commit, by anyone, with no source change
**Symptom:** deploy the companion, byte-verify it (`identical, nothing to do`), commit the session's work, re-run `build.py` — and it reports **"differs, would overwrite"** against a game copy nothing had touched, with the game down throughout.
**Cause:** the SDK embeds the git HEAD SHA into `AssemblyInformationalVersion` as `0.1.0+<40-hex>`, and the PE timestamp and MVID are content hashes that move with it. Measured **96 of 125,440 bytes** differ between two builds of identical source at different commits. The build is deterministic — three consecutive `--no-incremental` rebuilds at one commit were byte-identical — so "differs" is a precise statement that the copies came from different commits. In a shared tree another agent's commit moves HEAD under you mid-session.
**Fix:** `plan_deploy()` splits one signal into three — bytes equal → `identical, nothing to do`; stamps differ → `built from a DIFFERENT COMMIT`, expected, prints both SHAs; **stamps equal and bytes differ → 🔴 `*** DRIFT ***`**, impossible for a deterministic build, so someone hand-edited the deployed DLL. Investigate before `--apply` destroys it.
**Recurs when:** any repo→game byte-compare of a built artifact. Never annotate a detector with "differs is expected" in a handoff — that is how the only drift check on the deploy path gets disabled.

## `token=NO` during a load is the game still loading, not the WSL bug
**Symptom:** `resolve_endpoint()` returns `127.0.0.1:5174` with **no token** and the first call dies with `AttributeError: 'NoneType' object has no attribute 'sendall'` — character-for-character the WSL entry above, so you switch to `python.exe`, get the identical failure, and go hunting a networking problem that does not exist.
**Cause:** when you are already under `python.exe`, RimBridgeServer has not started yet. A cold load on this stack is 23–30 minutes and the bridge comes up late; `resolve_endpoint()` scrapes host/port/token out of `Player.log`, so before the startup line there is nothing to scrape. **An empty token is the tell** — a running bridge always has one.
**Fix:** settle it from the log before blaming the transport — `stat -c '%y %s' "$LOG"` (mtime ~now and small = still loading), `grep -ci rimbridge "$LOG"` (0 = server not started), `tail -3 "$LOG"` (def-loading lines = still in defs). A log being written **now** with no `rimbridge` line is a game mid-load; a **stale** log with no line is a game that is down.
**Recurs when:** two causes wearing one symptom — the symptom cannot be the diagnosis, so reach for the discriminator rather than the more familiar cause. `RimWorldWin64.exe` existing is not the service being ready.

## Do not quote a single bridge latency number
**Symptom:** every main-thread class measured 16.7 ms at 568 mods (`get_game_info` 16.656, `get_cell_info` 16.673, `jawa/set_terrain` 16.708) and was read as a hard 60 Hz frame gate. Two later runs on one map read `get_game_info` 5.673 then 4.358, `get_cell_info` 5.847 then 4.371, and `jawa/set_terrain` 21.017 then 13.648.
**Cause:** unknown, and every mechanism offered has been withdrawn — pawn count went **up** while latency went **down**, so "a busier colony is slower" is contradicted by our own data, and the `jawa/set_terrain` "+26% anomaly" moved 21.0 → 13.6 with no deliberate change. What survives: **there is no fixed 60 Hz gate**, since 4.4 ms reads cannot come from a 16.67 ms tick.
**Fix:** record the workload (colonist count, total pawns) and `ticksGame` alongside every benchmark — the `workload` block in `bridge_latency.py` caught its own author's wrong explanation within minutes of shipping. Quote a range and its conditions, or quote nothing.
**Recurs when:** naming `observed/2026-08-13/latency_*.json` by mod count. Mod tier is not the axis — three runs at 573 on one map disagree by 35%.

## You cannot photograph a stale mesh — moving the camera repaints it
**Symptom:** paint a rect with `refresh=false`, screenshot, call `jawa/refresh_rect`, screenshot again — **the two images are identical and the "stale" one already shows the new terrain.** Reads as "refresh_rect does nothing".
**Cause:** every framed-shot tool moves the camera — `rimworld/screenshot_cell_rect` re-roots and re-zooms, `Session.look()` calls `jump_camera_to_cell` first — and camera movement re-enters the map sections, triggering the very redraw the test was trying to catch.
**Fix:** none available. `refresh_rect`'s **visible half is UNPROVEN** and this method cannot prove it; its data half is proven, in that it accepts a well-formed rect and refuses a malformed one. A real test needs a shot from an already-stationary camera taken before the unrefreshed paint, which no current tool composes.
**Recurs when:** any visual A/B over the bridge — ask what the act of looking changes. Also: the tool is `rimworld/jump_camera_to_cell`; there is no `jump_camera_to`.

## `amount` is a request; RimWorld decides what lands
**Symptom:** `jawa/damage` with `amount=400` on a Scavenger reported `totalDamageDealt: 32.0` and `dead: false`; a second identical call killed it. Earlier, `amount=250` landed as `60.0`.
**Cause:** a single damage instance is capped by the body part it hits, plus armour. `amount` is what you asked for, not what arrived — and `totalDamageDealt` is why that field exists.
**Fix:** for cleanup, hit in a bounded loop until `dead` or `destroyed`, and treat exhausted attempts as a loud failure. `src/RimMandrake/bridgetools/prove_new_tools.py` does this. Never assume one call removes a pawn.
**Recurs when:** any mutation whose parameter is a *request* to a simulation applying its own rules. Read the delivered quantity back out of the response; a tool that reports none is a gap, not a convenience.

## Every tool is named `rimworld/…`, so a topic grep matches all 139
**Symptom:** a regex of `new|start|scenario|quick|test|load|save|game|world|map|colon` over the 139 tool names matched **every one**, because the namespace is `rimworld/`. It happened to surface `rimworld/start_debug_game`, so the answer arrived and the mistake went unnoticed.
**Cause:** a namespace prefix is not searchable content.
**Fix:** match the leaf — `[n for n in names if "faction" in n.split("/", 1)[-1]]`. Done correctly it shows there is **no faction, world or settlement tool** among the 139; world state comes from `save_game` plus a grep of the `.rws`.
**Recurs when:** grepping a `.rws` for a defName — count `<def>NAME</def>`, never the bare name. Bare `grep -c OuterRim_RebelAlliance` returns **1 on a world that does not contain the faction**, because the hit is the def-name registry entry beside `OuterRim_RebelPlayerFaction`. W6 closed as 0 instantiated against 3 controls at 1 each, out of 55 factions.

## The `jawa/` prefix says WHO SUPPLIES the tool, not what it does — it cannot be inferred
**Symptom:** a run-sheet line written for a live window called `jawa/spawn_thing`. There is no such tool. The call is `rimworld/spawn_thing`; `jawa/` carries `spawn_batch`, `spawn_pawn`, `order_pawn`, `set_terrain_batch` and 22 others. Caught offline by a peer against the 26 deployed names — had it shipped, the cost was a dead call inside a ~23–30 min load window.
**Cause:** the prefix was inferred from the *neighbourhood* of the work — the surrounding lines were companion calls, and the batch form really is `jawa/spawn_batch`, so the singular "obviously" matched it. But the namespace records **which assembly registered the tool**, and nothing about the verb. `spawn_batch` is `jawa/` and `spawn_thing` is `rimworld/` for the same reason: one was added, one was already there.
**Fix:** read the leaf out of `skills/rimbridge/references/capability-matrix.md` — it prints every call fully qualified — or list the deployed names off the DLL. **Never type a prefix you did not just read.** ⚠️ A sibling call in the same family is not evidence: `jawa/spawn_batch` existing is exactly what made the wrong prefix feel checked.
**Recurs when:** any two-namespace surface — and this one has 139 `rimworld/` names against 26 `jawa/`, so guessing `jawa/` is wrong ~84% of the time by count. Generalises past the bridge: this is `CLAUDE.md`'s *never guess a defName, field, or namespace*, and the namespace clause is the one that gets skipped because a prefix looks like syntax rather than content.

## 🔴 A prediction is only a test if the instrument can read its TERMS
**Symptom:** an A/B test was handed to the live seat with both verdicts committed in advance — place a thruster one way and predict **no `WarningThrusterInside`**, place the control and predict **`WarningThrusterInside`**. It was rigorous in every respect except one: **no tool on the bridge could read an inspect string.** `get_cell_info` returns `className: Verse.Building` and stops, and `CompGravshipThruster` folds base `CanBeActive`, `Blocked`, `BrokenDown` and `outdoors` into a single bool that is not exposed anywhere. The test would have produced two spawns and no verdict, and the two spawns would have looked like it ran.
**Cause:** the predicate was chosen from the **source** — the IL named the condition, so the condition felt observable. Nobody asked *which call returns this string*. Committing the prediction in advance made it feel more rigorous, not less, which is exactly why it survived review: pre-registration guards against moving the goalposts, and does nothing about aiming at a target the instrument cannot see.
**Fix:** before committing any prediction, **name the exact call and the exact field that will carry the answer**, and confirm that field exists today — not in the source, in the *tool surface*. If nothing returns it, the honest options are to build the reader first (this one became `jawa/inspect_string`) or to pick a predicate something already returns. ⭐ **Prefer testing the MECHANISM synthetically over testing your artifact.** The rescue here was a sealed room built from nothing on a throwaway map: it tests the `IsOutdoors` aft-strip rule the whole conclusion rests on, needs no deck, no save and no import, and if it holds, every derived claim inherits its confidence.
**Recurs when:** any conclusion drawn from decompiled or source-read logic, where the vocabulary of the *implementation* silently becomes the vocabulary of the *test*. Generalises past the bridge — it is one level earlier than "a correct measurement of the WRONG predicate": here the predicate was right and **unobservable**, and an unobservable predicate fails silently, because a call that returns nothing looks identical to a condition that did not fire.

## `jawa/list_pawns` returns `kind`, not `kindDef`
**Symptom:** 8 pawns spawned, `jawa/spawn_pawn` returning `success: true` with real ids, names and coordinates; the next `jawa/list_pawns` filtered on `p["kindDef"] == "Jawa_Spawn_Hutt"` returned **0**, and "neutral pawns despawn instantly" was stated out loud. Re-run against `kind`: **7 alive**, exactly where spawned.
**Cause:** there is no `kindDef` key, so `p.get("kindDef")` was `None` for every pawn and the filter matched nothing. A `KeyError` would have been caught instantly. "Faction `none` pawns are transient" is real RimWorld behaviour, so the wrong answer sounded like knowledge and survived three follow-up calls.
**Fix:** `print(json.dumps(pawns[0])[:300])` before trusting any filter — what are the keys ACTUALLY called — plus a named control: query something you know exists and confirm the filter finds it.
**Recurs when:** any `.get()`-based filter over a dict you did not define. An empty result is a claim about your query until proven a claim about the world.

## A long call times out, succeeds anyway, and retrying does it TWICE
**Symptom:** `rimworld/start_debug_game_ready` raised `RimBridgeError: timed out after 30.0s waiting for the bridge; RimWorld may be in a long event or the call may be frame-bound`. The map had generated normally — a fresh connection ~30 s later found it live with 34 pawns.
**Cause:** map generation is a long main-thread operation that outruns the client's 30 s timeout. The timeout is a property of how long we were willing to wait; nothing cancels the operation when the client stops listening.
**Fix:** ❌ do not retry on that connection — the late response desyncs it. ❌ do not re-issue on a fresh connection either: `start_debug_game_ready` is **not idempotent** and a second call generates a **second map**. ✅ drop the connection, open a fresh one and poll the post-condition — `jawa/list_pawns` either succeeds or returns `{'success': False, 'message': 'No current map. Load a game first.'}`. Two polls, ~30–45 s.
**Recurs when:** any bridge call that can exceed 30 s — `start_debug_game_ready`, `spawn_*`, `fire_incident`, loading a save. Timeout plus non-idempotent call is the dangerous pair; establish idempotence *before* retrying, and never infer "it failed" from "it timed out".
⏱️ **Measured 2026-08-13 on the 580-mod stack: `start_debug_game_ready` took 78.5 s**, not the ~30 s implied above — plan for well over a minute, and poll rather than guessing a sleep. Two independent runs the same day needed 8 polls at 10 s and one run of 78.5 s.
⚠️ **It needs `rimworld/go_to_main_menu` first** if a game is already loaded; from inside a running colony it will not start a fresh one.
🔴 **And it DISCARDS the current map without further warning** — that is how it gets you a clean map. Anything another seat left on the old one is gone. Announce before calling it, and check nobody is mid-audit.

## 🔴 Foundation can only be laid on BARE ground — a floor blocks it permanently
**Symptom:** `jawa/set_terrain_batch` with `layer='foundation'` reported `cellsChanged: 16` and `cellsFailedVerify: 12` on a 4×4 rect; only 4 cells held `Substructure`. The 12 that failed were exactly those already carrying `OuterRim_StoneHex_Slate` over `Soil`.
**Cause:** RimWorld refuses `SetFoundation` on any cell that already carries a floor terrain, **and the refusal is silent at the write**. Controlled three ways — bare ground: 25 changed / 0 failedVerify / 25 hold; `MetalTile` laid first: 25 changed / **25 failedVerify** / 0 hold; foundation first then floor: 25 / 0 / 25 hold, surviving the floor.
**Fix:** 🔴 the build order is the only order that works — **foundation → terrain → things**. There is no retrofit: a floor is a one-way door, recoverable only by demolish and rebuild, and not detectable by inspection afterwards. `cellsChanged: 16` was true and useless; only the read-back caught it, before 4,057 cells of silent failure went into a live build.
**Recurs when:** ⚠️ assuming affordance gates spawning — it does not. `GravshipHull` has `terrainAffordanceNeeded=Substructure` and spawns happily on bare ground, because `jawa/spawn_batch` routes through `GenSpawn`, which checks no affordance. Affordance constrains the build *designator*. A substructure-less ship is buildable and **not a gravship**, which is worse because everything looks right.

## Multi-cell things spawn CENTRED on the cell you name
**Symptom:** `jawa/spawn_batch` `GravEngine:172,172` — a 3×3 — occupied **x 171–173, z 171–173**.
**Cause:** `GenAdj.OccupiedRect` computes `minX = loc.x - (w-1)/2`, so the named cell is the centre. An offline audit found 18 machines emitting their min corner instead.
**Fix:** emit centres in any `Def:x,z` op grammar, and test coordinate semantics with the largest thing you have, never the most common one.
**Recurs when:** a plan that is 95% single-cell — 1×1 things are identical under both readings, so the plan looks perfect while every large thing places wrong.

## 🔴 You cannot enslave a pawn in your own faction — and `T: Enslave` says `success: true`
**Symptom:** `Actions\T: Enslave` returned `success: true` on four player colonists and **zero slaves existed afterwards**. `effects.logCount` was **0** — the call logged nothing at all, so there was no error to notice. Making them prisoners first changed nothing: still `success: true`, still `4 Prisoner / 0 Slave` in the save.
**Cause:** a GAME rule, not a bridge defect. A pawn already in your faction cannot be enslaved; it must belong to another faction first. That holds in the UI too — the bridge merely fails to say so. `T: Turn into prisoner` sets `guestStatus` **without changing faction**, so prisoner-first does not satisfy it either.
**Fix:** spawn into a *named* other faction, imprison, then enslave — `jawa/spawn_pawn {"kindDef":"Drifter","faction":"OuterRim_BinaryStarRaiders"}`, then `Actions\T: Turn into prisoner` and `Actions\T: Enslave` on `pawnId` = `"Thing_" + id`. Verified in the save: `4 Prisoner / 2 Slave`. ⚠️ Never pass `"hostile"` — it resolves via `FirstOrDefault` to Insect/Hive on this map, and a humanlike pawn there throws inside `PawnGenerator.GeneratePawn` (*"Humanlike pawn X was added to non-humanlike faction hive"*), an intermittent-looking separate failure.
**Recurs when:** any mutation refused by a game rule rather than a bug — the engine never attempts it, so there is nothing to log, and the return value, `effects.logCount` and the absence of an error all agree and all are wrong. Choose the readback channel by what it can **express**: `jawa/list_pawns` has no `guestStatus` field, so only `save_game` + grep of the `.rws` could tell success from failure.

## `Thing.set_Rotation` returns SILENTLY on a locked pawn, and the lock is saved
**Symptom:** a pawn is turned east and frozen for an art shot; the next call turns it north and reports the turn, and the pawn is still facing east. Nothing errors, nothing logs.
**Cause:** `Thing.set_Rotation` opens with `if (value == rotationInt || debugRotLocked) return;` — the freeze that makes the first turn *hold* is the same thing that makes every later turn a no-op. So the order is not a style choice: **clear `debugRotLocked`, set `Rotation`, re-lock.** Any other order writes nothing. Worse, `debugRotLocked` is written by `Thing.ExposeData`, so it goes into the `.rws`: a pawn left locked comes back locked after a load, and re-faces itself never again.
**Fix:** `jawa/set_pawn_rotation` does clear→set→lock and reports `applied` from a read-back of `pawn.Rotation`, not from "no exception". **Always call it again with `dir='unlock'` when the audit ends** — otherwise the next session inherits a pawn that cannot turn, with no visible cause. Without the lock at all, `Pawn_RotationTracker.UpdateRotation` re-faces the pawn on the next tick from its job and path, and a **drafted** pawn is slammed to South every tick.
**Recurs when:** any "freeze this so I can look at it" flag — the mechanism that defends the value against the engine also defends it against you, and if the flag persists to disk the damage outlives the session. Ask of every debug flag you set: does `ExposeData` write it?

## The renderer ignores `Rotation` for any laying pawn, so turning a downed one is a no-op
**Symptom:** `jawa/set_pawn_rotation` reports the rotation applied and read back correctly on a downed raider, and the screenshot shows it facing exactly as before. The field genuinely holds the new value.
**Cause:** `PawnRenderer` reads `Thing.Rotation` only for a **standing** (or crawling) pawn. For anything laying down — downed, sleeping, resting in a bed — it calls `PawnRenderer.LayingFacing()`, which derives the facing from the bed, the current job, or `thingIDNumber % 4`. `Rotation` is not consulted at all, so the write is real and invisible. Sleeping colonists and every downed test pawn are in this state.
**Fix:** stand the pawn up before photographing it, or accept the facing the bed gives you. `jawa/set_pawn_rotation` returns `posture` and `visible: false` per pawn and says so in `message` — believe that field over the picture you expected. In a proof harness, run rotation checks **before** the damage checks, or the pawn is downed by the time you turn it and a working tool records a FAIL.
**Recurs when:** a field the game reads only in some states — the read-back proves the *write*, never the *effect*. Verify against the channel that actually consumes the value, and ask which state the consumer is in.

---

## Fixed in the companion — one line each

Real traps, closed by the **B0** deploy. If a symptom below returns you are running
a **stale companion DLL**: rebuild and redeploy with the game closed
(`src/RimMandrake/bridgetools/build.py --apply`).

- **Terrain layer `'foundation'`** is accepted by `set_terrain`, `set_terrain_batch` and `get_terrain_batch`. Stale-build tell: `layer must be 'top' or 'under'`. `Substructure` lives in **`foundationGrid`**, a third grid beside `topGrid` and `underGrid` that `TerrainGrid.SetUnderTerrain` cannot reach, and 10 defs in `Buildings_Gravship.xml` (`GravshipHull`, `GravFieldExtender`, `PilotConsole`, …) demand it via `terrainAffordanceNeeded`.
- 🔴 **`jawa/list_factions` emits `countReturned`, `countAllIncludingHidden` and `isCompleteList`.** Stale-build tell: a bare `count`, which is the **visible subset only** — it read **34** against a true **54**, dropping 20 hidden factions including `Mechanoid` ("Oxslin Mechhive", `permanentEnemy`, goodwill −100). `includeHidden` defaults to `false` and the warning lived only in `message`, which no JSON caller reads.
- **`jawa/get_def` comps carry a `fields` map** of public scalar/string/enum/Def values by reflection. Stale-build tell: comps render as `{class, compClass}` only, so `GravEngine` returns 2,701 characters with **no field containing "radius"** and cannot answer what `CompProperties_SubstructureFootprint` holds. Stat values were always visible — `SubstructureSupport 632.7954` matched the owner's setting.

## An unknown parameter name is dropped silently, so the tool sees a caller who asked for nothing
**Symptom:** OPS fired six `jawa/damage` calls at a droid and nothing happened. Payload said `"success": false` while the envelope said `"Status": 2, "Success": true`. The conclusion very nearly filed was "the ion weapon is broken" — against a weapon that downs its target on the first correct hit.
**Cause:** the call passed `targetId`. `jawa/damage` takes **`thingId`**. The bridge SDK drops parameters the tool does not declare, before the tool runs — so the handler cannot see that you passed anything at all, and a wrong NAME is indistinguishable from an omitted one. The old code then fell through to the x/z branch with the defaults of -1, past a bounds check that tested only the upper bound, and damaged the zero things in a nonexistent cell.
**Fix:** two halves, and the second is the general one. *For the caller:* the parameter is `thingId`, and `jawa/list_pawns` / `jawa/spawn_pawn` both return it as `id`. *For the tool author:* **a refusal must name the parameters the tool accepts.** `jawa/damage` now refuses an empty target explicitly, lists its accepted names, and says outright that `targetId`/`pawnId`/`id` are not among them and were dropped. Built, **not yet deployed** — the game was up.
**Recurs when:** any bridge tool, any misremembered parameter name. Note the shape: the failure is silent, one-directional, and looks exactly like the feature under test being broken — so it costs you a false finding about someone ELSE's work, not just a wasted call.

## The envelope's `Success: true` is not the tool's `success`
**Symptom:** `"Status": 2, "Success": true` on the operation envelope, with `"success": false` and a refusal message in the payload directly above it. Read at a glance, the call looks like it worked. Seen twice in one session — `rimworld/get_game_info` returning `status: no_game`, and every failed `jawa/damage` call.
**Cause:** two different claims share a word. The envelope's `Success` means *the operation completed and returned a result*; the payload's `success` means *the game did the thing*. A tool that correctly refuses is a successful operation.
**Fix:** assert on the PAYLOAD field, never the envelope. `ok(resp)` in `prove_new_tools.py` gets this right — `resp.get("success") is True` on the parsed payload. Grepping raw output for `Success` matches the wrong one.
**Recurs when:** eyeballing raw JSON, and in any client that unwraps the envelope but reports its status.

## `rimworld/*` and `jawa/*` do not share a pawn identifier
**Symptom:** `rimworld/jump_camera_to_pawn {"pawnId":"Human333"}` returns *"Could not find current-map pawn id 'Human333'"* for a pawn that `jawa/list_pawns` had just returned as `id: Human333` and that `jawa/set_pawn_style` had just restyled by that same id.
**Cause:** the companion's tools resolve `Thing.ThingID`. The core `rimworld/*` tools use their own pawn addressing, which does not accept a ThingID.
**Fix:** read `x`/`z` off `jawa/list_pawns` and use `rimworld/jump_camera_to_cell`. Verified working immediately afterwards on the same pawn.
**Recurs when:** mixing the two tool families in one sequence — which is every screenshot workflow, since the camera verbs are core and the census verbs are ours.

## An armed architect designator swallows every later click, and nothing on the bridge disarms it
**Symptom:** after `select_architect_designator` + `click_cell`, all subsequent `click_cell` calls return `success: true` and select nothing — `list_selected_gizmos` returns `[]` forever, so no inspect panel can be read and no gizmo can be fired. Screenshots show the designator's "Shapes" palette still open with its refusal message pinned top-left.
**Cause:** the designator stays armed and consumes map clicks as designation attempts rather than selections. It is a *mode*, not a one-shot.
**Fix — none found from the bridge.** All of these were tried and all reported success while changing nothing: `press_cancel` ("Dispatched semantic 'cancel'… UI state did not change"), `right_click_cell` on empty ground, `clear_selection`, `close_context_menu`, `close_main_tab` ("No RimWorld main tab is currently open"), and `select_architect_designator` with a null id (errors). `get_designator_state` returned nothing useful. The owner clicking once in game clears it.
**Recurs when:** any use of `select_architect_designator`. ⚠️ **Treat arming a designator as a one-way door for the rest of your bridge session** — do every selection-based read you need FIRST, then designate last. Worth a companion tool that calls `Find.DesignatorManager.Deselect()` directly.

## 🔴 Zooming below the engine's floor renders the whole map FLAT RED — and it looks exactly like catastrophic texture corruption
**Symptom:** terrain replaced by flat saturated red/cyan/yellow blocks while pawns and UI text still draw correctly. Reads unmistakably as a broken texture atlas.
**Cause:** `rimworld/set_camera_zoom_extension {"enabled": true}` widens the camera range to 0..100. **`rootSize` below the engine's normal floor (~11) breaks the world mesh render.** `rootSize 6` produced it; 11–15 are clean.
**Fix:** keep `rootSize` ≥ 11, and **turn the extension off when you are done** — `{"enabled": false}`. It is not harmless litter.
**How to tell it apart from real corruption, cheaply:**
- **It heals.** Return to a legal `rootSize` and the frame is correct again. A corrupted atlas does not heal in place.
- **PNG file size is the corroborator.** Flat colour compresses tiny: the red frame was **0.49 MB** against **2.4–3.7 MB** for clean frames of the same scene. Check `ls -la` on the screenshot before believing your eyes.
- Bracket it: shoot at a legal zoom 30 s either side.
**Recurs when:** any wide-area capture, because the temptation is to zoom out past the floor to fit a big structure in frame. Use `rimworld/screenshot_cell_rect` instead.
🔴 **This nearly cost two false verdicts in one session** — OPS almost condemned eight working art mods, and BRIDGE diagnosed a corrupted texture atlas and told the owner to restart, wrongly blaming a peer's file prune. **The zoom artifact is more convincing than the real failure it imitates.**

## `take_screenshot` names files by the SECOND, so a burst silently collapses to one file
**Symptom:** four shots taken inside one second; four calls returned `success` with four paths; one file on disk. Three captures gone, no error.
**Cause:** the filename stamp has one-second resolution (`rimbridge_YYYYMMDD_HHMMSS`), and later writes overwrite earlier ones.
**Fix:** pass an explicit distinct `name` per shot, or space captures more than a second apart. Verify by `ls -la` on the directory, not by the returned path — the path is returned whether or not the file survived.
**Recurs when:** any scripted multi-shot pass, which is every contact sheet and every rotation audit.

## A jammed UI does NOT block the companion route
**Symptom:** with an architect designator armed, every `click_cell` selects nothing and `list_selected_gizmos` returns `[]` — the click-driven route is dead for the session.
**Cause/scope:** the jam is a UI *mode*. It only affects click-and-select.
**Fix — work around it, do not wait it out.** `jawa/spawn_pawn` places by coordinate, `jawa/set_pawn_rotation` and `jawa/set_pawn_style` act by `pawnId`, `jump_camera_to_cell` and `take_screenshot` need no selection at all. **A full spawn-rotate-photograph pass runs fine with the UI jammed** — measured by OPS, four spawns and screenshots, designator still armed throughout. Only inspect panels and gizmos are lost.
**Recurs when:** any session that has touched `select_architect_designator`.

## 🔴 A quicktest map reads as a campaign, so a census taken on one becomes a verdict on the other
**Symptom:** a faction census on the live map found **all 21 factions from the untick list present** and was read as *"the worldgen faction cut FAILED — regenerate the world now"*. That regeneration costs 25–30 minutes and would have been spent on nothing.
**Cause:** the map was a **dev quicktest** started via `rimworld/start_debug_game_ready` (rule 1c), not a generated campaign. **`start_debug_game_ready` never visits the Configure Factions page**, so a full default faction roster is the EXPECTED state. The cut was never offered, so it cannot have failed.
**Fix:** **state which map every census came from, in the same breath as the number.** A quicktest and a campaign are different CLAIMS, not different confidence levels in one claim.
**Tells that you are on a quicktest, any one of which is enough:**
- the default quicktest colonists are present — here `Human333` Alex, `Human336` Naoki, `Human340` Gwen
- nobody chose a scenario, storyteller or factions
- `ticksGame` is small and the colony has no history
⚠️ **A non-zero `ticksGame` plus living colonists is NOT evidence of worldgen.** Both are true on a map that was conjured in 30 seconds.
**Recurs when:** any world-, faction- or biome-level question asked of a map that BRIDGE created. This is the blast radius of rule 1c: making maps freely is cheap, and every census taken on one inherits the ambiguity. Caught 2026-08-13 by OPS before the regeneration was booked.

## 🔴 A correct measurement of the WRONG predicate — and a null baseline is the only thing that catches it
**Symptom:** `jawa/order_pawn` returned `canReach: true` for a pawn and a console, computed by a real `ReachabilityUtility.CanReach` call that ran, took the right arguments and answered honestly. It was **the wrong question**, and nothing in the response could say so.
**Cause:** the tool passed a **cell** with `PathEndMode.OnCell`. RimWorld's own launch gate passes the **thing** with `PathEndMode.InteractionCell` — `RitualBehaviorWorker_GravshipLaunch::PawnCanFillRole` IL_0065-006A, emitting `NoPathToPilotConsole` at IL_0072. **A pawn can reach the cell beside a console and still fail `InteractionCell`.** Those are two different verdicts wearing one field name, and `true` looks identical either way. Closing a launch gate on it would have been a confident, well-measured, wrong answer.
**Fix:** when a tool answers a question the GAME also asks, **read the game's own call and reproduce its arguments exactly** — not an equivalent-looking one. `targetId` + `pathEndMode` now do that (`bee5da9`). Where no engine call exists to copy, **score a null baseline**: CREATE caught the identical shape the same day in art, where a derivation recipe scored 77.2% against the donor's real texture and plain mirroring — doing nothing — scored 77.1%. A number with no baseline cannot tell "my method worked" from "anything would have scored that."
**Recurs when:** any predicate this bridge reports that the game evaluates for itself — reachability, buildability, launchability, "can this pawn fill this role". ⚠️ **This one is invisible to the first law.** `success: true` is not evidence *and neither is a correct number*: verifying that the tool ran, that the value is real, and that the value is honest all pass here. The only question that catches it is **"is this the same call the game makes?"** — so ask it before quoting a predicate at anyone, and never let a later cleanup "simplify" a mode argument back to a cell.

## 🔴 The bridge answering is NOT the game being reactive — ~40 seconds of it
**Symptom:** every readiness flag reads true — `currentMapReady`, `longEventPending` false, `playable` — the bridge answers calls normally, and mutations issued in the first half-minute produce results that cannot be attributed. Reads as an intermittent tool fault.
**Cause:** owner's measurement, 2026-08-14: **the game does not really become reactive until about forty seconds after the bridge first responds.** The bridge coming up and the simulation being ready to be driven are two different events, and every flag we have describes the first one.
**Fix:** wait out the window before mutating. `load_session.py --settle` defaults to 40 s and records the wait as a ledger row so nobody wonders later whether it was observed. **Read-only calls are fine inside it** — the tool census, a `get_def`, and the `LIVE BRIDGE TAKEN` announcement should all land immediately, not after the wait; only mutation is held.
**Recurs when:** any script that starts driving off a readiness flag. This is the same shape as the file's first law one level up: `success: true` says the tool ran, and a green readiness flag says the tool is *able* to run — neither says the game is in a state where your action means what you think. ⚠️ Do not "optimise" the settle away because a run once worked without it; the failure is intermittent by construction.

## 🔴 `python.exe` vs `python3` is a PER-SCRIPT choice, and the rule you carry points the wrong way half the time
**Symptom:** `preload_check.py` printed **NOT SAFE TO LOAD** for one seat and **SAFE TO LOAD** for two others, same commit, same minute, same files. It failed three Cherry Picker keys as unresolvable. A hand grep then "confirmed" it, and the pair went to the owner as a launch blocker. Both were wrong; the defs existed all along.
**Cause, and it is worse than a hardcoded path:** `preload_check.py:138` guards its platform-aware branch with `hasattr(GP, "STEAM_WORKSHOP")` — but `game_paths` exposes the attribute as **`WORKSHOP`** (`game_paths.py:64`, and it already resolves correctly under both interpreters). The guard is therefore **always False for every seat**, the resolved-path branch is dead code that has never once executed, and every run falls through to two hardcoded `/mnt/c/...` literals at `:139-140`. **A fallback that never falls back is indistinguishable from one that works, for as long as the fallback happens to be right.** **Windows Python cannot resolve a `/mnt/c` path**, so the Workshop root did not exist, every Workshop mod read as absent, and the gate reported a stack problem instead of its own blindness. The seat had run `python.exe` because of the standing rule *"use `python.exe`, never `python3` — WSL cannot reach the bridge."* **That rule is correct and it is about the NETWORK.** Applied to a script whose work is the FILESYSTEM, it silently inverts.
**Fix:** choose the interpreter from what the script TOUCHES, not from habit. **Talks to the bridge → `python.exe`** (WSL2 is NAT-mode and cannot reach Windows loopback). **Reads `/mnt/c` paths → `python3`.** Does both → it must resolve roots per-platform, and there is no interpreter that saves it. When a run disagrees with a peer's run of the same file, suspect the interpreter before the data.
**Recurs when:** any script that hardcodes one path style, and any rule that names a tool rather than a reason. ⚠️ **The deeper defect is that a MISSING root was indistinguishable from an EMPTY one** — `if not os.path.isdir(root): continue` swallows an absent root without a word, so the check failed OPEN and reported confidently. A configured root that is absent must make the tool REFUSE TO RUN, never report a result. Same mechanism produced the same seat's *"I grepped the whole tree"* an hour earlier: `common/RimWorld/Mods` + `Data` is **two of three roots**, and the missing third — `workshop/content/294100` — holds most of the stack. **Two wrong things pointing the same way read as corroboration.**

## 🔴 `?.` guards the RESULT, not the CALL — the whole companion is dead at a main menu
**Symptom:** at the main menu, **every** `jawa/*` tool returns a bare `Object reference not set to an instance of an object`. No tool name, no field, no hint that the cause is "there is no game". `jawa/get_def ThingDef/Steel` — a call that had worked all day — failed exactly like the brand-new `BiomeDef` branch, which is what proved it was environmental rather than a fresh bug.
**Cause:** almost every tool in the companion ends `ticksGame = Find.TickManager?.TicksGame ?? -1`. That **looks** null-guarded and is not. `Find.TickManager` compiles to `call Current::get_Game` then `ldfld Game::tickManager` — 11 bytes of IL with no null check. **With no game loaded, the GETTER throws before `?.` is ever reached**: the operator protects the value it returns, not the call that produces it. One unguarded property in a response field kills every tool that includes it.
**Fix:** ✅ **DONE 2026-08-14 — `TicksGameSafe()`, one helper, all 25 sites** (build md5 `d3ace1f6…`, 28 tools; deploys at the next shutdown window). `Current.Game != null && Find.TickManager != null ? Find.TickManager.TicksGame : -1` — `&&` short-circuits, so the getter is never touched until `Current.Game` is known non-null. Until that build is deployed, **the companion needs a GAME, not merely a map**: a quicktest fixes it instantly.
🔴 **Measured live at `programState: Entry`, and the live shape is worse than the IL suggested.** `jawa/get_defs` on two `RulePackDef`s returned a bare NRE whose stack names `<GetDefs>b__2 [0x002d4]` — the **response-construction** line, not the def lookup. **The defs had resolved correctly; the tool threw the right answer away while packing it.** So the symptom is not "the call could not run" but "the call ran, succeeded, and destroyed its own result" — and the message names nothing at all. ⚠️ **Defs are parsed once at startup and are not re-read when a game begins**, so every def question is answerable at the main menu and this bug is what made a whole class of no-game checks look impossible. It cost a real one: OPS's `maybeApostrophe` check had a closing window and could not be fired. ⚠️ Note the corollary for the run sheet — "this check needs no map" and "this check needs no game" are different claims, and a def read that is genuinely map-independent is still game-dependent.
**Recurs when:** any `Find.X` in a response field. `Find.CurrentMap` is safe (it null-checks internally); `Find.TickManager`, `Find.World` and friends dereference `Current.Game` and are not. ⚠️ Generalises past C#: **a null-safe operator on the last link of a chain says nothing about the links before it**, and the tidier the line reads the less likely anyone is to check. Measured live 2026-08-14 by comparing a known-good call against a new one — **keep a control you already trust in reach, because it converts "my new code is broken" into "the environment changed" in one call.**

## 🔴 A parameter you PASS is not a parameter that SURVIVES — the raid faction is rewritten by ref
**Symptom:** `jawa/fire_incident incidentDef=RaidEnemy faction=OuterRim_GalacticEmpire` returns `success: true`, a raid arrives, and it is **somebody else's raid**. Nothing in the reply flags the swap. The screenshot taken to answer *"does the Empire read as an antagonist"* is a photograph of a different faction.
**Cause, read out of `Assembly-CSharp` rather than recalled:** `IncidentWorker_RaidEnemy::TryResolveRaidFaction` keeps the faction you supplied **only if** it is non-null **AND** `FactionUtility::HostileTo(Faction.OfPlayer)` **AND** (`!deactivated` **OR** `parms.forced`). IL_001f, IL_0036 and IL_0055 all branch to IL_0059, where `ldflda IncidentParms::faction` passes the field **by reference** into `PawnGroupMakerUtility::TryGetRandomFactionForCombatPawnGroupWeighted` — which overwrites it with a weighted random pick. `IncidentParms` is a class, so the mutation is visible to the caller and invisible to anyone who does not look.
**Fix:** `dryRun=true` first and abort on `canFireNow:false`; then fire and **read the `faction` field in the REPLY, never the one you sent** — the companion reports `parms.faction` *after* the worker ran, so the read-back is the only evidence of which faction actually came. Pass `points` explicitly too: `points<=0` takes the storyteller default, which on a fresh quicktest is tens of points and answers no design question.
**Recurs when:** any engine worker taking a mutable parms object — raids, quests, trader arrivals. ⚠️ **Generalises past `IncidentParms`, and this is the half to carry: assert on the value READ BACK, never on the value sent.** Same shape as an unknown parameter name being dropped silently, arriving from the opposite direction — there the name never reached the tool, here it reached it and was overwritten. Both report `success: true`.

## 🔴 A tool built to break a conflation can INHERIT that conflation from the API it reads
**Symptom:** `jawa/biome_probe` was built specifically so a removal audit could tell *"the record was deleted"* from *"the record is still there at commonality 0"* — a real distinction, because a zeroed record still costs the world a def and comes straight back if anything re-weights it. The first build read `BiomeDef.AllWildAnimals` / `AllWildPlants`, reported `present: true/false`, and **could not tell the two apart at all.**
**Cause:** the engine's own resolved lists apply exactly the filter the tool existed to see past. `<get_AllWildAnimals>d__94::MoveNext` yields a kind only if `CommonalityOfAnimal > 0` **OR** `CommonalityOfPollutionAnimal > 0` **OR** `CommonalityOfCoastalAnimal > 0` (IL_0055 / IL_0063 / IL_0071); `get_AllWildPlants` filters on `CommonalityOfPlant > 0` (IL_0038). A zeroed record therefore drops out of both lists **identically to a deleted one**. Reading the resolved list *felt* like reading the truth, because the engine produced it.
**Fix:** decide the state against the **declared** records, not the resolved list — `spawning` (declared, resolves above zero) / `zeroed` (declared, weight 0) / `absent` (no record). On `BiomeDef` that means reflection: `wildAnimals`, `coastalWildAnimals` and `pollutionWildAnimals` are private; `wildPlants` is public.
**Recurs when:** any tool whose purpose is a distinction its data source has already collapsed. ⚠️ **Check the ENGINE's filter before trusting a list to be the whole set.** The failure is invisible in testing precisely because the tool agrees with the game — it inherits the game's blind spot and reports it with confidence. Caught 2026-08-14 only because VISION asked for the two columns to stay separate, which forced the question of whether they *could* be.

## The reflective def reader is blind to properties and privates, and says nothing about it
**Symptom:** twenty-eight biome removals were recorded as *"judged from def fields"*. No tool in this bridge can read those fields.
**Cause:** `Scalars()` — the reader behind `jawa/get_defs` and `jawa/get_def`'s `extra` block — enumerates `BindingFlags.Public | Instance` over **fields only**. No properties, no non-public. On `BiomeDef`, `wildAnimals`, `coastalWildAnimals`, `pollutionWildAnimals`, `diseases` and `allowedPackAnimals` are private, and `AllWildAnimals` / `AllWildPlants` are properties — so all seven are invisible. A field you *ask for* comes back `"(no such field)"`, which correctly flags a typo but reads identically to a field that exists and cannot be reached.
**Fix:** before trusting a conclusion drawn "from the def", check the instrument can SEE the field — `meta.py <Type>` in `ilprobe` lists visibility in one call. Where the answer is a property or a private, it needs a purpose-built tool, not another `fields=` list.
**Recurs when:** any engine type that caches its real answer behind a computed property — which is most of the interesting ones. ⚠️ **An absent reading and an unreadable one are not the same answer**, and only one of them is evidence. Same family as `strings -a` reporting a shipped method-body literal as ABSENT.

## A gate that greps "the source tree" greps the prose about it too
**Symptom:** the run sheet's tool-census derivation, written precisely so nobody would compare a live count against a stale number in a doc, returned **27** for a companion that defines **26**. A correct build would have failed the gate.
**Cause:** `grep -rhoE '"jawa/[a-z_]+"' src/RimMandrake/bridgetools/` sweeps the whole directory, and `prove_new_tools.py:112` contains the string `[Tool("jawa/x")]` **inside a comment** explaining how tool names are stored. The corpus included the commentary about the corpus.
**Fix:** scope the grep to the artifact's own language — `--include='*.cs'` → 26. Better still, derive from the built DLL, which cannot contain prose about itself.
**Recurs when:** any measurement whose corpus is a directory rather than a file type. **A derivation is only as good as its corpus**, and "derive it, never hardcode it" does not protect a derivation that is scoped wrong — it just moves the staleness somewhere less visible.

## 🔴 `search_debug_actions` walks the whole tree and FROZE the game — twice
**Symptom:** two `rimworld/search_debug_actions` calls each hung past a 120 s client timeout; the owner reported *"game appears frozen"*, then *"game is back"*. The answers eventually arrived and were worthless — six matches for "goodwill", all one `QuestPart` test entry.
**Cause:** it *"searches the full RimWorld debug-action tree globally by path, label, category and source metadata"* — with 585 mods that tree is enormous, and `limit` caps the RESULT, not the WALK. This is the same enumeration livelock already filed for pawn/def listing, arriving through a tool whose name sounds like a cheap lookup.
**Fix:** do not use it to answer *"does a debug action for X exist"*. Decide that from the engine instead — `ilprobe` on the type that would own the action — or accept the gap and build a companion tool. If it must be run, expect a stall and never fire a second one while the first is outstanding.
**Recurs when:** any global search tool on this bridge. ⚠️ **Generalises: `limit` bounds the answer, not the work.** A parameter that looks like a cost control is often only a truncation control, and the difference is invisible until the game stops rendering. Cost a real freeze 2026-08-14, on a seat that had this trap in its own file.

## Identify a thing by its accompanying signature, not by its own defName
**Symptom:** 4 `ChunkSlagSteel` on a map where our GenStep asked for ~50. **Were they ours, or vanilla's?** `ChunkSlagSteel` is scattered by vanilla and by other mods, so a second count of the same defName could never say — and the answer decided whether the step placed a handful or placed *nothing*.
**Fix:** look at what is AROUND the thing. Our def sets `filthDef` + `filthExpandBy`, so `jawa/list_things Filth_MachineBits rect=<box around the chunks>` returned **23** — the scatterer's own fingerprint — while `AncientCryptosleepCasket` in a 50×50 box returned **zero**, placing the ground hulk elsewhere entirely. **Ours, settled in two calls.**
**Recurs when:** any defName that more than one source can spawn — chunks, filth, corpses, ancient debris, most vanilla scatterables. 📌 **Counting the thing again cannot establish provenance; only its context can.** Pick a companion field your def sets and the other sources do not, and query for THAT.

## 🔴 An instrument can be blind to the exact branch that fails
**Symptom:** a scatter GenStep placed 4 of 50 things and logged **nothing**. The proposed fix was `<warnOnFail>true</warnOnFail>` — one field, the engine names its own failure. It would have shipped, cost a shutdown window, and reported nothing at all.
**Cause:** `warnOnFail` is read inside `GenStep_Scatterer::TryFindScatterCell`, the branch that finds a cluster **centre**. With `clusterSize > 1`, every member after the first goes down the *near-centre* branch instead, which never reaches that gate. **The instrument covered the one path that was working.** (The actual bug: `minSpacing` 4 against a hardcoded `ClusterRadius` 4 — about four members fit the disc, the fifth returns an invalid cell, and `GenStep_Scatterer::Generate` `ret`s **inside its loop**, discarding the other ~46.)
**Fix:** before shipping a diagnostic, name the branch you believe fails and check the diagnostic is *on that branch*. Two ungated `Log.Error`/`Log.Warning` calls in the same method already read zero, which was itself the clue: **a silent failure beside two loud paths that stayed silent means the failure is on neither of them.**
**Recurs when:** any opt-in logging flag, any `verbose` switch, any "turn on diagnostics and re-run". ⚠️ **Generalises hard: adding an instrument is a hypothesis about where the fault is.** If the hypothesis is wrong, the reading is a confident zero — and a window is gone. Also: **a partial result that looks like thinning can be an abort** — 4-of-50 read as "something is scaling the count down" and was really "it stopped at the 5th".

## 🔴 The denominator is the population that EXERCISED the rule
**Symptom:** a name-generation fix was declared confirmed on *"zero doubled apostrophes across 34 factions and 101 settlements"* — 135 generated names, which sounds overwhelming.
**Cause:** only the **Buzzer** namer carries the rule. Exactly **one** name in that set came from it. The grammar gives the defect branch weight 1 of 4, so **P(no defect visible | patch NOT applied, n=1) = 0.75** — a broken build had a 3-in-4 chance of producing precisely the observed result. The 135 was the population *collected*, not the population *at risk*, and it inflated a coin flip into a proof.
**Fix:** before quoting a sample size, ask **how many of these could possibly have shown the defect?** Then close on something deterministic instead — here, the absence of `Failed to find a node with the given xpath` for that mod in `Player.log`, given `PatchOperationFindMod` matched, proves both `Replace`s applied regardless of how many names rolled.
**Recurs when:** any "we checked N things and saw nothing" argument about a probabilistic defect. ⚠️ **A large irrelevant denominator is more dangerous than a small one, because it stops anyone asking.** Same family as *an absent reading is not a clean reading*.

## Client-call gotchas that cost real minutes — the exact spellings
Collected 2026-08-13; each one cost a seat time before it was written down.

- **There is no `rimbridge/list_tools`.** Use the protocol-level `tools/list`, or `rimbridge_client.py --list-tools`.
- **`RimBridge()` takes `timeout=`, not `read_timeout=`.**
- 🔴 **`RimBridge()` does NOT open the socket and does NOT find the token.** The constructor takes an explicit host/port/token; the token is regenerated every game start. Use `resolve_endpoint(None, None, None, None)` to scrape it from `Player.log`, then `rb.connect()`. Symptom of getting this wrong: `AttributeError: 'NoneType' object has no attribute 'sendall'`, then `session/hello failed: Invalid authentication token`.
- **WSL cannot reach the bridge at all** — RimBridge binds Windows loopback and WSL2 is NAT-mode. Run `python.exe`, never `python3`. This is not a timeout, it is no route.
- **`rimworld/set_camera_zoom` takes `{"rootSize": <number>}`** — a number, not a zoom name. `{"zoom": "Furthest"}` is an unknown key: dropped silently, `success: true`, camera does not move.
- **`rimworld/execute_gizmo` takes `{"gizmoId": "<id>"}`, not an index**, and the id changes every time the selection changes. Re-list; never cache one.
- **`rimworld/update_mod_settings` wants `values` as a DICT** — `{"gravEngineSupport": 4500}`. A list of pairs returns *"At least one settings path/value pair is required."*
- **`jawa/damage` takes `thingId`**, not `targetId`/`pawnId`/`id`. **`jawa/destroy_batch` takes `categories`**, plural.
- ⭐ **The pattern behind half of these: an unknown parameter name is DROPPED SILENTLY before the tool runs**, so a wrong name is indistinguishable from an omitted one and the call reports success. When a call succeeds and nothing happens, suspect the parameter NAME before suspecting the game.
