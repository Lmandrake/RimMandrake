# RimBridge traps: reading a result: defs, cells, instruments that are blind, denominators

Part of the trap catalogue indexed in [../traps.md](../traps.md); its first law and admission test are there. Append a new trap to the topic file it belongs to.

## `debugToolChanged: false` means nothing
**Symptom:** `effects.debugToolChanged: false` read as proof that `execute_debug_action` had done nothing; a confident bug report was filed against the mod for an unimplemented code path.
**Cause:** it is `false` on calls that demonstrably work, including one that killed a pawn outright. The bridge applies these directly without arming a UI tool, so the flag says nothing about success.
**Fix:** judge by world state. Calibrate any diagnostic against a known-good case before trusting its negative.
**Recurs when:** `effects.debugToolChanged` and `effects.logCount` — response metadata that describes the dispatcher, not the game.

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

## `rimbridge/list_logs` is a ring, not the log — a long session loses its startup lines

On a game that has run for hours, `list_logs limit=500` no longer reaches the startup
`[RimBridge]` line, so any check that reads startup state from it (GSS `proof_all` P2) goes
UNMEASURED. Read startup facts from `Player.log` itself, or restart / fresh-load before a
proof that needs them. A repeated exception there may show only `[Ref XXXXXXXX] Duplicate
stacktrace` with no frames — resolve it against the original in `Player.log`
(`rimworld-modding/references/player-log-triage.md`).

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

## The instrument that settles "did my world edit land"

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

## `rimworld/get_ui_state` has no `currentMap` — do not ask it whether a map exists

Its whole top-level set is window/UI state plus `programState` and `hasCurrentGame`. There is
no `currentMap`, `maps` or `mapCount` key — **absent, not null.** `hasCurrentGame` is true for a
loaded GAME with no map instantiated, so a "is a map live" guard built on it passes exactly when
it should refuse. 🔑 Use `rimworld/get_game_info` → `mapCount` (measured 1 on a 72-pawn map).

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

## `get_cell_info` reports the FOUNDATION as `terrainDefName` (2026-09-02, BENCH)

**Symptom.** Laid `Gravel` over 16 cells of Odyssey `Substructure`, then read them
back: `terrainDefName: "Substructure"`, 0 of 16 correct. Reads exactly like a floor
write that silently did nothing — the classic SetFoundation-refused failure.

**It was fine.** `jawa/get_terrain_layers` on the same rect: `top: "Gravel"`,
`foundation: "Substructure"`, `isSubstructure: true`, 16/16. `rimworld/get_cell_info`
exposes ONE terrain string and, where a substructure exists, that string is the
foundation — the floor above it is not reported at all and there is no field
suggesting a second layer exists.

**Fix.** 🔴 On any cell that might carry substructure, verify floors with
`jawa/get_terrain_layers`, never `get_cell_info`. Its `terrainDefName` is not wrong,
it is answering a different question with a plausible value.

**Generalises to:** an instrument that returns ONE value for a thing the game stores
as a STACK. The single value is never marked as partial, so the read looks complete.
Before believing "the write did nothing", ask whether the reader can see the layer
you wrote to at all.

## `jawa/get_defs` says "No def TYPE named 'X'" for a genuinely-loaded custom Def subclass
**Symptom:** `jawa/get_defs {"defs": "InhabitedPlaceDef/Foo"}` returns `"error": "No def TYPE
named 'InhabitedPlaceDef'."`, read as proof the mod/def never loaded.
**Cause:** `get_defs`'s def-type resolver does not recognise every project-custom `Def`
subclass — tried and failed on `SettlementManifestDef` and `InhabitedPlaceDef`, both from a
mod independently confirmed loaded (its `WorldObjectDef`s resolved fine via the same tool, its
`Player.log` init line printed, and its debug actions were present in the live debug tree).
Vanilla/common types (`ThingDef`, `WorldObjectDef`, `TraderKindDef`) resolve fine; some
project-custom ones do not — the boundary is untested beyond these two. The resolver finds a bare type name only in Verse/RimWorld (GenTypes plus `RimWorld.`/`Verse.` prefixes), so ask for a mod's own Def subclass by its FULL namespaced type name (e.g. `RimMandrake.StarWars.WeatherSuite.PlanetGeometryDef/RUT_WS_AshkarrGeometry`, `TitanicCreatures`-namespaced `RM_CrushRuleDef`); a bare name answers notFound "No def TYPE named X" on a load where the def is present. A null value comes back as `fields:{}` (treat as null, not missing) and floats come back as JSON numbers (63.0), so compare numerically, never `str(got)=="63"`.
**Fix:** never conclude "not loaded" from this error alone for a custom Def subclass. Verify
independently: a debug-action census (`rimworld/list_debug_action_children`), a
`Player.log` init line, or a live spawn/read through a different route.
**Recurs when:** querying any mod-defined (non-vanilla) Def subclass via `get_defs`.
(SETTLEMENT_VISIT_LOOP_1, 2026-09-24)

## `jawa/get_defs` cannot read everything a def holds
`jawa/get_defs` serialises at most 64 items of any list field, so rows APPENDED to a long list (a trader stock list of ~79 read exactly 64) fall off the end and read as "patch matched nothing": a read at exactly 64 cannot prove absence (say UNMEASURED). It returns only the TYPE NAME for list-valued fields (`["TerrainThreshold"]`), so a field-by-field diff silently calls complex fields identical: read the XML. It cannot read `System.Type` fields (`driverClass`, `workerClass`, a GenStep class; the read is "(no such field)") nor name the JobGiver/ThinkNode inside a `ThinkTreeDef` (scalar mode skips the object-valued `thinkRoot`, deep mode emits node fields, never type names), so a check asserting those always reads FAIL on a loaded, correct def: assert the class from the shipped XML (or a behaviour counter) and prove the def loaded (`foundCount 1`, a populated object); an unresolvable class discards the def. It takes ONE Type/defName per call (a comma list is looked up as one name and answers notFound). For resolved nested values no bridge tool reads (`tools[].power`, `projectile.damageAmountBase`), the live def dump `DefDump/defs.sqlite` (RimDefDump serialises the runtime DefDatabase after patches) is a resolved-value readback: check its `captured_utc`/fingerprint matches the mod set first.

