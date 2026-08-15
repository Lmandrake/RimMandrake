# CHECK queue — needs a running game or the bridge.

## C1 Drive the built-but-never-run bridge tools
spec:     `python.exe src/RimMandrake/bridgetools/prove_new_tools.py --pawns` covers `jawa/set_pawn_rotation`, `jawa/set_pawn_style`, `jawa/set_pawn_xenotype` and `xenotype=` on `spawn_pawn` (`7b8d5b7`, `e60197a`). Also deployed and never called: `jawa/get_defs`, `jawa/fire_quest`, `jawa/list_things` (`3adedbc`), `jawa/clear_ui` (`9a5b6fe`), the vehicle route in `spawn_batch` (`9a5b6fe`, routes `Vehicles.VehicleDef` through `Vehicles.VehicleSpawner.SpawnVehicleRandomized` by reflection — `ThingMaker` leaves `vehiclePather`/`ignition`/`drawTracker`/`kindDef` null), and the roof pair `set_roof_batch`/`get_roof_batch`. `jawa/world_stats` WAS called and its answer was discarded by a harness `NameError` (fixed `3e17731`) — re-run it. Do not compose calls at a live console: run `python.exe src/RimMandrake/bridgetools/load_session.py --phase any|fresh` (`--selftest` needs no game); it writes one ledger to `observed\<date>_load_session.md` and tracks LITTER, from which the release message is written.
verify:   EMPTY
criteria: each tool returns success on a live map; `world_stats` returns `{ tiles, pct, perimeter, raggedness, centroidLat }`. A capability is announced to peers when it has RUN, not when it has compiled.
state:    ready

## C2 L3 — the Galactic Empire raid, and read the faction back
spec:     Chain: game DOWN -> deploy BUILD B1 (`--gm`, 30 tools) -> up -> `jawa/set_faction_relation` make `OuterRim_GalacticEmpire` hostile -> `jawa/fire_incident incidentDef=RaidEnemy faction=OuterRim_GalacticEmpire dryRun=true` (abort on `canFireNow:false`) -> fire for real -> screenshot. PASS `points` EXPLICITLY: `points<=0` takes the storyteller default, which on a fresh quicktest is tens of points — one trivial attacker cannot answer whether the Empire reads as an antagonist.
verify:   EMPTY
criteria: read the `faction` field in the REPLY, never the one you sent — `IncidentWorker_RaidEnemy::TryResolveRaidFaction` keeps the passed faction only if non-null AND `HostileTo(Faction.OfPlayer)` AND (`!deactivated` OR `parms.forced`); otherwise IL_0059 passes `ldflda IncidentParms::faction` BY REFERENCE into `TryGetRandomFactionForCombatPawnGroupWeighted`, which overwrites it with a random weighted faction and still reports `success:true`. The tool reports `parms.faction` after the worker ran (`JawaBenchTerrainTools.cs:3588`). Then: does the antagonist read as the antagonist on screen.
state:    blocked

## C3 v1 row 4 — the scrapfields count
spec:     After BUILD B3 deploys, generate a fresh map (a 90 s quicktest counts; `Jawa_ScatterScrapfields` is a `GenStepDef` at order 960 hooking `Base_Player` genSteps, so it is not biome-gated), then take a FULL-MAP `listerThings` count of `ChunkSlagSteel` — no sampling — plus `TileInfo.Mutators` and the map size. NAME THE MAP. A GenStep runs at map generation and never again, so a map's count dates the def that BUILT it. The old "11 measured" was never a measurement: 9 rects of 30x30 = 8,100 cells (~13% of the map) holding 1 chunk each on two maps, extrapolated by /0.13; where the 9 rects sat is recorded nowhere. Full audits: `observed/2026-08-14_O15_scrapfields_offline.md`, `observed/2026-08-14_row4_live.md:97-101`.
verify:   EMPTY
criteria: **44–56 chunks in 4–6 clumps** on a map generated after B3. The 75–125 band was never measured — it omitted `GetPlacementFactor`, the product of `junkDensityFactor` over the tile's mutators, and `Dunes` is one of five live mutators whose factor is **ZERO**. On any older save the verdict is "not measurable here", NEVER "44–56 missed". Look before any destroy — the last map's evidence died in a 43,288-thing wipe.
state:    blocked

