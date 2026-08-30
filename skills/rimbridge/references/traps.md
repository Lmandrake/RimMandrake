# RimBridge traps

📁 **Which file am I in?** This one catalogues **BRIDGE, CLIENT, BUILD and WORKFLOW**
mistakes. If a RimWorld ENGINE method reported success and changed nothing, you want
`silent-failures.md` instead — that is a different, larger catalogue.

🔎 **No index, by design — this file is appended to, not curated.** Grep it for your verb
and read the hits, plus every 🔴 entry.


Quick append log. Symptom, cause, fix, **recurs when**. Append and move on — no index, no numbering, no line anchors. Cite it as "as per the trap file". Every entry cost a real cycle. Promote into
`SKILL.md` anything that should change default behaviour, and delete it from here
when you do. Admission test and entry format:
`skills/rimworld-modding/references/traps.md`.

**First law — most entries below are a special case of it: `success: true` means
the tool RAN, not that the game CHANGED.**

**The entries marked 🔴 have each destroyed something real.** Read those before
your first mutation, whatever else you skip.

---


## `debugToolChanged: false` means nothing
**Symptom:** `effects.debugToolChanged: false` read as proof that `execute_debug_action` had done nothing; a confident bug report was filed against the mod for an unimplemented code path.
**Cause:** it is `false` on calls that demonstrably work, including one that killed a pawn outright. The bridge applies these directly without arming a UI tool, so the flag says nothing about success.
**Fix:** judge by world state. Calibrate any diagnostic against a known-good case before trusting its negative.
**Recurs when:** `effects.debugToolChanged` and `effects.logCount` — response metadata that describes the dispatcher, not the game.

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

## Verifying a compiled-out tool: attribute names are UTF-8 blobs, not UTF-16 literals
**Symptom:** a byte-scan of the deployed companion for its fourteen tool names reported a confident **0/14** — on a DLL containing all fourteen. Reads as "the deploy did not land", and the next hour goes to a deploy problem that does not exist.
**Cause:** the scan searched UTF-16, because .NET string *literals* live in the `#US` metadata heap as UTF-16. A tool name is a `[Tool("jawa/...")]` **custom attribute argument**, stored in the metadata **blob heap as length-prefixed UTF-8**. Different heap, same source text.
**Fix:** `verify_gm_gate()` in `src/RimMandrake/bridgetools/build.py` tests `name.encode("utf-16-le") in blob or name.encode("utf-8") in blob`. It was proven by building both ways and confirming it flips — 115,712 B "verified absent" against 125,440 B "in DLL" — and it `sys.exit`s if gated tools appear, so every way it can be wrong ends in "do not deploy". It gates `jawa/fire_incident`, the one tool that can drop a raid on the colony the owner is playing.
**Recurs when:** a build flag that flips `DefineConstants` without `--no-incremental` — MSBuild keys incrementality off timestamps, not properties, so a `--gm` run can hand back the previous non-GM DLL. Also: an XML comment cannot contain `--`, so documenting a `--flag` inside a csproj comment is an `MSB4025` build failure; name the property (`/p:JawaGmTools=true`).

**⚠️ The mirror image bit again on 2026-08-13, with this entry already written.** `strings -a "<dll>" | grep -F "No target. jawa/damage takes"` came back **ABSENT** on a DLL that contained it, because plain `strings` scans 7-bit ASCII and a method-body literal is UTF-16LE. The same command found `jawa/order_pawn`, `spawnedCount` and `countAllIncludingHidden` — attribute blobs and metadata member names, both UTF-8 — so the scan **looked** like it was working, and the false ABSENT was read as "the damage fix never deployed". **So: `strings -a` proves a tool NAME present; only `strings -a -el` proves a MESSAGE present, and a mixed check must run both.** The heap a string lives in is decided by whether it is an attribute argument or a literal, never by what you are trying to verify.
⛔ **Neither form is available any more, and that is correct:** the blind-scan hook refuses `strings`/`grep` on a `.dll`, after a census of this same file reported **16 of 115** tool names. Use a reader that opens both heaps — `build.tool_surface(open(dll,'rb').read())` in `src/RimMandrake/bridgetools/build.py` game-down, or `prove_new_tools.py --census` game-up, which measures both sides instead of quoting either.

## The companion DLL changes on every commit, by anyone, with no source change
**Symptom:** deploy the companion, byte-verify it (`identical, nothing to do`), commit the session's work, re-run `build.py` — and it reports **"differs, would overwrite"** against a game copy nothing had touched, with the game down throughout.
**Cause:** the SDK embeds the git HEAD SHA into `AssemblyInformationalVersion` as `0.1.0+<40-hex>`, and the PE timestamp and MVID are content hashes that move with it. Measured **96 of 125,440 bytes** differ between two builds of identical source at different commits. The build is deterministic — three consecutive `--no-incremental` rebuilds at one commit were byte-identical — so "differs" is a precise statement that the copies came from different commits. In a shared tree another agent's commit moves HEAD under you mid-session.
**Fix:** `plan_deploy()` splits one signal into three — bytes equal → `identical, nothing to do`; stamps differ → `built from a DIFFERENT COMMIT`, expected, prints both SHAs; **stamps equal and bytes differ → 🔴 `*** DRIFT ***`**, impossible for a deterministic build, so someone hand-edited the deployed DLL. Investigate before `--apply` destroys it.
**Recurs when:** any repo→game byte-compare of a built artifact. Never annotate a detector with "differs is expected" in a handoff — that is how the only drift check on the deploy path gets disabled.

## `token=NO` during a load is the game still loading, not the WSL bug
**Symptom:** `resolve_endpoint()` returns `127.0.0.1:5174` with **no token** and the first call dies with `AttributeError: 'NoneType' object has no attribute 'sendall'` — character-for-character the WSL-cannot-reach-the-bridge rule in `SKILL.md` §1, so you switch to `python.exe`, get the identical failure, and go hunting a networking problem that does not exist.
**Cause:** when you are already under `python.exe`, RimBridgeServer has not started yet. A cold load on this stack is 23–30 minutes and the bridge comes up late; `resolve_endpoint()` scrapes host/port/token out of `Player.log`, so before the startup line there is nothing to scrape. **An empty token is the tell** — a running bridge always has one.
**Fix:** settle it from the log before blaming the transport — `stat -c '%y %s' "$LOG"` (mtime ~now and small = still loading), `grep -ci rimbridge "$LOG"` (0 = server not started), `tail -3 "$LOG"` (def-loading lines = still in defs). A log being written **now** with no `rimbridge` line is a game mid-load; a **stale** log with no line is a game that is down.
**Recurs when:** two causes wearing one symptom — the symptom cannot be the diagnosis, so reach for the discriminator rather than the more familiar cause. `RimWorldWin64.exe` existing is not the service being ready.