## `jawa/mod_settings_field` does not fire the mod's WriteSettings side effects
A mod setting written with `jawa/mod_settings_field` does NOT fire the mod's `WriteSettings` side effects (the settings window's `WholeMapChanged` never runs). Biomes world toggles (`worldBiomeSwirls` etc.) only redraw on `SetAllLayersDirty`, so follow the set with `jawa/world_commit redraw=true lazy=true` (60 px changed vs 214k with it). For FlowWorks art settings call `jawa/static_call RimMandrake.FlowWorks.SectionLayer_RMExcavationWalls.RedrawAll` (or `RM_PipePoles.RedrawSpans`) before a before/after screenshot, or the "after" frame shows the old art.

## FlowWorks reads that mislead
- A whole-notch `f` (`jawa/flowworks_excavation_rect`) floors a level surface: a 351-cell moat a hair under 2 m (1.99 m, one dry grate cell it levelled into) reads 1.5 m on EVERY cell. Before calling water lost, look for a dry dug cell the body touches through a grate (grates pass liquid; only a shut sluice seals) and read decilitres/the cell readout, not `f`.
- `jawa/flowworks_excavation_drive` (dig+fill) followed by a same-tick teleport into the new pool makes the pawn FALL (9.7 blunt, bruise + cracked clavicle): the swim-climb cache (`RM_MapComponent_Excavation.swimClimb`) refreshes only every `SwimRefreshTicks`=60 or after a pulse, so for that first tick a brim-full pool still reads as an 8-deep dry pit. Step >=60 ticks after driving fill before putting a pawn in; check `flowworks_pit_report` `recentDescents` + `pawn_get` hediffs, and heal with `jawa/pawn_health remove`. Injuries silently move ConstructionSpeed via Manipulation.

## `jawa/power_net` units
- **`jawa/power_net` reports watt-days per tick (1/60000 W),** so tiny numbers like 1.67e-05 are normal. Scale before judging a gain.

## Bridge and live-game traps
**Removing a mod can expose what it was masking, and a mapgen call reporting success is not a live map.** Biome Transitions overrode Odyssey's `MixedBiome`; with it gone, `MixedBiome` on a non-vanilla biome nulls the secondary biome and `GenStep_Plants`/`GenStep_Animals` throw, leaving a dead map (1 plant) from a call reporting success with `failedSteps 0`. Assert plant count and read 'Error in GenStep' in `Player.log`.
**A screenshot copy helper that waits only for the game's file to EXIST copies a stale picture** when a same-named shot from an earlier run is already there (a charge shot showed the previous attempt's message). Wait for mtime >= the call time, as `A.shot` in `src/RimMandrake/GimmeSomeSlack/validation_aerial.py` does, and audit any other shot helper that reuses file names.
**A copied harness helper inherits a known-dead tool.** Seven validation `_wait` copies called `rimworld/set_time_speed` (reports success, the game stays paused; see `silent-failures.md`) for a month. Speed-up waits go through `helpers.fast_advance` (`rimworld/play_for`), never `set_time_speed`. `jawa/set_plants` returns a generic 'cannot support' from the `writeNoReason:true` overload: ask the AcceptanceReport for the engine's reason.
**A FloatMenu opened by `rimworld/execute_debug_action` is gone before the next bridge call** (`get_context_menu_options` sees nothing), so a debug action's picker cannot be read or clicked that way. Use `jawa/debug_action_menu {path, pick|pickIndex}`: it runs the action and reads/picks its menu in one main-thread slice.
**`rimworld/dismiss_letter` takes `letterId`, not `id`.** The client's declared-parameter guard rejects the wrong name loudly instead of silently dropping it.
**`rimworld/step_game_ticks` advances only ~600 ticks per call on the 325 list.** Loop to a target `ticksGame`, and budget ~4 real minutes per 15,000 ticks.
**A Mod Settings search typed through `rimworld/set_text_field` persists after the window closes** (the owner would reopen a filtered page). Clear it with `mode=instant` on the field whose `screenRect` is the 420-wide search box, re-reading `get_ui_layout` first: target ids change every capture (`ui-element:N:...`).
**`jawa/world_tile_export` writes boolean CSV columns (`waterCovered`) as 0/1, not true/false.** A parser comparing to 'true' reads every tile as dry. Accept 0/1/true/false and treat anything else as UNMEASURED.
**Screenshotting a page that holds a server-sent-events stream open (RimPulse at localhost:8765): Edge headless `--screenshot` never returns,** because the page never finishes loading. Use Chrome headless with `--timeout=6000` (it shoots once the timeout passes) and its own `--user-data-dir`. Chrome headless will not go narrower than about 500 px (a 420 px window clips the right edge): shoot phone pages at 600 px and check the CSS caps width instead.

## Dumping the game process
- **`PssCaptureSnapshot` (VA clone) on a 1 GB process failed with error 1450 `ERROR_NO_SYSTEM_RESOURCES`** when ~3 GB commit was free (2 of 4 runs): a snapshot dump of a multi-GB game can fail under memory pressure. `health_minidump.py` falls back to a direct `MiniDumpWriteDump` and records `fallbackFrom`/`pssError`.