## C4 Are those chunks ours — attribute the `GenStep_ScatterThings` NRE
spec:     `Player.log:9022` (2026-08-14 ~15:00): `Error in GenStep: NullReferenceException at Verse.GenStep_ScatterThings.ScatterAt [0x0013f]`, called from `GenStep_ScatterThings.Generate [0x0010d]`, with a `BiomesCore.Patches.IslandGeysers` prefix on the same method. Exactly ONE occurrence in four generated worlds, and NOT on the 13:54 quicktest map where 4 chunks were counted (that map's generation sits before log line 6830; this throw is between lines 7975 and 9040). `Error in GenStep` names no defName and both `Jawa_ScatterScrapfields` and Biomes Core's scatterers are `GenStep_ScatterThings`; it is caught per-step, so generation continued — not a hang.
verify:   EMPTY
criteria: grep the log of the C3 quicktests. Vanishes with the `minSpacing` fix => it was ours. Recurs on a map where scrapfields now places ~50 => it is Biomes Core's. Free attribution riding already-scheduled work.
state:    blocked

## C5 The two xenotype picker icons
spec:     Two unresolvable `iconPath`s: `Jawa_Head_Plain` -> `UI/Icons/Genes/Gene_Hair`, and `Jawa_Xeno_Gamorrean` -> `UI/Icons/Xenotypes/Pigskin`. Not settleable offline — vanilla textures live in asset bundles. Open the xenotype picker and look at both.
verify:   EMPTY
criteria: a pink or blank square is the defect; both drawing closes this permanently.
state:    ready

## C6 O12 — the 30-second droid NRE confirmation
spec:     Spawn `KotORDroidGood_3C` twice on any map. Chain under test: `Jawa_Doctrine/Patches/DroidsAreMachines.xml` sets `isOrganic=false` on `ABF_FleshType_Synstruct_Base` -> `RaceProperties.IsFlesh => FleshType.isOrganic` -> `PawnComponentsUtility.CreateInitialComponents` builds `Pawn_RelationsTracker` only `if (pawn.RaceProps.IsFlesh)` -> HAR derefs it unguarded.
verify:   EMPTY
criteria: the SECOND same-def droid must NRE (`AlienRace.HarmonyPatches.GenerationChanceGenderless`, `HarmonyPatches.cs:2669`) — the throw is inside the weight selector iterating pawns that ALREADY EXIST, so the pawn with the missing tracker is `current`, the previously-spawned droid. If it does NOT throw, the chain is wrong and all three fix routes are moot.
state:    ready

## C7 Gravship radius — `get_def GravFieldExtender`
spec:     Read the live `GravFieldExtender` (and the engine radius) with `jawa/get_def`. Bigger Gravships is set to 34 in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3522759531_GravshipSizeSettings.xml`, and `GravshipSize.dll` stamps radii during implied-def generation, AFTER all XML patching. On disk the def reads 16.9/12.9 and is MEANT to disagree. Live state: `BG_gravEngineSupport` is **4500** (was 632.79541; compiled default 500.0) — any capacity reading starts from 4500. Setting it live needs `rimworld/update_mod_settings` PLUS the mod's own "Apply Settings Now!" button; the write alone does not reach the defs.
verify:   EMPTY
criteria: the live def carries the expanded radii. Until it does, DO NOT BUILD A SHIP — one built now will not lift and nothing logs why. Confirmatory, not load-bearing: do not spend a session's first call on it.
state:    ready

## C8 v1 row 4 — dune seas
spec:     Read the live `BiomeDef`. Do NOT eyeball it: a density change 0.65 -> 0.55 is unjudgeable without a control.
verify:   EMPTY
criteria: `terrainPatchMakers` read **0.55 / 0.50** on the live def.
state:    ready

## C9 The ground hulk and a casket bank
spec:     `00a1398` — one wide shot plus one casket bank. 619 of 1,200 cells; 0 overlaps, 0 out-of-bounds, 0 props off-deck.
verify:   EMPTY
criteria: does the broken deck read as a wreck, and do three banks read as a hold. Nobody has ever seen an `AncientCryptosleepCasket` — vanilla and DLC art is in AssetBundles, so 297 wreck defs cannot be rendered offline; defs, sizes and yields are proven, the look is not. `ShipChunk_Mech` needs `Light`, not `Heavy`; `BrokenSubstructure` has no `Inherit="False"` so it APPENDS to `FloorBase` — either layer satisfies the deck. Missing props means prefab placement, blocked cells or `spotMustBeStandable`; do not report "deck present, props absent".
state:    ready

## C10 The art-observation batch — Cerean and Saurid
spec:     Runnable on ANY live map; no fresh map, no new capability. **CereanManeFix**: spawn pawnkind `OuterRim_Cerean` (forces the xenotype, weight 999), then SET hair `OuterRim_CereanMane` (a fresh Cerean rolls it ~1 in 5 — set it, do not hope), face **SOUTH**. **SauridFrillFix**: spawn pawnkind `VRESaurids_Villager_Saurid`, then SET hair `VRESaurids_Littlefoot` (`texPath Pawn/CenterFrill/CenterFrill8`), face **NORTH** — the donor ships `CenterFrill8_north-.png` with a trailing hyphen while `CenterFrill7_north.png` beside it is named correctly, and north is the ONLY broken rotation. Tools: `jawa/spawn_pawn`, `jawa/set_pawn_style`, `jawa/set_pawn_rotation`. A pawnkind spawn ALONE tests neither — both are HairDef `texPath`s, not pawnkind art, so the style has to be SET or you photograph a default and call it passed.
verify:   EMPTY
criteria: the hair renders correctly in the named facing. OBSERVATION ONLY — the owner's stop on art fixing stands; looking is not fixing.
state:    ready

## C11 ToolBeltFix
spec:     `VAEA_Apparel_ToolBelt` is spawned by NO PawnKindDef — zero hits across the workshop tree, `Mods/` and `Data/` in `apparelRequired`, `specificApparelRequirements` or any fixed list, and its only tag `VAEA_Utility_Industrial` appears in no pawnkind, so there is no random path either. Every other reference is loot. Needs dev-spawn plus a FORCE-EQUIP tool, which does not exist yet. Hold for that tool, not for a load.
verify:   EMPTY
criteria: face **WEST** (`ToolBelt_west.png` is 753 bytes against `ToolBelt_east.png` at 16,945). `renderUtilityAsPack` is true so it draws in the pack layer — check from behind as well as straight west.
state:    blocked

## C12 `NoPathToPilotConsole` — launch gate
spec:     The export holds ZERO `PilotConsole`, so there is nothing to path to: PLACE a console first (defName `PilotConsole`, `Odyssey/Defs/ThingDefs_Buildings/Buildings_Gravship.xml`; `load_session.py` looks it up itself). Then `jawa/order_pawn pawnId=colonists targetId=<consoleThingId> waitTicks=0 unpause=false`; `jawa/list_things` produces the ThingID for a non-pawn. `pathEndMode` must be `interactioncell` (the default when `targetId` is set). Needs no movement.
verify:   EMPTY
criteria: the vanilla gate is `PawnCanFillRole` -> `ReachabilityUtility.CanReach(pawn, console, PathEndMode.InteractionCell, ...)` — a pawn can reach the cell BESIDE a console and still fail, so TARGET THE THING. Doors are in the export; a door is not a path.
state:    blocked

## C13 Thruster placement — a confirmation with a committed prediction
spec:     Remove hull at (45,132) and place a `SmallThruster` at (45,131) rot 2; control at (45,129) with the hull intact. Nine candidate sites at x41–49, z131/132; the aft strip (x,133) is off-deck.
verify:   EMPTY
criteria: (45,131) reads ACTIVE with no warning; the control reads `WarningThrusterInside`. Read it with `jawa/inspect_string` (`Thing.GetInspectString()`) — `get_cell_info` returns a className and stops.
state:    blocked

## C14 The sealed-room thruster test (CREATE's L8)
spec:     Sealed roofed room with a thruster inside -> predict INACTIVE. Thruster in the wall line with open sky aft -> predict ACTIVE.
verify:   EMPTY
criteria: send CREATE the RAW `jawa/inspect_string` lines, not a verdict — the whole roof derivation hangs off which sentence fires.
state:    blocked

## C15 Finish the sea seed sweep — 4 of 7
spec:     `python.exe src/RimMandrake/bridgetools/sea_seed_sweep.py 4`. Data, method and the near-miss: `observed/2026-08-14_sea_baseline_seeds.md`. ONLY when the owner is not at the keyboard — each iteration is a full RimWorld worldgen, it took loadavg to 22.58, and the owner read it as a hang. Every reading so far is the sea WITHOUT `JawaSeaShaper.dll` — a baseline we have never had, not a result.
verify:   EMPTY
criteria: seeds 5–7 land. What would reverse the S1 rescope (partition, not write): three-or-more bodies in the remaining seeds, or a wide water spread — nothing else. `25.0%` is NOT a constant: three seeds read exactly 25.0 and the fourth read **16.74**, so requirement 1 is a real gate. Do not author S1 until these land.
state:    ready

## C16 Score the sea gate — requirements 3 and 4 are miscalibrated until B1 ships
spec:     Per-requirement table: `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\worldgen_sea_spec.md`. A quicktest builds a FULL world — 119,904 tiles, `waterPct 25.0`, 2 bodies, `previewOnly:false`, in 127 ms — so the gate rehearses on disposable worlds without ever opening the planet page or the once-only Configure Factions screen.
verify:   EMPTY
criteria: do NOT score requirements 3 and 4 until B1's `world_stats` unit fix is deployed — `centroidLat` returns DEGREES against a FRACTIONAL 0.35–0.65 band, and `raggedness` counts tile EDGES where the spec means boundary TILES, up to 36x once squared. A correct world was already nearly rejected on this: 46.6° and 31.8° are 0.518 and 0.353, both inside the band. No candidate world is accepted on a partial pass; a full 5-of-5 pass is collectable (`perimeter`, `centroidLat`, `raggedness` are in the deployed binary — `strings -a -el` returns `{ tiles = {0}, pct = {1}, perimeter = {2}, raggedness = {3}, centroidLat = {4} }`, `JawaBenchTerrainTools.cs:3164-3178`).
state:    blocked

## C17 Worldgen — spend the ratified faction cut
spec:     `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` (`c269c6a`) — 21 untick / 6 keep, ratified, committed and UNSPENT. Executed by unticking factions on vanilla's Configure Factions page DURING the worldgen run; that page is seen ONCE and there is no fixing it afterwards without regenerating the world. Four rulings ride in the file header: R1 dangling refs, R2 Rebel Alliance stays suppressed, R3 vanilla `Empire` is a KEEP, R4 rough-outlander floor. There is no file we can write to suppress a faction — Faction Control's `density` is a CLUMPING RADIUS (`__result = dist < fd.Density;`), not a count, and the English key "setting to 0 disables the faction" is a pre-1.3 leftover. Before calling any missing faction a defect, grep `Jawa_Patches/` for its defName.
verify:   EMPTY
criteria: the generated world's faction roster matches the keep list. A quicktest map's roster PROVES NOTHING — a debug quicktest never visits the Configure Factions page, so every faction is present by default. State which map any census came from. Prior scale, from the deleted world: 53 factions across 107 settlements, of which the fiction-breakers held ~34.
state:    ready

## C18 `OuterRim_RebelAlliance` must be ABSENT at the next worldgen
spec:     One `jawa/list_factions` after worldgen. Control: `OuterRim_GalacticEmpire`, which must be PRESENT. Closes `EXPECTED_FAILURES` A3.
verify:   EMPTY
criteria: ABSENT is the DESIRED outcome — `RebelAlliance_Suppress.xml` does it deliberately — so PRESENT is the failure. Nothing in `Player.log` reports a faction that never generates; the only detection is looking on purpose. Observe, do not fix.
state:    ready

## C19 Live terrain edit — put the salt back in the dry lake bed
spec:     Geological Landforms hard-codes `SoftSand` on its dry-lake landform and the mod-side fix means editing a serialised NodeCanvas, so fix it LIVE on arrival. Target defName, verified: `Jawa_SaltCrust`, `src/Jawa/Jawa_Patches/Defs/TerrainDefs/JawaSaltCrust.xml:100`. Bound by BOTH a rect AND a source-terrain match, never terrain alone — a map-wide SoftSand->salt repaint erases the desert. Same session as worldgen, after rows 2 and 7. Not a blocker.
verify:   EMPTY
criteria: the deliverable is the CAPABILITY, not the pan — (a) can the bridge detect or be told a landform footprint, (b) set terrain over that region, (c) does it survive save/reload. First live evidence for tile-augmentation-on-approach, which has none (`design/Jawa/worldbuilding/tile_augmentation_catalogue.md`).
state:    ready

## C20 Re-shoot the twelve art screenshots
spec:     The 12 `NEEDS EYES` rows in `observed/2026-08-14_load_session.md` are NON-EVIDENCE: the Debug log window covers the CENTRE of the screen, which is exactly where `look()` puts the subject, and in `p5_004.png` and `p13_012.png` the subject is not in frame at all. `jawa/clear_ui` fixes it forward — closes every `Window_Dev`, drops the selection — and `rimbench.core.look()`/`.frame()` call it automatically. Closing the log by hand does not hold: auto-open-on-error.
verify:   EMPTY
criteria: twelve screenshots with the subject in frame and no dev window over it.
state:    ready

## C21 v1 row 3 — the rumour route, and does the quest RESOLVE
spec:     Spawn `Jawa_ClaimRumour` (`Jawa_ClaimRumour.xml:89-91` hands out `Jawa_TheClaim`, `rootMinPoints 0`), read it, and follow the quest to resolution. The quest already REGISTERS via `jawa/fire_quest questDef=Jawa_TheClaim points=800` — id 0, "The Claim", `State=NotYetAccepted`, `questCountAfter 1`, challengeRating 1, expiry 256,099 ticks, every field read back off `Find.QuestManager` after the call. The in-world-item route needs `rimworld/right_click_cell`, which is measured broken.
verify:   EMPTY
criteria: the quest fires from the rumour and RESOLVES — registration is not resolution.
state:    blocked

## C22 The ten art-fix mods — one spawn, one look each
spec:     Eight deployed and enabled; the two newest are `mandrake.phytokinbarkheadfix` @562 (donor @388) and `mandrake.kotorbandoliernorthfix` @**579** — deliberately outside the 556–563 art-fix slot because its donor `guy762.mm.kotorcore` sits at 572 and ships loose art. A loose PNG beats an AssetBundle regardless of order, but between two LOOSE files order decides, so a loose-art donor must be in `loadAfter` or the fix is invisible with no log line. Routes and click paths: `infrastructure/state/CREATE_TEST_PLAN.md`.
verify:   EMPTY
criteria: each fix renders in the facing it targets. Judge at DISPLAY size and render the tint — art can be correct at source and broken at render. Observation only.
state:    ready

## C23 Run `CREATE_TEST_PLAN.md` with its nine pre-flight corrections
spec:     `D:\Luke\dev\Rimworld\infrastructure\state\CREATE_TEST_PLAN.md` — eight art-fix mods, v1 row 3's `Jawa_ClaimRumour`, row 4's terrain plus the 619-cell ground hulk. Part 3 needs a FRESHLY GENERATED Desert / ExtremeDesert / AridShrubland map; a quicktest counts. Nine pre-flight corrections live in `infrastructure/state/AGENT_BRIDGE_state.md` — read them before typing at a live console: two are wrong parameters, one is a diagnostic string with no basis, and `ToolBelt` does not exist under that name. Also: `jawa/spawn_thing` DOES NOT EXIST — the call is vanilla `rimworld/spawn_thing`, or `jawa/spawn_batch` for more than one.
verify:   EMPTY
criteria: a screenshot is the evidence, a def query is not — every failure mode in the plan is silent.
state:    ready

## C24 Does Faction Customizer's settings dialog persist across worlds
spec:     One minute at the keyboard.
verify:   EMPTY
criteria: persists or does not — the roster's goodwill-cap mechanism depends on the answer.
state:    ready

## C25 `jawa/ideo_of` — verify the eleven, and measure whether NPC religion surfaces
spec:     `jawa/ideo_of` reads `Find.IdeoManager.IdeosListForReading` — an Ideo is a RUNTIME object, not a Def, so no def read can reach it. Believer counts split **colonists / otherOnMap / worldPawns**; it also exposes `PreceptDef.enabledForNPCFactions`. `ideologyActive:false` is a loud failure, never a count of zero.
verify:   EMPTY
criteria: diff the eleven built ideoligions against `faction_religions_spec.md`. Separately, `otherOnMap` measures how often NPC religion surfaces in play — the whole eleven-religion design is disciplined around "it rarely surfaces", which has NEVER been measured. A total alone would let the claim survive on the player colony's own believers. If it returns ~0, say so in the doc and stop treating the eleven as load-bearing.
state:    blocked

## C26 `jawa/biome_probe` — the 29 biome removals
spec:     `jawa/biome_probe find=<defName>` audits a removal across every biome in one call and needs NO map (`AllWildAnimals`/`AllWildPlants` build their own cache lazily, IL_0006). 28 of the 29 removals are UNEVIDENCED: `Scalars()` (`JawaBenchTerrainTools.cs:4111`) reads public instance FIELDS only, while `BiomeDef` keeps `wildAnimals`, `coastalWildAnimals`, `pollutionWildAnimals`, `diseases` and `allowedPackAnimals` PRIVATE and exposes `AllWildAnimals`/`AllWildPlants` as PROPERTIES — every other tool on this bridge is blind to them. The one removal ever looked at (Coastal dunes) was confirmed in two seconds. Record results at `design\Jawa\worldbuilding\cherrypick_inbox.md`.
verify:   EMPTY
criteria: each removal must report `spawning` / `zeroed` / `absent` against the DECLARED records — present-at-commonality-0 and absent are DIFFERENT defects, and the engine's own resolved lists drop a zeroed record exactly like a deleted one (`get_AllWildAnimals` yields a kind only if `CommonalityOfAnimal` or `…PollutionAnimal` or `…CoastalAnimal` > 0, IL_0055/0063/0071; `get_AllWildPlants` filters `CommonalityOfPlant > 0`, IL_0038).
state:    blocked

## C27 A coastal forsaken-crags tile
spec:     Roll one. It can roll Archipelago today, giving a permanently dark mostly-ocean map with zero new code.
verify:   EMPTY
criteria: does it read — this decides the deep.
state:    ready

## C28 Photograph the 25 vanilla mechs whose art is bundle-locked
spec:     Art is on disk for 55 of 80 (`data/mech_inventory.json`); the remaining 25 vanilla mechs are inside AssetBundles and cannot be rendered offline.
verify:   EMPTY
criteria: images for all 25 — unblocks the owner's mech review sheet, which is otherwise complete (axes committed in `data/mech_control_axes.md`).
state:    ready

## C29 Does `CharityRefused_Beggars` record without a `Charity_*` precept
spec:     ~2 min. The refusal hook is legal and measured: `CharityRefused_Beggars` fires when beggars leave empty-handed, and arresting them raises `CharityRefused_Beggars_Betrayed` (IL: `AnySignal(beggars.Killed, beggars.Arrested)`). Spec: `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\precept_the_unearned.md`. A `FactionDef` has no precept field; only a meme's `requireOne` forces one.
verify:   EMPTY
criteria: does the event record at all for a colony holding NO `Charity_*` precept. Blocks CREATE.
state:    ready

## C30 RimTunes tagging session `[v2]`
spec:     RimTunes has replaced the vanilla music system, dynamic mode is on (`enableDMS: True`), and `Config/RimTunes/` is EMPTY — it is scoring the game right now with nothing of ours in it. Answer two questions FIRST, both of which change how everything gets tagged: (1) what are the `Events` tags — the category exists in the language keys but the names are in neither the files nor the assembly; icons include `explosion.png` and `dove.png`; (2) do time-range tags mean clock time or position within a song — the dialog says "Play only during this part of the song" while the tag description says "Plays between {range}". Then confirm `SW_Sandstorm` and `SW_DrySandstorm` appear as weather tags (the assembly has `CreateBiomeTags` and `CreateWeatherTags`) — if they do we can score our own weather with no XML at all. Then tag: 102 songs auto-discovered; vanilla's 6 desert-appropriate relax tracks -> Require the desert biomes; the ~6 usable `Tense` tracks -> Require `Tense` (only 11 of 102 are tense and 5 of those are Caverns tracks locked to the fungal forest, so the real combat pool on a desert map is about six). Then back up `Config/RimTunes/` and `Config/Mod_3399705740_RimTunesMod.xml` to `deployed/config/` — hand tagging is otherwise unrecoverable. Context: `design/RimMandrake/music_protocol.md`.
verify:   EMPTY
criteria: both questions answered from the live dialog; the two weather tags present or absent.
state:    ready