## You cannot photograph a stale mesh — moving the camera repaints it
**Symptom:** paint a rect with `refresh=false`, screenshot, call `jawa/refresh_rect`, screenshot again — **the two images are identical and the "stale" one already shows the new terrain.** Reads as "refresh_rect does nothing".
**Cause:** every framed-shot tool moves the camera — `rimworld/screenshot_cell_rect` re-roots and re-zooms, `Session.look()` calls `jump_camera_to_cell` first — and camera movement re-enters the map sections, triggering the very redraw the test was trying to catch.
**Fix:** none available. `refresh_rect`'s **visible half is UNPROVEN** and this method cannot prove it; its data half is proven, in that it accepts a well-formed rect and refuses a malformed one. A real test needs a shot from an already-stationary camera taken before the unrefreshed paint, which no current tool composes.
**Recurs when:** any visual A/B over the bridge — ask what the act of looking changes. Also: the tool is `rimworld/jump_camera_to_cell`; there is no `jump_camera_to`.

## `jawa/list_pawns` returns `kind`, not `kindDef`
**Symptom:** 8 pawns spawned, `jawa/spawn_pawn` returning `success: true` with real ids, names and coordinates; the next `jawa/list_pawns` filtered on `p["kindDef"] == "Jawa_Spawn_Hutt"` returned **0**, and "neutral pawns despawn instantly" was stated out loud. Re-run against `kind`: **7 alive**, exactly where spawned.
**Cause:** there is no `kindDef` key, so `p.get("kindDef")` was `None` for every pawn and the filter matched nothing. A `KeyError` would have been caught instantly. "Faction `none` pawns are transient" is real RimWorld behaviour, so the wrong answer sounded like knowledge and survived three follow-up calls.
**Fix:** `print(json.dumps(pawns[0])[:300])` before trusting any filter — what are the keys ACTUALLY called — plus a named control: query something you know exists and confirm the filter finds it.
**Recurs when:** any `.get()`-based filter over a dict you did not define. An empty result is a claim about your query until proven a claim about the world.

---

## Fixed in the companion — one line each

Real traps, closed by the **B0** deploy. If a symptom below returns you are running
a **stale companion DLL**: rebuild and redeploy with the game closed
(`src/RimMandrake/bridgetools/build.py --apply`).

- **Terrain layer `'foundation'`** is accepted by `set_terrain`, `set_terrain_batch` and `get_terrain_batch`. Stale-build tell: `layer must be 'top' or 'under'`. `Substructure` lives in **`foundationGrid`**, a third grid beside `topGrid` and `underGrid` that `TerrainGrid.SetUnderTerrain` cannot reach, and 10 defs in `Buildings_Gravship.xml` (`GravshipHull`, `GravFieldExtender`, `PilotConsole`, …) demand it via `terrainAffordanceNeeded`.
- 🔴 **`jawa/list_factions` emits `countReturned`, `countAllIncludingHidden` and `isCompleteList`.** Stale-build tell: a bare `count`, which is the **visible subset only** — it read **34** against a true **54**, dropping 20 hidden factions including `Mechanoid` ("Oxslin Mechhive", `permanentEnemy`, goodwill −100). `includeHidden` defaults to `false` and the warning lived only in `message`, which no JSON caller reads.
- **`jawa/get_def` comps carry a `fields` map** of public scalar/string/enum/Def values by reflection. Stale-build tell: comps render as `{class, compClass}` only, so `GravEngine` returns 2,701 characters with **no field containing "radius"** and cannot answer what `CompProperties_SubstructureFootprint` holds. Stat values were always visible — `SubstructureSupport 632.7954` matched the owner's setting.

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
🔴 **This nearly cost two false verdicts in one session** — a retired seat almost condemned eight working art mods, and another seat diagnosed a corrupted texture atlas and told the owner to restart, wrongly blaming a peer's file prune. **The zoom artifact is more convincing than the real failure it imitates.**

## `take_screenshot` names files by the SECOND, so a burst silently collapses to one file
**Symptom:** four shots taken inside one second; four calls returned `success` with four paths; one file on disk. Three captures gone, no error.
**Cause:** the filename stamp has one-second resolution (`rimbridge_YYYYMMDD_HHMMSS`), and later writes overwrite earlier ones.
**Fix:** pass an explicit distinct `name` per shot, or space captures more than a second apart. Verify by `ls -la` on the directory, not by the returned path — the path is returned whether or not the file survived.
**Recurs when:** any scripted multi-shot pass, which is every contact sheet and every rotation audit.

## A jammed UI does NOT block the companion route
**Symptom:** with an architect designator armed, every `click_cell` selects nothing and `list_selected_gizmos` returns `[]` — the click-driven route is dead for the session.
**Cause/scope:** the jam is a UI *mode*. It only affects click-and-select.
**Fix — work around it, do not wait it out.** `jawa/spawn_pawn` places by coordinate, `jawa/set_pawn_rotation` and `jawa/set_pawn_style` act by `pawnId`, `jump_camera_to_cell` and `take_screenshot` need no selection at all. **A full spawn-rotate-photograph pass runs fine with the UI jammed** — measured by a retired seat, four spawns and screenshots, designator still armed throughout. Only inspect panels and gizmos are lost.
**Recurs when:** any session that has touched `select_architect_designator`.

