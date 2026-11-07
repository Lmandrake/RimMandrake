# RimBridge traps: the JawaBench companion: building, deploying, censusing, writing tools

Part of the trap catalogue indexed in [../traps.md](../traps.md); its first law and admission test are there. Append a new trap to the topic file it belongs to.

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

## Fixed in the companion — one line each

Real traps, closed by the **B0** deploy. If a symptom below returns you are running
a **stale companion DLL**: rebuild and redeploy with the game closed
(`src/RimMandrake/bridgetools/build.py --apply`).

- **Terrain layer `'foundation'`** is accepted by `set_terrain`, `set_terrain_batch` and `get_terrain_batch`. Stale-build tell: `layer must be 'top' or 'under'`. `Substructure` lives in **`foundationGrid`**, a third grid beside `topGrid` and `underGrid` that `TerrainGrid.SetUnderTerrain` cannot reach, and 10 defs in `Buildings_Gravship.xml` (`GravshipHull`, `GravFieldExtender`, `PilotConsole`, …) demand it via `terrainAffordanceNeeded`.
- 🔴 **`jawa/list_factions` emits `countReturned`, `countAllIncludingHidden` and `isCompleteList`.** Stale-build tell: a bare `count`, which is the **visible subset only** — it read **34** against a true **54**, dropping 20 hidden factions including `Mechanoid` ("Oxslin Mechhive", `permanentEnemy`, goodwill −100). `includeHidden` defaults to `false` and the warning lived only in `message`, which no JSON caller reads.
- **`jawa/get_def` comps carry a `fields` map** of public scalar/string/enum/Def values by reflection. Stale-build tell: comps render as `{class, compClass}` only, so `GravEngine` returns 2,701 characters with **no field containing "radius"** and cannot answer what `CompProperties_SubstructureFootprint` holds. Stat values were always visible — `SubstructureSupport 632.7954` matched the owner's setting.

## 🔴 `?.` guards the RESULT, not the CALL — the whole companion is dead at a main menu
**Symptom:** at the main menu, **every** `jawa/*` tool returns a bare `Object reference not set to an instance of an object`. No tool name, no field, no hint that the cause is "there is no game". `jawa/get_def ThingDef/Steel` — a call that had worked all day — failed exactly like the brand-new `BiomeDef` branch, which is what proved it was environmental rather than a fresh bug.
**Cause:** almost every tool in the companion ends `ticksGame = Find.TickManager?.TicksGame ?? -1`. That **looks** null-guarded and is not. `Find.TickManager` compiles to `call Current::get_Game` then `ldfld Game::tickManager` — 11 bytes of IL with no null check. **With no game loaded, the GETTER throws before `?.` is ever reached**: the operator protects the value it returns, not the call that produces it. One unguarded property in a response field kills every tool that includes it.
**Fix:** ✅ **DONE 2026-08-14 — `TicksGameSafe()`, one helper, all 25 sites** (build md5 `d3ace1f6…`, 28 tools; deploys at the next shutdown window). `Current.Game != null && Find.TickManager != null ? Find.TickManager.TicksGame : -1` — `&&` short-circuits, so the getter is never touched until `Current.Game` is known non-null. Until that build is deployed, **the companion needs a GAME, not merely a map**: a quicktest fixes it instantly.
🔴 **`jawa/get_defs` takes SEMICOLON-separated `DefType/defName` pairs.** A comma-separated list resolves as ONE malformed entry and reports `success: true` with `foundCount 0` — the unknown-separator failure is invisible because the call still succeeds (2026-08-30).

🔴 **Measured live at `programState: Entry`, and the live shape is worse than the IL suggested.** `jawa/get_defs` on two `RulePackDef`s returned a bare NRE whose stack names `<GetDefs>b__2 [0x002d4]` — the **response-construction** line, not the def lookup. **The defs had resolved correctly; the tool threw the right answer away while packing it.** So the symptom is not "the call could not run" but "the call ran, succeeded, and destroyed its own result" — and the message names nothing at all. ⚠️ **Defs are parsed once at startup and are not re-read when a game begins**, so every def question is answerable at the main menu and this bug is what made a whole class of no-game checks look impossible. It cost a real one: a retired seat's `maybeApostrophe` check had a closing window and could not be fired. ⚠️ Note the corollary for the run sheet — "this check needs no map" and "this check needs no game" are different claims, and a def read that is genuinely map-independent is still game-dependent.
**Recurs when:** any `Find.X` in a response field. `Find.CurrentMap` is safe (it null-checks internally); `Find.TickManager`, `Find.World` and friends dereference `Current.Game` and are not. ⚠️ Generalises past C#: **a null-safe operator on the last link of a chain says nothing about the links before it**, and the tidier the line reads the less likely anyone is to check. Measured live 2026-08-14 by comparing a known-good call against a new one — **keep a control you already trust in reach, because it converts "my new code is broken" into "the environment changed" in one call.**

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