## 🔴 `python.exe` vs `python3` is a PER-SCRIPT choice, and the rule you carry points the wrong way half the time
**Symptom:** `preload_check.py` printed **NOT SAFE TO LOAD** for one seat and **SAFE TO LOAD** for two others, same commit, same minute, same files. It failed three Cherry Picker keys as unresolvable. A hand grep then "confirmed" it, and the pair went to the owner as a launch blocker. Both were wrong; the defs existed all along.
**Cause, and it is worse than a hardcoded path:** `preload_check.py:138` guards its platform-aware branch with `hasattr(GP, "STEAM_WORKSHOP")` — but `game_paths` exposes the attribute as **`WORKSHOP`** (`game_paths.py:64`, and it already resolves correctly under both interpreters). The guard is therefore **always False for every seat**, the resolved-path branch is dead code that has never once executed, and every run falls through to two hardcoded `/mnt/c/...` literals at `:139-140`. **A fallback that never falls back is indistinguishable from one that works, for as long as the fallback happens to be right.** **Windows Python cannot resolve a `/mnt/c` path**, so the Workshop root did not exist, every Workshop mod read as absent, and the gate reported a stack problem instead of its own blindness. The seat had run `python.exe` because of the standing rule *"use `python.exe`, never `python3` — WSL cannot reach the bridge."* **That rule is correct and it is about the NETWORK.** Applied to a script whose work is the FILESYSTEM, it silently inverts.
**Fix:** choose the interpreter from what the script TOUCHES, not from habit. **Talks to the bridge → `python.exe`** (WSL2 is NAT-mode and cannot reach Windows loopback). **Reads `/mnt/c` paths → `python3`.** Does both → it must resolve roots per-platform, and there is no interpreter that saves it. When a run disagrees with a peer's run of the same file, suspect the interpreter before the data.
**Recurs when:** any script that hardcodes one path style, and any rule that names a tool rather than a reason. ⚠️ **The deeper defect is that a MISSING root was indistinguishable from an EMPTY one** — `if not os.path.isdir(root): continue` swallows an absent root without a word, so the check failed OPEN and reported confidently. A configured root that is absent must make the tool REFUSE TO RUN, never report a result. Same mechanism produced the same seat's *"I grepped the whole tree"* an hour earlier: `common/RimWorld/Mods` + `Data` is **two of three roots**, and the missing third — `workshop/content/294100` — holds most of the stack. **Two wrong things pointing the same way read as corroboration.**

## 🔴 `?.` guards the RESULT, not the CALL — the whole companion is dead at a main menu
**Symptom:** at the main menu, **every** `jawa/*` tool returns a bare `Object reference not set to an instance of an object`. No tool name, no field, no hint that the cause is "there is no game". `jawa/get_def ThingDef/Steel` — a call that had worked all day — failed exactly like the brand-new `BiomeDef` branch, which is what proved it was environmental rather than a fresh bug.
**Cause:** almost every tool in the companion ends `ticksGame = Find.TickManager?.TicksGame ?? -1`. That **looks** null-guarded and is not. `Find.TickManager` compiles to `call Current::get_Game` then `ldfld Game::tickManager` — 11 bytes of IL with no null check. **With no game loaded, the GETTER throws before `?.` is ever reached**: the operator protects the value it returns, not the call that produces it. One unguarded property in a response field kills every tool that includes it.
**Fix:** ✅ **DONE 2026-08-14 — `TicksGameSafe()`, one helper, all 25 sites** (build md5 `d3ace1f6…`, 28 tools; deploys at the next shutdown window). `Current.Game != null && Find.TickManager != null ? Find.TickManager.TicksGame : -1` — `&&` short-circuits, so the getter is never touched until `Current.Game` is known non-null. Until that build is deployed, **the companion needs a GAME, not merely a map**: a quicktest fixes it instantly.
🔴 **Measured live at `programState: Entry`, and the live shape is worse than the IL suggested.** `jawa/get_defs` on two `RulePackDef`s returned a bare NRE whose stack names `<GetDefs>b__2 [0x002d4]` — the **response-construction** line, not the def lookup. **The defs had resolved correctly; the tool threw the right answer away while packing it.** So the symptom is not "the call could not run" but "the call ran, succeeded, and destroyed its own result" — and the message names nothing at all. ⚠️ **Defs are parsed once at startup and are not re-read when a game begins**, so every def question is answerable at the main menu and this bug is what made a whole class of no-game checks look impossible. It cost a real one: a retired seat's `maybeApostrophe` check had a closing window and could not be fired. ⚠️ Note the corollary for the run sheet — "this check needs no map" and "this check needs no game" are different claims, and a def read that is genuinely map-independent is still game-dependent.
**Recurs when:** any `Find.X` in a response field. `Find.CurrentMap` is safe (it null-checks internally); `Find.TickManager`, `Find.World` and friends dereference `Current.Game` and are not. ⚠️ Generalises past C#: **a null-safe operator on the last link of a chain says nothing about the links before it**, and the tidier the line reads the less likely anyone is to check. Measured live 2026-08-14 by comparing a known-good call against a new one — **keep a control you already trust in reach, because it converts "my new code is broken" into "the environment changed" in one call.**