## ⚠️ A bare `catch {}` in your own tool is the same bug you are hunting

Written by me, 2026-08-19: the zone builder swallowed `AddCell` refusals, and a 6×6
stockpile silently took **11 of 36 cells** while reporting success. **If the engine can
refuse a cell, report which cells and why** — the whole value of a bridge tool over a
direct API call is that it explains itself.


## 🔴 A mod's own `[DebugAction]` methods do not surface through the bridge's debug-action tree

**Symptom.** `rimworld/list_debug_action_roots` returns `rootCount: 0` even with
`devModeEnabled: true`. `rimworld/list_debug_action_children {"path":"Actions"}` DOES
return a real 344-entry tree and vanilla leaves inside it execute fine
(`execute_debug_action {"path":"Actions\Spawn Pawn...\Pirate"}` worked), but neither
listing it nor `rimworld/search_debug_actions {"query":"<anything from a custom mod>"}`
ever finds a category registered by our own `[DebugAction(...)]` attributes — tried both
`Actions\<Category>\<Label>` and bare `<Category>\<Label>`, both "Could not find debug
action". Measured 2026-08-31 with a brand-new category (`RimMandrake.Oracle`) **and**
with an already-shipped, previously-working one (`RimMandrake.Inhabited`, whose debug
actions this project's own docs describe using) — `search_debug_actions {"query":
"inhabited"}` and `{"query":"stuff roster"}` both returned `matchCount: 0` too. So this
is not new-mod-specific: it reads as a general limitation of how the bridge's
`RimWorldDebugActions`/`DebugActionsCapabilityModule` builds its tree, not anything about
either mod's attributes, visibility, or `AllowedGameStates`.

**Cause.** Not chased to ground — would mean reading `RimBridgeServer.RimWorldDebugActions`
itself, out of scope for the session that hit it. The working theory, unverified: the
bridge's tree-walker may only descend into vanilla's own named categories (hence "Actions"
working) rather than doing a full `GenTypes.AllTypesWithAttribute<DebugActionAttribute>`
sweep across every active mod's assemblies — or the walk it does do depends on something
(the real in-game debug window having been opened at least once this session, populating
a cache the bridge reads rather than builds) that a bridge-only session never triggers.
Vendor source for `RimBridgeServer.RimWorldDebugActions` is not present in this checkout to
confirm either way.

✅ **Fix — skip the debug-action route entirely for a bridge-driven proof.** Add a normal
`[Tool]` method to the JawaBench companion instead (the `rimbridge-companion` skill) that
calls straight into the same code the `[DebugAction]` would have called. This is strictly
more work (a companion rebuild/redeploy/restart cycle) but is the proven, unambiguous path
— every other capability on the bridge already goes through `[Tool]`, none through
`[DebugAction]` discovery. Do **not** conclude a mod's debug actions are broken from this —
a human with Dev Mode open in the real client almost certainly still sees them; this trap
is specifically about the bridge's own tree not finding them, and both isolated ends of
that claim (a genuinely new category, and a previously-shipped one) failed the same way.

**Generalises to:** if a human-facing debug-menu verification path is part of a build's own
plan (as `design/RimMandrake/llm_ingame_wiring_spec.md` §4's "Ships as `selftest_*.py`-style
gate" implicitly assumed a debug-action hook would be bridge-drivable), budget for it to be
UNREACHABLE from the bridge and route the actual proof through a `[Tool]` instead — don't
discover this mid-verification by re-guessing path strings.

## JawaBench companion test grant expires
The JawaBench `companion_profile.json` test grant carries `expiresUtc`. Once lapsed, `P03_LOG_ALIVE` is refused as CAMPAIGN, the L1 log tap goes blind, and whole suites silently read UNMEASURED. Renew with the same keys and a new expiry before a round.

## Census the companion before you trust any `jawa/` call
- **Check the bridge tool list before declaring a mechanism unreachable.** `jawa/gravship_launch` and `jawa/gravship_land` are closed, proven tools reaching the real vanilla path (`WorldComponent_GravshipController.InitiateTakeoff` -> `GravshipUtility.GenerateGravship`; `Gravship.TickInterval` fires ArriveExistingMap/ArriveNewMap by itself). Six passes concluded "no debug shortcut exists" because they checked only the debug-action tree, never the `jawa/` surface. Proven ~10 minute route: `prove_gravship.py` minimal-ship recipe, then `gravship_launch`, `step_game_ticks`, `gravship_land`.
- **ModsConfig can hold a phantom id** such as `rimmandrake.biomes` next to the real `mandrake.rm.biomes` (suspected: `modlist_swap --enable` keeps a lowercased folder name when no About resolves). Harmless to the load, but "every one is already active" then proves nothing about that mod: read `jawa/running_mods` for the real packageId (the deployed About.xml).