## 🔴 A parameter you PASS is not a parameter that SURVIVES — the raid faction is rewritten by ref
**Symptom:** `jawa/fire_incident incidentDef=RaidEnemy faction=Empire` returns `success: true`  *(example re-pointed 2026-08-20: the Galactic Empire's vessel is vanilla `Empire`, not ~~`OuterRim_GalacticEmpire`~~ — `infrastructure/state/OWNER_DECISIONS.md`. The trap itself is unchanged.)*, a raid arrives, and it is **somebody else's raid**. Nothing in the reply flags the swap. The screenshot taken to answer *"does the Empire read as an antagonist"* is a photograph of a different faction.
**Cause, read out of `Assembly-CSharp` rather than recalled:** `IncidentWorker_RaidEnemy::TryResolveRaidFaction` keeps the faction you supplied **only if** it is non-null **AND** `FactionUtility::HostileTo(Faction.OfPlayer)` **AND** (`!deactivated` **OR** `parms.forced`). IL_001f, IL_0036 and IL_0055 all branch to IL_0059, where `ldflda IncidentParms::faction` passes the field **by reference** into `PawnGroupMakerUtility::TryGetRandomFactionForCombatPawnGroupWeighted` — which overwrites it with a weighted random pick. `IncidentParms` is a class, so the mutation is visible to the caller and invisible to anyone who does not look.
**Fix:** `dryRun=true` first and abort on `canFireNow:false`; then fire and **read the `faction` field in the REPLY, never the one you sent** — the companion reports `parms.faction` *after* the worker ran, so the read-back is the only evidence of which faction actually came. Pass `points` explicitly too: `points<=0` takes the storyteller default, which on a fresh quicktest is tens of points and answers no design question.
**Recurs when:** any engine worker taking a mutable parms object — raids, quests, trader arrivals. ⚠️ **Generalises past `IncidentParms`, and this is the half to carry: assert on the value READ BACK, never on the value sent.** Same shape as an unknown parameter name being dropped silently, arriving from the opposite direction — there the name never reached the tool, here it reached it and was overwritten. Both report `success: true`.

## 🔴 A tool built to break a conflation can INHERIT that conflation from the API it reads
**Symptom:** `jawa/biome_probe` was built specifically so a removal audit could tell *"the record was deleted"* from *"the record is still there at commonality 0"* — a real distinction, because a zeroed record still costs the world a def and comes straight back if anything re-weights it. The first build read `BiomeDef.AllWildAnimals` / `AllWildPlants`, reported `present: true/false`, and **could not tell the two apart at all.**
**Cause:** the engine's own resolved lists apply exactly the filter the tool existed to see past. `<get_AllWildAnimals>d__94::MoveNext` yields a kind only if `CommonalityOfAnimal > 0` **OR** `CommonalityOfPollutionAnimal > 0` **OR** `CommonalityOfCoastalAnimal > 0` (IL_0055 / IL_0063 / IL_0071); `get_AllWildPlants` filters on `CommonalityOfPlant > 0` (IL_0038). A zeroed record therefore drops out of both lists **identically to a deleted one**. Reading the resolved list *felt* like reading the truth, because the engine produced it.
**Fix:** decide the state against the **declared** records, not the resolved list — `spawning` (declared, resolves above zero) / `zeroed` (declared, weight 0) / `absent` (no record). On `BiomeDef` that means reflection: `wildAnimals`, `coastalWildAnimals` and `pollutionWildAnimals` are private; `wildPlants` is public.
**Recurs when:** any tool whose purpose is a distinction its data source has already collapsed. ⚠️ **Check the ENGINE's filter before trusting a list to be the whole set.** The failure is invisible in testing precisely because the tool agrees with the game — it inherits the game's blind spot and reports it with confidence. Caught 2026-08-14 only because a seat asked for the two columns to stay separate, which forced the question of whether they *could* be.

## A gate that greps "the source tree" greps the prose about it too
**Symptom:** the run sheet's tool-census derivation, written precisely so nobody would compare a live count against a stale number in a doc, returned **27** for a companion that defines **26**. A correct build would have failed the gate.
**Cause:** `grep -rhoE '"jawa/[a-z_]+"' src/RimMandrake/bridgetools/` sweeps the whole directory, and `prove_new_tools.py:112` contains the string `[Tool("jawa/x")]` **inside a comment** explaining how tool names are stored. The corpus included the commentary about the corpus.
**Fix:** scope the grep to the artifact's own language — `--include='*.cs'` → 26. Better still, derive from the built DLL, which cannot contain prose about itself.
**Recurs when:** any measurement whose corpus is a directory rather than a file type. **A derivation is only as good as its corpus**, and "derive it, never hardcode it" does not protect a derivation that is scoped wrong — it just moves the staleness somewhere less visible.

## 🔴 `search_debug_actions` walks the whole tree and FROZE the game — twice
**Symptom:** two `rimworld/search_debug_actions` calls each hung past a 120 s client timeout; the owner reported *"game appears frozen"*, then *"game is back"*. The answers eventually arrived and were worthless — six matches for "goodwill", all one `QuestPart` test entry.
**Cause:** it *"searches the full RimWorld debug-action tree globally by path, label, category and source metadata"* — with ~575 mods that tree is enormous, and `limit` caps the RESULT, not the WALK. This is the same enumeration livelock `SKILL.md` §4 forbids, arriving through a tool whose name sounds like a cheap lookup.
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
- 🔴 **`jawa/order_pawn` UNPAUSES the game by default.** Pass `unpause: false`. Measured 2026-08-15: the owner had deliberately left time stopped, one `order_pawn` ran the clock from tick 1035 to 19634 (~5 in-game hours) across a few calls, and nothing in the reply says time moved. Verify with two `ticksGame` reads seconds apart, not with the call's own `success`.
- **`jawa/order_pawn` `timeoutSeconds` is the SERVER's ceiling, not the client's.** Setting it above the client's 30 s socket timeout kills the connection mid-call — `timed out after 30.0s waiting for the bridge`. Keep `waitTicks` small enough to answer inside 30 s and loop, rather than asking for one long wait.
- **An UNDRAFTED pawn does not hold a move order** — it walks off to its own AI job, so a reachability measurement reads as failure. Draft for the measurement (`draft: true`), undraft only when you want the pawn to take a work job at the destination.
- 🔴 **A FactionDef's defName is not its filename.** `JawaAscendantHelix.xml` contains `<defName>Jawa_AscendantHelix</defName>`. Querying the filename returns `found=false`, which reads exactly like the def being absent — and on 2026-08-15 that manufactured a false "five factions are still broken" finding that was reported to another seat. Read the defName out of `<defName>`. A control def in the same call does NOT catch this unless the control is misspelt the same way.
- 🔴 **`Actions\T: Destroy` with `thingId` can kill something you did not name.** Measured 2026-08-15: 77 pawns targeted by explicit `Thing_<id>`, **78 died** — the one survivor I had deliberately excluded by name was destroyed too, and 3 of the 77 calls reported `success: false`. Cause not established; suspect an unresolvable `thingId` falling back to the current selection or the cursor cell. **Never fire a long batch of destroy calls and check the total only at the end** — re-read the survivor set every ~10 and abort on the first unexpected loss. Losing one wrong pawn is invisible in an aggregate count.

## Five traps from the 2026-08-15 unattended collection run

### 🔴 `set_camera_zoom` takes `rootSize` (a NUMBER), not `zoom` (a string)
`{"zoom": "Close"}` returns `success: true` and does **nothing** — the unknown
parameter name is dropped before the tool runs, exactly as the one law says. Every
screenshot in that session came out at max zoom while the calls all reported success,
and `get_camera_state` kept answering `zoomRange: "Closest"`.
Correct: `{"rootSize": 14.0}`. Roughly: 8–11 is nose-to-the-ground, **14 frames two
things six cells apart**, 60 is the far limit.
**Generalises to:** when a call succeeds and the picture does not change, read the
tool's own `inputSchema` off `list_tools` before doing anything else. Do not trust a
parameter name you inferred from a sibling tool.

### 🔴 A modal dialog FREEZES the rendered frame and corrupts its colours
While `Verse.Dialog_NodeTree` (a trade/comms offer) was open, `take_screenshot`
returned a **stale frame in wild false colour** — pure red ground, cyan water,
magenta pawns — with the clock frozen, while the UI layer on top drew correctly.
It is not a GPU fault and not a mod: `ticksGame` advanced exactly 60 on a stepped
call, so the SIM was alive and only the render was stuck.
🔑 `jawa/clear_ui` does **NOT** close it — it reports `closedCount: 0` and lists the
dialog in `remaining`. Use `rimworld/close_window {"windowType": "Dialog_NodeTree"}`,
which closes it cleanly; the very next screenshot renders correctly.
**Generalises to:** before believing anything you see in a screenshot, check
`clear_ui`'s `remaining` list. A window it cannot close can silently invalidate every
image you take, and false colour is easy to misread as an art or shader defect.

### ⚠️ Nothing on the bridge orders an ATTACK
No verb issues `JobDefOf.AttackMelee`. A drafted colonist holds at `Wait_Combat`
forever; `jawa/order_pawn` issues a GOTO whether given `targetId` or the enemy's own
cell; pawns from `jawa/spawn_pawn` have **no lord** so hostiles idle; and
`Actions\Spawn large enemy raid` plus 5,600 stepped ticks never produced an engagement
at the drafted pawn. Any "what does it look like DURING an attack" item is therefore
uncollectable unattended today.
Equipping, by contrast, is solved: `rimworld/select_pawn`, then
`Actions\Equip primary (selected)...\<WeaponDefName>` (808 leaves).
⛔ `Actions\Play Animation...` does not substitute — 208 leaves, **zero** `AM_` ones.
Melee Animation's 33 `AM_Duel_*`/`AM_Execution_*` AnimDefs are in the def dump but are
not exposed to that menu; they fire from real melee jobs only.

### ⚠️ `jawa/list_pawns` cannot tell you what a pawn is HOLDING
There is no equipment/weapon field — the record is id, kind, xenotype, position,
health, flags. `rimworld/get_selected_pawn_inventory_state` reads INVENTORY, not the
equipped primary. The cheapest reliable read of a primary weapon is a **screenshot of
the Gear panel** ("Equipped: Lightsaber (normal)"), which is also independent evidence
rather than the equip call's own `success`.

### ⚠️ `jawa/inspect_string` takes `thingIds`, and a JSON LIST throws
Singular `thingId` is dropped and the tool answers *"Give thingIds, defName, or
rect"*. Passing `thingIds` as a JSON array throws
`System.InvalidCastException: Object must implement IConvertible`. Pass a
**comma-separated string**.

### 🔑 Two things that worked first time, worth reaching for
* `rimworld/screenshot_cell_rect {x, z, width, height, paddingCells}` frames and crops
  to a cell rect — better than aiming the camera by hand. It writes
  `<name>__cell_rect.png`, not `<name>.png`.
* `rimworld/start_debug_game_ready {"readiness": "playable", "pauseIfNeeded": true}`
  took a quicktest colony from the main menu to paused-and-drivable in **118 s**, and
  returns the whole readiness ladder so there is nothing to poll yourself.

### ⚠️ From WSL, `python.exe` dies on non-ASCII output
`UnicodeEncodeError: 'charmap' codec` on a tool message containing an em-dash — the
call had already SUCCEEDED, so this destroys the report, not the work. Open every
bridge script with `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.

---

## 🔴 `Player.log` PERSISTS between runs — the readiness grep matches the LAST session

Grepping `Player.log` for `GABP server running standalone` to know the bridge is up
**returns instantly on a stale line from the previous run**, before the new game has even
started. You then connect, get `ConnectionRefused`, and go looking for a bridge fault that
does not exist.

**Wait for the log to TRUNCATE first.** `src/RimMandrake/bridgetools/launch_and_wait.sh`
records the size, waits for it to shrink, and only then looks for the marker.

## 🔴 Kill RimWorld BEFORE building the companion

`build.py` cannot overwrite a memory-mapped DLL and says so clearly — but a piped `grep`
can hide the refusal, and you then spend a whole cycle testing **stale code** and
concluding a new tool "was not found". Always `taskkill` first, and check for the word
`deployed` in the output rather than assuming.

## ⚠️ A docstring containing `jawa/world_*` made build.py report a phantom lost tool

`build.py` extracts tool names by scanning the assembly for `jawa/...` literals. A
docstring saying *"use the `jawa/world_*` family"* produced a phantom tool named
`jawa/world_`, and the next build "lost" it and refused to deploy. **Avoid `jawa/` prefixes
in prose inside tool descriptions.** The guard is right; the input was ambiguous.

## ⚠️ `rimworld/search_debug_actions` timed out at 30 s even on a 13-mod list

The documented debug-discovery hang is **not** only a heavy-modlist problem. Do not call
the four `*_debug_action*` discovery tools as if they were reads.

## ⚠️ An "ended" GameCondition still lists while the game is PAUSED

There is no `EndNow()`. Ending sets `Duration = TicksPassed`, which expires on the **next
tick** — so a paused game still shows it in `ActiveConditions` and it reads as a failed
end. Step a few ticks and it clears. Measured.

## ⚠️ A bare `catch {}` in your own tool is the same bug you are hunting

Written by me, 2026-08-19: the zone builder swallowed `AddCell` refusals, and a 6×6
stockpile silently took **11 of 36 cells** while reporting success. **If the engine can
refuse a cell, report which cells and why** — the whole value of a bridge tool over a
direct API call is that it explains itself.

---

## `Actions\Spawn Pawn...` reports success and places nobody on a blocked cell

CHECK, 2026-08-20. A 69-race lineup reported `ok=69 fail=0`; the map held **64**.
`execute_debug_action` returns `success: true` whether or not the pawn lands, so
five kinds — Chiss, Gamorrean, Herglic, Kaleesh, Kaminoan — vanished without a
word. Nothing was wrong with those defs: each spawned first try when given a free
cell, so the cause is the CELL, not the kind.

**Count what arrived, never what the spawner claimed.** `jawa/list_pawns` grouped by
`kindDef` and diffed against the requested list names the missing ones in one call.
Generalises to every `spawn`-family debug action.

## `jawa/destroy_batch` will not destroy pawns, and says so quietly

Same session. `rects` (not `thingIds`) is the required argument, and the reply ended
`"Destroyed 2 thing(s) across 9 cell(s); 2 pawn(s) left alone."` — the two pawns were
the entire point of the call. The refusal is real and it is in the message, but the
call is a `success`, so a script that checks only the flag deletes nothing and moves on.

## `jawa/clear_ui` defaults do NOT close an open info card

Same session, and it cost a screenshot: `clear_ui` with its defaults reported
`deselected 0 thing(s)` and `get_game_info` showed `selectedPawns: []`, yet the shot
came back with a full character card — Bio/Inventory/Health tabs — covering the frame.
`devWindows` covers `Window_Dev` descendants and `clearSelection` covers the bottom-left
pane; the info card is neither. **`{"all": true}` closes it.** Read back the pixels, not
the deselect count.

## `rimworld/load_game_ready` is NOT a readiness poll

CHECK, 2026-08-20, and it cost two dead waits totalling ~10 minutes. The name reads as
"is the game ready after a load"; it is not. It takes a **`saveName`** and answers whether
**that save exists and can be loaded** — a PREcondition check, not a POSTcondition. Called
with no argument it invents a default name, fails to find it, and returns
`success: false, "Save 'rimbridge_save_<timestamp>' does not exist."` forever. A polling
loop written around it never exits, while the game sat fully loaded the whole time.

**To wait out a load, poll `rimworld/get_game_info` for `status == "game_loaded"`** and a
`ticksGame` that answers. That is the postcondition.

## `rimworld/save_game` DOES honour a filename — under `saveName`

Same session, and it corrects a line that stood in the skill for months. `{"saveName":
"rt_probe"}` wrote `rt_probe.rws`. The old note said the tool "ignores your `fileName`":
it does, because `fileName` is not a parameter it has, and **an unknown parameter name is
dropped before the tool runs** — the documented failure mode, mistaken for a tool quirk.
Generalises: before recording "tool X ignores argument Y", check Y is spelled the way the
schema spells it.

## An unasserted string-replace in a patch script is a silent no-op

CHECK, 2026-08-20, correcting my own work from the night before. I "fixed"
`world_links_import` with a Python `s.replace(old, new)` whose `old` did not match the
file. `replace` does not raise when it matches nothing — it returns the string unchanged.
The build succeeded, the commit went out claiming a fix, the deploy was byte-verified, and
the tool was still broken. Only running it proved otherwise, a load later.

**Every scripted edit asserts its target exists before writing**, and asserts something
about the CONTEXT too — `assert old in s` catches a typo, but checking that the line sits
next to `ContainsKey("kind")` is what proves you are editing the call site you meant. A
build succeeding says the file still compiles, not that your change is in it.

## `.get("children") or []` turns a FAILED call into "zero results"

CHECK, 2026-08-20. `list_debug_action_children("Actions")` was returning
`success: false` with a NullReferenceException, and my reader did
`len(r.get("children") or [])` — printing "Actions children: 0". I read that as an empty
tree and went looking for why dev mode was off. Dev mode was on; the call was failing.

**Assert on `success` before reading the payload.** `or []` is the same defect as ignoring
an exit code: it converts "I could not answer" into "the answer is nothing", and those need
completely different responses. Generalises to every `.get(x) or default` over a bridge
reply.

## Three parameter names that produced fake catastrophes in one session — 2026-08-21, CHECK

All three calls returned `success: true` and answered a **different question than was asked**.
An unknown parameter name is dropped before the tool runs, so a wrong name is
indistinguishable from an omitted one. Generalises to: **every one of these looked like a
devastating content finding, and every one was the caller.**

| I passed | the tool wants | what it looked like |
|---|---|---|
| `jawa/pawn_get` `pawnId=` | **`pawn=`** | the param was dropped, the tool returned its brief LISTING with no `equipment` field, and every pawn read as unarmed — **a clean 0 of 270 armed** |
| `jawa/spawn_pawn` `faction="hostile"` | the kind's **own faction defName** | all 67 of our kinds carry `useFactionXenotypes: true`, so xenotype comes from the faction the pawn JOINS — reading **"49 of 55 kinds spawn Baseliners"**, i.e. the species identity of twelve factions apparently gone. Re-spawned into their own factions: Geonosians 4/4, Jawa 5/5, a five-species mercenary company. Exactly one faction was genuinely wrong |
| `rimworld/load_game` — | *(name was right)* | it returned `success: false, code: "save.missing_mods"` naming the mod, and I diagnosed "the load will not dispatch" from `Player.log` not growing for an hour **without reading the response** |

🔑 **The rule these three share is not "check parameter names".** It is: when a result is
dramatic, the caller is the first suspect, not the content. Re-run the same question a second
way before writing it down. Two of the three were caught that way; the third was caught by
finally reading a return value that had been sitting there the whole time.

⚠️ `jawa/pawn_gear` is a **WRITER**. Reading equipment off it answers with *"Give a
ThingDef."* and reports every pawn bare — a fourth route to the same false catastrophe.

## Four more, all measured live on full-583 — 2026-08-21, CHECK

### `rimworld/screenshot_cell_rect` captures the SCREEN, top window and all

It returned `success: true` four times, for four different cell rects with four different
filenames, and wrote **four byte-identical PNGs** — of the **Debug log window**, which was
open over the map. No warning, no hint in the reply; the only tell was that the file sizes
matched to the byte.

⇒ Before any capture: `rimworld/get_ui_state` and look at `topWindowType`, then
`rimworld/close_window` it. Closing `LudeonTK.EditWindow_Log` made every capture distinct.
🔑 **And hash your screenshots.** Four identical md5s is the cheapest possible detector, and
nothing else would have caught it — the image was a perfectly good screenshot of the wrong
thing.

### `rimworld/search_debug_actions` times out; the walk it exists to replace does not

Its own description says it exists *"so callers do not need to walk one subtree at a time"*.
On this stack it timed out at 30s and again at 150s, with params verified against its schema,
while `jawa/map_zones` answered in seconds either side. `rimworld/list_debug_action_children`
walked the same **646** nodes in seconds. **Walk it. Do not wait on the search.**

### `visible: false` on a debug node is not "absent" — and `category` is not a tree level

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

### Nothing reaches a `VehiclePawn`'s UI or its comps — four routes, four dead ends

- `rimworld/select_pawn` refuses it by id AND by name — *"Could not find player-controlled
  colonist"* — even though `jawa/set_pawn_faction` answers *"Pawn is already in
  PlayerColony"*. It filters on colonists and a `VehiclePawn` is not one. No selection ⇒
  `list_selected_gizmos`, `open_inspect_tab` and `get_ui_layout` all have nothing to read.
- `jawa/get_defs` with `fields: "components"` returns `["VehicleComponentProperties" × 5]` —
  the reflective reader flattens list elements to their class name and does not descend.
  `jawa/get_def` returns `comps` (the `CompProperties` list), which is a **different field**
  from `components` (the damageable parts).
- No tool anywhere mentions fuel or refuel; the only two vehicle debug actions on the whole
  583-mod stack are `Ground All Aerial Vehicles` and one mod's own list action.
- `rimbridge/run_lua` does **not** rescue this. It compiles a lowered subset and executes
  *"through the normal capability registry"* — it orchestrates existing tools, it does not
  reflect into game objects.

⇒ A vehicle's fuel level and health-tab labels are **unreadable from the bridge today**.
Say UNMEASURED; do not infer one from a hauler that did or did not move.

### The instrument that settles "did my world edit land"

⛔ Not a grep of the `.rws` (it stores biome indices, so counting defName occurrences
measures a lookup table). ⛔ Not a biome histogram either — a histogram agrees on a total
while disagreeing tile by tile. Use **`jawa/world_tile_validate`**, which compares live to a
CSV row by row and reads RAW fields, never the lazily-cached properties. Proven round trip:
`world_tile_import apply=true` → `world_commit` → `world_tile_validate` = **21,872/21,872,
mismatched 0**, about a second of engine time.

🔑 **And read the FIELD BREAKDOWN before raising an alarm.** A world that looked unpainted
turned out to be three commits stale: `byField: {rainfall: 20113, elevation: 312, biome: 3}`
— three fields, three hand edits, nothing else. **A regeneration disagrees everywhere; a
stale world disagrees only on the edits.** Two "signatures of a bare regeneration" written
into the spec both fired, and both were wrong about the cause.


## `rimworld/jump_camera_to_pawn` — `pawnId` needs a `Thing_` prefix, and it is NOT animals

Measured 2026-08-26, full 582-mod list, 72 pawns.

`jawa/list_pawns` and `jawa/pawn_get` return `Human335585` / `Qormot62098`.
`rimworld/jump_camera_to_pawn`'s `pawnId` wants the `rimworld/list_colonists` form:

```
pawnId=Qormot62098   -> False     pawnId=Thing_Qormot62098   -> True
pawnId=Human335585   -> False     pawnId=Thing_Human335585   -> True
```

🔑 `pawnId = "Thing_" + <jawa id>`. Without it the call refuses **humans too**, so a failure
here is never evidence about species.

⚠️ **By `pawnName` it refuses on AMBIGUITY, not species.** Three pawns called `Qormot` on one
map produced `"Ambiguous current-map pawn name"`; `Loth-cat`, `Geralinura` and `Fungal ferret`
each aimed first try. ⛔ `rimworld/list_colonists` lists COLONISTS only (3 rows / 72 pawns) —
an animal never appears there, which is what made the id space look closed to animals.

## `rimworld/get_ui_state` has no `currentMap` — do not ask it whether a map exists

Its whole top-level set is window/UI state plus `programState` and `hasCurrentGame`. There is
no `currentMap`, `maps` or `mapCount` key — **absent, not null.** `hasCurrentGame` is true for a
loaded GAME with no map instantiated, so a "is a map live" guard built on it passes exactly when
it should refuse. 🔑 Use `rimworld/get_game_info` → `mapCount` (measured 1 on a 72-pawn map).

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

## 🔴 `jawa/pawn_stats` — a stat that APPAREL moves must be read on a STRIPPED pawn

Measured 2026-08-26 on the tool's first real use, and it very nearly shipped a wrong answer.

`ComfyTemperatureMin` / `ComfyTemperatureMax` include worn apparel's insulation. Spawned pawns come
dressed by the generator, so reading them compares **clothes**, not xenotypes:

```
dressed   Baseliner -56.32 ... 47.50    MandrakeJawa -77.32 ... 60.28
          three xenotypes with NO temperature gene at all read -74.76, -55.92 and -88.80
```

🔑 **Three gene-free xenotypes disagreeing by 33 °C is the tell.** Strip first:

```
jawa/pawn_gear {pawn: <id>, action: "clear", clearWhat: "apparel"}
```

```
stripped  Baseliner / Ugnaught / Twilek / KelDor   -40.00 ... 45.00   (identical, no gene)
          MandrakeJawa    -50.00 ... 55.00   Small down + Small up
          RimMandrakeChiss  -60.00 ... 40.50   Large down + MaxSmall down
          RimMandrakeWookiee -60.00 ... 55.00   Furskin STACKS a further -10 on the min
```

⇒ Gene tiers, measured: **Small = ±10 · Large = −20 on min · `MaxTemp_SmallDecrease` = −4.5.**
⚠️ The same discipline applies to any stat apparel, a weapon or a hediff can move. The tool reports
the instance faithfully; the instance is just wearing something.

## `[JawaBench] ready` is LAZY — a missing line is not a failed deploy

The module initializer waits for the first `jawa/*` **tool call**, not assembly load, and
`tools/list` does not trigger it. Measured 2026-08-26: `harvest_log.py` scored
`RED  JawaBench ready  0  MISSING` at the main menu with a perfectly good 166-tool DLL, and the line
appeared the instant `jawa/get_def` was called. ⇒ **Census the live tool list; never use that line as
the deploy signature.**

## `rimworld/start_debug_game_ready` returns before the map is DRIVABLE

```
start_debug_game_ready -> success true, "RimWorld map data is available"
                          state: programState MapInitializing, currentMapId NULL
get_game_info          -> mapCount 1                       <- and yet
jawa/spawn_pawn        -> "No current map. Load a game first."
```

⚠️ **`mapCount: 1` answers "does a map exist", NOT "can I drive it".** `Find.CurrentMap` was still
null. Poll `rimworld/get_cell_info` → `state.currentMapId` until it is non-null (a few seconds); that
is the only reading that means the map will accept a write.

## 🔴 The bridge SILENTLY DROPS any parameter a tool's schema does not declare

Proven 2026-08-26 on purpose, after two calls in one session were mis-named and nothing complained.

```
jawa/new_allowed_area {label: "CHECK_correct"}           -> success, label "CHECK_correct"
jawa/new_allowed_area {name: "CHECK_wrong", banana: 42}  -> success, label "Area 3"
jawa/time_clock       {zzz: "nonsense"}                  -> success, full correct payload
```

`success: true` every time. ⇒ **A typo in a parameter name is invisible.** It is caught only when the
tool then misses a *required* field and refuses; where a default exists you get a successful call
that did something else — `new_allowed_area` wants `label` not `name`, `stop_job` wants `mode` not
`action`, and both quietly used their defaults.

⚠️ **Four grammars on tools that look alike, all in one session:**
`rect` (`room_get`) · `rects` (`destroy_batch`) · `ops` (`set_terrain_batch`, `set_roof_batch`,
`paint_area`, `build_batch`) · and `faction: "player"` accepted by `spawn_pawn`, refused by
`build_batch` which wants `PlayerColony`.

🔑 **Read the schema, not the sibling tool.** `b.list_tools()` carries the accepted keys; diff your
arguments against them before a batch. This is a property of the BRIDGE, not of any one tool.

---

## 🔴 A raid census taken immediately after `jawa/fire_raid` reads ZERO — 2026-08-27, BUILD

**Symptom.** `jawa/fire_raid` returns `executed: true, "Raid fired."`; `jawa/list_pawns` run
straight afterwards shows **no new pawns**. Reads exactly like a raid that never fired.

**Cause.** The raid is in flight. Measured: a raid fired at tick T had **0** new pawns at
+60 ticks and **19** at +300, on a paused game (the pawns appear as `step_game_ticks` runs).

**Fix.** Step ticks in stages and census after each — `+60, +300, +1200` — before concluding
anything. ⛔ A zero taken immediately is not a result.

**Generalises to:** any incident with an arrival mode. `success: true` tells you the worker
ran; arrival is a later tick, and on a paused game it is a tick you must supply yourself.

---

## 🔴 `jawa/set_faction_relation` CANNOT make a neutral faction hostile — 2026-08-27, BUILD

**Symptom.** `jawa/set_faction_relation {faction, kind:"Hostile", goodwill:-100}` returns
**`success: false`** with:

    kind Neutral -> Neutral, goodwill 0 -> -100.
    ⚠️ READ-BACK DOES NOT MATCH THE REQUEST — the engine overrode it.

It writes the goodwill and never flips the relation kind, leaving `goodwill -100` with
`hostile: false` — a faction that will never raid.

⭐ **The refusal is the tool working.** It verified its own write and refused to report a
success it had not achieved. ⛔ **But its own description says it "Exists to unblock aimed
raids", which is exactly what it does not do** — do not trust that sentence.

**Fix.** Use **`jawa/faction_relations_set`** instead:

```python
rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile",
                                       "goodwill": -100, "clampGoodwillToKind": True,
                                       "both": True, "sendLetter": False})
# -> kind Neutral->Hostile (reverse Neutral->Hostile); list_factions then reads hostile: true
```

**Why it matters.** An incident worker silently substitutes a random faction for one that is
not hostile — so this failure does not look like a failure, it looks like a raid from the
wrong faction. Confirmed twice the same session: an aimed `Jawa_HuttCartel` raid delivered
19 `AG_XenohumanPirates`, then 12 `GiantAnt`, while `resolved.faction` echoed
`Jawa_HuttCartel` both times.

**Generalises to:** two tools with overlapping names where the narrower one carries the
broader one's promise in its description. Read what a tool DID from its read-back, never
from what it says it is for.

---

## 🔴 `jawa/pawn_get` nests everything in `pawns[0]` — 2026-08-27, BUILD

**Symptom.** `resp.get("equipment")` returns nothing for every pawn, printing as
*"8 of 8 BARE"*. This is the documented false reading that once produced the conclusion
"all Jawa spawn bare-handed", and it was hit again.

**Cause.** The payload is `{"success": true, "count": 1, "pawns": [ {...everything...} ]}`.
`equipment` and `apparel` live inside `pawns[0]`, not at the top level.

**Fix.** `d = (resp.get("pawns") or [{}])[0]; eq = d.get("equipment") or []`.
⚠️ And entries are keyed **`def`**, not `defName` — `{"def": "guy762_ionpistol", "stuff": null,
"isPrimary": true}`. Reading `.defName` gives `None` for a fully armed pawn.

**Generalises to:** an empty collection from a bridge read is a shape hypothesis, not a
measurement. Dump the RAW response once per tool before believing any absence.

### 🔑 A Dialog_NodeTree can absorb ALL input while ignoring its OWN buttons
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

## get_cell_info returns empty things + terrain None while the thing verifiably exists (2026-08-29)

**Symptom:** after 74 successful `rimworld/spawn_thing` calls (real thingIds), `get_cell_info`
on the exact spawn centers read `things: []` and `terrain: None` on every cell sampled — 0/10.
**Truth:** `get_map_target_info {thingId}` found the same things at those cells (Map_0, correct
cellRect); a debug-action destroy then acted on one, proving liveness. `terrain: None` is the
tell — no real cell lacks terrain, so the reader answered about nothing, not about an empty cell.
**Context:** full 585 stack, JawaBench companion unregistered (bill_add alias collision), stock
tools only. Unknown whether the same call misreads when the companion is up.
**Fix:** verify spawns with `get_map_target_info {thingId}` (or a save parse), never
`get_cell_info` alone. **Generalises to:** any read tool whose "empty" answer carries an
impossible sibling field (terrain None) is answering the wrong question — check a field that
CANNOT be empty before believing one that can.

## 🔴 Whole-map Set-terrain-(rect) cascaded into a per-frame NRE storm and render corruption (2026-08-29)

**What worked first:** rect debug tools ARE drivable stock: `execute_debug_action` on the
rect leaf arms the tool, then TWO `click_cell` calls (corner, corner) apply it — click-click,
not a drag; the tool stays armed for further pairs. Proven on a 10x10 (screenshot-verified).
**What then failed:** painting the full 250x250 map (10 bands x 2 passes, first with
VFEArch_Grass — a CONSTRUCTED lawn floor that renders error-red painted raw) alongside
destroy-non-colonists/clear-fog produced an every-frame `Root level exception in Update():
NullReferenceException` (one ref, repeated forever), map-wide magenta/blue material
corruption, and an unusable session. A 10x10 pass is NOT evidence for 62,500 cells x
thousands of plant destructions on a 585-mod stack.
**Also:** the debug LOG window auto-opens on the first error and then ABSORBS `click_cell`
clicks (the dispatcher clicks center-screen after jumping the camera), so follow-up rect
corners silently do nothing while the tool reads "First corner...". `rimworld/close_window`
(stock) closes it — but by then the storm may already be running.
**Fix:** terrain at scale is `jawa/set_terrain_batch`'s job; keep rect debug tools to small
patches; pick NATURAL terrain defs (GrasslandSoil), never constructed floors; check
`get_ui_state` for an open EditWindow_Log before any click_cell sequence.
**Generalises to:** any stock click-driven tool — a window that auto-opens on error eats
every later click, so the first error silently invalidates the rest of the batch.

## CORRECTION on the 2026-08-29 render-death: it is the WALL-MOUNT/shielded turret spawns, and it happened twice identically

Both sessions (worldmap, then gravship_scratch) died with the SAME per-frame NRE
(`[Ref 36A0E3C1]` PowerConnectionMaker.TryConnectToAnyPowerNet <- PowerNetManager <-
Map.MapUpdate), and in BOTH logs the storm begins immediately after the last stuffable
1x1's MakeThing line — i.e. among the spawns that log nothing: VQE_AncientShieldedTurret
+ the 10 wall-mounted turrets (HMC_Wall_*, ShipWallMountMiniTurret) spawned free-standing.
`MakeThing ... stuff=null, assigning default` is BENIGN (fired for the large batch that
rendered fine). Once the exception is on the map, every frame aborts before the map
drawer runs — the "wildly colorful"/blue screen is UNRENDERED frames, not texture
corruption — and it persists until the save is reloaded, because the broken power comp
is still spawned. Fog-clear and terrain-paint were exonerated by the second incident.
**Rule:** never bridge-spawn wall-mounted or shield-comp turrets onto open ground;
exclude `HMC_Wall_*`, `ShipWallMountMiniTurret`, `VQE_AncientShieldedTurret` from any
free-standing lineup, or give walls first.

## `select_pawn` and every `ToolMapForPawns` debug action require `IsColonist` — a bridge-spawned pawn, even faction PlayerColony, does not qualify

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
